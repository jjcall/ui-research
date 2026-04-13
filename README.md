# UI Research Plugin

Research UI/UX patterns for any concept. This Claude plugin decomposes design concepts into searchable patterns, runs parallel searches across design sources (Dribbble, Behance, Mobbin, v0, etc.), extracts images, and generates a browsable HTML gallery.

## Features

- **Smart Decomposition**: Breaks concepts into sub-patterns with synonym expansion and product-aware queries
- **Multi-Source Search**: Searches across Dribbble, Behance, Mobbin, Figma Community, v0.dev, and more
- **Image Extraction**: Extracts OG images and screenshots where possible
- **Interactive Gallery**: Generates a self-contained HTML gallery with filtering and search
- **Tier-Based Execution**: Adapts to available tools (Playwright, WebFetch, etc.)

## Installation

No pip install required - the plugin uses only Python standard library.

```bash
# Clone to your Claude plugins directory
cd ~/.claude/plugins
git clone https://github.com/jjcall/ui-research.git
```

**Optional enhancements:**
```bash
# Better HTML parsing (falls back to regex without this)
pip install beautifulsoup4

# Tier 0 full-page screenshots
pip install playwright && playwright install chromium
```

## Usage

### As a Claude Skill

Trigger phrases:
- "UI research for [concept]"
- "Design inspiration for [concept]"
- "How do other apps handle [concept]"

### CLI

```bash
# Research a concept
python scripts/ui_research.py "planning mode UI"

# Check environment
python scripts/ui_research.py --diagnose

# Use mock data (for testing)
python scripts/ui_research.py --mock "kanban board"

# View research history
python scripts/ui_research.py --history

# Re-run previous research
python scripts/ui_research.py --rerun abc123
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

## License

MIT
