# UI Research Plugin

Research UI/UX patterns for any concept. This Claude plugin decomposes design concepts into searchable patterns, runs parallel searches across design sources (Dribbble, Behance, Mobbin, v0, etc.), extracts images, and generates a browsable HTML gallery.

## Features

- **Smart Decomposition**: Breaks concepts into sub-patterns with synonym expansion and product-aware queries
- **Multi-Source Search**: Searches across Dribbble, Behance, Mobbin, Figma Community, v0.dev, and more
- **Image Extraction**: Extracts OG images and screenshots where possible
- **Interactive Gallery**: Generates a self-contained HTML gallery with filtering and search
- **Tier-Based Execution**: Adapts to available tools (Playwright, WebFetch, etc.)

## Installation

### Install from GitHub (Recommended)

```bash
# Add the repo as a marketplace
claude marketplace add github:jjcall/ui-research

# Install the plugin
claude plugin install uir
```

Then invoke with:
```
/uir planning mode UI
```

### Local Development

```bash
# Clone the repo
git clone https://github.com/jjcall/ui-research.git ~/Code/ui-research

# Run Claude with plugin directory
claude --plugin-dir ~/Code/ui-research
```

Then invoke with:
```
/uir planning mode UI
```

## Usage

### Trigger Phrases

- `/uir:research planning mode UI`
- "UI research for [concept]"
- "Design inspiration for [concept]"
- "How do other apps handle [concept]"

### CLI

```bash
# Research a concept
python scripts/ui_research.py "planning mode UI"

# Check environment (tier detection)
python scripts/ui_research.py --diagnose

# Use mock data (for testing)
python scripts/ui_research.py --mock "kanban board"

# View research history
python scripts/ui_research.py --history

# Re-run previous research
python scripts/ui_research.py --rerun abc123
```

## Optional Dependencies

No pip install required - the plugin uses only Python standard library.

**Optional enhancements:**
```bash
# Better HTML parsing (falls back to regex without this)
pip install beautifulsoup4

# Tier 0 full-page screenshots
pip install playwright && playwright install chromium
```

## Tiers

| Tier | Environment | Image Source | Gallery Size |
|------|-------------|--------------|--------------|
| 0 | CLI + Playwright | Full-page screenshots | 10-30MB |
| 1 | Cursor (restricted) | None (links only) | 50-100KB |
| 2 | Cursor + WebFetch | OG images extracted | 2-5MB |
| 3 | Chrome extension | Live captures | 10-30MB |

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=scripts/lib --cov-report=html
```

## How Distribution Works

This GitHub repo acts as its own marketplace. Users:
1. Add it: `claude marketplace add github:jjcall/ui-research`
2. Install: `claude plugin install uir`

The plugin name (`uir`) matches the skill name, so users get `/uir` directly (no namespace).

## License

MIT
