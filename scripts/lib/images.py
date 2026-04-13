"""OG image extraction and CDN pattern matching."""

import re
import json
import base64
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urljoin

# Try to import beautifulsoup, but make it optional
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# Minimum image dimensions to consider (skip icons, avatars, etc.)
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100

# Patterns that indicate small/icon images to skip
SKIP_PATTERNS = [
    r'/avatar[s]?/',
    r'/icon[s]?/',
    r'/logo[s]?/',
    r'/favicon',
    r'/emoji/',
    r'/badge[s]?/',
    r'/button[s]?/',
    r'\b\d{1,2}x\d{1,2}\b',  # e.g., 16x16, 32x32
    r'_thumb\.',
    r'_small\.',
    r'_tiny\.',
    r'_icon\.',
]


def _load_sources_data() -> dict:
    """Load sources.json data."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    filepath = data_dir / "sources.json"
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def get_cdn_patterns(source_id: str) -> list[str]:
    """Get CDN patterns for a source."""
    data = _load_sources_data()
    source = data.get("sources", {}).get(source_id, {})
    return source.get("cdnPatterns", [])


def get_source_color(source_id: str) -> str:
    """Get the color for a source (for placeholder generation)."""
    data = _load_sources_data()
    source = data.get("sources", {}).get(source_id, {})
    return source.get("color", "#666666")


def extract_og_image(html: str) -> Optional[str]:
    """
    Extract the og:image URL from HTML content.
    
    Works with or without BeautifulSoup.
    """
    if HAS_BS4:
        return _extract_og_image_bs4(html)
    else:
        return _extract_og_image_regex(html)


def _extract_og_image_bs4(html: str) -> Optional[str]:
    """Extract og:image using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Try og:image first
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        return og_image["content"]
    
    # Try twitter:image
    twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
    if twitter_image and twitter_image.get("content"):
        return twitter_image["content"]
    
    # Try twitter:image:src
    twitter_image_src = soup.find("meta", attrs={"name": "twitter:image:src"})
    if twitter_image_src and twitter_image_src.get("content"):
        return twitter_image_src["content"]
    
    return None


def _extract_og_image_regex(html: str) -> Optional[str]:
    """Extract og:image using regex (fallback when no BS4)."""
    patterns = [
        r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']',
        r'<meta\s+name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']twitter:image["\']',
        r'<meta\s+name=["\']twitter:image:src["\']\s+content=["\']([^"\']+)["\']',
        r'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']twitter:image:src["\']',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_srcset_images(html: str, base_url: str = "") -> list[dict]:
    """
    Extract images from srcset attributes, returning highest resolution versions.
    
    Returns list of dicts with 'url' and 'width' keys, sorted by width descending.
    """
    images = []
    
    # Pattern to match srcset attribute
    srcset_pattern = r'srcset=["\']([^"\']+)["\']'
    
    for match in re.finditer(srcset_pattern, html, re.IGNORECASE):
        srcset = match.group(1)
        
        # Parse srcset entries (url width, url width, ...)
        for entry in srcset.split(","):
            entry = entry.strip()
            parts = entry.split()
            if parts:
                url = parts[0]
                width = 0
                
                # Try to extract width descriptor (e.g., "800w")
                if len(parts) > 1:
                    width_match = re.match(r'(\d+)w', parts[1])
                    if width_match:
                        width = int(width_match.group(1))
                
                # Resolve relative URLs
                if base_url and not url.startswith(("http://", "https://", "//")):
                    url = urljoin(base_url, url)
                
                if url and not url.startswith("data:"):
                    images.append({"url": url, "width": width})
    
    # Sort by width, highest first
    images.sort(key=lambda x: -x["width"])
    
    return images


def extract_images_from_html(html: str, base_url: str = "") -> list[str]:
    """
    Extract image URLs from HTML content.
    
    Looks for:
    - <img> tags with src attributes
    - srcset attributes (highest resolution)
    - data-src attributes (lazy loading)
    - picture source elements
    """
    images = []
    seen = set()
    
    def add_image(src: str):
        if src and src not in seen and not src.startswith("data:"):
            if base_url and not src.startswith(("http://", "https://", "//")):
                src = urljoin(base_url, src)
            if not _is_likely_icon(src):
                seen.add(src)
                images.append(src)
    
    if HAS_BS4:
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract from srcset first (highest quality)
        for img in soup.find_all(["img", "source"]):
            srcset = img.get("srcset")
            if srcset:
                srcset_imgs = extract_srcset_images(str(img), base_url)
                for item in srcset_imgs[:1]:  # Just the highest res
                    add_image(item["url"])
        
        # Find all img tags
        for img in soup.find_all("img"):
            # Try multiple attributes
            for attr in ["src", "data-src", "data-lazy-src", "data-original"]:
                src = img.get(attr)
                if src:
                    add_image(src)
                    break
        
        # Find picture source elements
        for source in soup.find_all("source"):
            src = source.get("srcset") or source.get("src")
            if src:
                # Handle srcset with multiple images
                first_src = src.split(",")[0].split()[0]
                add_image(first_src)
        
        # Extract background images from style attributes
        for elem in soup.find_all(style=True):
            style = elem.get("style", "")
            bg_match = re.search(r'background(?:-image)?:\s*url\(["\']?([^"\')\s]+)["\']?\)', style)
            if bg_match:
                add_image(bg_match.group(1))
    else:
        # Regex fallback - less comprehensive but works without BS4
        
        # srcset first
        srcset_imgs = extract_srcset_images(html, base_url)
        for item in srcset_imgs[:3]:
            add_image(item["url"])
        
        # img src/data-src
        img_pattern = r'<img[^>]+(?:src|data-src|data-lazy-src)=["\']([^"\']+)["\']'
        for match in re.finditer(img_pattern, html, re.IGNORECASE):
            add_image(match.group(1))
        
        # background-image
        bg_pattern = r'background(?:-image)?:\s*url\(["\']?([^"\')\s]+)["\']?\)'
        for match in re.finditer(bg_pattern, html, re.IGNORECASE):
            add_image(match.group(1))
    
    return images


def _is_likely_icon(url: str) -> bool:
    """Check if a URL looks like it points to an icon/small image."""
    url_lower = url.lower()
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, url_lower):
            return True
    return False


