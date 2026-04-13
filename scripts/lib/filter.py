"""URL quality filtering for design references."""

import re
from typing import Optional
from .schema import Reference


# Patterns that indicate individual items (high quality) - regex
INDIVIDUAL_PATTERNS: dict[str, list[str]] = {
    # Tier 1: Real Apps
    "mobbin": [r"/explore/screens/[a-f0-9-]+", r"/screens/[a-f0-9-]+"],
    "screenlane": [r"/ios/flows/[\w-]+/$", r"/web/flows/[\w-]+/$"],
    "pageflows": [r"/post/[\w-]+/[\w-]+/[\w-]+/"],
    "uisources": [r"/apps/[\w-]+/", r"/pattern/[\w-]+$"],
    "pttrns": [r"/patterns/\d+", r"/applications/[\w-]+$"],
    
    # Tier 2: Design Galleries
    "dribbble": [r"/shots/\d+"],
    "behance": [r"/gallery/\d+/"],
    "figma": [r"/community/file/\d+"],
    
    # Tier 3: AI Sources
    "v0": [r"/chat/[\w-]+", r"/t/[\w]+"],
    "uisyntax": [r"/design/[\w-]+"],
    "inspoai": [r"app\.inspoai\.io"],
    
    # Tier 4: Specialized
    "lapaninja": [r"/post/[\w-]+/"],
    "saaspages": [r"/sites/[\w-]+$"],
    "godly": [r"/website/[\w-]+-\d+"],
    "awwwards": [r"/sites/[\w-]+$"],
    "designspells": [r"/spell/[\w-]+"],
    
    # Tier 5: Community/Video
    "youtube": [r"/watch\?v=[\w-]+"],
    "reddit": [r"/r/[\w_]+/comments/[\w]+/"],
}

# Patterns that indicate collection/search pages (filter out) - substring match
COLLECTION_PATTERNS: dict[str, list[str]] = {
    # Tier 1: Real Apps
    "mobbin": ["/browse/", "/explore/mobile/screens", "/explore/web/screens", "/explore/mobile/flows"],
    "screenlane": ["/screens/all/", "/filters/", "/signup/", "/pricing"],
    "pageflows": ["/web/flows/$", "/ios/flows/$", "/pricing"],
    "uisources": ["/pattern/$", "/apps/$", "/pricing"],
    "pttrns": ["/patterns$", "/apps$", "/pricing"],
    
    # Tier 2: Design Galleries
    "dribbble": ["/search?", "/tags/", "/designers", "/resources/", "/hiring"],
    "behance": ["/search/projects/", "/galleries/", "/onboarding"],
    "figma": ["/community/search", "/@", "/community/explore"],
    
    # Tier 3: AI Sources
    "v0": ["/chat$", "/docs/", "/pricing"],
    "uisyntax": ["/$"],
    "inspoai": ["/blogs/", "/features/", "/solutions/", "/pricing", "/compare/"],
    
    # Tier 4: Specialized
    "lapaninja": ["/category/", "/color/", "/year/", "/pricing"],
    "saaspages": ["/blocks/", "/sites$", "/roadmap"],
    "godly": ["/websites/", "/info"],
    "awwwards": ["/collections/", "/nominees/", "/websites/", "/blog/"],
    "designspells": ["/spells$"],
    
    # Tier 5: Community/Video
    "youtube": ["/results?", "/playlist?", "/@", "/channel/"],
    "reddit": ["/search", "/top", "/hot", "/new", "/rising"],
}


