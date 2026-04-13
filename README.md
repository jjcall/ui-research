# Design Research

Research UI/UX patterns without leaving your editor. Give it a concept like "planning mode UI" and it searches design galleries (Dribbble, Behance, Mobbin, Figma), social platforms (Reddit, X, Hacker News), and video tutorials (YouTube). Shows you what designers are building AND what they're saying about it.

## What it does

You ask for research. It breaks your concept into sub-patterns—kanban boards, timeline views, calendar UIs, whatever makes sense—and runs parallel searches across design sources AND social platforms. Then it shows you a grouped summary:

```
📋 Found 67 references for "planning mode UI"

Design References (34)
  ★ dribbble.com/shots/25799561 — Kanban Dashboard Redesign [img]
  ★ behance.net/gallery/198234567 — Task Board UI Kit [img]
  ...

Discussions (18)
  ★ r/UI_Design: "How Linear nailed planning mode" [847↑ • 234💬]
  ★ @frankchimero: "The best planning UIs let you zoom..." [1.2K♥ • 89↺]
  ...

Tutorials (8)
  ★ youtube.com/watch?v=abc — Building Planning UI in Figma [12K▶]
  ...

───────────────────────────────────────
67 total • 34 designs • 18 discussions • 8 tutorials
Top voices: @frankchimero, r/UI_Design, Juxtopposed
```

From here you can say "build gallery", "open in tabs", "show insights", or keep refining.

## Install

```bash
claude marketplace add github:jjcall/design-research
claude plugin install design-research
```

Then:
```
/design-research planning mode UI
```

For local dev, clone the repo and point Claude at it:
```bash
git clone https://github.com/jjcall/design-research.git ~/Code/design-research
claude --plugin-dir ~/Code/design-research
```

## After the summary

| Say this | It does this |
|----------|--------------|
| "build gallery" | Generates HTML with screenshots |
| "open in tabs" | Opens all refs in your browser |
| "open top 10" | Opens the first 10 |
| "open dribbble only" | Just Dribbble refs |
| "show insights" | Sentiment analysis of discussions |
| "more kanban examples" | Runs more searches |
| "remove medium" | Filters out a source |

## Configuration

API keys unlock better search results for Reddit, X, and other platforms.

### Quick setup

```bash
python scripts/design_research.py --config set --scrapecreators-key YOUR_KEY
```

This saves your key to `~/.config/design-research/.env` with secure permissions.

### Check current config

```bash
python scripts/design_research.py --config
```

Outputs:
```
Config source: global:~/.config/design-research/.env

ScrapeCreators: ✓ configured (seQGRbkj...)
  → Reddit API search enabled

OpenAI: ✓ using Codex auth
```

### Config priority

Keys are loaded in this order (highest priority first):
1. Environment variables (`export SCRAPECREATORS_API_KEY=...`)
2. Per-project config (`.claude/design-research.env` in your project)
3. Global config (`~/.config/design-research/.env`)

### Supported keys

| Key | Purpose | Where to get it |
|-----|---------|-----------------|
| `SCRAPECREATORS_API_KEY` | Reddit API search | [scrapecreators.com](https://scrapecreators.com) (100 free credits) |
| `OPENAI_API_KEY` | OpenAI fallback (optional) | [platform.openai.com](https://platform.openai.com) |

Without a ScrapeCreators key, the plugin falls back to WebSearch for Reddit. Works fine, just fewer engagement metrics.

## Why Playwright

Some sites don't play nice with direct image fetching. Figma Community returns 403. Mobbin needs JS to render. So the plugin uses Playwright for screenshots when you build the gallery.

One-time setup:
```bash
python scripts/design_research.py --setup
```

Test it works:
```bash
python scripts/design_research.py --screenshot "https://figma.com/community/file/123456"
```

## CLI reference

```bash
# Research
python scripts/design_research.py "concept"           # Research a concept
python scripts/design_research.py --diagnose          # Check environment

# Screenshots
python scripts/design_research.py --setup             # Install Playwright
python scripts/design_research.py --screenshot URL    # Test a screenshot
python scripts/design_research.py --clear-cache       # Clear screenshot cache

# History
python scripts/design_research.py --history           # Past research
python scripts/design_research.py --open abc123       # Open a gallery
python scripts/design_research.py --open-tabs abc123  # Open refs in tabs

# Configuration
python scripts/design_research.py --config            # Show current config
python scripts/design_research.py --config set --scrapecreators-key KEY
python scripts/design_research.py --config path       # Print config file path
```

## Filtering

Search results include a lot of noise—collection pages, browse pages, search result pages. The plugin filters those out and only keeps individual designs.

★ means it matched a known pattern for an individual page (like `/shots/123` on Dribbble).
○ means unknown—might be good, might not.

## Tests

```bash
python -m unittest discover tests -v
```

## License

MIT
