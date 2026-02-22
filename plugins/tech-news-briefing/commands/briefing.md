---
description: Generate a 3-tab tech news briefing for today
allowed-tools: [WebSearch, WebFetch, Read, Write, Bash, Glob, Grep, TodoWrite]
model: sonnet
---

# Generate Tech News Briefing

Execute the full news briefing pipeline for a 3-tab daily briefing (AI News, AI Breakthroughs & Viral, Cyber Intel).

1. **Date context** — Determine today's date, ISO week number, and output path (`/Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/YYYY-MM-DD.md`). Create the directory if needed.

2. **Load pre-fetch data** — Check for pre-fetched data files at `~/.config/tech-news-briefing/prefetch/`:
   - `osint-YYYY-MM-DD.json` — CISA KEV entries, NVD CVEs, RSS items
   - `podcasts-YYYY-MM-DD.json` — Spotify episodes, Apple Charts (used by weekly only, skip for daily)

   If the OSINT file exists, read it and use the data to seed the Cyber Intel tab. These structured records bypass WebSearch — incorporate them directly as `cyber-intel` category stories.

3. **Research** — Follow the `research` skill. Search all 23 sources using WebSearch and WebFetch. Tag each story with a `category` (`ai-news`, `breakthroughs`, or `cyber-intel`). Include the current date in queries for freshness. Capture title, URL, source, summary, date, and category for each story.

4. **Curate** — Follow the `curation` skill:
   - Deduplicate stories (prefer authoritative sources)
   - Check against yesterday's briefing (remove repeats, keep updates)
   - Apply quality filters
   - Score each story (Impact 0.30 + Novelty 0.25 + Relevance 0.25 + Authority 0.20)
   - Route to tabs by category:
     - **AI News**: tier into Must-Read (>= 7.5), Worth Knowing (5.0-7.4), On the Radar (3.0-4.9)
     - **Breakthroughs**: include if composite >= 8.0 or 3+ source coverage. Flat list.
     - **Cyber Intel**: route into 4 sections (AI x Cyber, Breaches & Incidents, Active Threats, OSINT Signal)

5. **Format** — Follow the `formatting` skill. Produce the final markdown using the template at `${CLAUDE_PLUGIN_ROOT}/templates/daily.md`. Use `<!-- tab: Name -->` markers for each tab. Each item: `**[Title](url)** — summary. *Source: Name*`. No emoji. Omit empty tabs/sections entirely.

6. **Save** — Write the briefing to the output path. Confirm it was saved.

7. **Publish to GitHub** — Commit and push the briefing to the remote repository. Run these commands in sequence using Bash:
   ```
   git -C /Users/benjamingiordano/BPG_Tech-News add YYYY/week-WW/YYYY-MM-DD.md
   git -C /Users/benjamingiordano/BPG_Tech-News commit -m "briefing: YYYY-MM-DD"
   git -C /Users/benjamingiordano/BPG_Tech-News push origin main
   ```
   Replace YYYY, WW, MM, DD with the actual date values from Step 1. If the push fails, log the error but continue to the next step.

8. **Email delivery** — Send the briefing via email using the Python script:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/send-email.py /Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/YYYY-MM-DD.md
   ```
   If the script fails (non-zero exit), log the error but do not treat it as a pipeline failure. The briefing is already saved and pushed.

9. **Report** — Summarize: stories scanned vs. included, breakdown by tab (and tier/section within each tab), any unreachable sources, file path, git push status, email delivery status.
