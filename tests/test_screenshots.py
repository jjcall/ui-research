"""Tests for screenshot capture module."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.screenshots import (
    get_cache_dir,
    get_cache_path,
    get_cached_screenshot,
    is_playwright_available,
    HAS_PLAYWRIGHT,
)


class TestCacheDir(unittest.TestCase):
    """Tests for cache directory functions."""
    
    def test_cache_dir_is_path(self):
        cache_dir = get_cache_dir()
        self.assertIsInstance(cache_dir, Path)
    
    def test_cache_dir_under_home(self):
        cache_dir = get_cache_dir()
        self.assertTrue(str(cache_dir).startswith(str(Path.home())))
    
    def test_cache_dir_contains_ui_research(self):
        cache_dir = get_cache_dir()
        self.assertIn("ui-research", str(cache_dir))


class TestCachePath(unittest.TestCase):
    """Tests for cache path generation."""
    
    def test_cache_path_is_png(self):
        path = get_cache_path("https://example.com/page")
        self.assertTrue(str(path).endswith(".png"))
    
    def test_same_url_same_path(self):
        url = "https://example.com/test"
        path1 = get_cache_path(url)
        path2 = get_cache_path(url)
        self.assertEqual(path1, path2)
    
    def test_different_urls_different_paths(self):
        path1 = get_cache_path("https://example.com/a")
        path2 = get_cache_path("https://example.com/b")
        self.assertNotEqual(path1, path2)


class TestCachedScreenshot(unittest.TestCase):
    """Tests for cached screenshot retrieval."""
    
    def test_nonexistent_returns_none(self):
        result = get_cached_screenshot("https://definitely-not-cached.example.com/xyz123")
        self.assertIsNone(result)


class TestPlaywrightAvailable(unittest.TestCase):
    """Tests for Playwright availability check."""
    
    def test_returns_bool(self):
        result = is_playwright_available()
        self.assertIsInstance(result, bool)
    
    def test_has_playwright_is_bool(self):
        self.assertIsInstance(HAS_PLAYWRIGHT, bool)


if __name__ == "__main__":
    unittest.main()
