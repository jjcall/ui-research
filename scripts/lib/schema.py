"""Data models for UI Research plugin."""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
import json


@dataclass
class SubPattern:
    """A decomposed sub-pattern with expanded search terms."""
    name: str
    description: str
    base_terms: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    product_queries: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    def all_search_terms(self) -> list[str]:
        """Return all searchable terms for this pattern."""
        terms = set(self.base_terms)
        terms.update(self.synonyms)
        terms.update(self.product_queries)
        return list(terms)
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "SubPattern":
        return cls(**data)


@dataclass
class Decomposition:
    """Result of decomposing a concept into sub-patterns."""
    concept: str
    sub_patterns: list[SubPattern] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "concept": self.concept,
            "subPatterns": [p.to_dict() for p in self.sub_patterns],
            "generatedAt": self.generated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Decomposition":
        return cls(
            concept=data["concept"],
            sub_patterns=[SubPattern.from_dict(p) for p in data.get("subPatterns", [])],
            generated_at=data.get("generatedAt", datetime.now().isoformat())
        )


@dataclass
class Engagement:
    """Engagement metrics for a reference."""
    likes: int = 0
    comments: int = 0
    shares: int = 0  # retweets, reposts
    views: int = 0
    saves: int = 0
    upvotes: int = 0
    downvotes: int = 0
    
    @property
    def score(self) -> int:
        """Combined engagement score for sorting."""
        return self.likes + self.upvotes + (self.comments * 2) + (self.shares * 3) + (self.views // 1000)
    
    def to_dict(self) -> dict:
        return {
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "views": self.views,
            "saves": self.saves,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "score": self.score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Engagement":
        if not data:
            return cls()
        return cls(
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            views=data.get("views", 0),
            saves=data.get("saves", 0),
            upvotes=data.get("upvotes", 0),
            downvotes=data.get("downvotes", 0)
        )
    
    def format_compact(self) -> str:
        """Format engagement for terminal display."""
        parts = []
        if self.upvotes:
            parts.append(f"{self._format_num(self.upvotes)}↑")
        if self.likes:
            parts.append(f"{self._format_num(self.likes)}♥")
        if self.comments:
            parts.append(f"{self._format_num(self.comments)}💬")
        if self.shares:
            parts.append(f"{self._format_num(self.shares)}↺")
        if self.views:
            parts.append(f"{self._format_num(self.views)}▶")
        return " • ".join(parts) if parts else ""
    
    @staticmethod
    def _format_num(n: int) -> str:
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)


@dataclass
class Reference:
    """A single design reference."""
    url: str
    title: str
    description: str
    source: str
    category: str
    source_label: str = ""
    source_type: str = "design"  # design, discussion, video, launch
    primary_tag: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    image_url: Optional[str] = None
    image_data: Optional[str] = None  # base64 encoded
    has_code: bool = False
    url_quality: float = 0.5  # 0.0=collection, 0.5=unknown, 1.0=individual
    image_status: str = "unknown"  # unknown, available, unavailable
    engagement: Optional[Engagement] = None
    author: Optional[str] = None  # @handle, u/username, channel name
    published_at: Optional[str] = None  # ISO date string
    
    def __post_init__(self):
        if not self.source_label:
            self.source_label = self.source.title()
        if self.engagement is None:
            self.engagement = Engagement()
    
    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "desc": self.description,
            "source": self.source,
            "sourceLabel": self.source_label,
            "sourceType": self.source_type,
            "cat": self.category,
            "tag": self.primary_tag,
            "tags": self.tags,
            "img": self.image_data or self.image_url,
            "hasCode": self.has_code,
            "urlQuality": self.url_quality,
            "imageStatus": self.image_status,
            "engagement": self.engagement.to_dict() if self.engagement else None,
            "author": self.author,
            "publishedAt": self.published_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Reference":
        img = data.get("img") or ""
        engagement = None
        if data.get("engagement"):
            engagement = Engagement.from_dict(data["engagement"])
        return cls(
            url=data["url"],
            title=data["title"],
            description=data.get("desc", data.get("description", "")),
            source=data["source"],
            source_label=data.get("sourceLabel", ""),
            source_type=data.get("sourceType", "design"),
            category=data.get("cat", data.get("category", "")),
            primary_tag=data.get("tag"),
            tags=data.get("tags", []),
            image_url=img if img and not img.startswith("data:") else None,
            image_data=img if img and img.startswith("data:") else None,
            has_code=data.get("hasCode", False),
            url_quality=data.get("urlQuality", 0.5),
            image_status=data.get("imageStatus", "unknown"),
            engagement=engagement,
            author=data.get("author"),
            published_at=data.get("publishedAt")
        )


@dataclass
class Category:
    """A category for organizing references."""
    id: str
    label: str
    count: int = 0
    
    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "count": self.count}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(id=data["id"], label=data["label"], count=data.get("count", 0))


