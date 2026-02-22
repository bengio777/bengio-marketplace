#!/usr/bin/env python3
"""Pre-fetch podcast data for the Weekly briefing's Podcasts tab.

Gathers episode metadata from Spotify API and Apple Podcasts Charts — zero LLM tokens.
Writes JSON to ~/.config/tech-news-briefing/prefetch/podcasts-YYYY-MM-DD.json

Spotify credentials: macOS Keychain service "tech-news-briefing-spotify"
  account = client_id, password = client_secret

Usage: python3 fetch-podcasts.py [--date YYYY-MM-DD] [--days 7]
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode
from base64 import b64encode

PREFETCH_DIR = Path.home() / ".config" / "tech-news-briefing" / "prefetch"
USER_AGENT = "BPG-Tech-News/2.0 (prefetch)"

# Tracked shows — Spotify show IDs
# To find a show ID: open in Spotify, copy link, extract ID from URL
TRACKED_SHOWS = {
    # AI / Tech
    "6UJ6cnotchKOCrzKm6O21B": "My First Million",
    "4kI3lwGJE4VKbbJkWkMFyc": "All-In Podcast",
    "6E709HRH7XaiZrMfgtNCun": "Hard Fork",
    "6fhXaOEt4VaTSIaEVHfO3Z": "The Vergecast",
    "5bC65RDzs4KRb4qHU3IbMM": "a16z Podcast",
    "2qmpMOC8QdCAJR2nqMQHAu": "The Artificial Intelligence Show",
    "0d9RC595XFGAeDHrXpmFJD": "Acquired",
    "7wZygk3mUUqBaQsLBOmkjN": "Latent Space",
    "2p7zZVwVF6Yk0Zsb4QmT7t": "Cognitive Revolution",
    "0gJwMh01bTTBRnuUBHTTQO": "TWIML AI Podcast",
    "2nEOFcgN4IjRGDjYM9VlqB": "Gradient Dissent",
    "0KxdEdeY2Wb3zr28dMlQva": "Practical AI",
    "3vBiDjHsJbXMSiSDcFyrLq": "Bloomberg Technology",
    "0e8IPkPohYFmI5PiLLxJUL": "Masters of Scale",
    # Security
    "4XPl3uEEL9hvqMkoZrzbx5": "Darknet Diaries",
    "3NnRsPnXQsCRrwOwg1e7Wr": "Smashing Security",
    "1KHjbpnmNpFmNTczQmTZlR": "Malicious Life",
    # Y Combinator
    "7BjjnYSmDLGBfNkDhJklIi": "Y Combinator",
}


def get_spotify_credentials() -> tuple[str, str] | None:
    """Read Spotify client credentials from macOS Keychain."""
    try:
        # Get client_id (stored as account name)
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "tech-news-briefing-spotify"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("  WARN: Spotify credentials not found in Keychain", file=sys.stderr)
            return None

        client_id = None
        for line in result.stdout.splitlines():
            if '"acct"' in line:
                client_id = line.split("=")[-1].strip().strip('"')
                break

        if not client_id:
            return None

        # Get client_secret (stored as password)
        result = subprocess.run(
            ["security", "find-generic-password",
             "-s", "tech-news-briefing-spotify", "-a", client_id, "-w"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return None

        client_secret = result.stdout.strip()
        return client_id, client_secret
    except Exception as e:
        print(f"  WARN: Keychain error: {e}", file=sys.stderr)
        return None


def get_spotify_token(client_id: str, client_secret: str) -> str | None:
    """Get Spotify access token using client_credentials flow."""
    auth = b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urlencode({"grant_type": "client_credentials"}).encode()
    req = Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("access_token")
    except (URLError, json.JSONDecodeError) as e:
        print(f"  WARN: Spotify auth failed: {e}", file=sys.stderr)
        return None


def fetch_spotify_episodes(token: str, show_id: str, show_name: str, since: datetime) -> list[dict]:
    """Fetch recent episodes from a Spotify show."""
    url = f"https://api.spotify.com/v1/shows/{show_id}/episodes?limit=10&market=US"
    req = Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    })
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError) as e:
        print(f"  WARN: Failed to fetch episodes for {show_name}: {e}", file=sys.stderr)
        return []

    results = []
    for ep in data.get("items", []):
        release = ep.get("release_date", "")
        try:
            release_dt = datetime.strptime(release, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if release_dt < since:
            continue

        results.append({
            "show": show_name,
            "show_id": show_id,
            "title": ep.get("name", ""),
            "description": (ep.get("description") or "")[:300],
            "url": ep.get("external_urls", {}).get("spotify", ""),
            "release_date": release,
            "duration_ms": ep.get("duration_ms", 0),
        })

    return results


def fetch_apple_charts() -> list[dict]:
    """Fetch Apple Podcasts Technology top 25 charts."""
    print("Fetching Apple Podcasts Technology Charts...", file=sys.stderr)
    # Apple RSS generator for top podcasts in Technology category (id=1318)
    url = "https://rss.applemarketingtools.com/api/v2/us/podcasts/top/25/podcasts.json?genre=1318"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError) as e:
        print(f"  WARN: Failed to fetch Apple Charts: {e}", file=sys.stderr)
        return []

    results = []
    for i, entry in enumerate(data.get("feed", {}).get("results", []), 1):
        results.append({
            "position": i,
            "name": entry.get("name", ""),
            "artist": entry.get("artistName", ""),
            "url": entry.get("url", ""),
            "apple_id": entry.get("id", ""),
        })

    print(f"  Found {len(results)} shows in Apple Tech Charts", file=sys.stderr)
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pre-fetch podcast data")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)", default=None)
    parser.add_argument("--days", help="Look back N days for episodes", type=int, default=7)
    args = parser.parse_args()

    target_date = args.date or datetime.now().strftime("%Y-%m-%d")
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    PREFETCH_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PREFETCH_DIR / f"podcasts-{target_date}.json"

    print(f"Podcast pre-fetch for {target_date}", file=sys.stderr)
    print(f"Looking back {args.days} days to {since.date()}", file=sys.stderr)

    result = {
        "date": target_date,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "spotify_episodes": [],
        "apple_charts": [],
    }

    # Spotify episodes
    creds = get_spotify_credentials()
    if creds:
        client_id, client_secret = creds
        token = get_spotify_token(client_id, client_secret)
        if token:
            print(f"Fetching episodes from {len(TRACKED_SHOWS)} shows...", file=sys.stderr)
            for show_id, show_name in TRACKED_SHOWS.items():
                episodes = fetch_spotify_episodes(token, show_id, show_name, since)
                if episodes:
                    print(f"  {show_name}: {len(episodes)} new episodes", file=sys.stderr)
                result["spotify_episodes"].extend(episodes)
        else:
            print("  Skipping Spotify (auth failed)", file=sys.stderr)
    else:
        print("  Skipping Spotify (no credentials)", file=sys.stderr)

    # Apple Charts
    result["apple_charts"] = fetch_apple_charts()

    # Summary
    total = len(result["spotify_episodes"]) + len(result["apple_charts"])
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {total} items to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
