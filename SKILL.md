---
name: uir
description: Research UI/UX patterns for any concept. Use when the user asks for 'ui research', 'design inspiration', 'moodboard', 'UI examples', or 'how do other apps handle X'. Decomposes concepts into searchable patterns, searches design sources (Dribbble, Behance, Mobbin, v0), and presents a scannable summary. User can then request a full HTML gallery.
---

# UI Research Skill

Research UI/UX patterns for any concept. Uses a **two-phase flow**:

1. **Phase 1 (default)**: Search, filter, and display a scannable summary in the terminal
2. **Phase 2 (on demand)**: Build a browsable HTML gallery with images

This lets you review results quickly before committing to the heavier gallery generation.

## Trigger Phrases

- "ui research for {concept}"
- "design inspiration for {concept}"
- "how do other apps handle {concept}"
- "moodboard for {concept}"
- "find UI examples of {concept}"

## Step 1: Parse User Intent

When the user requests UI research, extract:

```
CONCEPT: {the design concept to research}
QUERY_TYPE: inspiration | comparison | deep-dive
CONTEXT: {any additional context provided}
```

Display your parsing:
```
📋 Researching: {CONCEPT}
   Type: {QUERY_TYPE}
   Context: {CONTEXT if any}
```

## Step 2: Smart Decomposition

Break the concept into 5-8 searchable sub-patterns using three passes:

### Pass 1: Direct Decomposition
Identify the obvious, directly-related patterns:

```
"planning mode UI" →
  - Task lists and todos
  - Kanban boards
  - Timeline/Gantt views
  - Calendar interfaces
  - View switcher patterns
```

### Pass 2: Lateral Expansion
Identify adjacent patterns the user didn't ask for but will find useful:

```
Adjacent patterns:
  - Approval gates
  - AI reasoning visualization
  - Mode toggle UX
  - Bulk editing
  - Drag-and-drop interactions
```

### Pass 3: Semantic Expansion
For each pattern, use bundled data files to expand terms:

1. **Load synonym data** from `data/synonyms.json`
2. **Load product mappings** from `data/products.json`
3. **Generate queries** combining base terms + synonyms + product-specific searches

Example expansion for "kanban board":
```
Base terms: ["kanban", "task board"]
Synonyms: ["card view", "column layout", "swim lanes", "board view"]
Product queries: ["Linear board", "Trello UI", "Notion kanban", "Asana board"]
```

### Decomposition Output

Display the decomposition to the user:
```
🔍 Decomposed into {N} patterns:

1. **Kanban Boards** — Card-based task organization
   Terms: kanban, task board, column layout
   Products: Linear, Trello, Notion

2. **Timeline Views** — Chronological display
   Terms: timeline, gantt, roadmap
   Products: Linear, Notion, Airtable

...
```

## Step 3: Search Sprint

Run 20-30 parallel WebSearch queries across design sources AND social platforms.

### Source Categories

**Design References** (visual examples):
```
site:dribbble.com {terms} UI 2025 2026
site:behance.net {terms} UI UX case study
site:figma.com/community {terms}
site:mobbin.com {terms}
```

**Discussions** (what designers are saying):

Reddit (uses ScrapeCreators API if `SCRAPECREATORS_API_KEY` is set):
```python
# With API key: better engagement data, more results
search_reddit_scrapecreators(query, timeframe="month")

# Fallback: WebSearch
site:reddit.com (r/UI_Design OR r/web_design OR r/userexperience) {terms}
```

X/Twitter and HN (WebSearch):
```
site:x.com {terms} UI design
site:news.ycombinator.com {terms} design
```

**Video Tutorials** (walkthroughs):
```
site:youtube.com {terms} UI tutorial
site:youtube.com {terms} figma walkthrough
```

**Product Launches** (new tools):
```
site:producthunt.com {terms}
```

**AI Sources** (generated examples):
```
site:v0.dev {terms}
site:ui-syntax.com {terms}
```

### Query Generation

For each sub-pattern, generate queries using templates from `data/sources.json`:

```python
queries = []
for pattern in sub_patterns:
    for source in ['mobbin', 'dribbble', 'behance', 'v0']:
        queries.append(generate_query(source, pattern.base_terms[0]))
    for product_query in pattern.product_queries[:3]:
        queries.append(product_query + " UI")
```

