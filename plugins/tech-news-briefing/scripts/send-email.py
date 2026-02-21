#!/usr/bin/env python3
"""Send tech news briefing via Google Workspace SMTP.

Usage: python3 send-email.py /path/to/YYYY-MM-DD.md

Credentials are read from macOS Keychain:
  - Service "tech-news-briefing-smtp": account = FROM email, password = app password
  - Service "tech-news-briefing-to": account = "tech-news-briefing", password = TO email
"""

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


def get_to_email():
    """Get TO email address from Keychain."""
    return get_keychain_password("tech-news-briefing-to", "tech-news-briefing")


def send_briefing(briefing_path):
    """Read briefing and send via SMTP."""
    path = Path(briefing_path)
    if not path.exists():
        raise FileNotFoundError(f"Briefing file not found: {briefing_path}")

    content = path.read_text(encoding="utf-8")
    date_str = path.stem  # e.g., "2026-02-21"
    subject = f"Tech News Briefing -- {date_str}"

    from_email, password = get_smtp_credentials()
    to_email = get_to_email()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"BPG Tech News <{from_email}>"
    msg["To"] = to_email

    text_part = MIMEText(content, "plain", "utf-8")
    msg.attach(text_part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(from_email, password)
        server.send_message(msg)

    print(f"Briefing emailed to {to_email}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <briefing-file-path>", file=sys.stderr)
        sys.exit(1)

    try:
        send_briefing(sys.argv[1])
    except Exception as e:
        print(f"Email delivery failed: {e}", file=sys.stderr)
        sys.exit(1)
