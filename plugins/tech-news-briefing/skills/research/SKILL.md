---
name: research
description: >
  Use this skill when researching tech news from multiple sources. Activates when
  the agent or user needs to "search for news", "research tech stories", "gather
  headlines", "check news sources", "find recent tech announcements", or "scan
  sources for today's news".
version: 2.0.0
---

# Tech News Research

Research the latest tech news by systematically querying sources across three domains: AI, Breakthroughs/Viral, and Cybersecurity. Prioritize freshness and breadth.

## Pre-fetch Data

Before running searches, check for pre-fetched data files:

```
~/.config/tech-news-briefing/prefetch/osint-YYYY-MM-DD.json
~/.config/tech-news-briefing/prefetch/podcasts-YYYY-MM-DD.json
```

If the OSINT file exists, read it and incorporate the data directly into the Cyber Intel tab — these are structured records from CISA KEV and NVD that don't need WebSearch.

## Source Query Strategy

Execute searches in this order. Use WebSearch for most sources and WebFetch for sources with known direct URLs. Tag each story with a **category** for downstream routing.

### Group 1: AI News Sources

These feed the **AI News** tab.

1. **Anthropic Blog** — WebFetch `https://www.anthropic.com/news`
   - Category: `ai-news`
   - Look for: Claude updates, safety research, company announcements

2. **OpenAI Blog** — WebFetch `https://openai.com/news/`
   - Category: `ai-news`
   - Look for: GPT updates, product launches, research papers

3. **Ben's Bites Newsletter** — WebFetch `https://bensbites.beehiiv.com/`
   - Category: `ai-news`
   - Look for: curated AI product launches, funding, tools

4. **Hacker News (AI)** — WebSearch `site:news.ycombinator.com AI OR "machine learning" OR "large language model" OR Claude OR OpenAI`
   - Category: `ai-news`
   - Look for: trending technical discussions, new tools

5. **Ars Technica** — WebSearch `site:arstechnica.com AI OR "artificial intelligence" [current month year]`
   - Category: `ai-news`
   - Look for: deep technical analysis, policy, research coverage

6. **The Verge** — WebSearch `site:theverge.com AI OR tech news [current month year]`
   - Category: `ai-news`
   - Look for: product announcements, industry news

7. **TechCrunch** — WebSearch `site:techcrunch.com AI OR startup OR funding [current month year]`
   - Category: `ai-news`
   - Look for: funding rounds, product launches, startup coverage

8. **Microsoft AI** — WebSearch `site:microsoft.com AI blog OR "Azure AI" OR Copilot [current month year]`
   - Category: `ai-news`
   - Look for: Azure AI updates, Copilot features

9. **Meta AI** — WebSearch `site:ai.meta.com OR "Meta AI" blog [current month year]`
   - Category: `ai-news`
   - Look for: Llama updates, open-source releases

10. **Twitter/X (AI)** — WebSearch `site:x.com (@AnthropicAI OR @alexalbert__ OR @OpenAI OR @GoogleDeepMind) [current month year]`
    - Category: `ai-news`
    - Look for: product announcements, release notes

### Group 2: Breakthrough & Viral Sources

These feed the **AI Breakthroughs & Viral** tab. Focus on stories with high wow-factor from the past 72 hours.

11. **arXiv / Research papers** — WebSearch `site:arxiv.org AI breakthrough OR "state of the art" OR "large language model" [current month year]`
    - Category: `breakthroughs`
    - Look for: papers trending on social media, benchmark-breaking results

12. **Product Hunt** — WebSearch `site:producthunt.com AI tools [current month year]`
    - Category: `breakthroughs`
    - Look for: viral AI product launches, trending tools

13. **GitHub Trending** — WebSearch `github trending AI OR "machine learning" repositories [current month year]`
    - Category: `breakthroughs`
    - Look for: viral open-source projects, new frameworks

