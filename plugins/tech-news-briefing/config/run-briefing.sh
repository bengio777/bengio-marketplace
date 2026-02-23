#!/bin/bash
# run-briefing.sh — Wrapper for launchd to run tech news briefings
# Location: ~/.config/tech-news-briefing/run-briefing.sh
#
# Usage: run-briefing.sh [daily|weekly|monthly]
#   daily   — 3-tab briefing (AI News, Breakthroughs, Cyber Intel)   [default]
#   weekly  — 4-tab deep dive with podcasts
#   monthly — long-form retrospective
#
# How it works:
#   1. Pre-fetch structured data (OSINT feeds, podcast charts) using Python
#   2. Build a self-contained prompt by inlining command + skills + template
#   3. Pass the full prompt to `claude -p` (no plugin discovery needed)

set -euo pipefail

# --- Configuration ---
BRIEFING_DIR="/Users/benjamingiordano/BPG_Tech-News"
PLUGIN_DIR="/Users/benjamingiordano/bengio-marketplace/plugins/tech-news-briefing"
LOG_DIR="$HOME/.config/tech-news-briefing/logs"
CADENCE="${1:-daily}"
DATE=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/${DATE}-${CADENCE}.log"

# Ensure PATH includes claude CLI, python3, and homebrew
export PATH="/Users/benjamingiordano/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Prevent nested-session errors if invoked from within Claude Code
unset CLAUDECODE 2>/dev/null || true

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# --- Logging ---
exec > >(tee -a "$LOG_FILE") 2>&1

echo "========================================"
echo "Tech News Briefing — ${DATE} (${CADENCE})"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "========================================"

# --- Pre-fetch (non-fatal) ---
echo ""
echo "--- Pre-fetch phase ---"

# OSINT pre-fetch (for daily and weekly)
if [[ "$CADENCE" == "daily" || "$CADENCE" == "weekly" ]]; then
    echo "Running OSINT pre-fetch..."
    python3 "${PLUGIN_DIR}/scripts/fetch-osint.py" --date "$DATE" || {
        echo "WARN: OSINT pre-fetch failed (non-fatal), continuing..."
    }
fi

# Podcast pre-fetch (for weekly only)
if [[ "$CADENCE" == "weekly" ]]; then
    echo "Running podcast pre-fetch..."
    python3 "${PLUGIN_DIR}/scripts/fetch-podcasts.py" --date "$DATE" --days 7 || {
        echo "WARN: Podcast pre-fetch failed (non-fatal), continuing..."
    }
fi

echo "--- Pre-fetch complete ---"
echo ""

# --- Build self-contained prompt ---
# Instead of "Run /tech-news-briefing:briefing" (which claude -p can't resolve),
# we inline the full command body + referenced skills + template into one prompt.
echo "--- Building prompt ---"

# Strip YAML frontmatter from a markdown file (everything before second ---)
strip_frontmatter() {
    awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$1"
}

# Resolve ${CLAUDE_PLUGIN_ROOT} references to actual path
resolve_plugin_root() {
    sed "s|\${CLAUDE_PLUGIN_ROOT}|${PLUGIN_DIR}|g"
}

PROMPT_FILE=$(mktemp)
trap "rm -f $PROMPT_FILE" EXIT

case "$CADENCE" in
    daily)
        {
            echo "# INSTRUCTIONS"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/commands/briefing.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Research Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/research/SKILL.md"
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Curation Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/curation/SKILL.md"
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Formatting Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/formatting/SKILL.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Daily Template"
            echo ""
            cat "${PLUGIN_DIR}/templates/daily.md"
        } > "$PROMPT_FILE"
        ;;
    weekly)
        {
            echo "# INSTRUCTIONS"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/commands/briefing-weekly.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Synthesis Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/synthesis/SKILL.md"
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Podcasts Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/podcasts/SKILL.md"
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Formatting Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/formatting/SKILL.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Weekly Template"
            echo ""
            cat "${PLUGIN_DIR}/templates/weekly.md"
        } > "$PROMPT_FILE"
        ;;
    monthly)
        {
            echo "# INSTRUCTIONS"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/commands/briefing-monthly.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Synthesis Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/synthesis/SKILL.md"
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Formatting Skill"
            echo ""
            strip_frontmatter "${PLUGIN_DIR}/skills/formatting/SKILL.md" | resolve_plugin_root
            echo ""
            echo "---"
            echo ""
            echo "# REFERENCE: Monthly Template"
            echo ""
            cat "${PLUGIN_DIR}/templates/monthly.md"
        } > "$PROMPT_FILE"
        ;;
    *)
        echo "ERROR: Unknown cadence '${CADENCE}'. Use: daily, weekly, or monthly."
        exit 1
        ;;
esac

PROMPT_LINES=$(wc -l < "$PROMPT_FILE")
echo "Prompt built: ${PROMPT_LINES} lines"
echo "--- Starting Claude ---"
echo ""

# --- Run Claude ---
cd "$BRIEFING_DIR"

# Read prompt from temp file and pass as argument.
# $() inside double quotes preserves all special characters.
claude -p \
  --model sonnet \
  --dangerously-skip-permissions \
  --max-budget-usd 2.00 \
  "$(cat "$PROMPT_FILE")"

EXIT_CODE=$?

echo ""

# --- Trigger Vercel rebuild (non-fatal) ---
if [[ $EXIT_CODE -eq 0 ]]; then
    VERCEL_HOOK=$(security find-generic-password -s tech-news-briefing-vercel-hook -w 2>/dev/null || true)
    if [[ -n "$VERCEL_HOOK" ]]; then
        echo "Triggering Vercel deploy..."
        curl -s -X POST "$VERCEL_HOOK" > /dev/null && echo "Vercel deploy triggered." || echo "WARN: Vercel deploy hook failed (non-fatal)"
    fi
fi

echo "========================================"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "Exit code: ${EXIT_CODE}"
echo "========================================"

# --- Cleanup old logs (keep 30 days) ---
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
