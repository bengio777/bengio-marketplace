---
description: Generate a monthly tech news retrospective (1st of month)
allowed-tools: [WebSearch, WebFetch, Read, Write, Bash, Glob, Grep, TodoWrite]
model: sonnet
---

# Generate Monthly Tech News Retrospective

Execute the monthly retrospective pipeline — synthesize the previous month's weekly recaps into a long-form review.

1. **Date context** — Determine today's date. The retrospective covers the previous month. Calculate the previous month and year. The output path is `/Users/benjamingiordano/BPG_Tech-News/YYYY/YYYY-MM-recap.md`. Create the directory if needed.

2. **Load weekly recaps** — Read all weekly recaps from the previous month. Find them by scanning week directories in the year folder:
   ```
   /Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/week-WW-recap.md
   ```
   A weekly recap belongs to the previous month if any of its daily briefings fall within that month. If no weekly recaps exist, fall back to reading individual daily briefings.

3. **Load daily briefings** — Also read the daily briefings from the previous month to supplement the weeklies with any stories that were dropped during weekly synthesis.

4. **Synthesize** — Follow the `synthesis` skill with monthly scope:
   - **Month in Review**: The 10 most defining stories of the month. For each, write a 2-3 sentence analysis covering what happened, why it matters, and current status. Rank by persistence across weeks and overall impact.
   - **Trend Lines**: Identify 3-5 themes that strengthened or weakened over the month. For each, describe the trajectory and what's driving it.
   - **By the Numbers**: Aggregate metrics across the month (total funding, CVEs, product launches, notable benchmarks).
   - **Podcast Highlights**: The 5 most relevant podcast episodes from the month's weekly recaps. Brief note on why each is worth a listen.
   - **What to Watch**: 3-5 stories or themes likely to develop next month. Brief rationale for each.

5. **Format** — Use the template at `${CLAUDE_PLUGIN_ROOT}/templates/monthly.md`. Monthly recaps are **long-form** with no tab markers — just H2 sections:
   - Month in Review
   - Trend Lines
   - By the Numbers
   - Podcast Highlights
   - What to Watch

   Writing rules:
   - Analysis paragraphs encouraged — this is a retrospective, not a link list
   - Use specific data points, quotes, and metrics
   - Active voice, no hedging, no emoji
   - Include links to source articles where relevant
   - Total length: 1500-3000 words

6. **Save** — Write the retrospective to the output path.

7. **Publish to GitHub** — Commit and push:
   ```
   git -C /Users/benjamingiordano/BPG_Tech-News add YYYY/YYYY-MM-recap.md
   git -C /Users/benjamingiordano/BPG_Tech-News commit -m "monthly: YYYY-MM retrospective"
   git -C /Users/benjamingiordano/BPG_Tech-News push origin main
   ```

8. **Email delivery** — Send the retrospective via email:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/send-email.py /Users/benjamingiordano/BPG_Tech-News/YYYY/YYYY-MM-recap.md
   ```

9. **Report** — Summarize: weeks covered, stories analyzed, top themes identified, file path, git/email status.
