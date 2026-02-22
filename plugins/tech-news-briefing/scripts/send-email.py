#!/usr/bin/env python3
"""Send tech news briefing via Google Workspace SMTP.

Usage: python3 send-email.py /path/to/YYYY-MM-DD.md

Credentials are read from macOS Keychain:
  - Service "tech-news-briefing-smtp": account = FROM email, password = app password
  - Service "tech-news-briefing-to": account = "tech-news-briefing", password = comma-separated TO emails
"""

import re
import sys
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


def get_keychain_password(service, account):
    """Retrieve a password from macOS Keychain."""
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Keychain lookup failed for service={service}, account={account}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def get_smtp_credentials():
    """Get FROM email and SMTP password from Keychain."""
    # Query the entry without -w to parse the account name (FROM email)
    result = subprocess.run(
        ["security", "find-generic-password", "-s", "tech-news-briefing-smtp"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Cannot find SMTP credentials in Keychain: {result.stderr.strip()}")

    from_email = None
    for line in result.stdout.splitlines():
        if '"acct"' in line:
            from_email = line.split("=")[-1].strip().strip('"')
            break

    if not from_email:
        raise RuntimeError("Cannot parse FROM email from Keychain entry")

    password = get_keychain_password("tech-news-briefing-smtp", from_email)
    return from_email, password


def get_to_emails():
    """Get TO email addresses from Keychain (comma-separated)."""
    raw = get_keychain_password("tech-news-briefing-to", "tech-news-briefing")
    return [addr.strip() for addr in raw.split(",") if addr.strip()]


def markdown_to_html(md):
    """Convert briefing markdown to simple HTML for email rendering."""
    lines = md.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Skip tab markers
        if stripped.startswith("<!-- tab:"):
            continue

        # Horizontal rules
        if stripped == "---":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append('<hr style="border:none;border-top:1px solid #e4e4e7;margin:24px 0;">')
            continue

        # H1
        if stripped.startswith("# "):
            html_lines.append(f'<h1 style="font-size:1.5em;font-weight:700;margin:0 0 8px;">{stripped[2:]}</h1>')
            continue

        # H2
        if stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f'<h2 style="font-size:1.2em;font-weight:600;margin:24px 0 12px;color:#3f3f46;">{stripped[3:]}</h2>')
            continue

        # List items with markdown links/bold
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append('<ul style="padding-left:20px;margin:0;">')
                in_list = True
            item = stripped[2:]
            # Convert **[text](url)** to <a><strong>
            item = re.sub(
                r'\*\*\[(.+?)\]\((.+?)\)\*\*',
                r'<a href="\2" style="color:#2563eb;text-decoration:none;font-weight:600;">\1</a>',
                item
            )
            # Convert remaining **text** to <strong>
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            # Convert *text* to <em>
            item = re.sub(r'\*(.+?)\*', r'<em>\1</em>', item)
            html_lines.append(f'<li style="margin:12px 0;line-height:1.6;">{item}</li>')
            continue

        # Bold metadata line
        if stripped.startswith("**") and "|" in stripped:
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            html_lines.append(f'<p style="color:#71717a;margin:0 0 16px;">{text}</p>')
            continue

        # Italic footer lines
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            text = stripped.strip("*")
            html_lines.append(f'<p style="font-size:0.85em;color:#a1a1aa;margin:4px 0;"><em>{text}</em></p>')
            continue

        # Empty lines
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Fallback paragraph
        html_lines.append(f'<p style="margin:8px 0;line-height:1.6;">{stripped}</p>')

    if in_list:
        html_lines.append("</ul>")

    body = "\n".join(html_lines)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:20px;color:#18181b;max-width:680px;margin:0 auto;padding:24px;line-height:1.6;">
{body}
</body>
</html>"""


def detect_cadence(content):
    """Detect briefing cadence from content."""
    if "| Weekly |" in content:
        return "Weekly"
    if "| Monthly |" in content or "Monthly Recap" in content:
        return "Monthly"
    return "Daily"


def send_briefing(briefing_path):
    """Read briefing and send via SMTP."""
    path = Path(briefing_path)
    if not path.exists():
        raise FileNotFoundError(f"Briefing file not found: {briefing_path}")

    content = path.read_text(encoding="utf-8")
    date_str = path.stem  # e.g., "2026-02-21" or "week-08-recap"
    cadence = detect_cadence(content)
    subject = f"{cadence} Tech Briefing -- {date_str}"

    from_email, password = get_smtp_credentials()
    to_emails = get_to_emails()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"BPG Tech News <{from_email}>"
    msg["To"] = ", ".join(to_emails)

    # Plain text fallback
    text_part = MIMEText(content, "plain", "utf-8")
    msg.attach(text_part)

    # HTML version with larger font
    html_content = markdown_to_html(content)
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, password)
        server.send_message(msg)

    print(f"{cadence} briefing emailed to {', '.join(to_emails)}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <briefing-file-path>", file=sys.stderr)
        sys.exit(1)

    try:
        send_briefing(sys.argv[1])
    except Exception as e:
        print(f"Email delivery failed: {e}", file=sys.stderr)
        sys.exit(1)
