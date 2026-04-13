"""Search query generation from decomposed patterns."""

import json
from pathlib import Path
from typing import Optional
from .schema import SubPattern, Decomposition, Reference, Source


def _load_sources_data() -> dict:
    """Load sources.json data."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    filepath = data_dir / "sources.json"
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


_sources_data: Optional[dict] = None


def get_sources_data() -> dict:
    """Get the sources data, loading it if necessary."""
    global _sources_data
    if _sources_data is None:
        _sources_data = _load_sources_data()
    return _sources_data


def get_source_info(source_id: str) -> dict:
    """Get info for a specific source."""
    data = get_sources_data()
    return data.get("sources", {}).get(source_id, {})


def get_all_sources() -> list[Source]:
    """Get all sources as Source objects."""
    data = get_sources_data()
    sources = []
    for source_id, info in data.get("sources", {}).items():
        sources.append(Source(
            id=source_id,
            label=info.get("label", source_id.title()),
            color=info.get("color", "#666666")
        ))
    return sources


def generate_query(source_id: str, terms: str) -> str:
    """
    Generate a search query for a specific source.
    
    Uses the query template from sources.json.
    """
    info = get_source_info(source_id)
    template = info.get("queryTemplate", "{terms}")
    return template.replace("{terms}", terms)


def generate_queries_for_pattern(
    pattern: SubPattern,
    source_ids: list[str] = None,
    include_products: bool = True,
    include_synonyms: bool = True,
    max_queries_per_source: int = 3
) -> list[dict]:
    """
    Generate search queries for a single pattern.
    
    Returns a list of dicts with 'query', 'source', 'pattern', 'term' keys.
    """
    if source_ids is None:
        # Default priority sources
        source_ids = [
            "mobbin", "dribbble", "behance", "figma",
            "v0", "product", "patterns"
        ]
    
    queries = []
    
    # Collect search terms
    search_terms = list(pattern.base_terms)
    
    if include_synonyms and pattern.synonyms:
        # Add a couple of synonyms
        search_terms.extend(pattern.synonyms[:2])
    
    # Generate queries for each source and term
    for source_id in source_ids:
        source_queries = []
        
        for term in search_terms[:max_queries_per_source]:
            query = generate_query(source_id, term)
            source_queries.append({
                "query": query,
                "source": source_id,
                "pattern": pattern.name,
                "term": term
            })
        
        queries.extend(source_queries)
    
    # Add product-specific queries
    if include_products and pattern.product_queries:
        for pq in pattern.product_queries[:5]:
            queries.append({
                "query": pq + " UI",
                "source": "product",
                "pattern": pattern.name,
                "term": pq
            })
    
    return queries


def generate_queries_for_decomposition(
    decomposition: Decomposition,
    source_ids: list[str] = None,
    max_queries_per_pattern: int = 10
) -> list[dict]:
    """
    Generate all search queries for a decomposition.
    
    Returns a deduplicated list of query dicts.
    """
    all_queries = []
    seen_queries = set()
    
    for pattern in decomposition.sub_patterns:
        pattern_queries = generate_queries_for_pattern(
            pattern,
            source_ids=source_ids
        )
        
        for q in pattern_queries:
            query_str = q["query"].lower()
            if query_str not in seen_queries:
                seen_queries.add(query_str)
                all_queries.append(q)
                
                if len([x for x in all_queries if x["pattern"] == pattern.name]) >= max_queries_per_pattern:
                    break
    
    # Also add generic concept queries
    concept = decomposition.concept
    generic_sources = ["dribbble", "behance", "product", "patterns"]
    
    for source_id in generic_sources:
        query = generate_query(source_id, concept)
        if query.lower() not in seen_queries:
            all_queries.append({
                "query": query,
                "source": source_id,
                "pattern": "general",
                "term": concept
            })
            seen_queries.add(query.lower())
    
    return all_queries


def deduplicate_references(refs: list[Reference]) -> list[Reference]:
    """
    Deduplicate references by URL.
    
    When duplicates are found, merge their categories and tags.
    """
    seen = {}
    
    for ref in refs:
        url = ref.url.lower().rstrip("/")
        
        if url in seen:
            existing = seen[url]
            # Merge tags
            existing.tags = list(set(existing.tags + ref.tags))
            # Keep the better description
            if len(ref.description) > len(existing.description):
                existing.description = ref.description
        else:
            seen[url] = ref
    
    return list(seen.values())


def categorize_url(url: str) -> str:
    """
    Determine the source type from a URL.
    
    Returns a source_id string.
    """
    url_lower = url.lower()
    
    source_patterns = {
        "dribbble": ["dribbble.com"],
        "behance": ["behance.net"],
        "figma": ["figma.com/community"],
        "mobbin": ["mobbin.com"],
        "screenlane": ["screenlane.com"],
        "pageflows": ["pageflows.com"],
        "v0": ["v0.dev"],
        "uisyntax": ["ui-syntax.com"],
        "inspoai": ["inspoai.io"],
        "lapaninja": ["lapa.ninja"],
        "godly": ["godly.website"],
        "awwwards": ["awwwards.com"],
        "youtube": ["youtube.com", "youtu.be"],
        "reddit": ["reddit.com"],
    }
    
    for source_id, patterns in source_patterns.items():
        for pattern in patterns:
            if pattern in url_lower:
                return source_id
    
    return "product"


def extract_domain(url: str) -> str:
    """Extract the domain from a URL for display."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url


def parse_search_result(
    url: str,
    title: str,
    description: str,
    category: str,
    tags: list[str] = None
) -> Reference:
    """
    Create a Reference from a search result.
    
    Automatically determines the source from the URL.
    """
    source_id = categorize_url(url)
    source_info = get_source_info(source_id)
    
    return Reference(
        url=url,
        title=title,
        description=description,
        source=source_id,
        source_label=source_info.get("label", source_id.title()),
        category=category,
        tags=tags or [],
        has_code=source_info.get("hasCode", False)
    )
