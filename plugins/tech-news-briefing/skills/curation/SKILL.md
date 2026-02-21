---
name: curation
description: >
  Use this skill when curating, scoring, or ranking news stories. Activates when
  the agent or user needs to "curate stories", "rank news", "score articles",
  "deduplicate headlines", "tier the stories", "filter noise from signal", or
  "prioritize the most important stories".
version: 1.0.0
---

# Tech News Curation

Score, deduplicate, and tier raw stories into a prioritized briefing. Quality over quantity.

## Step 1: Deduplicate

Scan the raw story list for duplicates — the same story reported by multiple sources.

**Deduplication rules:**
- Two stories are duplicates if they cover the same announcement, event, or development
- When merging duplicates, keep the URL from the most authoritative source:
  1. Official company blog (primary source) — highest preference
  2. Major tech publication (TechCrunch, Ars Technica, The Verge)
  3. Newsletter or aggregator (Ben's Bites, Hacker News)
  4. Community source (Dev.to, Twitter/X)
- Combine summary details from multiple sources if one adds useful context the other lacks

## Step 2: Check Previous Briefing

If a previous day's briefing exists, read it and compare. Remove any story that:
- Appeared in the previous briefing with the same core information
- Is a follow-up with no meaningfully new information

Keep a story if:
- There is a significant update to a previously reported story (e.g., new details, official response, correction)
- Mark these as updates: "**Update:** ..." in the summary

## Step 3: Apply Quality Filters

Reject stories that match any of these criteria:

| Filter | Reject if... |
|--------|-------------|
| Stale | Published more than 48 hours ago |
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
| 9-10 | Major product launch (GPT-5, Claude 4), industry-defining announcement |
| 7-8 | Significant feature release, large funding round (>$100M), policy change |
| 5-6 | Notable update, medium funding round, meaningful research paper |
| 3-4 | Minor feature, small funding round, niche tool launch |
| 1-2 | Bug fix, internal change, limited-audience announcement |

### Novelty (weight: 0.25)
Is this genuinely new information?

| Score | Example |
|-------|---------|
| 9-10 | First report of a breaking announcement, previously unknown information |
| 7-8 | Official confirmation of rumored development, significant new details |
| 5-6 | New analysis or perspective on a known development |
| 3-4 | Summary of previously reported information with minor additions |
| 1-2 | Rehash of old news, no new information |

### Relevance (weight: 0.25)
How relevant to AI/tech practitioners and enthusiasts?

| Score | Example |
|-------|---------|
| 9-10 | Core AI development (new models, capabilities, safety research) |
| 7-8 | Developer tools, frameworks, APIs that practitioners use |
| 5-6 | Industry trends, business strategy with technical implications |
| 3-4 | Adjacent tech news, consumer product updates |
| 1-2 | Tangentially related, entertainment, lifestyle tech |

### Source Authority (weight: 0.20)
How credible is the source?

| Score | Example |
|-------|---------|
| 9-10 | Official company blog, peer-reviewed research |
| 7-8 | Major tech publication (TechCrunch, Ars Technica, The Verge) |
| 5-6 | Established newsletter (Ben's Bites), curated aggregator (Hacker News front page) |
| 3-4 | Community platform (Dev.to), social media (Twitter/X) |
| 1-2 | Unknown blog, unverified social media account |

### Composite Score

```
composite = (impact * 0.30) + (novelty * 0.25) + (relevance * 0.25) + (authority * 0.20)
```

## Step 5: Assign Tiers

| Tier | Composite Score | Item Limit | Description |
|------|----------------|------------|-------------|
| Must-Read | >= 7.5 | 3-5 items | Stories you cannot afford to miss today |
| Worth Knowing | 5.0-7.4 | 5-8 items | Important stories worth your attention |
| On the Radar | 3.0-4.9 | 3-5 items | Emerging stories to keep an eye on |
| Drop | < 3.0 | — | Not worth including |

**If a tier exceeds its limit**, keep only the highest-scoring items within that tier.

**If Must-Read has zero items**, do not force stories into it. It's acceptable for a quiet news day to have no must-read stories. Move the top Worth Knowing item up only if its composite is >= 7.0.

## Step 6: Order Within Tiers

Within each tier, order stories by composite score (highest first). If scores are tied, prefer:
1. More recent stories
2. Stories from higher-authority sources
3. Stories with broader impact

## Output

Pass the tiered, ordered story list to the formatting step. Each story should carry:
- Title, URL, source name, summary
- Assigned tier
- Composite score (for internal reference, not shown in output)