### Recency Filtering

By default, prioritize recent content (last 30 days). Can be adjusted:

```
/uir planning mode UI              # Default: last 30 days
/uir planning mode UI --days=7     # Last week only
/uir planning mode UI --days=90    # Last quarter
/uir planning mode UI --quick      # Fewer sources, faster
/uir planning mode UI --deep       # More sources, comprehensive
```

For design galleries (Dribbble, Behance), append current year to queries.
For social sources (Reddit, X, YouTube), filter by post date.

### Post-Search Filtering (CRITICAL)

**BEFORE proceeding to image collection**, filter out collection/search pages:

1. For each URL from search results, classify it:
   - **Individual pages** (quality 1.0): `/shots/12345`, `/gallery/123/`, `/explore/screens/uuid`
   - **Collection pages** (quality 0.0): `/search?q=`, `/browse/`, `/tags/`, `/designers/`
   - **Unknown** (quality 0.5): URLs that don't match known patterns

2. **Remove all collection pages** (quality 0.0) — these redirect or show lists, not individual designs

3. Log what was filtered:
   ```
   📋 URL Quality Check:
      - 45 URLs collected
      - 12 filtered as collection/search pages
      - 33 individual pages kept
   
   Filtered examples:
      ✗ dribbble.com/search?q=kanban (collection)
      ✗ mobbin.com/browse/web/screens (collection)
   ```

4. **Only proceed with individual/unknown URLs** to Step 4

### URL Pattern Reference

| Source | Individual Pattern | Collection Patterns |
|--------|-------------------|---------------------|
| Dribbble | `/shots/\d+` | `/search?`, `/tags/`, `/designers` |
| Behance | `/gallery/\d+/` | `/search/projects/`, `/galleries/` |
| Mobbin | `/explore/screens/[uuid]` | `/browse/`, `/explore/web/screens`, `/explore/mobile/screens` |
| Figma | `/community/file/\d+` | `/community/search`, `/community/explore` |
| v0 | `/t/[id]`, `/chat/[id]` | `/chat$`, `/docs/` |

## Step 4: Display Summary (Phase 1 — Default)

After filtering, display a **scannable summary** grouped by source type. Do NOT build the gallery yet.

### Summary Format

Group results into four categories:
1. **Design References** — Visual examples from Dribbble, Behance, Figma, Mobbin
2. **Discussions** — Reddit threads, X posts, HN stories
3. **Tutorials** — YouTube videos, walkthroughs
4. **Launches** — Product Hunt, new tools

Show engagement metrics inline for social sources.

### Example Output

```
📋 Found 67 references for "planning mode UI"

Design References (34)
  ★ dribbble.com/shots/25799561 — Kanban Dashboard Redesign [img]
  ★ behance.net/gallery/198234567 — Task Board UI Kit [img]
  ★ figma.com/community/file/1234 — Kanban Components [img]
  ★ mobbin.com/explore/screens/abc — Linear Roadmap [img]
  ... +30 more

Discussions (18)
  ★ r/UI_Design: "How Linear nailed planning mode" [847↑ • 234💬]
  ★ r/web_design: "Best planning UI patterns in 2026" [523↑ • 156💬]
  ★ @frankchimero: "The best planning UIs let you zoom..." [1.2K♥ • 89↺]
  ★ @round: "Linear's planning mode is *chef's kiss*" [892♥ • 45↺]
  ○ HN: "Show HN: Open-source planning tool" [234↑ • 89💬]
  ... +13 more

Tutorials (8)
  ★ youtube.com/watch?v=abc — Building a Planning App in Figma [12K▶]
  ★ youtube.com/watch?v=xyz — Linear Clone Tutorial [8.5K▶]
  ★ youtube.com/watch?v=def — Kanban Board from Scratch [6.2K▶]
  ... +5 more

Launches (7)
  ★ producthunt.com/posts/planwise — "AI planning assistant" [456↑]
  ★ producthunt.com/posts/taskflow — "Visual task management" [312↑]
  ... +5 more

───────────────────────────────────────
67 total • 34 designs • 18 discussions • 8 tutorials • 7 launches
Top voices: @frankchimero, r/UI_Design, Juxtopposed

Say "build gallery", "open in tabs", or "show insights"
```

