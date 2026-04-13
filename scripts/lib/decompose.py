"""Concept decomposition with semantic expansion."""

import json
from pathlib import Path
from typing import Optional
from .schema import SubPattern, Decomposition


def _load_data_file(filename: str) -> dict:
    """Load a JSON data file from the data directory."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    filepath = data_dir / filename
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


_synonyms_data: Optional[dict] = None
_products_data: Optional[dict] = None


def get_synonyms_data() -> dict:
    """Get the synonyms data, loading it if necessary."""
    global _synonyms_data
    if _synonyms_data is None:
        _synonyms_data = _load_data_file("synonyms.json")
    return _synonyms_data


def get_products_data() -> dict:
    """Get the products data, loading it if necessary."""
    global _products_data
    if _products_data is None:
        _products_data = _load_data_file("products.json")
    return _products_data


def expand_synonyms(term: str) -> list[str]:
    """
    Expand a term using bundled synonyms.
    
    Returns the original term plus any known synonyms.
    For unknown terms, returns just the original term.
    """
    term_lower = term.lower().strip()
    term_normalized = term_lower.replace(" ", "-").replace("_", "-")
    
    data = get_synonyms_data()
    patterns = data.get("patterns", {})
    
    # Try exact match first
    if term_normalized in patterns:
        synonyms = patterns[term_normalized].get("synonyms", [])
        return [term] + synonyms
    
    # Try without hyphens
    term_no_hyphens = term_normalized.replace("-", "")
    for key, value in patterns.items():
        if key.replace("-", "") == term_no_hyphens:
            synonyms = value.get("synonyms", [])
            return [term] + synonyms
    
    # No match found
    return [term]


def get_related_patterns(term: str) -> list[str]:
    """Get related patterns for a term from the synonyms data."""
    term_lower = term.lower().strip()
    term_normalized = term_lower.replace(" ", "-").replace("_", "-")
    
    data = get_synonyms_data()
    patterns = data.get("patterns", {})
    
    if term_normalized in patterns:
        return patterns[term_normalized].get("related", [])
    
    return []


def get_product_queries(pattern_name: str) -> list[str]:
    """
    Get product-specific queries for a pattern.
    
    Returns queries like "Linear board", "Trello UI" for known patterns.
    For unknown patterns, returns an empty list.
    """
    pattern_lower = pattern_name.lower().strip()
    pattern_normalized = pattern_lower.replace(" ", "-").replace("_", "-")
    
    # Also try common variations
    variations = [
        pattern_normalized,
        pattern_normalized.replace("-", ""),
        pattern_normalized.replace("-board", ""),
        pattern_normalized.replace("-view", ""),
    ]
    
    data = get_products_data()
    patterns = data.get("patterns", {})
    
    for variant in variations:
        if variant in patterns:
            products = patterns[variant].get("products", [])
            # Create product-specific queries
            return [f"{p} {pattern_name}" for p in products[:6]]
    
    return []


def get_products_by_category(category: str) -> list[str]:
    """Get all products in a given category."""
    data = get_products_data()
    by_category = data.get("productsByCategory", {})
    return by_category.get(category, [])


def create_sub_pattern(
    name: str,
    description: str,
    base_terms: list[str],
    tags: list[str] = None
) -> SubPattern:
    """
    Create a SubPattern with full semantic expansion.
    
    Automatically expands synonyms and product queries from bundled data.
    """
    # Expand synonyms for each base term
    all_synonyms = set()
    for term in base_terms:
        expanded = expand_synonyms(term)
        all_synonyms.update(expanded)
    
    # Remove base terms from synonyms
    synonyms = list(all_synonyms - set(base_terms))
    
    # Get product queries
    product_queries = []
    for term in base_terms:
        pq = get_product_queries(term)
        product_queries.extend(pq)
    
    # Dedupe
    product_queries = list(dict.fromkeys(product_queries))
    
    return SubPattern(
        name=name,
        description=description,
        base_terms=base_terms,
        synonyms=synonyms,
        product_queries=product_queries[:10],  # Limit to 10
        tags=tags or []
    )


def decompose_concept(concept: str, sub_patterns_data: list[dict]) -> Decomposition:
    """
    Create a Decomposition from a list of sub-pattern definitions.
    
    This is a helper for when Claude provides the initial decomposition
    and we need to expand it with synonyms and product queries.
    
    Args:
        concept: The original concept being decomposed
        sub_patterns_data: List of dicts with 'name', 'description', 'base_terms', 'tags'
    
    Returns:
        A Decomposition with fully expanded SubPatterns
    """
    sub_patterns = []
    
    for sp_data in sub_patterns_data:
        sp = create_sub_pattern(
            name=sp_data["name"],
            description=sp_data.get("description", ""),
            base_terms=sp_data.get("base_terms", sp_data.get("baseTerms", [])),
            tags=sp_data.get("tags", [])
        )
        sub_patterns.append(sp)
    
    return Decomposition(
        concept=concept,
        sub_patterns=sub_patterns
    )


def suggest_lateral_patterns(concept: str, direct_patterns: list[str]) -> list[str]:
    """
    Suggest additional patterns that might be related but weren't directly mentioned.
    
    This uses the 'related' field from synonyms.json to find adjacent patterns.
    """
    suggestions = set()
    
    for pattern in direct_patterns:
        related = get_related_patterns(pattern)
        suggestions.update(related)
    
    # Remove patterns that were already directly mentioned
    direct_lower = {p.lower().replace(" ", "-") for p in direct_patterns}
    suggestions = {s for s in suggestions if s not in direct_lower}
    
    return list(suggestions)
