#!/usr/bin/env python3
"""Pre-fetch OSINT data for the Cyber Intel tab.

Gathers structured data from public APIs and RSS feeds — zero LLM tokens.
Writes JSON to ~/.config/tech-news-briefing/prefetch/osint-YYYY-MM-DD.json

Sources:
  - CISA Known Exploited Vulnerabilities (KEV) catalog — last 48 hours
  - NVD (National Vulnerability Database) — CVSS >= 8.0, last 48 hours
  - RSS feeds: SANS ISC, Schneier on Security, Risky Business

Usage: python3 fetch-osint.py [--date YYYY-MM-DD]
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

PREFETCH_DIR = Path.home() / ".config" / "tech-news-briefing" / "prefetch"
USER_AGENT = "BPG-Tech-News/2.0 (prefetch)"


def fetch_json(url: str, timeout: int = 30) -> dict | list | None:
    """Fetch JSON from a URL. Returns None on failure."""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  WARN: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_text(url: str, timeout: int = 30) -> str | None:
    """Fetch text/XML from a URL. Returns None on failure."""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (URLError, TimeoutError) as e:
        print(f"  WARN: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_cisa_kev(cutoff: datetime) -> list[dict]:
    """Fetch CISA KEV entries added after cutoff."""
    print("Fetching CISA KEV catalog...", file=sys.stderr)
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    data = fetch_json(url, timeout=60)
    if not data or "vulnerabilities" not in data:
        return []

    results = []
    for vuln in data["vulnerabilities"]:
        added = vuln.get("dateAdded", "")
        try:
            added_dt = datetime.strptime(added, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if added_dt < cutoff:
            continue

        results.append({
            "source": "CISA KEV",
            "cve_id": vuln.get("cveID", ""),
            "vendor": vuln.get("vendorProject", ""),
            "product": vuln.get("product", ""),
            "name": vuln.get("vulnerabilityName", ""),
            "description": vuln.get("shortDescription", ""),
            "date_added": added,
            "due_date": vuln.get("dueDate", ""),
            "known_ransomware": vuln.get("knownRansomwareCampaignUse", "Unknown"),
        })

    print(f"  Found {len(results)} KEV entries since {cutoff.date()}", file=sys.stderr)
    return results


def fetch_nvd(cutoff: datetime) -> list[dict]:
    """Fetch NVD CVEs with CVSS >= 8.0 published after cutoff."""
    print("Fetching NVD high-severity CVEs...", file=sys.stderr)
    # NVD API 2.0 — public, no key required (rate limited to 5 req/30s)
    start = cutoff.strftime("%Y-%m-%dT%H:%M:%S.000")
    end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000")
    url = (
        f"https://services.nvd.nist.gov/rest/json/cves/2.0"
        f"?pubStartDate={start}&pubEndDate={end}"
        f"&cvssV3Severity=HIGH&cvssV3Severity=CRITICAL"
        f"&resultsPerPage=50"
    )
    data = fetch_json(url, timeout=60)
    if not data or "vulnerabilities" not in data:
        return []

    results = []
    for item in data["vulnerabilities"]:
        cve = item.get("cve", {})
        cve_id = cve.get("id", "")
        descriptions = cve.get("descriptions", [])
        desc_en = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

        # Extract CVSS score
        metrics = cve.get("metrics", {})
        cvss_score = None
        cvss_vector = None
        for key in ["cvssMetricV31", "cvssMetricV30"]:
            if key in metrics and metrics[key]:
                cvss_data = metrics[key][0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore")
                cvss_vector = cvss_data.get("baseSeverity", "")
                break

        if cvss_score is not None and cvss_score < 8.0:
            continue

        results.append({
            "source": "NVD",
            "cve_id": cve_id,
            "description": desc_en[:300],
            "cvss_score": cvss_score,
            "cvss_severity": cvss_vector,
            "published": cve.get("published", ""),
        })

    print(f"  Found {len(results)} high-severity CVEs since {cutoff.date()}", file=sys.stderr)
    return results


def fetch_rss(url: str, name: str, cutoff: datetime) -> list[dict]:
    """Fetch items from an RSS/Atom feed published after cutoff."""
    print(f"Fetching RSS: {name}...", file=sys.stderr)
    xml_text = fetch_text(url)
    if not xml_text:
        return []

    results = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  WARN: Failed to parse RSS from {name}: {e}", file=sys.stderr)
        return []

    # Handle both RSS 2.0 and Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # Try RSS 2.0 items
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()

        if title and link:
            results.append({
                "source": name,
                "title": title,
                "url": link,
                "description": description[:300],
                "pub_date": pub_date,
            })

    # Try Atom entries if no RSS items found
    if not results:
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
            link_el = entry.find("atom:link", ns)
            link = link_el.get("href", "") if link_el is not None else ""
            summary = (entry.findtext("atom:summary", namespaces=ns) or "").strip()

            if title and link:
                results.append({
                    "source": name,
                    "title": title,
                    "url": link,
                    "description": summary[:300],
                })

    # Limit to most recent items (RSS feeds may not support date filtering well)
    results = results[:10]
    print(f"  Found {len(results)} items from {name}", file=sys.stderr)
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pre-fetch OSINT data")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()

    if args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    PREFETCH_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREFETCH_DIR / f"osint-{target_date}.json"

    print(f"OSINT pre-fetch for {target_date}", file=sys.stderr)
    print(f"Cutoff: {cutoff.isoformat()}", file=sys.stderr)

    result = {
        "date": target_date,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cisa_kev": fetch_cisa_kev(cutoff),
        "nvd_cves": fetch_nvd(cutoff),
        "rss_feeds": {},
    }

    # RSS feeds
    rss_sources = [
        ("https://isc.sans.edu/rssfeed.xml", "SANS ISC"),
        ("https://www.schneier.com/feed/atom/", "Schneier on Security"),
        ("https://risky.biz/feeds/risky-business/", "Risky Business"),
    ]
    for url, name in rss_sources:
        items = fetch_rss(url, name, cutoff)
        result["rss_feeds"][name] = items

    # Summary
    total = (
        len(result["cisa_kev"])
        + len(result["nvd_cves"])
        + sum(len(v) for v in result["rss_feeds"].values())
    )

    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {total} items to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
