"""Tests for social platform search module."""

import sys
import unittest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.social import (
    parse_reddit_result,
    parse_x_result,
    parse_youtube_result,
    parse_hackernews_result,
    parse_producthunt_result,
    parse_search_result,
    group_refs_by_type,
    generate_social_queries,
    format_engagement_stats,
    has_scrapecreators_key,
    _parse_number,
)
from lib.schema import Reference, Engagement


class TestParseNumber(unittest.TestCase):
    """Tests for _parse_number helper."""
    
    def test_plain_number(self):
        self.assertEqual(_parse_number("123"), 123)
    
    def test_number_with_comma(self):
        self.assertEqual(_parse_number("1,234"), 1234)
    
    def test_k_suffix(self):
        self.assertEqual(_parse_number("1.2K"), 1200)
        self.assertEqual(_parse_number("5k"), 5000)
    
    def test_m_suffix(self):
        self.assertEqual(_parse_number("1.5M"), 1500000)
        self.assertEqual(_parse_number("2m"), 2000000)


class TestParseRedditResult(unittest.TestCase):
    """Tests for parse_reddit_result."""
    
    def test_parses_valid_reddit_url(self):
        result = {
            "url": "https://reddit.com/r/UI_Design/comments/abc123/how_linear_nailed_planning_mode/",
            "title": "How Linear nailed planning mode",
            "description": "847 upvotes, 234 comments"
        }
        ref = parse_reddit_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "reddit")
        self.assertEqual(ref.source_type, "discussion")
        self.assertEqual(ref.engagement.upvotes, 847)
        self.assertEqual(ref.engagement.comments, 234)
        self.assertIn("r/UI_Design", ref.tags)
    
    def test_skips_non_reddit_url(self):
        result = {"url": "https://dribbble.com/shots/123", "title": "Test"}
        ref = parse_reddit_result(result)
        self.assertIsNone(ref)
    
    def test_skips_search_page(self):
        result = {"url": "https://reddit.com/search?q=kanban", "title": "Search"}
        ref = parse_reddit_result(result)
        self.assertIsNone(ref)


class TestParseXResult(unittest.TestCase):
    """Tests for parse_x_result."""
    
    def test_parses_valid_x_url(self):
        result = {
            "url": "https://x.com/frankchimero/status/123456789",
            "title": "@frankchimero on X: The best planning UIs...",
            "description": "1.2K likes, 89 retweets"
        }
        ref = parse_x_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "x")
        self.assertEqual(ref.source_type, "discussion")
        self.assertEqual(ref.author, "@frankchimero")
        self.assertEqual(ref.engagement.likes, 1200)
        self.assertEqual(ref.engagement.shares, 89)
    
    def test_parses_twitter_url(self):
        result = {
            "url": "https://twitter.com/round/status/987654321",
            "title": "Tweet content"
        }
        ref = parse_x_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "x")
        self.assertEqual(ref.author, "@round")


class TestParseYoutubeResult(unittest.TestCase):
    """Tests for parse_youtube_result."""
    
    def test_parses_watch_url(self):
        result = {
            "url": "https://youtube.com/watch?v=abc123xyz",
            "title": "Building a Planning App in Figma",
            "description": "12K views, 456 likes"
        }
        ref = parse_youtube_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "youtube")
        self.assertEqual(ref.source_type, "video")
        self.assertEqual(ref.engagement.views, 12000)
        self.assertEqual(ref.engagement.likes, 456)
        self.assertIn("i.ytimg.com", ref.image_url)
    
    def test_parses_youtu_be_url(self):
        result = {
            "url": "https://youtu.be/abc123xyz",
            "title": "Short video"
        }
        ref = parse_youtube_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.image_url, "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg")
    
    def test_skips_playlist(self):
        result = {"url": "https://youtube.com/playlist?list=abc", "title": "Playlist"}
        ref = parse_youtube_result(result)
        self.assertIsNone(ref)