### Symbol Legend

| Symbol | Meaning |
|--------|---------|
| ★ | Individual page (quality 1.0) |
| ○ | Unknown quality (0.5) |
| [img] | Image available |
| ↑ | Upvotes (Reddit, HN, PH) |
| ♥ | Likes (X, Dribbble) |
| 💬 | Comments |
| ↺ | Shares/Retweets |
| ▶ | Views (YouTube) |

### Engagement Display Rules

1. Show engagement inline for social sources (Reddit, X, YouTube, HN, PH)
2. Format numbers: 1.2K, 3.4M
3. Sort by engagement score within each group
4. Show "Top voices" in footer (most-engaged authors)

### Retain Context

After displaying the summary, store in memory:
```
RESEARCH_STATE: {
  concept: "{CONCEPT}",
  refs: [...all references with metadata...],
  categories: [...],
  engagement_stats: {...},
  filtered_count: {N},
  ready_for_gallery: true
}
```

## Step 4b: Show Insights (Optional)

When user says "show insights", analyze the discussions and generate a sentiment summary:

```
📊 What Designers Are Saying About "planning mode UI"

Loved (mentioned positively):
- Linear's keyboard-first approach (12 mentions)
- Notion's flexibility for custom workflows (8)
- "Finally a Gantt that doesn't suck" — r/UI_Design (6)

Criticized (common complaints):
- Mobile planning UIs are all terrible (9)
- Feature overload, hard to learn (7)
- "Why can't I just drag tasks?" — @round (5)

Hot Debates:
- Timeline vs Kanban for sprint planning
- AI-generated tasks: helpful or annoying?

Products Mentioned:
- Linear (23x) — keyboard shortcuts, clean design
- Notion (18x) — flexibility, databases
- Asana (12x) — enterprise, integrations
- Height (8x) — newcomer, AI features
```

### How to Generate Insights

1. Scan discussion refs (Reddit, X, HN) for sentiment patterns
2. Extract product names and count mentions
3. Identify common themes (praise, complaints, debates)
4. Quote specific comments when they're particularly insightful

## Step 5: Build Gallery (Phase 2 — On Demand)

**Only run this step when user says**: "build gallery", "generate it", "looks good", "create the HTML", etc.

### Screenshot Capture with Playwright

The skill uses **Playwright** for reliable screenshot capture. This handles:
- Figma Community (bypasses 403 errors)
- Mobbin (handles JS rendering + auth)
- Any site that blocks WebFetch

#### Setup (one-time)

If Playwright isn't installed, run:
```bash
cd ~/Code/ui-research
python scripts/ui_research.py --setup
```

This installs Playwright and Chromium (~150MB).

#### Screenshot Process

1. **Check cache** — Screenshots are cached in `~/.cache/ui-research/screenshots/`
2. **Batch capture** — Capture up to 5 URLs in parallel
3. **Fallback to OG images** — For URLs that fail screenshot capture

```
📸 Capturing screenshots...
   [1/34] dribbble.com/shots/25799561 ✓
   [2/34] figma.com/community/file/1234 ✓
   [3/34] mobbin.com/explore/screens/abc ✓
   ...
   
   Done: 30 captured, 4 failed (using placeholders)
```

#### Fallback: OG Image Extraction

For URLs where Playwright fails, try WebFetch + OG tags:
```html
<meta property="og:image" content="...">
<meta name="twitter:image" content="...">
```

#### CDN Patterns (for scoring)
| Source | CDN Pattern |
|--------|-------------|
| Dribbble | `cdn.dribbble.com/userupload` |
| Behance | `mir-s3-cdn-cf.behance.net` |
| Figma | `figma.com/community/thumbnail` |
| Mobbin | `mobbin.com/_next/image` |
| v0.dev | Preview images in meta tags |

### Gallery Generation

1. **Read template**: Load `data/gallery-template.html`

