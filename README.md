# Bengio Marketplace

Claude Code plugins by Benjamin Giordano -- product development, workflow automation, and more.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add bengio777/bengio-marketplace
```

Then install plugins:

```
/plugin install prd-builder@bengio-marketplace
/plugin install build-journal@bengio-marketplace
```

## Available Plugins

### PRD Builder

Generate production-ready Product Requirements Documents through structured discovery, version coaching, and iterative refinement.

**What it does:** A 6-phase workflow backed by 10 reference files that takes you from "I have an idea" to a document ready to hand off to a developer or AI coding agent.

**Trigger phrases:**
- "I have an app idea"
- "Help me plan this product"
- "Write a PRD"
- "Scope this project"
- "What should I build first"
- "Help me ship this"

**Phases:**
1. Discovery interview
2. Version coaching (MVP vs. full product)
3. PRD generation from template
4. Quality review and scoring
5. Optional deep-dive modules (competitive analysis, revenue architecture, platform integration)
6. Implementation handoff

### Build Journal

Auto-captures build metadata during coding sessions and generates tiered retrospective documents.

**What it does:** Tracks what you built, how you built it, and what you learned. Includes a session-start hook that asks whether to enable tracking, and interview templates for end-of-session retrospectives.

**Trigger phrases:**
- "Build journal"
- "Generate retrospective"
- "Log this build"
- "Wrapping up the build"
- "Done for the day"
- "Closing out this session"

**Modes:**
- Full Retrospective -- when a build is complete
- Daily Recap -- end-of-day session summary

## Distribution

This marketplace supports three deployment configurations depending on your GitHub repo visibility:

| Scenario | GitHub Setting | Who Can Access | Install Command |
|----------|---------------|----------------|-----------------|
| **Private team** | Private repo + collaborator invites | Named team members only | Same `/plugin marketplace add` (requires GitHub access) |
| **Organizational** | Internal repo in a GitHub org | All org members | Same command (org members auto-authenticated) |
| **Public community** | Public repo | Anyone | Same command (no auth needed) |

This marketplace is currently **public**.

## License

MIT
