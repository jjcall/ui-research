"""Social platform search for UI research.

Searches Reddit, X/Twitter, YouTube, and Hacker News for design discussions.
Uses ScrapeCreators API for Reddit when configured.
"""

import re
import json
import sys
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime, timezone
from .schema import Reference, Engagement

# Lazy import config to avoid circular imports
_config = None

def _get_config():
    global _config
    if _config is None:
        from . import config as cfg
        _config = cfg
    return _config

SCRAPECREATORS_REDDIT_BASE = "https://api.scrapecreators.com/v1/reddit"

# Try to import requests, fall back to urllib
try:
    import requests as _requests
except ImportError:
    _requests = None


def _log(msg: str):
    """Log to stderr."""
    sys.stderr.write(f"[UIR Social] {msg}\n")
    sys.stderr.flush()


def _sc_headers(token: str) -> dict:
    """Build ScrapeCreators request headers."""
    return {
        "x-api-key": token,
        "Content-Type": "application/json",
    }


def _parse_reddit_date(created_utc) -> Optional[str]:
    """Convert Unix timestamp to ISO date string."""
    if not created_utc:
        return None
    try:
        dt = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, TypeError, OSError):
        return None


def search_reddit_scrapecreators(
    query: str,
    subreddits: Optional[list[str]] = None,
    timeframe: str = "month",
    limit: int = 20,
    category: str = "discussion",
) -> list[Reference]:
    """
    Search Reddit using ScrapeCreators API.
    
    Args:
        query: Search query
        subreddits: Optional list of subreddits to search (searches globally if None)
        timeframe: Time filter (hour, day, week, month, year, all)
        limit: Max results to return
        category: Category to assign to results
    
    Returns:
        List of Reference objects
    """
    cfg = _get_config()
    token = cfg.get_scrapecreators_key()
    
    if not token:
        _log("No SCRAPECREATORS_API_KEY configured, skipping Reddit API search")
        return []
    
    refs = []
    
    # Global search
    try:
        if _requests:
            resp = _requests.get(
                f"{SCRAPECREATORS_REDDIT_BASE}/search",
                params={"query": query, "sort": "relevance", "timeframe": timeframe},
                headers=_sc_headers(token),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        else:
            # Fallback to urllib
            import urllib.request
            params = urlencode({"query": query, "sort": "relevance", "timeframe": timeframe})
            url = f"{SCRAPECREATORS_REDDIT_BASE}/search?{params}"
            req = urllib.request.Request(url, headers=_sc_headers(token))
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
        
        posts = data.get("posts", data.get("data", []))
        
        for i, post in enumerate(posts[:limit]):
            permalink = post.get("permalink", "")
            url = f"https://www.reddit.com{permalink}" if permalink else ""
            
            if not url or "reddit.com" not in url:
                continue
            
            subreddit = post.get("subreddit", "")
            title = str(post.get("title", "")).strip()
            selftext = str(post.get("selftext", ""))[:200]
            
            engagement = Engagement(
                upvotes=post.get("ups") or post.get("score", 0),
                comments=post.get("num_comments", 0),
            )
            
            refs.append(Reference(
                url=url,
                title=title,
                description=selftext if selftext else f"Discussion in r/{subreddit}",
                source="reddit",
                source_label="Reddit",
                source_type="discussion",
                category=category,
                tags=[f"r/{subreddit}"] if subreddit else [],
                author=f"r/{subreddit}" if subreddit else None,
                engagement=engagement,
                published_at=_parse_reddit_date(post.get("created_utc")),
                url_quality=1.0,
            ))
        
        _log(f"Reddit API: found {len(refs)} posts for '{query}'")
        
    except Exception as e:
        _log(f"Reddit API error: {e}")
    
    return refs


def has_scrapecreators_key() -> bool:
    """Check if ScrapeCreators API key is available."""
    cfg = _get_config()
    return cfg.is_reddit_api_available()


# Source type mappings
SOURCE_TYPES = {
    "reddit": "discussion",
    "x": "discussion",
    "twitter": "discussion",
    "youtube": "video",
    "hackernews": "discussion",
    "producthunt": "launch",
    "dribbble": "design",
    "behance": "design",
    "figma": "design",
    "mobbin": "design",
}

# Source colors
SOURCE_COLORS = {
    "reddit": "#ff4500",
    "x": "#000000",
    "youtube": "#ff0000",
    "hackernews": "#ff6600",
    "producthunt": "#da552f",
}


def parse_reddit_result(result: dict, category: str = "discussion") -> Optional[Reference]:
    """
    Parse a Reddit search result into a Reference.
    
    Expected result format from WebSearch:
    {
        "title": "Post title",
        "url": "https://reddit.com/r/UI_Design/comments/...",
        "description": "Post snippet..."
    }
    """
    url = result.get("url", "")
    if "reddit.com" not in url:
        return None
    
    # Skip collection pages
    if "/search" in url or url.endswith("/top") or url.endswith("/hot"):
        return None
    
    title = result.get("title", "")
    description = result.get("description", "")
    
    # Extract subreddit
    subreddit_match = re.search(r"/r/([^/]+)", url)
    subreddit = subreddit_match.group(1) if subreddit_match else "reddit"
    
    # Parse engagement from title/description patterns like "[500 upvotes]" or "500 points"
    engagement = Engagement()
    
    upvotes_match = re.search(r"(\d+(?:,\d+)?)\s*(?:upvotes?|points?|↑)", description, re.I)
    if upvotes_match:
        engagement.upvotes = int(upvotes_match.group(1).replace(",", ""))
    
    comments_match = re.search(r"(\d+(?:,\d+)?)\s*comments?", description, re.I)
    if comments_match:
        engagement.comments = int(comments_match.group(1).replace(",", ""))
    
    return Reference(
        url=url,
        title=title,
        description=description,
        source="reddit",
        source_label="Reddit",
        source_type="discussion",
        category=category,
        tags=[f"r/{subreddit}"],
        author=f"r/{subreddit}",
        engagement=engagement,
        url_quality=1.0 if "/comments/" in url else 0.5
    )


def parse_x_result(result: dict, category: str = "discussion") -> Optional[Reference]:
    """
    Parse an X/Twitter search result into a Reference.
    
    Expected result format from WebSearch:
    {
        "title": "@handle: Tweet text...",
        "url": "https://x.com/handle/status/123...",
        "description": "Tweet content..."
    }
    """
    url = result.get("url", "")
    if "x.com" not in url and "twitter.com" not in url:
        return None
    
    title = result.get("title", "")
    description = result.get("description", "")
    
    # Extract handle
    handle_match = re.search(r"(?:x\.com|twitter\.com)/([^/]+)", url)
    handle = handle_match.group(1) if handle_match else None
    
    # Clean up title (often has "on X: " or similar)
    title = re.sub(r"^.*? on X:\s*", "", title)
    title = re.sub(r"^.*? on Twitter:\s*", "", title)
    
    # Parse engagement from description
    engagement = Engagement()
    
    likes_match = re.search(r"(\d+(?:[.,]\d+)?[KkMm]?)\s*(?:likes?|♥|❤)", description, re.I)
    if likes_match:
        engagement.likes = _parse_number(likes_match.group(1))
    
    retweets_match = re.search(r"(\d+(?:[.,]\d+)?[KkMm]?)\s*(?:retweets?|reposts?|RTs?|↺)", description, re.I)
    if retweets_match:
        engagement.shares = _parse_number(retweets_match.group(1))
    
    return Reference(
        url=url,
        title=title[:200] if len(title) > 200 else title,
        description=description,
        source="x",
        source_label="X",
        source_type="discussion",
        category=category,
        tags=["twitter"],
        author=f"@{handle}" if handle else None,
        engagement=engagement,
        url_quality=1.0 if "/status/" in url else 0.5
    )


def parse_youtube_result(result: dict, category: str = "tutorial") -> Optional[Reference]:
    """
    Parse a YouTube search result into a Reference.
    
    Expected result format from WebSearch:
    {
        "title": "Video title",
        "url": "https://youtube.com/watch?v=...",
        "description": "Video description..."
    }
    """
    url = result.get("url", "")
    if "youtube.com" not in url and "youtu.be" not in url:
        return None
    
    # Skip collection pages
    if "/playlist" in url or "/channel" in url or "/@" in url:
        return None
    
    title = result.get("title", "")
    description = result.get("description", "")
    
    # Extract video ID for thumbnail
    video_id = None
    if "watch?v=" in url:
        parsed = urlparse(url)
        video_id = parse_qs(parsed.query).get("v", [None])[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
    
    thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg" if video_id else None
    
    # Parse engagement from description
    engagement = Engagement()
    
    views_match = re.search(r"(\d+(?:[.,]\d+)?[KkMm]?)\s*(?:views?|▶)", description, re.I)
    if views_match:
        engagement.views = _parse_number(views_match.group(1))
    
    likes_match = re.search(r"(\d+(?:[.,]\d+)?[KkMm]?)\s*(?:likes?|👍)", description, re.I)
    if likes_match:
        engagement.likes = _parse_number(likes_match.group(1))
    
    # Extract channel name (often in description or title)
    channel = None
    channel_match = re.search(r"by\s+([^|•\-]+)", description, re.I)
    if channel_match:
        channel = channel_match.group(1).strip()
    
    return Reference(
        url=url,
        title=title,
        description=description,
        source="youtube",
        source_label="YouTube",
        source_type="video",
        category=category,
        tags=["video", "tutorial"],
        image_url=thumbnail,
        author=channel,
        engagement=engagement,
        url_quality=1.0 if video_id else 0.5,
        image_status="available" if thumbnail else "unknown"
    )


def parse_hackernews_result(result: dict, category: str = "discussion") -> Optional[Reference]:
    """
    Parse a Hacker News search result into a Reference.
    
    Expected result format from WebSearch or Algolia API:
    {
        "title": "Story title",
        "url": "https://news.ycombinator.com/item?id=...",
        "description": "Story snippet..."
    }
    """
    url = result.get("url", "")
    
    # Handle both HN discussion links and external links
    is_hn_link = "news.ycombinator.com" in url or "hn.algolia.com" in url
    
    title = result.get("title", "")
    description = result.get("description", "")
    
    # Parse engagement
    engagement = Engagement()
    
    points_match = re.search(r"(\d+)\s*(?:points?|↑)", description, re.I)
    if points_match:
        engagement.upvotes = int(points_match.group(1))
    
    comments_match = re.search(r"(\d+)\s*comments?", description, re.I)
    if comments_match:
        engagement.comments = int(comments_match.group(1))
    
    # Extract author
    author = None
    author_match = re.search(r"by\s+(\w+)", description, re.I)
    if author_match:
        author = author_match.group(1)
    
    return Reference(
        url=url,
        title=title,
        description=description,
        source="hackernews",
        source_label="Hacker News",
        source_type="discussion",
        category=category,
        tags=["hn", "tech"],
        author=author,
        engagement=engagement,
        url_quality=1.0 if "item?id=" in url else 0.5
    )


def parse_producthunt_result(result: dict, category: str = "launch") -> Optional[Reference]:
    """
    Parse a Product Hunt search result into a Reference.
    """
    url = result.get("url", "")
    if "producthunt.com" not in url:
        return None
    
    title = result.get("title", "")
    description = result.get("description", "")
    
    # Parse engagement
    engagement = Engagement()
    
    upvotes_match = re.search(r"(\d+)\s*(?:upvotes?|↑|🔺)", description, re.I)
    if upvotes_match:
        engagement.upvotes = int(upvotes_match.group(1))
    
    return Reference(
        url=url,
        title=title,
        description=description,
        source="producthunt",
        source_label="Product Hunt",
        source_type="launch",
        category=category,
        tags=["launch", "product"],
        engagement=engagement,
        url_quality=1.0 if "/posts/" in url else 0.5
    )


def _parse_number(s: str) -> int:
    """Parse a number string like '1.2K' or '3,400' into an integer."""
    s = s.strip().replace(",", "")
    
    multiplier = 1
    if s and s[-1].upper() == "K":
        multiplier = 1000
        s = s[:-1]
    elif s and s[-1].upper() == "M":
        multiplier = 1000000
        s = s[:-1]
    
    try:
        return int(float(s) * multiplier)
    except ValueError:
        return 0


UI_DESIGN_SUBREDDITS = [
    "UI_Design", "web_design", "userexperience", "Frontend", "webdev",
    "reactjs", "nextjs", "tailwindcss", "figma", "UXDesign",
]


def generate_social_queries(concept: str, terms: list[str]) -> dict[str, list[str]]:
    """
    Generate search queries for social platforms.
    
    Returns dict mapping source to list of queries.
    """
    queries = {
        "reddit": [],
        "x": [],
        "youtube": [],
        "hackernews": [],
        "producthunt": [],
    }
    
    # Reddit queries
    for term in terms[:3]:
        queries["reddit"].append(f'site:reddit.com ({" OR ".join(f"r/{s}" for s in UI_DESIGN_SUBREDDITS[:5])}) {term}')
    queries["reddit"].append(f'site:reddit.com/r/UI_Design OR site:reddit.com/r/web_design "{concept}"')
    
    # X/Twitter queries
    for term in terms[:3]:
        queries["x"].append(f'site:x.com {term} UI design')
    queries["x"].append(f'site:x.com "{concept}" (UI OR UX OR design)')
    
    # YouTube queries
    for term in terms[:2]:
        queries["youtube"].append(f'site:youtube.com {term} UI tutorial')
    queries["youtube"].append(f'site:youtube.com "{concept}" design walkthrough')
    queries["youtube"].append(f'site:youtube.com "{concept}" figma')
    
    # Hacker News queries
    queries["hackernews"].append(f'site:news.ycombinator.com {concept}')
    for term in terms[:2]:
        queries["hackernews"].append(f'site:news.ycombinator.com {term} design')
    
    # Product Hunt queries
    queries["producthunt"].append(f'site:producthunt.com {concept}')
    for term in terms[:2]:
        queries["producthunt"].append(f'site:producthunt.com {term}')
    
    return queries


def parse_search_result(result: dict, source: str, category: str = "general") -> Optional[Reference]:
    """
    Parse a search result based on detected source.
    """
    url = result.get("url", "")
    
    # Auto-detect source from URL if not specified
    if not source or source == "auto":
        if "reddit.com" in url:
            source = "reddit"
        elif "x.com" in url or "twitter.com" in url:
            source = "x"
        elif "youtube.com" in url or "youtu.be" in url:
            source = "youtube"
        elif "news.ycombinator.com" in url:
            source = "hackernews"
        elif "producthunt.com" in url:
            source = "producthunt"
    
    parsers = {
        "reddit": parse_reddit_result,
        "x": parse_x_result,
        "twitter": parse_x_result,
        "youtube": parse_youtube_result,
        "hackernews": parse_hackernews_result,
        "producthunt": parse_producthunt_result,
    }
    
    parser = parsers.get(source)
    if parser:
        return parser(result, category)
    
    return None


def group_refs_by_type(refs: list[Reference]) -> dict[str, list[Reference]]:
    """
    Group references by source type for display.
    """
    groups = {
        "design": [],
        "discussion": [],
        "video": [],
        "launch": [],
    }
    
    for ref in refs:
        source_type = ref.source_type or SOURCE_TYPES.get(ref.source, "design")
        if source_type in groups:
            groups[source_type].append(ref)
        else:
            groups["design"].append(ref)
    
    return groups


def format_engagement_stats(refs: list[Reference]) -> dict:
    """
    Calculate aggregate engagement stats across all refs.
    """
    stats = {
        "total_refs": len(refs),
        "total_likes": 0,
        "total_upvotes": 0,
        "total_comments": 0,
        "total_views": 0,
        "total_shares": 0,
        "by_source": {},
        "top_voices": [],
    }
    
    author_engagement = {}
    
    for ref in refs:
        if ref.engagement:
            stats["total_likes"] += ref.engagement.likes
            stats["total_upvotes"] += ref.engagement.upvotes
            stats["total_comments"] += ref.engagement.comments
            stats["total_views"] += ref.engagement.views
            stats["total_shares"] += ref.engagement.shares
            
            # Track by source
            if ref.source not in stats["by_source"]:
                stats["by_source"][ref.source] = {"count": 0, "engagement": 0}
            stats["by_source"][ref.source]["count"] += 1
            stats["by_source"][ref.source]["engagement"] += ref.engagement.score
            
            # Track author engagement
            if ref.author:
                if ref.author not in author_engagement:
                    author_engagement[ref.author] = 0
                author_engagement[ref.author] += ref.engagement.score
    
    # Get top voices
    sorted_authors = sorted(author_engagement.items(), key=lambda x: -x[1])
    stats["top_voices"] = [author for author, _ in sorted_authors[:5]]
    
    return stats