2. **Build data object**:
   ```json
   {
     "concept": "planning mode UI",
     "categories": [
       { "id": "all", "label": "All", "count": 52 },
       { "id": "kanban", "label": "Kanban Boards", "count": 15 }
     ],
     "sources": [
       { "id": "dribbble", "label": "Dribbble", "color": "#ea4c89", "count": 12 }
     ],
     "refs": [
       {
         "url": "https://dribbble.com/shots/123",
         "title": "Kanban Board Design",
         "desc": "Clean task management UI",
         "source": "dribbble",
         "sourceLabel": "Dribbble",
         "cat": "kanban",
         "tags": ["kanban", "tasks"],
         "img": "https://cdn.dribbble.com/...",
         "urlQuality": 1.0,
         "imageStatus": "available"
       }
     ],
     "allTags": ["kanban", "timeline", "calendar"],
     "tier": 2,
     "generatedAt": "2024-04-12T10:30:00"
   }
   ```

3. **Inject data** at the `/*GALLERY_DATA*/` marker

4. **Write to** `.uir-output/{date}-{concept}.html`

### Gallery Features

- Sidebar: Category navigation
- Header: Concept title + stats
- Search bar: Cmd+K shortcut
- Source chips: Filter by Dribbble, Mobbin, etc.
- Tag chips: Filter by tags
- Grid/List view toggle
- Image previews (in list view)
- Quality indicators
- Keyboard navigation
- URL state persistence

### Output

```
✅ Gallery built!

📊 Results:
   - {N} references
   - {M} with images
   - Sources: Dribbble ({X}), Mobbin ({Y}), ...

📁 Saved: .uir-output/{filename}

🔗 Opening in browser...
```

## Step 6: Follow-Up Mode

After displaying the summary (Phase 1), retain context for follow-ups:

```
RESEARCH_STATE: {
  concept: "{CONCEPT}",
  refs: [...all references...],
  categories: [...],
  decomposition: {...},
  filtered_count: {N},
  gallery_built: false
}
```

### Follow-Up Behaviors

| User says | Claude does |
|-----------|-------------|
| "build gallery" / "generate it" / "looks good" | → Run Step 5 (gallery generation) |
| "open in tabs" / "open all" | → Open all references in browser tabs |
| "open kanban in tabs" | → Open only kanban category refs in tabs |
| "open top 10 in tabs" | → Open first 10 refs in tabs |
| "open dribbble in tabs" | → Open only Dribbble refs in tabs |
| "more kanban examples" | Run targeted searches, add to refs, show updated summary |
| "focus on dribbble only" | Filter refs to Dribbble, show filtered summary |
| "remove the medium articles" | Filter out medium.com refs, show updated summary |
| "now do mobile" | New research sprint with mobile queries |
| "compare Linear vs Asana" | Pull from refs + targeted searches |

### Open in Tabs

When user says "open in tabs", "open all", or similar:

1. **Filter refs** based on any constraints (category, source, count)
2. **Warn if many tabs** — if > 15 refs, confirm first:
   ```
   This will open 34 tabs. Continue? (say "yes" or specify a limit like "top 10")
   ```
3. **Open tabs** — use Shell to open URLs in default browser:
   ```bash
   open "https://dribbble.com/shots/123"
   open "https://figma.com/community/file/456"
   # ... etc
   ```
4. **Confirm**:
   ```
   ✓ Opened 15 tabs in your browser
   ```

#### Filtering Options

| Command | Behavior |
|---------|----------|
| "open in tabs" | All refs (with confirmation if > 15) |
| "open top 10" | First 10 refs (highest quality) |
| "open top 5 kanban" | First 5 from kanban category |
| "open dribbble in tabs" | All Dribbble refs |
| "open ★ only" | Only quality 1.0 (individual pages) |

### After Summary (Phase 1)

```
Say "build gallery" to generate the browsable HTML.
Say "open in tabs" to open all references in your browser.

Or refine:
- "more {category} examples"
- "focus on {source} only"  
- "remove {source}"
- "open top 10 in tabs"
```

### After Gallery (Phase 2)

```
Gallery saved. I still have all {N} references in memory.

- "add more examples" → extend and rebuild
- "open in tabs" → open refs in browser
- "new research for {concept}" → start fresh
```

