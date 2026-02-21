---
description: Open the tech news briefing web viewer in your browser
allowed-tools: [Bash, Read]
---

# Open Tech News Viewer

1. Check if the Next.js dev server is running: `lsof -i :3000`
2. If not running, start it:
   ```
   cd /Users/benjamingiordano/Projects/tech-news-viewer && npm run dev &
   ```
3. Wait 3 seconds for the server to start
4. Open in the default browser: `open http://localhost:3000`