14. **Reddit AI** — WebSearch `site:reddit.com/r/MachineLearning OR site:reddit.com/r/artificial breakthrough OR "new model" [current month year]`
    - Category: `breakthroughs`
    - Look for: community excitement around new capabilities

15. **Dev.to** — WebSearch `site:dev.to AI OR "machine learning" OR "LLM" popular [current month year]`
    - Category: `breakthroughs`
    - Look for: hands-on demos, tool comparisons that go viral

### Group 3: Cybersecurity & OSINT Sources

These feed the **Cyber Intel** tab. If pre-fetch OSINT data exists, use it for CISA/NVD items and focus WebSearch on editorial sources.

16. **BleepingComputer** — WebSearch `site:bleepingcomputer.com vulnerability OR breach OR ransomware [current month year]`
    - Category: `cyber-intel`
    - Look for: active exploits, breach reports, malware analysis

17. **Dark Reading** — WebSearch `site:darkreading.com vulnerability OR threat OR breach [current month year]`
    - Category: `cyber-intel`
    - Look for: threat intelligence, industry analysis

18. **SecurityWeek** — WebSearch `site:securityweek.com vulnerability OR cyber OR breach [current month year]`
    - Category: `cyber-intel`
    - Look for: vulnerability disclosures, APT reports

19. **Krebs on Security** — WebSearch `site:krebsonsecurity.com [current month year]`
    - Category: `cyber-intel`
    - Look for: investigative cybersecurity reporting

20. **The Record** — WebSearch `site:therecord.media cyber OR vulnerability OR ransomware [current month year]`
    - Category: `cyber-intel`
    - Look for: nation-state activity, policy, major incidents

21. **Hacker News (Security)** — WebSearch `site:news.ycombinator.com vulnerability OR security OR CVE OR breach [current month year]`
    - Category: `cyber-intel`
    - Look for: trending security discussions

22. **r/netsec** — WebSearch `site:reddit.com/r/netsec [current month year]`
    - Category: `cyber-intel`
    - Look for: vulnerability research, exploit PoCs, CTF writeups

23. **Twitter/X (InfoSec)** — WebSearch `site:x.com (@caborsi OR @GossiTheDog OR @vaborsi OR @MalwareHunterTeam) [current month year]`
    - Category: `cyber-intel`
    - Look for: real-time threat intel, zero-day announcements

## Data Capture

For each story found, record:

| Field | Description |
|-------|-------------|
| `title` | Headline or post title |
| `url` | Direct link to the specific article page (NEVER a homepage or section page — see URL rules below) |
| `source` | Source name (e.g., "BleepingComputer", "TechCrunch") |
| `summary` | 1-2 sentence description of the content |
| `date` | Publish date (approximate if not explicit) |
| `category` | One of: `ai-news`, `breakthroughs`, `cyber-intel` |

## URL Rules

Every story **must** link to the specific article page. Homepage and section-page URLs are strictly prohibited.

**Rejected URL patterns** (these are homepages/section pages, NOT article links):
- `https://thehackernews.com/`
- `https://www.bleepingcomputer.com/`
- `https://techcrunch.com/`
- `https://arstechnica.com/`
- Any URL that is just a domain root or ends in a category path like `/security/` or `/ai/`

**If you cannot find the direct article URL:**
1. Search again with the article's headline in quotes: `"exact headline text" site:source.com`
2. If still not found, search for the headline without site restriction to find the story on any source
3. If the story truly cannot be linked to a specific article, **drop the story entirely** — do not use a homepage URL as a placeholder

## Error Handling

- If a WebFetch fails (timeout, 403, etc.), fall back to WebSearch for that source
- If a WebSearch returns no results, try broadening the query (remove date constraint)
- Log any source that returns zero results — include in the final report
- Never stop the pipeline because one source failed. Continue with remaining sources.

## Output

Produce a raw list of all stories found across all sources, each tagged with its category. Do not score or filter at this stage — that is the curation skill's job. Include duplicates if they exist; deduplication happens during curation.
