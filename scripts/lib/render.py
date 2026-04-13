"""Gallery HTML rendering."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from .schema import Gallery, Reference, Category, Source
from .images import get_source_color as get_source_color_from_data


def get_gallery_template() -> str:
    """Load the gallery HTML template."""
    template_path = Path(__file__).parent.parent.parent / "data" / "gallery-template.html"
    if template_path.exists():
        with open(template_path, "r") as f:
            return f.read()
    return DEFAULT_TEMPLATE


def render_gallery(gallery: Gallery) -> str:
    """
    Render a Gallery to a self-contained HTML file.
    
    Embeds all data and styling inline for portability.
    """
    template = get_gallery_template()
    
    # Prepare data for embedding
    gallery_data = gallery.to_dict()
    gallery_json = json.dumps(gallery_data, indent=2)
    
    # Generate stats
    stats = generate_stats(gallery)
    
    # Replace placeholders
    html = template.replace("{{CONCEPT}}", escape_html(gallery.concept))
    html = html.replace("{{GALLERY_DATA}}", gallery_json)
    html = html.replace("{{GENERATED_AT}}", gallery.generated_at)
    html = html.replace("{{TIER}}", str(gallery.tier))
    html = html.replace("{{REF_COUNT}}", str(len(gallery.refs)))
    html = html.replace("{{STATS}}", stats)
    
    return html


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def generate_stats(gallery: Gallery) -> str:
    """Generate stats summary for the gallery."""
    gallery.update_counts()
    
    lines = []
    lines.append(f"Total: {len(gallery.refs)} references")
    
    # Source breakdown
    source_counts = {}
    for ref in gallery.refs:
        source_counts[ref.source_label] = source_counts.get(ref.source_label, 0) + 1
    
    if source_counts:
        source_parts = [f"{label}: {count}" for label, count in sorted(source_counts.items(), key=lambda x: -x[1])]
        lines.append("Sources: " + ", ".join(source_parts[:5]))
    
    # Image coverage
    with_images = sum(1 for r in gallery.refs if r.image_url or r.image_data)
    lines.append(f"Images: {with_images} of {len(gallery.refs)} references have images")
    
    return " | ".join(lines)


def render_reference_card(ref: Reference, show_image: bool = False) -> str:
    """Render a single reference card as HTML."""
    tag_html = ""
    if ref.primary_tag:
        tag_html = f'<span class="ref-tag">{escape_html(ref.primary_tag)}</span>'
    
    source_color = get_source_color(ref.source)
    
    # Image or placeholder
    image_html = ""
    if show_image:
        if ref.image_url or ref.image_data:
            img_src = ref.image_data or ref.image_url
            image_html = f'<img class="ref-image" src="{img_src}" loading="lazy" alt="" onerror="this.classList.add(\'error\')">'
        else:
            # Source-colored placeholder
            image_html = f'''<div class="ref-image ref-placeholder" style="background: {source_color}">
                <span class="placeholder-label">{escape_html(ref.source_label[:2].upper())}</span>
            </div>'''
    
    # Quality indicator (only show for high or low quality)
    quality_html = ""
    if hasattr(ref, 'url_quality'):
        if ref.url_quality >= 0.9:
            quality_html = '<span class="quality-badge quality-high" title="Individual page">★</span>'
        elif ref.url_quality <= 0.1:
            quality_html = '<span class="quality-badge quality-low" title="Collection page">⚠</span>'
    
    tags_html = ""
    if ref.tags:
        tags_html = " ".join(f'<span class="tag-pill">{escape_html(t)}</span>' for t in ref.tags[:3])
    
    return f'''
    <a href="{escape_html(ref.url)}" target="_blank" rel="noopener" class="ref-item" data-cat="{escape_html(ref.category)}" data-source="{escape_html(ref.source)}" data-quality="{getattr(ref, 'url_quality', 0.5)}">
        {image_html}
        <div class="ref-content">
            <div class="ref-header">
                <span class="ref-title">{escape_html(ref.title)}</span>
                {quality_html}
                {tag_html}
                <span class="ref-arrow">↗</span>
            </div>
            <div class="ref-desc">{escape_html(ref.description)}</div>
            <div class="ref-meta">
                <span class="ref-source" style="color: {source_color}">{escape_html(ref.source_label)}</span>
                {tags_html}
            </div>
        </div>
    </a>
    '''


def get_source_color(source_id: str) -> str:
    """Get the color for a source from sources.json."""
    return get_source_color_from_data(source_id)


def render_sidebar(gallery: Gallery) -> str:
    """Render the sidebar navigation HTML."""
    items = []
    
    for cat in gallery.categories:
        active = "active" if cat.id == "all" else ""
        items.append(f'''
        <button class="sidebar-item {active}" data-cat="{cat.id}">
            <span class="sidebar-label">{escape_html(cat.label)}</span>
            <span class="sidebar-count">{cat.count}</span>
        </button>
        ''')
    
    return "\n".join(items)


def render_source_chips(gallery: Gallery) -> str:
    """Render the source filter chips HTML."""
    chips = []
    
    for src in gallery.sources:
        active = "active" if src.id == "all" else ""
        style = f'style="--chip-color: {src.color}"' if src.color else ""
        chips.append(f'''
        <button class="source-chip {active}" data-source="{src.id}" {style}>
            {escape_html(src.label)}
            <span class="chip-count">{src.count}</span>
        </button>
        ''')
    
    return "\n".join(chips)


def render_tag_chips(tags: list[str]) -> str:
    """Render the tag filter chips HTML."""
    chips = []
    
    for tag in sorted(tags)[:15]:  # Limit to 15 tags
        chips.append(f'''
        <button class="tag-chip" data-tag="{escape_html(tag)}">
            {escape_html(tag)}
        </button>
        ''')
    
    return "\n".join(chips)


def save_gallery(gallery: Gallery, output_path: Path) -> Path:
    """
    Save a rendered gallery to a file.
    
    Returns the path to the saved file.
    """
    html = render_gallery(gallery)
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    return output_path


def get_default_output_path(concept: str) -> Path:
    """Get the default output path for a gallery."""
    # Sanitize concept for filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in concept)
    safe_name = safe_name.strip().replace(" ", "-").lower()[:50]
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{safe_name}.html"
    
    output_dir = Path.home() / "Documents" / "UIResearch" / "galleries"
    return output_dir / filename


# Default template when gallery-template.html doesn't exist
DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{CONCEPT}} — UI Research</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #fff;
            color: #1a1a1a;
            line-height: 1.5;
        }
        .app {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 240px;
            border-right: 1px solid #e5e5e5;
            padding: 24px 16px;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }
        .sidebar-title {
            font-size: 14px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }
        .sidebar-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding: 8px 12px;
            border: none;
            background: none;
            font-size: 14px;
            color: #333;
            cursor: pointer;
            border-radius: 6px;
            text-align: left;
            margin-bottom: 2px;
        }
        .sidebar-item:hover { background: #f5f5f5; }
        .sidebar-item.active {
            background: #f0f0f0;
            font-weight: 500;
            border-left: 3px solid #333;
        }
        .sidebar-count {
            font-size: 12px;
            color: #999;
        }
        .main {
            flex: 1;
            margin-left: 240px;
            padding: 32px 48px;
            max-width: 960px;
        }
        .header {
            margin-bottom: 32px;
        }
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .header .stats {
            font-size: 13px;
            color: #666;
        }
        .search-bar {
            position: relative;
            margin-bottom: 16px;
        }
        .search-bar input {
            width: 100%;
            padding: 10px 16px 10px 40px;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }
        .search-bar input:focus { border-color: #999; }
        .search-bar::before {
            content: "⌘K";
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 12px;
            color: #999;
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .filters {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 24px;
        }
        .source-chip, .tag-chip {
            padding: 6px 12px;
            border: 1px solid #e5e5e5;
            background: #fff;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .source-chip:hover, .tag-chip:hover {
            background: #f5f5f5;
        }
        .source-chip.active {
            background: var(--chip-color, #333);
            color: #fff;
            border-color: var(--chip-color, #333);
        }
        .tag-chip.active {
            background: #333;
            color: #fff;
            border-color: #333;
        }
        .chip-count {
            font-size: 11px;
            opacity: 0.7;
            margin-left: 4px;
        }
        .ref-list {
            display: flex;
            flex-direction: column;
            gap: 1px;
        }
        .ref-item {
            display: flex;
            gap: 16px;
            padding: 16px;
            text-decoration: none;
            color: inherit;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.15s;
        }
        .ref-item:hover {
            background: #fafafa;
            padding-left: 20px;
        }
        .ref-item:hover .ref-arrow { opacity: 1; }
        .ref-image {
            width: 120px;
            height: 80px;
            object-fit: cover;
            border-radius: 6px;
            background: #f5f5f5;
            flex-shrink: 0;
        }
        .ref-image.error {
            display: none;
        }
        .ref-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255,255,255,0.9);
            font-weight: 600;
            font-size: 18px;
        }
        .placeholder-label {
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }
        .quality-badge {
            font-size: 10px;
            padding: 2px 5px;
            border-radius: 3px;
            margin-left: 4px;
        }
        .quality-high {
            background: #dcfce7;
            color: #166534;
        }
        .quality-low {
            background: #fef3c7;
            color: #92400e;
        }
        .ref-content { flex: 1; min-width: 0; }
        .ref-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }
        .ref-title {
            font-size: 14px;
            font-weight: 500;
            color: #1a1a1a;
        }
        .ref-item:hover .ref-title { color: #0066cc; }
        .ref-tag {
            font-size: 11px;
            padding: 2px 8px;
            background: #f0f0f0;
            border-radius: 4px;
            color: #666;
        }
        .ref-arrow {
            margin-left: auto;
            opacity: 0;
            color: #999;
            transition: opacity 0.15s;
        }
        .ref-desc {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .ref-meta {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        .ref-source { font-weight: 500; }
        .tag-pill {
            padding: 2px 6px;
            background: #f5f5f5;
            border-radius: 4px;
            color: #666;
        }
        .empty-state {
            text-align: center;
            padding: 48px;
            color: #666;
        }
        .toggle-images {
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 10px 16px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
        }
        .toggle-images:hover { background: #444; }
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; padding: 16px; }
        }
    </style>
</head>
<body>
    <div class="app">
        <nav class="sidebar">
            <div class="sidebar-title">Categories</div>
            <div id="sidebar-items"></div>
        </nav>
        <main class="main">
            <header class="header">
                <h1>{{CONCEPT}}</h1>
                <p class="stats">{{STATS}}</p>
            </header>
            <div class="search-bar">
                <input type="text" id="search" placeholder="Search references...">
            </div>
            <div class="filters" id="source-chips"></div>
            <div class="filters" id="tag-chips"></div>
            <div class="ref-list" id="ref-list"></div>
        </main>
    </div>
    <button class="toggle-images" id="toggle-images">Show previews</button>
    <script>
        const data = {{GALLERY_DATA}};
        
        let state = {
            category: 'all',
            sources: [],
            tags: [],
            search: '',
            showImages: false
        };
        
        function parseHash() {
            const hash = window.location.hash.slice(1);
            const params = new URLSearchParams(hash);
            if (params.get('category')) state.category = params.get('category');
            if (params.get('source')) state.sources = params.get('source').split(',');
            if (params.get('tags')) state.tags = params.get('tags').split(',');
            if (params.get('search')) state.search = params.get('search');
            if (params.get('images') === 'true') state.showImages = true;
        }
        
        function updateHash() {
            const params = new URLSearchParams();
            if (state.category !== 'all') params.set('category', state.category);
            if (state.sources.length) params.set('source', state.sources.join(','));
            if (state.tags.length) params.set('tags', state.tags.join(','));
            if (state.search) params.set('search', state.search);
            if (state.showImages) params.set('images', 'true');
            window.location.hash = params.toString();
        }
        
        function filterRefs() {
            return data.refs.filter(ref => {
                const matchesCat = state.category === 'all' || ref.cat === state.category;
                const matchesSource = state.sources.length === 0 || state.sources.includes(ref.source);
                const matchesTags = state.tags.length === 0 || state.tags.some(t => ref.tags && ref.tags.includes(t));
                const matchesSearch = !state.search || 
                    ref.title.toLowerCase().includes(state.search.toLowerCase()) ||
                    (ref.desc && ref.desc.toLowerCase().includes(state.search.toLowerCase()));
                return matchesCat && matchesSource && matchesTags && matchesSearch;
            });
        }
        
        function renderSidebar() {
            const el = document.getElementById('sidebar-items');
            el.innerHTML = data.categories.map(cat => `
                <button class="sidebar-item ${state.category === cat.id ? 'active' : ''}" data-cat="${cat.id}">
                    <span class="sidebar-label">${cat.label}</span>
                    <span class="sidebar-count">${cat.count}</span>
                </button>
            `).join('');
            el.querySelectorAll('.sidebar-item').forEach(btn => {
                btn.onclick = () => { state.category = btn.dataset.cat; updateHash(); render(); };
            });
        }
        
        function renderSourceChips() {
            const el = document.getElementById('source-chips');
            el.innerHTML = data.sources.map(src => `
                <button class="source-chip ${state.sources.includes(src.id) ? 'active' : ''}" 
                        data-source="${src.id}" style="--chip-color: ${src.color}">
                    ${src.label}
                    <span class="chip-count">${src.count}</span>
                </button>
            `).join('');
            el.querySelectorAll('.source-chip').forEach(btn => {
                btn.onclick = () => {
                    const src = btn.dataset.source;
                    if (src === 'all') {
                        state.sources = [];
                    } else {
                        const idx = state.sources.indexOf(src);
                        if (idx >= 0) state.sources.splice(idx, 1);
                        else state.sources.push(src);
                    }
                    updateHash();
                    render();
                };
            });
        }
        
        function renderTagChips() {
            const el = document.getElementById('tag-chips');
            const tags = data.allTags.slice(0, 15);
            el.innerHTML = tags.map(tag => `
                <button class="tag-chip ${state.tags.includes(tag) ? 'active' : ''}" data-tag="${tag}">
                    ${tag}
                </button>
            `).join('');
            el.querySelectorAll('.tag-chip').forEach(btn => {
                btn.onclick = () => {
                    const tag = btn.dataset.tag;
                    const idx = state.tags.indexOf(tag);
                    if (idx >= 0) state.tags.splice(idx, 1);
                    else state.tags.push(tag);
                    updateHash();
                    render();
                };
            });
        }
        
        function getSourceColor(sourceId) {
            const src = data.sources.find(s => s.id === sourceId);
            return src ? src.color : '#666666';
        }
        
        function renderRefs() {
            const refs = filterRefs();
            const el = document.getElementById('ref-list');
            if (refs.length === 0) {
                el.innerHTML = '<div class="empty-state">No references match your filters</div>';
                return;
            }
            el.innerHTML = refs.map(ref => {
                const color = getSourceColor(ref.source);
                let imgHtml = '';
                if (state.showImages) {
                    if (ref.img) {
                        imgHtml = `<img class="ref-image" src="${ref.img}" loading="lazy" alt="" onerror="this.classList.add('error')">`;
                    } else {
                        const initials = (ref.sourceLabel || ref.source || '??').substring(0, 2).toUpperCase();
                        imgHtml = `<div class="ref-image ref-placeholder" style="background: ${color}">
                            <span class="placeholder-label">${initials}</span>
                        </div>`;
                    }
                }
                const tagHtml = ref.tag ? `<span class="ref-tag">${ref.tag}</span>` : '';
                const tagsHtml = (ref.tags || []).slice(0, 3).map(t => 
                    `<span class="tag-pill">${t}</span>`).join('');
                
                let qualityHtml = '';
                const quality = ref.urlQuality || 0.5;
                if (quality >= 0.9) {
                    qualityHtml = '<span class="quality-badge quality-high" title="Individual page">★</span>';
                } else if (quality <= 0.1) {
                    qualityHtml = '<span class="quality-badge quality-low" title="Collection page">⚠</span>';
                }
                
                return `
                    <a href="${ref.url}" target="_blank" rel="noopener" class="ref-item" data-quality="${quality}">
                        ${imgHtml}
                        <div class="ref-content">
                            <div class="ref-header">
                                <span class="ref-title">${ref.title}</span>
                                ${qualityHtml}
                                ${tagHtml}
                                <span class="ref-arrow">↗</span>
                            </div>
                            <div class="ref-desc">${ref.desc || ''}</div>
                            <div class="ref-meta">
                                <span class="ref-source" style="color: ${color}">${ref.sourceLabel}</span>
                                ${tagsHtml}
                            </div>
                        </div>
                    </a>
                `;
            }).join('');
        }
        
        function render() {
            renderSidebar();
            renderSourceChips();
            renderTagChips();
            renderRefs();
        }
        
        // Initialize
        parseHash();
        render();
        
        // Search
        const searchInput = document.getElementById('search');
        searchInput.value = state.search;
        searchInput.oninput = () => {
            state.search = searchInput.value;
            updateHash();
            renderRefs();
        };
        
        // Keyboard shortcuts
        document.addEventListener('keydown', e => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
            if (e.key === 'Escape') {
                state.search = '';
                state.sources = [];
                state.tags = [];
                searchInput.value = '';
                updateHash();
                render();
            }
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                const cats = data.categories;
                const idx = cats.findIndex(c => c.id === state.category);
                const newIdx = e.key === 'ArrowLeft' ? 
                    (idx - 1 + cats.length) % cats.length : 
                    (idx + 1) % cats.length;
                state.category = cats[newIdx].id;
                updateHash();
                render();
            }
        });
        
        // Toggle images
        document.getElementById('toggle-images').onclick = () => {
            state.showImages = !state.showImages;
            document.getElementById('toggle-images').textContent = 
                state.showImages ? 'Hide previews' : 'Show previews';
            updateHash();
            renderRefs();
        };
        
        // Hash change
        window.addEventListener('hashchange', () => {
            parseHash();
            render();
        });
    </script>
</body>
</html>'''
