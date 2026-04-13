---
name: uir
version: "1.0.0"
description: "Research UI/UX patterns for any concept. Also invoked as 'ui research'. Triggers: 'uir kanban board', 'ui research for X', 'design inspiration for X', 'how do other apps handle X'. Decomposes concepts, searches design sources, generates visual gallery."
argument-hint: 'uir planning mode, uir kanban boards, ui research for checkout flow'
allowed-tools: Bash, Read, Write, WebSearch, WebFetch
user-invocable: true
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      bins:
        - python3
    optionalBins:
        - playwright
    files:
      - "scripts/*"
    tags:
      - design
      - ui
      - ux
      - research
      - moodboard
---

# UI Research Skill

Research UI/UX patterns for any concept. Decomposes design concepts into searchable patterns, searches across design sources (Dribbble, Behance, Mobbin, v0, etc.), extracts images, and generates a browsable HTML gallery.

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

Run 15-20 parallel WebSearch queries across design sources.

### Source Priority

**Tier 1 — Real Apps (highest value):**
```
site:mobbin.com {terms}
site:screenlane.com {terms}
```

**Tier 2 — Design Galleries:**
```
site:dribbble.com {terms} UI 2025 2026
site:behance.net {terms} UI UX case study
site:figma.com/community {terms}
```

**Tier 3 — AI Sources:**
```
site:v0.dev {terms}
site:ui-syntax.com {terms}
```

**Tier 4 — Products & Analysis:**
```
{terms} UI {category} 2025 2026
{terms} UX design patterns examples
site:reddit.com/r/UI_Design {terms}
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

### Recency Bias

Append "2025 2026" to queries. Skip pre-2024 results unless iconic.

## Step 4: Image Collection

### Tier Detection

Check available tools:
```
1. If Playwright available → Tier 0 (full screenshots)
2. If WebFetch works → Tier 2 (OG images)
3. Otherwise → Tier 1 (links only)
```

### OG Image Extraction (Tier 2)

For each URL, use WebFetch and extract:
```html
<meta property="og:image" content="...">
<meta name="twitter:image" content="...">
```

### CDN Patterns

Source-specific image extraction:

| Source | CDN Pattern |
|--------|-------------|
| Dribbble | `cdn.dribbble.com/userupload` |
| Behance | `mir-s3-cdn-cf.behance.net` |
| Figma | `figma.com/community/thumbnail` |
| Mobbin | `mobbin.com/_next/image` |
| v0.dev | Preview images in meta tags |

## Step 5: Gallery Builder

Generate a self-contained HTML gallery with:

### Structure
```
- Sidebar: Category navigation
- Header: Concept title + stats
- Search bar: Cmd+K shortcut
- Source chips: Filter by Dribbble, Mobbin, etc.
- Tag chips: Filter by tags
- Reference list: Clean, scannable items
```

### Features
- URL state persistence (`#category=kanban&source=dribbble`)
- Keyboard navigation (arrows, Esc, Cmd+K)
- Image preview toggle
- Responsive layout

### Output

Save gallery to `~/Documents/UIResearch/galleries/{date}-{concept}.html`

Display completion:
```
✅ Research complete!

📊 Results:
   - {N} references collected
   - {M} with images
   - Sources: Dribbble ({X}), Mobbin ({Y}), ...

📁 Gallery saved: ~/Documents/UIResearch/galleries/{filename}

🔗 Opening in browser...
```

## Step 6: Follow-Up Mode

After delivering the gallery, retain context:

```
CONCEPT: {what was researched}
SUB_PATTERNS: {full decomposition}
KEY_FINDINGS: {cross-pattern insights}
ALL_REFS: {complete refs list}
SOURCE_DATA: {which sites had richest results}
```

### Follow-Up Behaviors

| User says | Claude does |
|-----------|-------------|
| "Show me more kanban examples" | Run targeted searches, extend gallery |
| "Which products handle view switching best?" | Answer from memory, cite refs |
| "Now do the mobile version" | New research sprint with mobile queries |
| "Compare Linear vs Asana" | Pull from refs + targeted searches |

### Follow-Up Invitation

After delivering results:
```
I'm now deep in the research for {CONCEPT}. Some things I can help with:

- Go deeper on any pattern category (e.g., "more timeline examples")
- Compare specific products ("how does Linear vs Notion handle planning?")
- Explore the mobile version of these patterns
- Research an adjacent concept that came up

Just ask.
```

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

| Tier | Environment | Image Source | Time |
|------|-------------|--------------|------|
| 0 | CLI + Playwright | Full screenshots | 5-8 min |
| 1 | Cursor (restricted) | Links only | 3 min |
| 2 | Cursor + WebFetch | OG images | 5 min |
| 3 | Chrome extension | Live captures | 8-10 min |

## Data Files

The plugin includes bundled data for term expansion:

- `data/synonyms.json` — UI/UX terminology map (100+ patterns)
- `data/products.json` — Pattern → product mappings (100+ patterns × 5-10 products)
- `data/sources.json` — Source metadata (CDN patterns, colors, query templates)

These are **seed data for acceleration**, not restrictions. For novel concepts not in the data files, generate expansions dynamically.
