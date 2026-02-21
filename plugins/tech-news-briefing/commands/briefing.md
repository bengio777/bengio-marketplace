---
description: Generate a tech news briefing for today
allowed-tools: [WebSearch, WebFetch, Read, Write, Bash, Glob, Grep, TodoWrite]
model: sonnet
---

# Generate Tech News Briefing

Execute the full news briefing pipeline:

1. **Date context** — Determine today's date, ISO week number, and output path (`/Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/YYYY-MM-DD.md`). Create the directory if needed.

2. **Research** — Follow the `research` skill. Search all 12 sources using WebSearch and WebFetch. Include the current date in queries for freshness. Capture title, URL, source, summary, and date for each story.

3. **Curate** — Follow the `curation` skill. Deduplicate stories, check against yesterday's briefing, apply quality filters, score each story (Impact 0.30 + Novelty 0.25 + Relevance 0.25 + Authority 0.20), assign tiers (Must-Read >= 7.5, Worth Knowing 5.0-7.4, On the Radar 3.0-4.9, drop < 3.0).

4. **Format** — Follow the `formatting` skill. Produce the final markdown using the template at `${CLAUDE_PLUGIN_ROOT}/templates/briefing.md`. Each item: `**[Title](url)** — summary. *Source: Name*`. No emoji. Omit empty tier sections.

5. **Save** — Write the briefing to the output path. Confirm it was saved.

6. **Report** — Summarize: stories scanned vs. included, breakdown by tier, any unreachable sources, file path.
