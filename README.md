# UI Research

Research UI/UX patterns without leaving your editor. Give it a concept like "planning mode UI" and it searches Dribbble, Behance, Mobbin, Figma Community, and other design sources. It filters out the junk (search result pages, browse pages) and shows you actual designs.

## What it does

You ask for research. It breaks your concept into sub-patterns—kanban boards, timeline views, calendar UIs, whatever makes sense—and runs parallel searches. Then it shows you a summary in the terminal so you can decide what to do next.

```
📋 Found 34 references for "planning mode UI"

Kanban Boards (12)
  ★ dribbble.com/shots/25799561 — Kanban Dashboard Redesign [img]
  ★ behance.net/gallery/198234567 — Task Board UI Kit [img]
  ○ medium.com/design/kanban-patt... — Kanban UX Patterns
  ... +9 more

Timeline Views (8)
  ★ mobbin.com/explore/screens/abc — Linear Roadmap Screen [img]
  ...

───────────────────────────────────────
34 total • 24 high-quality (★) • 12 filtered as collections
```

From here you can say "build gallery" to get a browsable HTML file, "open in tabs" to just open everything in your browser, or keep refining.

## Install

```bash
claude marketplace add github:jjcall/ui-research
claude plugin install uir
```

Then:
```
/uir planning mode UI
```

For local dev, clone the repo and point Claude at it:
```bash
git clone https://github.com/jjcall/ui-research.git ~/Code/ui-research
claude --plugin-dir ~/Code/ui-research
```

## After the summary

| Say this | It does this |
|----------|--------------|
| "build gallery" | Generates HTML with screenshots |
| "open in tabs" | Opens all refs in your browser |
| "open top 10" | Opens the first 10 |
| "open dribbble only" | Just Dribbble refs |
| "more kanban examples" | Runs more searches |
| "remove medium" | Filters out a source |

## Why Playwright

Some sites don't play nice with direct image fetching. Figma Community returns 403. Mobbin needs JS to render. So the plugin uses Playwright for screenshots when you build the gallery.

One-time setup:
```bash
python scripts/ui_research.py --setup
```

Test it works:
```bash
python scripts/ui_research.py --screenshot "https://figma.com/community/file/123456"
```

## CLI reference

```bash
python scripts/ui_research.py --diagnose          # Check environment
python scripts/ui_research.py --setup             # Install Playwright
python scripts/ui_research.py --screenshot URL    # Test a screenshot
python scripts/ui_research.py --history           # Past research
python scripts/ui_research.py --open abc123       # Open a gallery
python scripts/ui_research.py --open-tabs abc123  # Open refs in tabs
python scripts/ui_research.py --clear-cache       # Clear screenshots
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
