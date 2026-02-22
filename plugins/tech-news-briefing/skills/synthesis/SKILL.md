---
name: synthesis
description: >
  Use this skill when synthesizing patterns across multiple daily briefings into
  a weekly or monthly recap. Activates when the agent needs to "synthesize the
  week's news", "find cross-day patterns", "create a weekly recap", "identify
  persistent stories", "rank the week's themes", or "write analysis paragraphs".
version: 1.0.0
---

# News Synthesis

Analyze a week (or month) of daily briefings to extract patterns, persistent themes, and meaningful analysis.

## Input

Read all daily briefings from the target period. Each daily briefing is a markdown file at:
```
/Users/benjamingiordano/BPG_Tech-News/YYYY/week-WW/YYYY-MM-DD.md
```

## Step 1: Extract Stories Across Days

Build a unified story list from all dailies in the period. For each story, note:
- Which day(s) it appeared
- Whether it evolved across days (initial report → update → resolution)
- Its tier/section from the daily briefing

## Step 2: Identify Persistent Stories

A **persistent story** appeared across 2+ days or had significant follow-up coverage. These are the week's biggest stories.

Rank persistent stories by:
1. Number of days covered
2. Highest tier achieved (Must-Read > Worth Knowing > On the Radar)
3. Total coverage volume

## Step 3: Detect Themes

Group stories into emerging themes. Common patterns:
- **Product launches**: Multiple companies shipping in same space
- **Funding waves**: Cluster of funding announcements in a sector
- **Security campaigns**: Related vulnerabilities or threat actor activity
- **Research breakthroughs**: Connected papers or capability demonstrations
- **Policy/regulation**: Government or industry body actions

For each theme:
- Name it concisely (2-5 words)
- List the contributing stories
- Write a 2-3 sentence analysis paragraph explaining the pattern and its significance

## Step 4: Track Story Arcs

For stories that evolved across days, write a brief narrative arc:
- **Day 1**: Initial report
- **Day N**: Update/development
- **Resolution**: Current status

## Step 5: Generate "By the Numbers"

Extract quantifiable data points from the week:
- Total funding announced ($ amount)
- Number of CVEs/vulnerabilities disclosed
- Number of product launches
- Any notable metrics from stories (users, revenue, benchmark scores)

## Output

Produce structured content for the synthesis/recap tabs:

### For Weekly Recap
- **Top persistent stories** (ranked, with day count and arc summary)
- **Emerging themes** (named, with contributing stories and analysis)
- **By the Numbers** (key metrics from the week)

### For Monthly Recap
- **Month's defining stories** (top 10 persistent across weeks)
- **Trend Lines** (themes that strengthened/weakened over the month)
- **By the Numbers** (aggregated monthly metrics)
- **What to Watch** (stories/themes likely to develop next month)
