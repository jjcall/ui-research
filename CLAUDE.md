# Design Research

A Claude skill/plugin for researching UI/UX patterns without leaving your editor. Decomposes design concepts into searchable sub-patterns, runs parallel searches across design sources (Dribbble, Behance, Mobbin, v0) and social platforms (Reddit, X, YouTube, HN), and presents results as a scannable summary or browsable HTML gallery.

## Quick Reference

```bash
# Run research
python scripts/design_research.py "planning mode UI"

# Run tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov

# Setup Playwright (optional, for Tier 0 screenshots)
python scripts/design_research.py --setup

# Show environment capabilities
python scripts/design_research.py --diagnose

# Config management
python scripts/design_research.py --config
python scripts/design_research.py --config set --scrapecreators-key YOUR_KEY

# Research history
python scripts/design_research.py --history
python scripts/design_research.py --rerun <id>
```

## Architecture

**Entry point**: `scripts/design_research.py` - CLI orchestration via argparse.

**Core library** (`scripts/lib/`):

| Module | Purpose |
|---|---|
| `schema.py` | Dataclasses: `SubPattern`, `Decomposition`, `Reference`, `Engagement`, `Gallery` |
| `decompose.py` | Concept decomposition with synonym expansion |
| `search.py` | Search query generation across all sources |
| `filter.py` | URL quality scoring, collection page detection |
| `images.py` | OG image extraction, CDN pattern matching |
| `screenshots.py` | Async Playwright full-page capture with MD5 caching |
| `social.py` | Reddit (ScrapeCreators), X, YouTube, HN search |
| `render.py` | Gallery HTML template rendering |
| `config.py` | Multi-source config: env vars > project `.env` > global `~/.config/design-research/.env` |

**Bundled data** (`data/`):
- `synonyms.json` - 100+ UI/UX pattern synonyms for term expansion
- `products.json` - Pattern-to-product mappings (e.g., kanban -> Linear, Trello)
- `sources.json` - Source metadata, CDN patterns, query templates
- `gallery-template.html` - Self-contained client-side gallery template

**Research flow**: Decompose concept -> Generate 20-30 parallel search queries -> Filter URLs by quality -> Extract images (Playwright or OG fallback) -> Present summary (Phase 1) -> Build HTML gallery on demand (Phase 2).

## Code Conventions

- **Python 3** with standard library only for core functionality
- **Type hints** throughout (Python 3.10+ style)
- **Dataclasses** with `.to_dict()` / `.from_dict()` for all serialization
- **Lazy loading** for data files (cached in module globals)
- **Optional imports** with graceful fallback (BeautifulSoup -> regex, Playwright -> OG images)
- **Google-style docstrings** for public functions
- **PEP 8** naming and formatting
- Each `scripts/lib/` module has a single responsibility - no circular dependencies

## Dependencies

No required dependencies. All optional:
- `beautifulsoup4 >= 4.12.0` - Better HTML parsing (regex fallback exists)
- `playwright >= 1.40.0` - Full-page screenshot capture
- `pytest >= 8.0.0` / `pytest-cov >= 4.1.0` - Testing

## Testing

Tests live in `tests/` with one test file per lib module. Fixtures in `tests/fixtures/`. All tests are unit tests using mocks - no external API calls needed.

## Key Design Decisions

- **Three-tier quality**: Tier 0 (Playwright screenshots) > Tier 1 (CLI image extraction) > Tier 2 (WebFetch OG images). Degrades gracefully.
- **Two-phase UX**: Fast summary first, heavy gallery second. Don't make users wait for screenshots they might not need.
- **Data-driven expansion**: Synonyms and product mappings are JSON files, not hardcoded. Edit the data to change behavior.
- **Client-side galleries**: Output is self-contained HTML with embedded JSON. No server needed.
- **Engagement-weighted ranking**: Reddit upvotes, YouTube views, HN scores all feed a unified scoring formula.

## Output

Generated galleries are saved to `.design-research-output/` with timestamps. This directory is gitignored.
