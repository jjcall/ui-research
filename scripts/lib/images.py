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
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def extract_images_from_html(html: str, base_url: str = "") -> list[str]:
    """
    Extract image URLs from HTML content.
    
    Looks for:
    - <img> tags with src attributes
    - CSS background-image URLs
    - data-src attributes (lazy loading)
    """
    images = []
    
    if HAS_BS4:
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all img tags
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and not src.startswith("data:"):
                if base_url and not src.startswith(("http://", "https://", "//")):
                    src = urljoin(base_url, src)
                images.append(src)
    else:
        # Regex fallback
        img_pattern = r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']'
        for match in re.finditer(img_pattern, html, re.IGNORECASE):
            src = match.group(1)
            if not src.startswith("data:"):
                if base_url and not src.startswith(("http://", "https://", "//")):
                    src = urljoin(base_url, src)
                images.append(src)
    
    return images


def filter_images_by_cdn(images: list[str], source_id: str) -> list[str]:
    """
    Filter images to only include those matching CDN patterns.
    """
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


def find_best_image(
    html: str,
    url: str,
    source_id: str
) -> Optional[str]:
    """
    Find the best image for a reference.
    
    Priority:
    1. OG image
    2. Images matching CDN patterns
    3. First large image in content
    """
    # Try OG image first
    og_image = extract_og_image(html)
    if og_image:
        return og_image
    
    # Extract domain for base URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Get all images
    all_images = extract_images_from_html(html, base_url)
    
    # Filter by CDN patterns
    cdn_images = filter_images_by_cdn(all_images, source_id)
    if cdn_images:
        return cdn_images[0]
    
    # Return first image as fallback
    if all_images:
        return all_images[0]
    
    return None


def is_valid_image_url(url: str) -> bool:
    """Check if a URL looks like a valid image URL."""
    if not url:
        return False
    
    # Must be http/https
    if not url.startswith(("http://", "https://", "//")):
        return False
    
    # Check common image extensions
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]
    url_lower = url.lower()
    
    # Check if URL has image extension
    for ext in image_extensions:
        if ext in url_lower:
            return True
    
    # Some CDNs don't use extensions, check common CDN patterns
    cdn_patterns = [
        "cdn.dribbble.com",
        "behance.net",
        "figma.com",
        "i.ytimg.com",
        "i.redd.it",
        "imgur.com",
        "cloudinary.com",
        "cloudfront.net",
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
    
    # Remove tracking parameters
    if "?" in url:
        base_url = url.split("?")[0]
        # Keep parameters that look image-related
        params = url.split("?")[1] if "?" in url else ""
        if not any(p in params.lower() for p in ["width", "height", "w=", "h=", "size"]):
            url = base_url
    
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
