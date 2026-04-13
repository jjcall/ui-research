"""Playwright-based screenshot capture for UI references."""

import asyncio
import base64
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Playwright is optional - check if available
try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    async_playwright = None
    Browser = None
    Page = None
    PlaywrightTimeout = Exception


# Screenshot settings
VIEWPORT_WIDTH = 1440
VIEWPORT_HEIGHT = 900
SCREENSHOT_TIMEOUT = 15000  # 15 seconds per page
MAX_CONCURRENT = 5  # Max concurrent browser pages


def is_playwright_available() -> bool:
    """Check if Playwright is installed and browsers are available."""
    if not HAS_PLAYWRIGHT:
        return False
    
    # Check if chromium is installed
    try:
        import subprocess
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True
    except Exception:
        # If we can't check, assume it's available if the module imported
        return HAS_PLAYWRIGHT


def get_cache_dir() -> Path:
    """Get the screenshot cache directory."""
    cache_dir = Path.home() / ".cache" / "ui-research" / "screenshots"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_path(url: str) -> Path:
    """Get the cache file path for a URL."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return get_cache_dir() / f"{url_hash}.png"


def get_cached_screenshot(url: str) -> Optional[str]:
    """Get a cached screenshot as base64 if it exists."""
    cache_path = get_cache_path(url)
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            data = f.read()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    return None


def save_to_cache(url: str, screenshot_data: bytes) -> Path:
    """Save screenshot data to cache."""
    cache_path = get_cache_path(url)
    with open(cache_path, "wb") as f:
        f.write(screenshot_data)
    return cache_path


async def capture_screenshot(
    page: "Page",
    url: str,
    wait_for: str = "networkidle",
    full_page: bool = False
) -> Optional[bytes]:
    """
    Capture a screenshot of a URL using an existing page.
    
    Args:
        page: Playwright page instance
        url: URL to capture
        wait_for: Wait strategy ("networkidle", "load", "domcontentloaded")
        full_page: If True, capture full scrollable page
    
    Returns:
        Screenshot bytes or None if failed
    """
    try:
        # Navigate to URL
        await page.goto(url, wait_until=wait_for, timeout=SCREENSHOT_TIMEOUT)
        
        # Wait a bit for any animations/lazy loading
        await page.wait_for_timeout(1000)
        
        # Hide cookie banners and modals
        await _hide_overlays(page)
        
        # Take screenshot
        screenshot = await page.screenshot(
            full_page=full_page,
            type="png"
        )
        
        return screenshot
        
    except PlaywrightTimeout:
        # Try with shorter timeout and different wait strategy
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=10000)
            await page.wait_for_timeout(500)
            return await page.screenshot(type="png")
        except Exception:
            return None
    except Exception as e:
        print(f"Screenshot failed for {url}: {e}")
        return None


async def _hide_overlays(page: "Page") -> None:
    """Hide common overlay elements like cookie banners."""
    selectors_to_hide = [
        # Cookie consent
        '[class*="cookie"]',
        '[class*="consent"]',
        '[class*="gdpr"]',
        '[id*="cookie"]',
        '[id*="consent"]',
        # Modals and overlays
        '[class*="modal"]',
        '[class*="overlay"]',
        '[class*="popup"]',
        '[class*="banner"]',
        # Common specific selectors
        '.onetrust-consent-sdk',
        '#CybotCookiebotDialog',
        '.cc-banner',
    ]
    
    for selector in selectors_to_hide:
        try:
            await page.evaluate(f'''
                document.querySelectorAll('{selector}').forEach(el => {{
                    el.style.display = 'none';
                }});
            ''')
        except Exception:
            pass


async def capture_screenshots_batch(
    urls: list[str],
    max_concurrent: int = MAX_CONCURRENT,
    use_cache: bool = True,
    progress_callback: Optional[callable] = None
) -> dict[str, Optional[str]]:
    """
    Capture screenshots for multiple URLs in parallel.
    
    Args:
        urls: List of URLs to capture
        max_concurrent: Maximum concurrent browser pages
        use_cache: Whether to use/update the screenshot cache
        progress_callback: Optional callback(completed, total, url) for progress
    
    Returns:
        Dict mapping URL to base64 data URL (or None if failed)
    """
    if not HAS_PLAYWRIGHT:
        return {url: None for url in urls}
    
    results = {}
    urls_to_capture = []
    
    # Check cache first
    if use_cache:
        for url in urls:
            cached = get_cached_screenshot(url)
            if cached:
                results[url] = cached
            else:
                urls_to_capture.append(url)
    else:
        urls_to_capture = list(urls)
    
    if not urls_to_capture:
        return results
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        semaphore = asyncio.Semaphore(max_concurrent)
        completed = len(results)
        total = len(urls)
        
        async def capture_with_semaphore(url: str) -> tuple[str, Optional[str]]:
            nonlocal completed
            async with semaphore:
                page = await context.new_page()
                try:
                    screenshot_data = await capture_screenshot(page, url)
                    
                    if screenshot_data:
                        if use_cache:
                            save_to_cache(url, screenshot_data)
                        b64 = base64.b64encode(screenshot_data).decode()
                        result = f"data:image/png;base64,{b64}"
                    else:
                        result = None
                    
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, url)
                    
                    return url, result
                finally:
                    await page.close()
        
        # Capture all URLs concurrently (limited by semaphore)
        tasks = [capture_with_semaphore(url) for url in urls_to_capture]
        captured = await asyncio.gather(*tasks)
        
        for url, data in captured:
            results[url] = data
        
        await browser.close()
    
    return results


def capture_screenshots_sync(
    urls: list[str],
    max_concurrent: int = MAX_CONCURRENT,
    use_cache: bool = True,
    progress_callback: Optional[callable] = None
) -> dict[str, Optional[str]]:
    """
    Synchronous wrapper for capture_screenshots_batch.
    
    Use this from non-async code.
    """
    return asyncio.run(
        capture_screenshots_batch(
            urls,
            max_concurrent=max_concurrent,
            use_cache=use_cache,
            progress_callback=progress_callback
        )
    )


def clear_cache() -> int:
    """Clear all cached screenshots. Returns number of files deleted."""
    cache_dir = get_cache_dir()
    count = 0
    for f in cache_dir.glob("*.png"):
        f.unlink()
        count += 1
    return count


def get_cache_stats() -> dict:
    """Get cache statistics."""
    cache_dir = get_cache_dir()
    files = list(cache_dir.glob("*.png"))
    total_size = sum(f.stat().st_size for f in files)
    
    return {
        "count": len(files),
        "size_bytes": total_size,
        "size_mb": round(total_size / (1024 * 1024), 2),
        "path": str(cache_dir)
    }
