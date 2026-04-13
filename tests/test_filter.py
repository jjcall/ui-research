"""Tests for URL quality filtering."""

import sys
import unittest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.filter import (
    is_individual_page,
    is_collection_page,
    score_url_quality,
    filter_references,
    classify_url,
    debug_url,
    debug_urls,
    INDIVIDUAL_PATTERNS,
    COLLECTION_PATTERNS,
)
from lib.schema import Reference


class TestIsIndividualPage(unittest.TestCase):
    """Tests for is_individual_page function."""
    
    def test_mobbin_individual_screen(self):
        url = "https://mobbin.com/explore/screens/f8ebcf5b-5795-4f31-8209-536194617a26"
        self.assertTrue(is_individual_page(url, "mobbin"))
    
    def test_mobbin_collection_page(self):
        url = "https://mobbin.com/explore/mobile/screens"
        self.assertFalse(is_individual_page(url, "mobbin"))
    
    def test_dribbble_shot(self):
        url = "https://dribbble.com/shots/25799561-Orium-AI-powered-cloud-data-platform"
        self.assertTrue(is_individual_page(url, "dribbble"))
    
    def test_dribbble_search(self):
        url = "https://dribbble.com/search?q=kanban"
        self.assertFalse(is_individual_page(url, "dribbble"))
    
    def test_behance_gallery(self):
        url = "https://www.behance.net/gallery/123456789/Dashboard-UI-Design"
        self.assertTrue(is_individual_page(url, "behance"))
    
    def test_behance_search(self):
        url = "https://www.behance.net/search/projects/dashboard"
        self.assertFalse(is_individual_page(url, "behance"))
    
    def test_figma_community_file(self):
        url = "https://www.figma.com/community/file/1034483012549130899"
        self.assertTrue(is_individual_page(url, "figma"))
    
    def test_youtube_watch(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertTrue(is_individual_page(url, "youtube"))
    
    def test_youtube_playlist(self):
        url = "https://www.youtube.com/playlist?list=PLxyz"
        self.assertFalse(is_individual_page(url, "youtube"))
    
    def test_reddit_comment(self):
        url = "https://www.reddit.com/r/UI_Design/comments/abc123/my_design"
        self.assertTrue(is_individual_page(url, "reddit"))
    
    def test_v0_chat(self):
        url = "https://v0.dev/chat/page-structure-example-xKZIc1bIaJN"
        self.assertTrue(is_individual_page(url, "v0"))
    
    def test_v0_t(self):
        url = "https://v0.dev/t/zbCjlXw9LLl"
        self.assertTrue(is_individual_page(url, "v0"))
    
    def test_godly_website(self):
        url = "https://godly.website/website/entire-studios-872"
        self.assertTrue(is_individual_page(url, "godly"))
    
    def test_awwwards_site(self):
        url = "https://www.awwwards.com/sites/stripe-checkout"
        self.assertTrue(is_individual_page(url, "awwwards"))
    
    def test_lapaninja_post(self):
        url = "https://www.lapa.ninja/post/every-layout-2/"
        self.assertTrue(is_individual_page(url, "lapaninja"))
    
    def test_uisyntax_design(self):
        url = "https://ui-syntax.com/design/luxury-product-showcase-ui"
        self.assertTrue(is_individual_page(url, "uisyntax"))


class TestIsCollectionPage(unittest.TestCase):
    """Tests for is_collection_page function."""
    
    def test_mobbin_browse(self):
        url = "https://mobbin.com/browse/ios"
        self.assertTrue(is_collection_page(url, "mobbin"))
    
    def test_mobbin_mobile_screens(self):
        url = "https://mobbin.com/explore/mobile/screens"
        self.assertTrue(is_collection_page(url, "mobbin"))
    
    def test_dribbble_tags(self):
        url = "https://dribbble.com/tags/dashboard"
        self.assertTrue(is_collection_page(url, "dribbble"))
    
    def test_dribbble_designers(self):
        url = "https://dribbble.com/designers"
        self.assertTrue(is_collection_page(url, "dribbble"))
    
    def test_behance_galleries(self):
        url = "https://www.behance.net/galleries/interaction"
        self.assertTrue(is_collection_page(url, "behance"))
    
    def test_figma_community_search(self):
        url = "https://www.figma.com/community/search?q=dashboard"
        self.assertTrue(is_collection_page(url, "figma"))
    
    def test_youtube_results(self):
        url = "https://www.youtube.com/results?search_query=ui+design"
        self.assertTrue(is_collection_page(url, "youtube"))
    
    def test_youtube_channel(self):
        url = "https://www.youtube.com/@DesignCourse"
        self.assertTrue(is_collection_page(url, "youtube"))
    
    def test_reddit_search(self):
        url = "https://www.reddit.com/r/UI_Design/search?q=dashboard"
        self.assertTrue(is_collection_page(url, "reddit"))
    
    def test_reddit_hot(self):
        url = "https://www.reddit.com/r/UI_Design/hot"
        self.assertTrue(is_collection_page(url, "reddit"))
    
    def test_lapaninja_category(self):
        url = "https://www.lapa.ninja/category/saas/"
        self.assertTrue(is_collection_page(url, "lapaninja"))
    
    def test_godly_websites(self):
        url = "https://godly.website/websites/e-commerce"
        self.assertTrue(is_collection_page(url, "godly"))
    
    def test_awwwards_collections(self):
        url = "https://www.awwwards.com/collections/portfolio"
        self.assertTrue(is_collection_page(url, "awwwards"))
    
    def test_individual_not_collection(self):
        url = "https://dribbble.com/shots/12345678-My-Design"
        self.assertFalse(is_collection_page(url, "dribbble"))


class TestScoreUrlQuality(unittest.TestCase):
    """Tests for score_url_quality function."""
    
    def test_individual_page_high_score(self):
        url = "https://dribbble.com/shots/12345678-Dashboard"
        score = score_url_quality(url, "dribbble")
        self.assertEqual(score, 1.0)
    
    def test_collection_page_zero_score(self):
        url = "https://dribbble.com/search?q=dashboard"
        score = score_url_quality(url, "dribbble")
        self.assertEqual(score, 0.0)
    
    def test_unknown_url_middle_score(self):
        url = "https://example.com/some-page"
        score = score_url_quality(url, "product")
        self.assertEqual(score, 0.5)
    
    def test_empty_url_zero_score(self):
        score = score_url_quality("", "dribbble")
        self.assertEqual(score, 0.0)


class TestFilterReferences(unittest.TestCase):
    """Tests for filter_references function."""
    
    def create_ref(self, url: str, source: str, title: str = "Test") -> Reference:
        return Reference(
            url=url,
            title=title,
            description="Test description",
            source=source,
            source_label=source.title(),
            category="test"
        )
    
    def test_removes_collection_pages(self):
        refs = [
            self.create_ref("https://dribbble.com/shots/123", "dribbble", "Individual"),
            self.create_ref("https://dribbble.com/search?q=test", "dribbble", "Collection"),
            self.create_ref("https://mobbin.com/explore/screens/abc-123", "mobbin", "Screen"),
        ]
        filtered = filter_references(refs, remove_collections=True)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r.title != "Collection" for r in filtered))
    
    def test_keeps_collection_pages_when_disabled(self):
        refs = [
            self.create_ref("https://dribbble.com/shots/123", "dribbble", "Individual"),
            self.create_ref("https://dribbble.com/search?q=test", "dribbble", "Collection"),
        ]
        filtered = filter_references(refs, remove_collections=False)
        self.assertEqual(len(filtered), 2)
    
    def test_sorts_by_quality(self):
        refs = [
            self.create_ref("https://example.com/unknown", "product", "Unknown"),
            self.create_ref("https://dribbble.com/shots/123", "dribbble", "Individual"),
        ]
        filtered = filter_references(refs)
        self.assertEqual(filtered[0].title, "Individual")  # Quality 1.0
        self.assertEqual(filtered[1].title, "Unknown")  # Quality 0.5
    
    def test_min_quality_filter(self):
        refs = [
            self.create_ref("https://dribbble.com/shots/123", "dribbble", "High"),
            self.create_ref("https://example.com/unknown", "product", "Medium"),
        ]
        filtered = filter_references(refs, min_quality=0.8)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "High")