## Debug Mode

When troubleshooting research results (images not loading, wrong pages appearing), output diagnostic information:

### URL Classification Debug

After collecting search results, show classification for each URL:

```
DEBUG: URL Classification
────────────────────────────────────────
URL: https://dribbble.com/shots/12345678-kanban-board
  Source: dribbble
  Quality: 1.0 (individual)
  Pattern: /shots/\d+

URL: https://dribbble.com/search?q=kanban
  Source: dribbble
  Quality: 0.0 (collection) ← FILTERED
  Pattern: /search?

URL: https://mobbin.com/browse/web/screens
  Source: mobbin
  Quality: 0.0 (collection) ← FILTERED
  Pattern: /browse/

URL: https://medium.com/design/kanban-patterns
  Source: unknown
  Quality: 0.5 (unknown)
  Pattern: none
────────────────────────────────────────
Summary: 28 kept, 17 filtered as collections
```

### Image Extraction Debug

For URLs that pass filtering, show WebFetch results:

```
DEBUG: Image Extraction
────────────────────────────────────────
URL: https://dribbble.com/shots/12345678
  Fetched: Yes
  OG Image: https://cdn.dribbble.com/userupload/12345/original.png
  Status: ✓ Image found

URL: https://behance.net/gallery/123456/project
  Fetched: Yes
  OG Image: null
  CDN Search: Found mir-s3-cdn-cf.behance.net/project_modules/...
  Status: ✓ Image found via CDN

URL: https://mobbin.com/explore/screens/abc-123
  Fetched: No (blocked/timeout)
  Fallback: Using source placeholder
  Status: ✗ No image
────────────────────────────────────────
Summary: 24 with images, 9 without (using placeholders)
```

### When to Use Debug Mode

Enable debug output when:
- Gallery shows mostly placeholders instead of images
- Clicking references leads to search/browse pages instead of individual designs
- A source (e.g., Mobbin) consistently redirects to home page
- Stats show "X with images" but images don't display

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| All placeholders | WebFetch not attempted or failing | Check if URLs are being fetched |
| Search pages in results | Post-search filtering not applied | Ensure Step 3 filtering runs |
| Mobbin redirects | Captured browse URLs, not screen URLs | Mobbin browse pages require auth; filter them out |
| "X with images" but none show | `img` field has URL but it's broken | Check OG image URLs are valid |

## CLI Usage

The plugin includes a CLI for direct use:

```bash
# Research a concept
python scripts/ui_research.py "planning mode UI"

# Check environment (tier detection)
python scripts/ui_research.py --diagnose

# Use mock data for testing
python scripts/ui_research.py --mock "kanban board" --no-open

# View research history
python scripts/ui_research.py --history

# Re-run previous research
python scripts/ui_research.py --rerun {id}

# Open previous gallery
python scripts/ui_research.py --open {id}
```

## Tier Reference

| Tier | Environment | Image Source | Time | Quality |
|------|-------------|--------------|------|---------|
| 0 | **Playwright (recommended)** | Full screenshots | 3-5 min | ★★★★★ |
| 1 | CLI (no screenshots) | Links only | 1 min | ★☆☆☆☆ |
| 2 | WebFetch | OG images | 3 min | ★★★☆☆ |

### Why Playwright?

Playwright provides:
- **Figma Community** — WebFetch gets 403, Playwright renders the page
- **Mobbin** — Requires JS rendering and auth cookies
- **Consistent quality** — Same viewport, same screenshot format
- **Caching** — Screenshots cached locally, instant on re-runs
- **Parallel capture** — 5 pages at once, fast batch processing

### Setup

```bash
python scripts/ui_research.py --setup
```

### Test a URL

```bash
python scripts/ui_research.py --screenshot "https://figma.com/community/file/123456"
```

## Data Files

The plugin includes bundled data for term expansion:

- `data/synonyms.json` — UI/UX terminology map (100+ patterns)
- `data/products.json` — Pattern → product mappings (100+ patterns × 5-10 products)
- `data/sources.json` — Source metadata (CDN patterns, colors, query templates)

These are **seed data for acceleration**, not restrictions. For novel concepts not in the data files, generate expansions dynamically.
