# UI Research Plugin

Research UI/UX patterns for any concept. This Claude plugin decomposes design concepts into searchable patterns, runs parallel searches across design sources (Dribbble, Behance, Mobbin, v0, etc.), extracts images, and generates a browsable HTML gallery.

## Features

- **Smart Decomposition**: Breaks concepts into sub-patterns with synonym expansion and product-aware queries
- **Multi-Source Search**: Searches across Dribbble, Behance, Mobbin, Figma Community, v0.dev, and more
- **Image Extraction**: Extracts OG images and screenshots where possible
- **Interactive Gallery**: Generates a self-contained HTML gallery with filtering and search
- **Tier-Based Execution**: Adapts to available tools (Playwright, WebFetch, etc.)

## Installation

### Option 1: From Marketplace (Recommended)

```bash
claude plugin install uir
```

Then invoke with:
```
/uir:research planning mode UI
```

### Option 2: Local Development

```bash
# Clone the repo
git clone https://github.com/jjcall/ui-research.git ~/Code/ui-research

# Run Claude with plugin directory
claude --plugin-dir ~/Code/ui-research
```

Then invoke with:
```
/uir:research planning mode UI
```

### Option 3: As a Standalone Skill (for `/uir` command without namespace)

If you prefer the shorter `/uir` command (without the `:research` suffix), install as a standalone skill:

```bash
# Create skill directory
mkdir -p ~/.claude/skills/uir

# Copy skill files
cp ~/Code/ui-research/SKILL.md ~/.claude/skills/uir/
cp -r ~/Code/ui-research/scripts ~/.claude/skills/uir/
cp -r ~/Code/ui-research/data ~/.claude/skills/uir/
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

## Publishing to Marketplace

To make this plugin available via `claude plugin install uir`:

1. Host a marketplace JSON file (can be on GitHub, your own server, etc.)
2. Users add your marketplace: `claude marketplace add <url>`
3. Users install: `claude plugin install uir`

Example marketplace entry:
```json
{
  "plugins": [
    {
      "name": "uir",
      "version": "1.0.0",
      "description": "Research UI/UX patterns for any concept",
      "repository": "https://github.com/jjcall/ui-research"
    }
  ]
}
```

## License

MIT