class TestClassifyUrl(unittest.TestCase):
    """Tests for classify_url function."""
    
    def test_detects_source_from_url(self):
        result = classify_url("https://dribbble.com/shots/12345")
        self.assertEqual(result["source_id"], "dribbble")
        self.assertTrue(result["is_individual"])
        self.assertFalse(result["is_collection"])
        self.assertEqual(result["quality"], 1.0)
    
    def test_detects_collection(self):
        result = classify_url("https://www.behance.net/search/projects/dashboard")
        self.assertEqual(result["source_id"], "behance")
        self.assertFalse(result["is_individual"])
        self.assertTrue(result["is_collection"])
        self.assertEqual(result["quality"], 0.0)
    
    def test_unknown_url(self):
        result = classify_url("https://example.com/page")
        self.assertFalse(result["is_individual"])
        self.assertFalse(result["is_collection"])
        self.assertEqual(result["quality"], 0.5)
    
    def test_empty_url(self):
        result = classify_url("")
        self.assertIsNone(result["source_id"])
        self.assertEqual(result["quality"], 0.5)


class TestAllSourcesHavePatterns(unittest.TestCase):
    """Tests to ensure all expected sources have patterns defined."""
    
    EXPECTED_SOURCES = [
        "mobbin", "screenlane", "pageflows", "uisources", "pttrns",
        "dribbble", "behance", "figma",
        "v0", "uisyntax", "inspoai",
        "lapaninja", "saaspages", "godly", "awwwards", "designspells",
        "youtube", "reddit"
    ]
    
    def test_individual_patterns_exist(self):
        for source in self.EXPECTED_SOURCES:
            self.assertIn(source, INDIVIDUAL_PATTERNS, f"Missing individual patterns for {source}")
            self.assertGreater(len(INDIVIDUAL_PATTERNS[source]), 0, f"Empty individual patterns for {source}")
    
    def test_collection_patterns_exist(self):
        for source in self.EXPECTED_SOURCES:
            self.assertIn(source, COLLECTION_PATTERNS, f"Missing collection patterns for {source}")
            self.assertGreater(len(COLLECTION_PATTERNS[source]), 0, f"Empty collection patterns for {source}")


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and special scenarios."""
    
    def test_case_insensitive(self):
        url = "https://DRIBBBLE.COM/shots/12345"
        self.assertTrue(is_individual_page(url, "dribbble"))
    
    def test_with_query_params(self):
        url = "https://dribbble.com/shots/12345?utm_source=test"
        self.assertTrue(is_individual_page(url, "dribbble"))
    
    def test_with_fragment(self):
        url = "https://dribbble.com/shots/12345#comments"
        self.assertTrue(is_individual_page(url, "dribbble"))
    
    def test_without_source_id_checks_all(self):
        url = "https://dribbble.com/shots/12345"
        self.assertTrue(is_individual_page(url))
        
        url = "https://dribbble.com/search?q=test"
        self.assertTrue(is_collection_page(url))
    
    def test_youtu_be_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = classify_url(url)
        self.assertEqual(result["source_id"], "youtube")


class TestDebugUrl(unittest.TestCase):
    """Tests for debug_url function."""
    
    def test_individual_page_output(self):
        url = "https://dribbble.com/shots/12345678"
        output = debug_url(url)
        self.assertIn("URL: https://dribbble.com/shots/12345678", output)
        self.assertIn("Source: dribbble", output)
        self.assertIn("1.0 (individual)", output)
        self.assertIn("Pattern:", output)
    
    def test_collection_page_output(self):
        url = "https://dribbble.com/search?q=kanban"
        output = debug_url(url)
        self.assertIn("0.0 (collection)", output)
        self.assertIn("FILTERED", output)
    
    def test_unknown_page_output(self):
        url = "https://example.com/some-design"
        output = debug_url(url)
        self.assertIn("0.5 (unknown)", output)


class TestDebugUrls(unittest.TestCase):
    """Tests for debug_urls function."""
    
    def test_summary_counts(self):
        urls = [
            "https://dribbble.com/shots/12345",  # individual
            "https://dribbble.com/search?q=test",  # collection
            "https://example.com/page",  # unknown
        ]
        output = debug_urls(urls)
        self.assertIn("2 kept", output)
        self.assertIn("1 filtered", output)
    
    def test_includes_header(self):
        urls = ["https://dribbble.com/shots/12345"]
        output = debug_urls(urls)
        self.assertIn("DEBUG: URL Classification", output)


if __name__ == "__main__":
    unittest.main()
