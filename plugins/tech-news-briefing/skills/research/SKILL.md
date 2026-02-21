---
name: research
description: >
  Use this skill when researching tech news from multiple sources. Activates when
  the agent or user needs to "search for news", "research tech stories", "gather
  headlines", "check news sources", "find recent tech announcements", or "scan
  sources for today's news".
version: 1.0.0
---

# Tech News Research

Research the latest tech news by systematically querying 12 sources. Prioritize freshness and breadth.

## Source Query Strategy

Execute searches in this order. Use WebSearch for most sources and WebFetch for sources with known direct URLs.

### Group 1: Direct-Access Sources (WebFetch)

Fetch these pages directly and extract recent posts:

1. **Anthropic Blog**
   - WebFetch `https://www.anthropic.com/news`
   - Extract: post titles, dates, URLs, and first-paragraph summaries
   - Look for: Claude updates, safety research, company announcements

2. **OpenAI Blog**
   - WebFetch `https://openai.com/news/`
   - Extract: post titles, dates, URLs, and first-paragraph summaries
   - Look for: GPT updates, product launches, research papers

3. **Ben's Bites Newsletter**
   - WebFetch `https://bensbites.beehiiv.com/`
   - Extract: latest newsletter items with links
   - Look for: curated AI product launches, funding, tools

### Group 2: Search-Based Sources (WebSearch)

For each source, include the current date in queries to get fresh results.

4. **Hacker News**
   - Query: `site:news.ycombinator.com AI OR "machine learning" OR "large language model" OR Claude OR OpenAI`
   - Also try: `Hacker News top stories AI today [current date]`
   - Look for: trending technical discussions, new tools, research

5. **Ars Technica**
   - Query: `site:arstechnica.com AI OR "artificial intelligence" OR tech [current month year]`
   - Look for: deep technical analysis, policy, research coverage

6. **The Verge**
   - Query: `site:theverge.com AI OR tech news [current month year]`
   - Look for: product announcements, industry news, consumer tech

7. **TechCrunch**
   - Query: `site:techcrunch.com AI OR startup OR funding [current month year]`
   - Look for: funding rounds, product launches, startup coverage

### Group 3: Twitter/X Monitoring (WebSearch)

8. **Key accounts**
   - Query: `site:x.com (@AnthropicAI OR @alexalbert__ OR @OpenAI OR @GoogleDeepMind) [current month year]`
   - Also try individual account searches if the combined query returns limited results
   - Look for: product announcements, release notes, research highlights

### Group 4: Supplementary Sources (WebSearch)

9. **Microsoft AI**
   - Query: `site:microsoft.com AI blog OR "Azure AI" OR Copilot [current month year]`
   - Look for: Azure AI updates, Copilot features, research

10. **Meta AI**
    - Query: `site:ai.meta.com OR "Meta AI" blog [current month year]`
    - Look for: Llama updates, open-source releases, research

11. **Dev.to**
    - Query: `site:dev.to AI OR "machine learning" OR "LLM" popular [current month year]`
    - Look for: developer tutorials, hands-on guides, tool comparisons

12. **Product Hunt**
    - Query: `site:producthunt.com AI tools [current month year]`
    - Look for: new AI product launches, trending tools

## Data Capture

For each story found, record:

| Field | Description |
|-------|-------------|
| `title` | Headline or post title |
| `url` | Direct link to the story |
| `source` | Source name (e.g., "Anthropic Blog", "TechCrunch") |
| `summary` | 1-2 sentence description of the content |
| `date` | Publish date (approximate if not explicit) |

## Error Handling

- If a WebFetch fails (timeout, 403, etc.), fall back to WebSearch for that source
- If a WebSearch returns no results, try broadening the query (remove date constraint)
- Log any source that returns zero results — include in the final report
- Never stop the pipeline because one source failed. Continue with remaining sources.

## Output

Produce a raw list of all stories found across all sources. Do not score or filter at this stage — that is the curation skill's job. Include duplicates if they exist; deduplication happens during curation.
