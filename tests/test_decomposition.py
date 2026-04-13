"""Tests for decompose module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import decompose


class TestExpandSynonyms(unittest.TestCase):
    """Tests for expand_synonyms function."""
    
    def test_known_term_expands(self):
        result = decompose.expand_synonyms("kanban")
        self.assertIn("kanban", result)
        self.assertIn("task board", result)
        self.assertIn("column view", result)
    
    def test_known_term_with_spaces(self):
        result = decompose.expand_synonyms("kanban board")
        # Should match "kanban" after normalization
        self.assertIn("kanban board", result)
    
    def test_modal_expands(self):
        result = decompose.expand_synonyms("modal")
        self.assertIn("modal", result)
        self.assertIn("dialog", result)
        self.assertIn("popup", result)
    
    def test_tabs_expands(self):
        result = decompose.expand_synonyms("tabs")
        self.assertIn("tabs", result)
        self.assertIn("tab navigation", result)
    
    def test_unknown_term_returns_original(self):
        result = decompose.expand_synonyms("xyzzy-unknown-pattern")
        self.assertEqual(result, ["xyzzy-unknown-pattern"])
    
    def test_case_insensitive(self):
        result1 = decompose.expand_synonyms("Kanban")
        result2 = decompose.expand_synonyms("KANBAN")
        result3 = decompose.expand_synonyms("kanban")
        # All should have synonyms
        self.assertTrue(len(result1) > 1)
        self.assertTrue(len(result2) > 1)
        self.assertTrue(len(result3) > 1)
    
    def test_hyphen_underscore_equivalence(self):
        result1 = decompose.expand_synonyms("command-palette")
        result2 = decompose.expand_synonyms("command_palette")
        # Both should expand
        self.assertTrue(len(result1) > 1)
        self.assertTrue(len(result2) > 1)


class TestGetRelatedPatterns(unittest.TestCase):
    """Tests for get_related_patterns function."""
    
    def test_kanban_has_related(self):
        result = decompose.get_related_patterns("kanban")
        self.assertIn("drag-and-drop", result)
    
    def test_modal_has_related(self):
        result = decompose.get_related_patterns("modal")
        self.assertIn("dialog", result)
    
    def test_unknown_returns_empty(self):
        result = decompose.get_related_patterns("unknown-thing")
        self.assertEqual(result, [])


class TestGetProductQueries(unittest.TestCase):
    """Tests for get_product_queries function."""
    
    def test_kanban_includes_linear(self):
        result = decompose.get_product_queries("kanban")
        # Should have queries like "Linear kanban"
        self.assertTrue(any("Linear" in q for q in result))
    
    def test_kanban_includes_trello(self):
        result = decompose.get_product_queries("kanban")
        self.assertTrue(any("Trello" in q for q in result))
    
    def test_modal_includes_products(self):
        result = decompose.get_product_queries("modal")
        self.assertTrue(len(result) > 0)
    
    def test_unknown_returns_empty(self):
        result = decompose.get_product_queries("unknown-thing")
        self.assertEqual(result, [])
    
    def test_query_format(self):
        result = decompose.get_product_queries("dashboard")
        # Queries should be "Product pattern"
        for query in result:
            self.assertIn(" ", query)  # Has space
            self.assertIn("dashboard", query.lower())


class TestGetProductsByCategory(unittest.TestCase):
    """Tests for get_products_by_category function."""
    
    def test_productivity_has_products(self):
        result = decompose.get_products_by_category("productivity")
        self.assertIn("Linear", result)
        self.assertIn("Notion", result)
    
    def test_design_has_figma(self):
        result = decompose.get_products_by_category("design")
        self.assertIn("Figma", result)
    
    def test_unknown_category_empty(self):
        result = decompose.get_products_by_category("unknown")
        self.assertEqual(result, [])


class TestCreateSubPattern(unittest.TestCase):
    """Tests for create_sub_pattern function."""
    
    def test_creates_with_expansion(self):
        sp = decompose.create_sub_pattern(
            name="Kanban Boards",
            description="Card-based task organization",
            base_terms=["kanban"],
            tags=["productivity"]
        )
        
        self.assertEqual(sp.name, "Kanban Boards")
        self.assertEqual(sp.description, "Card-based task organization")
        self.assertIn("kanban", sp.base_terms)
        self.assertIn("productivity", sp.tags)
        
        # Should have synonyms
        self.assertTrue(len(sp.synonyms) > 0)
        
        # Should have product queries
        self.assertTrue(len(sp.product_queries) > 0)
    
    def test_limits_product_queries(self):
        sp = decompose.create_sub_pattern(
            name="Test",
            description="",
            base_terms=["dashboard"]
        )
        # Should be limited to 10
        self.assertLessEqual(len(sp.product_queries), 10)
    
    def test_unknown_term_no_expansion(self):
        sp = decompose.create_sub_pattern(
            name="Unknown Thing",
            description="",
            base_terms=["xyzzy-unknown"]
        )
        self.assertEqual(sp.synonyms, [])
        self.assertEqual(sp.product_queries, [])


class TestDecomposeConcept(unittest.TestCase):
    """Tests for decompose_concept function."""
    
    def test_basic_decomposition(self):
        sub_patterns_data = [
            {
                "name": "Kanban Boards",
                "description": "Card-based task organization",
                "base_terms": ["kanban", "task board"],
                "tags": ["productivity"]
            },
            {
                "name": "Timeline Views",
                "description": "Chronological task display",
                "base_terms": ["timeline", "gantt"],
                "tags": ["productivity"]
            }
        ]
        
        result = decompose.decompose_concept("planning mode UI", sub_patterns_data)
        
        self.assertEqual(result.concept, "planning mode UI")
        self.assertEqual(len(result.sub_patterns), 2)
        
        # First pattern
        sp1 = result.sub_patterns[0]
        self.assertEqual(sp1.name, "Kanban Boards")
        self.assertTrue(len(sp1.synonyms) > 0)
        self.assertTrue(len(sp1.product_queries) > 0)
    
    def test_to_dict(self):
        sub_patterns_data = [
            {"name": "Test", "description": "Desc", "base_terms": ["modal"]}
        ]
        
        result = decompose.decompose_concept("test concept", sub_patterns_data)
        d = result.to_dict()
        
        self.assertEqual(d["concept"], "test concept")
        self.assertEqual(len(d["subPatterns"]), 1)


class TestSuggestLateralPatterns(unittest.TestCase):
    """Tests for suggest_lateral_patterns function."""
    
    def test_suggests_related(self):
        direct = ["kanban"]
        suggestions = decompose.suggest_lateral_patterns("planning UI", direct)
        
        # Should suggest related patterns like drag-and-drop
        self.assertIn("drag-and-drop", suggestions)
    
    def test_excludes_direct_patterns(self):
        direct = ["kanban", "drag-and-drop"]
        suggestions = decompose.suggest_lateral_patterns("planning UI", direct)
        
        # Should not include patterns already in direct
        self.assertNotIn("kanban", suggestions)
        self.assertNotIn("drag-and-drop", suggestions)
    
    def test_multiple_patterns(self):
        direct = ["modal", "form"]
        suggestions = decompose.suggest_lateral_patterns("settings UI", direct)
        
        # Should have suggestions from both patterns' related
        self.assertTrue(len(suggestions) > 0)


if __name__ == "__main__":
    unittest.main()
