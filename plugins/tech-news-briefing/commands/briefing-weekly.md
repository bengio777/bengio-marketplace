---
description: Generate a weekly tech news recap (Sunday deep dive)
allowed-tools: [WebSearch, WebFetch, Read, Write, Bash, Glob, Grep, TodoWrite]
model: sonnet
---

# Generate Weekly Tech News Recap

Execute the weekly recap pipeline — synthesize the week's daily briefings into a 4-tab deep dive with podcasts.

1. **Date context** — Determine today's date and ISO week number. The output path is `/Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/week-WW-recap.md`. Create the directory if needed.

2. **Load daily briefings** — Read all daily briefings from this week's directory (`/Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/YYYY-MM-DD.md`). List the files and read each one. If fewer than 3 dailies exist, log a warning but continue.

3. **Load pre-fetch data** — Check for pre-fetched data files at `~/.config/tech-news-briefing/prefetch/`:
   - `osint-YYYY-MM-DD.json` — CISA KEV entries, NVD CVEs, RSS items
   - `podcasts-YYYY-MM-DD.json` — Spotify episodes from 18 tracked shows, Apple Charts top 25

4. **Synthesize** — Follow the `synthesis` skill:
   - Extract all stories across the week's dailies
   - Identify persistent stories (appeared 2+ days)
   - Detect emerging themes with analysis paragraphs
   - Track story arcs (initial report → update → resolution)
   - Generate "By the Numbers" metrics

5. **Curate podcasts** — Follow the `podcasts` skill:
   - Match pre-fetched Spotify episodes to the week's stories and themes
   - Cross-reference with Apple Charts for chart positions
   - Categorize into: News-Connected, Trending, Discovery Pick
   - If no podcast data exists, omit the Podcasts tab

6. **Format** — Follow the `formatting` skill with these adaptations for weekly:
   - Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/weekly.md`
   - Use `<!-- tab: -->` markers: `Week in AI`, `Breakthroughs Recap`, `Cyber Weekly`, `Podcasts`
   - **Week in AI**: Top persistent AI stories (ranked) + emerging themes with analysis paragraphs
   - **Breakthroughs Recap**: Week's standout breakthroughs with context on why they matter
   - **Cyber Weekly**: Persistent threats, week's incidents, security metrics
   - **Podcasts**: Use the podcast item format: `**[Title](url)** — Show: *Name*. Connects to: [relevance]. *#N Apple Tech Charts*`
   - Analysis paragraphs are allowed (2-3 sentences) in weekly — this is a deep dive, not just links

7. **Save** — Write the recap to the output path.

8. **Publish to GitHub** — Commit and push:
   ```
   git -C /Users/benjamingiordano/BPG_Tech-News add YYYY/week-WW/week-WW-recap.md
   git -C /Users/benjamingiordano/BPG_Tech-News commit -m "weekly: week-WW recap"
   git -C /Users/benjamingiordano/BPG_Tech-News push origin main
   ```

9. **Email delivery** — Send the recap via email:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/send-email.py /Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/week-WW-recap.md
   ```

10. **Report** — Summarize: dailies read, stories synthesized, persistent stories found, themes identified, podcast episodes matched, file path, git/email status.