def filter_images_by_cdn(images: list[str], source_id: str) -> list[str]:
    """Filter images to only include those matching CDN patterns."""
    patterns = get_cdn_patterns(source_id)
    if not patterns:
        return images
    
    filtered = []
    for img in images:
        for pattern in patterns:
            if pattern in img:
                filtered.append(img)
                break
    
    return filtered


def extract_image_dimensions(img_tag: str) -> tuple[int, int]:
    """Extract width and height from an img tag string."""
    width = 0
    height = 0
    
    width_match = re.search(r'width=["\']?(\d+)', img_tag, re.IGNORECASE)
    if width_match:
        width = int(width_match.group(1))
    
    height_match = re.search(r'height=["\']?(\d+)', img_tag, re.IGNORECASE)
    if height_match:
        height = int(height_match.group(1))
    
    return width, height


def score_image_url(url: str, source_id: str = "") -> float:
    """
    Score an image URL from 0.0 to 1.0 based on quality indicators.
    
    Higher scores indicate better quality images.
    """
    score = 0.5  # Base score
    url_lower = url.lower()
    
    # Boost for CDN patterns
    if source_id:
        cdn_patterns = get_cdn_patterns(source_id)
        for pattern in cdn_patterns:
            if pattern in url_lower:
                score += 0.3
                break
    
    # Boost for high-res indicators
    if any(x in url_lower for x in ["_large", "_original", "_full", "max_", "@2x", "@3x", "hd", "1200", "1920"]):
        score += 0.2
    
    # Penalty for low-res indicators
    if any(x in url_lower for x in ["_thumb", "_small", "_tiny", "thumbnail", "preview", "100x", "50x"]):
        score -= 0.3
    
    # Penalty for likely icons
    if _is_likely_icon(url):
        score -= 0.5
    
    return max(0.0, min(1.0, score))


def find_best_image(
    html: str,
    url: str,
    source_id: str
) -> Optional[str]:
    """
    Find the best image for a reference.
    
    Priority:
    1. OG image (if valid)
    2. Highest-scored image from srcset
    3. CDN-matching images
    4. Highest-scored regular image
    """
    # Try OG image first
    og_image = extract_og_image(html)
    if og_image and is_valid_image_url(og_image) and not _is_likely_icon(og_image):
        return normalize_image_url(og_image)
    
    # Extract domain for base URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Try srcset images (usually highest quality)
    srcset_images = extract_srcset_images(html, base_url)
    for item in srcset_images:
        img_url = item["url"]
        if is_valid_image_url(img_url) and not _is_likely_icon(img_url):
            # Prefer images with width > 400
            if item["width"] == 0 or item["width"] >= 400:
                return normalize_image_url(img_url)
    
    # Get all images
    all_images = extract_images_from_html(html, base_url)
    
    # Filter by CDN patterns first
    cdn_images = filter_images_by_cdn(all_images, source_id)
    if cdn_images:
        # Score and sort
        scored = [(img, score_image_url(img, source_id)) for img in cdn_images]
        scored.sort(key=lambda x: -x[1])
        if scored:
            return normalize_image_url(scored[0][0])
    
    # Score all images and return best
    if all_images:
        scored = [(img, score_image_url(img, source_id)) for img in all_images]
        scored.sort(key=lambda x: -x[1])
        # Only return if score is decent
        if scored and scored[0][1] >= 0.3:
            return normalize_image_url(scored[0][0])
    
    return None


