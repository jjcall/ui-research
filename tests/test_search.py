"""Tests for search module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import search, schema


class TestGetSourceInfo(unittest.TestCase):
    """Tests for get_source_info function."""
    
    def test_dribbble_has_info(self):
        info = search.get_source_info("dribbble")
        self.assertEqual(info["label"], "Dribbble")
        self.assertEqual(info["color"], "#ea4c89")
    
    def test_mobbin_has_info(self):
        info = search.get_source_info("mobbin")
        self.assertEqual(info["label"], "Mobbin")
    
    def test_unknown_returns_empty(self):
        info = search.get_source_info("unknown-source")
        self.assertEqual(info, {})


class TestGetAllSources(unittest.TestCase):
    """Tests for get_all_sources function."""
    
    def test_returns_sources(self):
        sources = search.get_all_sources()
        self.assertTrue(len(sources) > 0)
        self.assertIsInstance(sources[0], schema.Source)
    
    def test_includes_dribbble(self):
        sources = search.get_all_sources()
        dribbble = next((s for s in sources if s.id == "dribbble"), None)
        self.assertIsNotNone(dribbble)
        self.assertEqual(dribbble.label, "Dribbble")


class TestGenerateQuery(unittest.TestCase):
    """Tests for generate_query function."""
    
    def test_dribbble_query(self):
        query = search.generate_query("dribbble", "kanban board")
        self.assertIn("site:dribbble.com", query)
        self.assertIn("kanban board", query)
    
    def test_mobbin_query(self):
        query = search.generate_query("mobbin", "dashboard")
        self.assertIn("site:mobbin.com", query)
        self.assertIn("dashboard", query)
    
    def test_product_query(self):
        query = search.generate_query("product", "settings page")
        self.assertIn("settings page", query)
        self.assertIn("UI", query)


class TestGenerateQueriesForPattern(unittest.TestCase):
    """Tests for generate_queries_for_pattern function."""
    
    def test_generates_queries(self):
        pattern = schema.SubPattern(
            name="Kanban Boards",
            description="",
            base_terms=["kanban", "task board"],
            synonyms=["card view"],
            product_queries=["Linear board"]
        )
        
        queries = search.generate_queries_for_pattern(pattern)
        
        self.assertTrue(len(queries) > 0)
        self.assertIn("query", queries[0])
        self.assertIn("source", queries[0])
        self.assertIn("pattern", queries[0])
    
    def test_includes_product_queries(self):
        pattern = schema.SubPattern(
            name="Test",
            description="",
            base_terms=["test"],
            product_queries=["Linear test"]
        )
        
        queries = search.generate_queries_for_pattern(pattern)
        
        product_queries = [q for q in queries if "Linear" in q["query"]]
        self.assertTrue(len(product_queries) > 0)
    
    def test_respects_source_filter(self):
        pattern = schema.SubPattern(
            name="Test",
            description="",
            base_terms=["test"]
        )
        
        queries = search.generate_queries_for_pattern(
            pattern,
            source_ids=["dribbble"],
            include_products=False
        )
        
        for q in queries:
            self.assertEqual(q["source"], "dribbble")


class TestGenerateQueriesForDecomposition(unittest.TestCase):
    """Tests for generate_queries_for_decomposition function."""
    
    def test_generates_for_all_patterns(self):
        decomp = schema.Decomposition(
            concept="planning mode UI",
            sub_patterns=[
                schema.SubPattern(name="Kanban", description="", base_terms=["kanban"]),
                schema.SubPattern(name="Timeline", description="", base_terms=["timeline"])
            ]
        )
        
        queries = search.generate_queries_for_decomposition(decomp)
        
        # Should have queries for both patterns
        kanban_queries = [q for q in queries if q["pattern"] == "Kanban"]
        timeline_queries = [q for q in queries if q["pattern"] == "Timeline"]
        
        self.assertTrue(len(kanban_queries) > 0)
        self.assertTrue(len(timeline_queries) > 0)
    
    def test_includes_generic_concept_queries(self):
        decomp = schema.Decomposition(
            concept="checkout flow",
            sub_patterns=[
                schema.SubPattern(name="Test", description="", base_terms=["form"])
            ]
        )
        
        queries = search.generate_queries_for_decomposition(decomp)
        
        general_queries = [q for q in queries if q["pattern"] == "general"]
        self.assertTrue(len(general_queries) > 0)
    
    def test_deduplicates(self):
        decomp = schema.Decomposition(
            concept="test",
            sub_patterns=[
                schema.SubPattern(name="A", description="", base_terms=["modal"]),
                schema.SubPattern(name="B", description="", base_terms=["modal"])
            ]
        )
        
        queries = search.generate_queries_for_decomposition(decomp)
        
        # Should not have duplicate queries
        query_strings = [q["query"].lower() for q in queries]
        self.assertEqual(len(query_strings), len(set(query_strings)))


class TestDeduplicateReferences(unittest.TestCase):
    """Tests for deduplicate_references function."""
    
    def test_removes_duplicates(self):
        refs = [
            schema.Reference(url="https://example.com/1", title="A", description="", source="dribbble", category="test"),
            schema.Reference(url="https://example.com/1", title="B", description="", source="dribbble", category="test"),
            schema.Reference(url="https://example.com/2", title="C", description="", source="dribbble", category="test")
        ]
        
        result = search.deduplicate_references(refs)
        
        self.assertEqual(len(result), 2)
    
    def test_merges_tags(self):
        refs = [
            schema.Reference(url="https://example.com/1", title="A", description="", source="dribbble", category="test", tags=["a", "b"]),
            schema.Reference(url="https://example.com/1", title="B", description="", source="dribbble", category="test", tags=["c", "d"])
        ]
        
        result = search.deduplicate_references(refs)
        
        self.assertEqual(len(result), 1)
        self.assertIn("a", result[0].tags)
        self.assertIn("c", result[0].tags)
    
    def test_keeps_longer_description(self):
        refs = [
            schema.Reference(url="https://example.com/1", title="A", description="short", source="dribbble", category="test"),
            schema.Reference(url="https://example.com/1", title="B", description="this is a longer description", source="dribbble", category="test")
        ]
        
        result = search.deduplicate_references(refs)
        
        self.assertEqual(result[0].description, "this is a longer description")


class TestCategorizeUrl(unittest.TestCase):
    """Tests for categorize_url function."""
    
    def test_dribbble(self):
        self.assertEqual(search.categorize_url("https://dribbble.com/shots/123"), "dribbble")
    
    def test_behance(self):
        self.assertEqual(search.categorize_url("https://www.behance.net/gallery/123"), "behance")
    
    def test_figma(self):
        self.assertEqual(search.categorize_url("https://figma.com/community/file/123"), "figma")
    
    def test_mobbin(self):
        self.assertEqual(search.categorize_url("https://mobbin.com/browse/ios/apps/linear"), "mobbin")
    
    def test_v0(self):
        self.assertEqual(search.categorize_url("https://v0.dev/t/abc123"), "v0")
    
    def test_youtube(self):
        self.assertEqual(search.categorize_url("https://youtube.com/watch?v=123"), "youtube")
        self.assertEqual(search.categorize_url("https://youtu.be/123"), "youtube")
    
    def test_reddit(self):
        self.assertEqual(search.categorize_url("https://reddit.com/r/UI_Design/comments/123"), "reddit")
    
    def test_unknown_is_product(self):
        self.assertEqual(search.categorize_url("https://linear.app/features"), "product")


class TestExtractDomain(unittest.TestCase):
    """Tests for extract_domain function."""
    
    def test_basic(self):
        self.assertEqual(search.extract_domain("https://dribbble.com/shots/123"), "dribbble.com")
    
    def test_removes_www(self):
        self.assertEqual(search.extract_domain("https://www.behance.net/gallery"), "behance.net")
    
    def test_handles_paths(self):
        self.assertEqual(search.extract_domain("https://example.com/path/to/page"), "example.com")


class TestParseSearchResult(unittest.TestCase):
    """Tests for parse_search_result function."""
    
    def test_creates_reference(self):
        ref = search.parse_search_result(
            url="https://dribbble.com/shots/123",
            title="Test Shot",
            description="A test design",
            category="kanban",
            tags=["productivity"]
        )
        
        self.assertIsInstance(ref, schema.Reference)
        self.assertEqual(ref.source, "dribbble")
        self.assertEqual(ref.source_label, "Dribbble")
        self.assertEqual(ref.title, "Test Shot")
        self.assertIn("productivity", ref.tags)
    
    def test_v0_has_code(self):
        ref = search.parse_search_result(
            url="https://v0.dev/t/abc123",
            title="Component",
            description="",
            category="test"
        )
        
        self.assertTrue(ref.has_code)
    
    def test_dribbble_no_code(self):
        ref = search.parse_search_result(
            url="https://dribbble.com/shots/123",
            title="Shot",
            description="",
            category="test"
        )
        
        self.assertFalse(ref.has_code)


if __name__ == "__main__":
    unittest.main()