class TestParseHackernewsResult(unittest.TestCase):
    """Tests for parse_hackernews_result."""
    
    def test_parses_hn_url(self):
        result = {
            "url": "https://news.ycombinator.com/item?id=12345678",
            "title": "Show HN: Open-source planning tool",
            "description": "234 points, 89 comments by johndoe"
        }
        ref = parse_hackernews_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "hackernews")
        self.assertEqual(ref.engagement.upvotes, 234)
        self.assertEqual(ref.engagement.comments, 89)
        self.assertEqual(ref.author, "johndoe")


class TestParseProducthuntResult(unittest.TestCase):
    """Tests for parse_producthunt_result."""
    
    def test_parses_ph_url(self):
        result = {
            "url": "https://producthunt.com/posts/planwise",
            "title": "Planwise - AI planning assistant",
            "description": "456 upvotes"
        }
        ref = parse_producthunt_result(result)
        
        self.assertIsNotNone(ref)
        self.assertEqual(ref.source, "producthunt")
        self.assertEqual(ref.source_type, "launch")
        self.assertEqual(ref.engagement.upvotes, 456)


class TestParseSearchResult(unittest.TestCase):
    """Tests for parse_search_result with auto-detection."""
    
    def test_auto_detects_reddit(self):
        result = {"url": "https://reddit.com/r/UI_Design/comments/abc/test/", "title": "Test"}
        ref = parse_search_result(result, "auto")
        self.assertEqual(ref.source, "reddit")
    
    def test_auto_detects_youtube(self):
        result = {"url": "https://youtube.com/watch?v=abc", "title": "Test"}
        ref = parse_search_result(result, "auto")
        self.assertEqual(ref.source, "youtube")


class TestGroupRefsByType(unittest.TestCase):
    """Tests for group_refs_by_type."""
    
    def test_groups_correctly(self):
        refs = [
            Reference(url="a", title="A", description="", source="dribbble", category="test", source_type="design"),
            Reference(url="b", title="B", description="", source="reddit", category="test", source_type="discussion"),
            Reference(url="c", title="C", description="", source="youtube", category="test", source_type="video"),
            Reference(url="d", title="D", description="", source="producthunt", category="test", source_type="launch"),
        ]
        
        groups = group_refs_by_type(refs)
        
        self.assertEqual(len(groups["design"]), 1)
        self.assertEqual(len(groups["discussion"]), 1)
        self.assertEqual(len(groups["video"]), 1)
        self.assertEqual(len(groups["launch"]), 1)


class TestGenerateSocialQueries(unittest.TestCase):
    """Tests for generate_social_queries."""
    
    def test_generates_queries_for_all_platforms(self):
        queries = generate_social_queries("planning mode", ["kanban", "timeline"])
        
        self.assertIn("reddit", queries)
        self.assertIn("x", queries)
        self.assertIn("youtube", queries)
        self.assertIn("hackernews", queries)
        self.assertIn("producthunt", queries)
        
        self.assertTrue(len(queries["reddit"]) > 0)
        self.assertTrue(len(queries["youtube"]) > 0)


class TestEngagement(unittest.TestCase):
    """Tests for Engagement class."""
    
    def test_score_calculation(self):
        eng = Engagement(likes=100, comments=50, shares=10)
        # score = 100 + 0 + (50 * 2) + (10 * 3) + 0 = 230
        self.assertEqual(eng.score, 230)
    
    def test_format_compact(self):
        eng = Engagement(upvotes=847, comments=234)
        formatted = eng.format_compact()
        self.assertIn("847↑", formatted)
        self.assertIn("234💬", formatted)
    
    def test_format_k_suffix(self):
        eng = Engagement(likes=1200, views=15000)
        formatted = eng.format_compact()
        self.assertIn("1.2K♥", formatted)
        self.assertIn("15.0K▶", formatted)


class TestScrapecreatorsIntegration(unittest.TestCase):
    """Tests for ScrapeCreators API integration."""
    
    def test_has_scrapecreators_key_returns_bool(self):
        result = has_scrapecreators_key()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