def is_individual_page(url: str, source_id: Optional[str] = None) -> bool:
    """
    Check if a URL matches individual item patterns.
    
    Returns True if the URL appears to be an individual design/screen/shot,
    not a collection or search results page.
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # If source_id provided, only check that source's patterns
    if source_id and source_id in INDIVIDUAL_PATTERNS:
        patterns = INDIVIDUAL_PATTERNS[source_id]
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return True
        return False
    
    # Check all sources
    for patterns in INDIVIDUAL_PATTERNS.values():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return True
    
    return False


def is_collection_page(url: str, source_id: Optional[str] = None) -> bool:
    """
    Check if a URL matches collection/search page patterns.
    
    Returns True if the URL appears to be a collection, search results,
    or browse page rather than an individual item.
    """
    if not url:
        return False
    
    url_lower = url.lower()
    
    # If source_id provided, only check that source's patterns
    if source_id and source_id in COLLECTION_PATTERNS:
        patterns = COLLECTION_PATTERNS[source_id]
        for pattern in patterns:
            # Handle regex-style patterns (ending with $)
            if pattern.endswith("$"):
                if re.search(pattern, url_lower):
                    return True
            # Simple substring match
            elif pattern in url_lower:
                return True
        return False
    
    # Check all sources
    for patterns in COLLECTION_PATTERNS.values():
        for pattern in patterns:
            if pattern.endswith("$"):
                if re.search(pattern, url_lower):
                    return True
            elif pattern in url_lower:
                return True
    
    return False


def score_url_quality(url: str, source_id: Optional[str] = None) -> float:
    """
    Score URL quality from 0.0 to 1.0.
    
    - 1.0: Confirmed individual page (matches individual pattern)
    - 0.5: Unknown/neutral (no patterns match)
    - 0.0: Confirmed collection page (matches collection pattern)
    """
    if not url:
        return 0.0
    
    # Collection pages get lowest score
    if is_collection_page(url, source_id):
        return 0.0
    
    # Individual pages get highest score
    if is_individual_page(url, source_id):
        return 1.0
    
    # Unknown URLs get middle score
    return 0.5


def filter_references(
    refs: list[Reference],
    remove_collections: bool = True,
    min_quality: float = 0.0
) -> list[Reference]:
    """
    Filter references by URL quality.
    
    Args:
        refs: List of Reference objects to filter
        remove_collections: If True, remove URLs that match collection patterns
        min_quality: Minimum quality score to keep (0.0-1.0)
    
    Returns:
        Filtered list of references, sorted by quality (highest first)
    """
    filtered = []
    
    for ref in refs:
        quality = score_url_quality(ref.url, ref.source)
        
        # Skip collection pages if requested
        if remove_collections and quality == 0.0:
            continue
        
        # Skip below minimum quality
        if quality < min_quality:
            continue
        
        # Store quality score on reference for sorting
        ref.url_quality = quality
        filtered.append(ref)
    
    # Sort by quality (highest first), then by title
    filtered.sort(key=lambda r: (-getattr(r, 'url_quality', 0.5), r.title.lower()))
    
    return filtered


def classify_url(url: str) -> dict:
    """
    Classify a URL and return detailed info.
    
    Returns dict with:
        - source_id: Detected source (or None)
        - is_individual: Whether URL matches individual patterns
        - is_collection: Whether URL matches collection patterns
        - quality: Quality score 0.0-1.0
        - matched_pattern: The pattern that matched (if any)
    """
    result = {
        "source_id": None,
        "is_individual": False,
        "is_collection": False,
        "quality": 0.5,
        "matched_pattern": None,
    }
    
    if not url:
        return result
    
    url_lower = url.lower()
    
    # Try to detect source from URL
    source_hints = {
        "dribbble.com": "dribbble",
        "behance.net": "behance",
        "figma.com/community": "figma",
        "mobbin.com": "mobbin",
        "screenlane.com": "screenlane",
        "pageflows.com": "pageflows",
        "v0.dev": "v0",
        "ui-syntax.com": "uisyntax",
        "inspoai.io": "inspoai",
        "lapa.ninja": "lapaninja",
        "saaspages.xyz": "saaspages",
        "godly.website": "godly",
        "awwwards.com": "awwwards",
        "designspells.com": "designspells",
        "youtube.com": "youtube",
        "youtu.be": "youtube",
        "reddit.com": "reddit",
        "uisources.com": "uisources",
        "pttrns.com": "pttrns",
    }
    
    for hint, source_id in source_hints.items():
        if hint in url_lower:
            result["source_id"] = source_id
            break
    
    # Check individual patterns
    for source_id, patterns in INDIVIDUAL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                result["is_individual"] = True
                result["matched_pattern"] = pattern
                if result["source_id"] is None:
                    result["source_id"] = source_id
                break
        if result["is_individual"]:
            break
    
    # Check collection patterns
    for source_id, patterns in COLLECTION_PATTERNS.items():
        for pattern in patterns:
            if pattern.endswith("$"):
                if re.search(pattern, url_lower):
                    result["is_collection"] = True
                    result["matched_pattern"] = pattern
                    break
            elif pattern in url_lower:
                result["is_collection"] = True
                result["matched_pattern"] = pattern
                break
        if result["is_collection"]:
            break
    
    # Calculate quality
    if result["is_collection"]:
        result["quality"] = 0.0
    elif result["is_individual"]:
        result["quality"] = 1.0
    else:
        result["quality"] = 0.5
    
    return result


def debug_url(url: str) -> str:
    """
    Return human-readable debug info about a URL's classification.
    
    Use this to troubleshoot why URLs are being filtered or kept.
    """
    info = classify_url(url)
    
    # Determine quality label
    if info["quality"] == 1.0:
        quality_label = "1.0 (individual)"
    elif info["quality"] == 0.0:
        quality_label = "0.0 (collection) ← FILTERED"
    else:
        quality_label = "0.5 (unknown)"
    
    lines = [
        f"URL: {url}",
        f"  Source: {info['source_id'] or 'unknown'}",
        f"  Quality: {quality_label}",
    ]
    
    if info["matched_pattern"]:
        lines.append(f"  Pattern: {info['matched_pattern']}")
    
    return "\n".join(lines)


def debug_urls(urls: list[str]) -> str:
    """
    Return debug info for multiple URLs.
    
    Summarizes how many would be kept vs filtered.
    """
    lines = ["DEBUG: URL Classification", "─" * 40]
    
    kept = 0
    filtered = 0
    
    for url in urls:
        info = classify_url(url)
        lines.append(debug_url(url))
        lines.append("")
        
        if info["quality"] == 0.0:
            filtered += 1
        else:
            kept += 1
    
    lines.append("─" * 40)
    lines.append(f"Summary: {kept} kept, {filtered} filtered as collections")
    
    return "\n".join(lines)