@dataclass
class Source:
    """A source for design references."""
    id: str
    label: str
    color: str
    count: int = 0
    
    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "color": self.color, "count": self.count}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        return cls(
            id=data["id"],
            label=data["label"],
            color=data.get("color", "#666666"),
            count=data.get("count", 0)
        )


@dataclass
class Gallery:
    """A complete gallery of design references."""
    concept: str
    categories: list[Category] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    refs: list[Reference] = field(default_factory=list)
    all_tags: list[str] = field(default_factory=list)
    tier: int = 1
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    decomposition: Optional[Decomposition] = None
    
    def __post_init__(self):
        # Auto-add "All" category if not present
        if not any(c.id == "all" for c in self.categories):
            self.categories.insert(0, Category(id="all", label="All", count=len(self.refs)))
        
        # Auto-add "All" source if not present
        if not any(s.id == "all" for s in self.sources):
            self.sources.insert(0, Source(id="all", label="All", color="#666666", count=len(self.refs)))
        
        # Collect all unique tags from refs
        if not self.all_tags:
            tags = set()
            for ref in self.refs:
                tags.update(ref.tags)
            self.all_tags = sorted(tags)
    
    def update_counts(self):
        """Update category and source counts based on refs."""
        # Category counts
        cat_counts = {"all": len(self.refs)}
        for ref in self.refs:
            cat_counts[ref.category] = cat_counts.get(ref.category, 0) + 1
        
        for cat in self.categories:
            cat.count = cat_counts.get(cat.id, 0)
        
        # Source counts
        src_counts = {"all": len(self.refs)}
        for ref in self.refs:
            src_counts[ref.source] = src_counts.get(ref.source, 0) + 1
        
        for src in self.sources:
            src.count = src_counts.get(src.id, 0)
    
    def to_dict(self) -> dict:
        return {
            "concept": self.concept,
            "categories": [c.to_dict() for c in self.categories],
            "sources": [s.to_dict() for s in self.sources],
            "refs": [r.to_dict() for r in self.refs],
            "allTags": self.all_tags,
            "tier": self.tier,
            "generatedAt": self.generated_at,
            "decomposition": self.decomposition.to_dict() if self.decomposition else None
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Gallery":
        decomp = None
        if data.get("decomposition"):
            decomp = Decomposition.from_dict(data["decomposition"])
        
        return cls(
            concept=data["concept"],
            categories=[Category.from_dict(c) for c in data.get("categories", [])],
            sources=[Source.from_dict(s) for s in data.get("sources", [])],
            refs=[Reference.from_dict(r) for r in data.get("refs", [])],
            all_tags=data.get("allTags", []),
            tier=data.get("tier", 1),
            generated_at=data.get("generatedAt", datetime.now().isoformat()),
            decomposition=decomp
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Gallery":
        return cls.from_dict(json.loads(json_str))


@dataclass
class ResearchHistory:
    """A record of past research for history tracking."""
    id: str
    concept: str
    date: str
    tier: int
    ref_count: int
    gallery_path: str
    sub_patterns: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "concept": self.concept,
            "date": self.date,
            "tier": self.tier,
            "refCount": self.ref_count,
            "galleryPath": self.gallery_path,
            "subPatterns": self.sub_patterns
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ResearchHistory":
        return cls(
            id=data["id"],
            concept=data["concept"],
            date=data["date"],
            tier=data["tier"],
            ref_count=data.get("refCount", 0),
            gallery_path=data.get("galleryPath", ""),
            sub_patterns=data.get("subPatterns", [])
        )


@dataclass
class EnvironmentInfo:
    """Information about the execution environment."""
    playwright_available: bool = False
    chrome_tools_available: bool = False
    webfetch_available: bool = False
    detected_tier: int = 1
    
    def to_dict(self) -> dict:
        return {
            "playwrightAvailable": self.playwright_available,
            "chromeToolsAvailable": self.chrome_tools_available,
            "webfetchAvailable": self.webfetch_available,
            "detectedTier": self.detected_tier
        }
