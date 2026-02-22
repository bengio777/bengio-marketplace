---
name: podcasts
description: >
  Use this skill when curating podcast episodes for the weekly briefing. Activates
  when the agent needs to "match podcasts to news", "curate podcast episodes",
  "find relevant episodes", "check podcast charts", or "build the podcasts tab".
version: 1.0.0
---

# Podcast Curation

Match podcast episodes to the week's news stories, identify charting shows, and pick a discovery recommendation.

## Input

1. **Pre-fetch data** — Read `~/.config/tech-news-briefing/prefetch/podcasts-YYYY-MM-DD.json` which contains:
   - `spotify_episodes`: Recent episodes from tracked shows (title, description, show, URL, release date)
   - `apple_charts`: Current Apple Podcasts Technology top 25 (position, name, artist, URL)

2. **Week's stories** — The curated stories from the synthesis step (persistent stories, themes)

## Step 1: Match Episodes to News

For each Spotify episode, check if it covers any of the week's stories or themes:
- Compare episode title and description against story titles and summaries
- Look for explicit mentions of companies, products, CVEs, or people from the week's news
- A match means the episode discusses the same topic, not just tangentially mentions it

Assign a **relevance note** to each matched episode:
```
Connects to: [brief description of which story/theme it covers]
```

## Step 2: Flag Charting Shows

Cross-reference Spotify episodes against the Apple Charts data:
- If a tracked show appears in the Apple Tech top 25, note its chart position
- Format: `#N Apple Tech Charts`

## Step 3: Categorize Episodes

Sort matched episodes into sections:

### News-Connected Episodes
Episodes that directly cover one of the week's stories or themes. These are the most valuable — listeners get audio deep-dives on stories they already know about.

Order by: number of story connections (more = first), then chart position.

### Trending in Tech Podcasts
Episodes from charting shows that don't directly connect to this week's news but cover relevant tech/AI/security topics.

Order by: chart position.

### Discovery Pick
Choose ONE episode from a less well-known show that covers an interesting angle not represented in the week's news. This introduces the reader to new voices.

Criteria:
- Not from a show that charts regularly
- Covers a genuinely interesting topic
- Episode is well-produced (check description quality as a proxy)

## Step 4: Format for Output

Each podcast item follows this format:
```markdown
- **[Episode Title](url)** — Show: *Show Name*. Connects to: [relevance note]. *#N Apple Tech Charts*
```

Rules:
- Episode title links to the Spotify episode URL
- Show name is italicized after "Show:"
- Relevance note explains the connection to the week's news
- Chart position appears only if the show is in the Apple top 25
- No emoji

## Output

Pass the formatted podcast sections to the weekly formatting step:
- **News-Connected Episodes** (3-8 items)
- **Trending in Tech Podcasts** (2-4 items)
- **Discovery Pick** (1 item)

If pre-fetch data is missing or empty, note in the output that podcasts were unavailable and omit the Podcasts tab entirely.
