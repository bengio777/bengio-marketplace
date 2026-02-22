---
name: curation
description: >
  Use this skill when curating, scoring, or ranking news stories. Activates when
  the agent or user needs to "curate stories", "rank news", "score articles",
  "deduplicate headlines", "tier the stories", "filter noise from signal", or
  "prioritize the most important stories".
version: 2.0.0
---

# Tech News Curation

Score, deduplicate, and route raw stories into a 3-tab briefing. Quality over quantity.

## Step 1: Deduplicate

Scan the raw story list for duplicates — the same story reported by multiple sources.

**Deduplication rules:**
- Two stories are duplicates if they cover the same announcement, event, or development
- When merging duplicates, keep the URL from the most authoritative source:
  1. Official company blog (primary source) — highest preference
  2. Major tech publication (TechCrunch, Ars Technica, The Verge)
  3. Security publication (BleepingComputer, Dark Reading, SecurityWeek, Krebs)
  4. Newsletter or aggregator (Ben's Bites, Hacker News)
  5. Community source (Dev.to, Reddit, Twitter/X)
- Combine summary details from multiple sources if one adds useful context the other lacks
- Note multi-source coverage: stories covered by 3+ sources get a virality signal boost

## Step 2: Check Previous Briefing

If a previous day's briefing exists, read it and compare. Remove any story that:
- Appeared in the previous briefing with the same core information
- Is a follow-up with no meaningfully new information

Keep a story if:
- There is a significant update to a previously reported story
- Mark these as updates: "**Update:** ..." in the summary

## Step 3: Apply Quality Filters

Reject stories that match any of these criteria:

| Filter | Reject if... |
|--------|-------------|
| Stale | Published more than 48 hours ago (72 hours for breakthroughs tab) |
| Paywalled | Full content is behind a paywall with no summary available |
| Click-bait | Title is sensational but content is thin or speculative |
| Listicle | "Top 10...", "Best X tools...", "X things you need to know..." |
| Promotional | Sponsored content, press releases with no editorial angle |
| Trivial | Minor version bumps, routine maintenance, cosmetic changes |

## Step 4: Score Remaining Stories

Rate each surviving story on four dimensions (0-10 scale):

### Impact (weight: 0.30)
How many people does this affect?

| Score | Example |
|-------|---------|
| 9-10 | Major product launch (GPT-5, Claude 4), industry-defining announcement, critical CVE (CVSS 9.0+) |
| 7-8 | Significant feature release, large funding round (>$100M), policy change, actively exploited vuln |
| 5-6 | Notable update, medium funding round, meaningful research paper, major breach |
| 3-4 | Minor feature, small funding round, niche tool launch, routine advisory |
| 1-2 | Bug fix, internal change, limited-audience announcement |

### Novelty (weight: 0.25)
Is this genuinely new information?

| Score | Example |
|-------|---------|
| 9-10 | First report of a breaking announcement, previously unknown information |
| 7-8 | Official confirmation of rumored development, zero-day disclosure |
| 5-6 | New analysis or perspective on a known development |
| 3-4 | Summary of previously reported information with minor additions |
| 1-2 | Rehash of old news, no new information |

### Relevance (weight: 0.25)
How relevant to AI/tech practitioners and cybersecurity professionals?

| Score | Example |
|-------|---------|
| 9-10 | Core AI development, critical infrastructure vulnerability |
| 7-8 | Developer tools, frameworks, major threat campaign |
| 5-6 | Industry trends, business strategy, breach with lessons learned |
| 3-4 | Adjacent tech news, consumer product updates, routine patches |
| 1-2 | Tangentially related, entertainment, lifestyle tech |

### Source Authority (weight: 0.20)
How credible is the source?

| Score | Example |
|-------|---------|
| 9-10 | Official company blog, CISA advisory, peer-reviewed research, NVD |
| 7-8 | Major tech pub (TechCrunch, Ars Technica), security pub (Krebs, BleepingComputer) |
| 5-6 | Established newsletter, curated aggregator (Hacker News front page) |
| 3-4 | Community platform (Dev.to, Reddit), social media (Twitter/X) |
| 1-2 | Unknown blog, unverified social media account |

### Composite Score

```
composite = (impact * 0.30) + (novelty * 0.25) + (relevance * 0.25) + (authority * 0.20)
```

### Virality Boost

If a story was found across 3+ independent sources, add +0.5 to the composite score (capped at 10.0). This signals genuine significance rather than one outlet's coverage.

## Step 5: Route to Tabs by Category

Stories are routed to tabs based on their `category` field from research:

### Tab 1: AI News
- Stories with `category: ai-news`
- Assign tiers based on composite score:

| Tier | Composite Score | Target Count |
|------|----------------|--------------|
| Must-Read | >= 7.5 | 3-5 items |
| Worth Knowing | 5.0-7.4 | 5-8 items |
| On the Radar | 3.0-4.9 | 3-5 items |
| Drop | < 3.0 | — |

### Tab 2: AI Breakthroughs & Viral
- Stories with `category: breakthroughs`
- Include if: composite >= 8.0 **OR** found in 3+ sources (virality signal)
- **No tier headings** — flat list ordered by composite score
- Target: 3-6 items. If fewer than 3 qualify, it's fine — don't pad.

### Tab 3: Cyber Intel
- Stories with `category: cyber-intel`
- Route into 4 sections based on content:

| Section | Content |
|---------|---------|
| AI x Cyber | Stories at the intersection of AI and cybersecurity |
| Breaches & Incidents | Data breaches, ransomware, compromises |
| Active Threats | Actively exploited vulns, CISA KEV additions, zero-days |
| OSINT Signal | Interesting threat intel, APT reports, research |

- Within each section, order by composite score. If a section has 0 items, omit it.

### Cross-tab stories

If a story could fit multiple tabs (e.g., an AI-powered vulnerability scanner), place it in the tab where it has the highest relevance. Do not duplicate across tabs.

## Step 6: Order Within Tabs

- **AI News**: Order within each tier by composite score (highest first)
- **Breakthroughs**: Order by composite score (highest first)
- **Cyber Intel**: Order within each section by composite score (highest first)

Ties broken by: more recent > higher authority source > broader impact.

## Output

Pass the routed, ordered story list to the formatting step. Each story should carry:
- Title, URL, source name, summary
- Assigned tab + section/tier
- Composite score (for internal reference, not shown in output)