def is_valid_image_url(url: str) -> bool:
    """Check if a URL looks like a valid image URL."""
    if not url:
        return False
    
    # Must be http/https
    if not url.startswith(("http://", "https://", "//")):
        return False
    
    # Check common image extensions
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif"]
    url_lower = url.lower()
    
    # Remove query params for extension check
    url_path = url_lower.split("?")[0]
    
    # Check if URL has image extension
    for ext in image_extensions:
        if url_path.endswith(ext):
            return True
    
    # Some CDNs don't use extensions, check common CDN patterns
    cdn_patterns = [
        "cdn.dribbble.com",
        "d13yacurqjgara.cloudfront.net",
        "mir-s3-cdn-cf.behance.net",
        "mir-cdn.behance.net",
        "figma-alpha-api.s3.us-west-2.amazonaws.com",
        "behance.net",
        "figma.com",
        "i.ytimg.com",
        "i.redd.it",
        "imgur.com",
        "cloudinary.com",
        "cloudfront.net",
        "mobbin.com/_next/image",
        "res.cloudinary.com",
        "assets.awwwards.com",
    ]
    
    for pattern in cdn_patterns:
        if pattern in url_lower:
            return True
    
    return False


def normalize_image_url(url: str) -> str:
    """Normalize an image URL."""
    if not url:
        return url
    
    # Handle protocol-relative URLs
    if url.startswith("//"):
        url = "https:" + url
    
    # Keep image-related query params, remove tracking params
    if "?" in url:
        base, params_str = url.split("?", 1)
        params = params_str.split("&")
        
        # Params to keep (image-related)
        keep_params = []
        image_param_patterns = ["width", "height", "w=", "h=", "size", "format", "quality", "fit", "crop"]
        
        for param in params:
            param_lower = param.lower()
            if any(p in param_lower for p in image_param_patterns):
                keep_params.append(param)
        
        if keep_params:
            url = base + "?" + "&".join(keep_params)
        else:
            url = base
    
    return url


def encode_image_to_base64(image_data: bytes, content_type: str = "image/png") -> str:
    """Encode image data to a base64 data URL."""
    b64 = base64.b64encode(image_data).decode("utf-8")
    return f"data:{content_type};base64,{b64}"


def get_content_type_from_url(url: str) -> str:
    """Guess content type from URL."""
    url_lower = url.lower()
    
    if ".png" in url_lower:
        return "image/png"
    elif ".gif" in url_lower:
        return "image/gif"
    elif ".webp" in url_lower:
        return "image/webp"
    elif ".svg" in url_lower:
        return "image/svg+xml"
    elif ".avif" in url_lower:
        return "image/avif"
    else:
        return "image/jpeg"


def extract_reddit_images(html: str) -> list[str]:
    """Extract images from Reddit post content."""
    images = []
    
    # Look for imgur links
    imgur_pattern = r'https?://(?:i\.)?imgur\.com/[a-zA-Z0-9]+(?:\.[a-z]+)?'
    for match in re.finditer(imgur_pattern, html):
        url = match.group(0)
        if not url.endswith((".jpg", ".png", ".gif")):
            url += ".jpg"
        images.append(url)
    
    # Look for i.redd.it links
    reddit_pattern = r'https?://i\.redd\.it/[a-zA-Z0-9]+\.[a-z]+'
    for match in re.finditer(reddit_pattern, html):
        images.append(match.group(0))
    
    return images


def construct_dribbble_thumbnail(shot_url: str) -> Optional[str]:
    """
    Construct a Dribbble thumbnail URL from a shot URL.
    
    Dribbble shot URLs: https://dribbble.com/shots/12345678-Some-Title
    Thumbnail pattern: https://cdn.dribbble.com/userupload/12345678/file/original-hash.png
    
    Note: This is a best-effort construction; may not work for all shots.
    """
    match = re.search(r'/shots/(\d+)', shot_url)
    if not match:
        return None
    
    shot_id = match.group(1)
    # Return a pattern that could work (actual implementation would need API)
    return f"https://cdn.dribbble.com/userupload/{shot_id}/file/original.png"


def construct_youtube_thumbnail(video_url: str) -> Optional[str]:
    """
    Construct a YouTube thumbnail URL from a video URL.
    
    YouTube video URLs:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    
    Thumbnail: https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg
    """
    # Try watch?v= pattern
    match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', video_url)
    if not match:
        # Try youtu.be pattern
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', video_url)
    
    if not match:
        return None
    
    video_id = match.group(1)
    return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"


def get_fallback_image_for_source(url: str, source_id: str) -> Optional[str]:
    """
    Get a fallback image URL when direct fetch fails.
    
    Uses source-specific URL construction.
    """
    if source_id == "youtube":
        return construct_youtube_thumbnail(url)
    elif source_id == "dribbble":
        return construct_dribbble_thumbnail(url)
    
    return None
