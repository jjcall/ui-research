"""Tests for schema module."""

import sys
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import schema


class TestSubPattern(unittest.TestCase):
    """Tests for SubPattern dataclass."""
    
    def test_create_basic(self):
        sp = schema.SubPattern(
            name="Kanban Boards",
            description="Card-based task organization"
        )
        self.assertEqual(sp.name, "Kanban Boards")
        self.assertEqual(sp.description, "Card-based task organization")
        self.assertEqual(sp.base_terms, [])
    
    def test_create_with_terms(self):
        sp = schema.SubPattern(
            name="Kanban Boards",
            description="Card-based task organization",
            base_terms=["kanban", "task board"],
            synonyms=["card view", "column layout"],
            product_queries=["Linear board", "Trello UI"],
            tags=["productivity"]
        )
        self.assertIn("kanban", sp.base_terms)
        self.assertIn("card view", sp.synonyms)
        self.assertIn("Linear board", sp.product_queries)
    
    def test_all_search_terms(self):
        sp = schema.SubPattern(
            name="Kanban",
            description="",
            base_terms=["kanban"],
            synonyms=["task board"],
            product_queries=["Linear board"]
        )
        terms = sp.all_search_terms()
        self.assertIn("kanban", terms)
        self.assertIn("task board", terms)
        self.assertIn("Linear board", terms)
    
    def test_to_dict(self):
        sp = schema.SubPattern(name="Test", description="Desc")
        d = sp.to_dict()
        self.assertEqual(d["name"], "Test")
        self.assertEqual(d["description"], "Desc")
    
    def test_from_dict(self):
        data = {
            "name": "Test",
            "description": "Desc",
            "base_terms": ["a", "b"],
            "synonyms": [],
            "product_queries": [],
            "tags": []
        }
        sp = schema.SubPattern.from_dict(data)
        self.assertEqual(sp.name, "Test")
        self.assertIn("a", sp.base_terms)


class TestDecomposition(unittest.TestCase):
    """Tests for Decomposition dataclass."""
    
    def test_create_empty(self):
        d = schema.Decomposition(concept="planning mode UI")
        self.assertEqual(d.concept, "planning mode UI")
        self.assertEqual(d.sub_patterns, [])
    
    def test_create_with_patterns(self):
        sp = schema.SubPattern(name="Kanban", description="")
        d = schema.Decomposition(
            concept="planning mode UI",
            sub_patterns=[sp]
        )
        self.assertEqual(len(d.sub_patterns), 1)
    
    def test_to_dict(self):
        sp = schema.SubPattern(name="Kanban", description="")
        d = schema.Decomposition(concept="test", sub_patterns=[sp])
        data = d.to_dict()
        self.assertEqual(data["concept"], "test")
        self.assertEqual(len(data["subPatterns"]), 1)
    
    def test_from_dict(self):
        data = {
            "concept": "test",
            "subPatterns": [{"name": "A", "description": "B", "base_terms": [], "synonyms": [], "product_queries": [], "tags": []}]
        }
        d = schema.Decomposition.from_dict(data)
        self.assertEqual(d.concept, "test")
        self.assertEqual(len(d.sub_patterns), 1)


class TestReference(unittest.TestCase):
    """Tests for Reference dataclass."""
    
    def test_create_basic(self):
        ref = schema.Reference(
            url="https://dribbble.com/shot/1",
            title="Test Shot",
            description="A test design",
            source="dribbble",
            category="kanban"
        )
        self.assertEqual(ref.url, "https://dribbble.com/shot/1")
        self.assertEqual(ref.source, "dribbble")
        self.assertEqual(ref.source_label, "Dribbble")
    
    def test_source_label_auto(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="behance",
            category="test"
        )
        self.assertEqual(ref.source_label, "Behance")
    
    def test_source_label_custom(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="v0",
            source_label="v0.dev",
            category="test"
        )
        self.assertEqual(ref.source_label, "v0.dev")
    
    def test_to_dict(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="Desc",
            source="dribbble",
            category="kanban",
            tags=["productivity"]
        )
        d = ref.to_dict()
        self.assertEqual(d["url"], "https://example.com")
        self.assertEqual(d["desc"], "Desc")
        self.assertEqual(d["cat"], "kanban")
        self.assertIn("productivity", d["tags"])
    
    def test_from_dict(self):
        data = {
            "url": "https://example.com",
            "title": "Test",
            "desc": "Description",
            "source": "dribbble",
            "cat": "kanban"
        }
        ref = schema.Reference.from_dict(data)
        self.assertEqual(ref.url, "https://example.com")
        self.assertEqual(ref.description, "Description")
        self.assertEqual(ref.category, "kanban")
    
    def test_with_image_url(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="test",
            image_url="https://cdn.dribbble.com/image.png"
        )
        d = ref.to_dict()
        self.assertEqual(d["img"], "https://cdn.dribbble.com/image.png")
    
    def test_with_image_data(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="test",
            image_data="data:image/png;base64,abc123"
        )
        d = ref.to_dict()
        self.assertEqual(d["img"], "data:image/png;base64,abc123")


class TestCategory(unittest.TestCase):
    """Tests for Category dataclass."""
    
    def test_create(self):
        cat = schema.Category(id="kanban", label="Kanban Boards")
        self.assertEqual(cat.id, "kanban")
        self.assertEqual(cat.label, "Kanban Boards")
        self.assertEqual(cat.count, 0)
    
    def test_to_dict(self):
        cat = schema.Category(id="kanban", label="Kanban Boards", count=5)
        d = cat.to_dict()
        self.assertEqual(d["id"], "kanban")
        self.assertEqual(d["count"], 5)


class TestSource(unittest.TestCase):
    """Tests for Source dataclass."""
    
    def test_create(self):
        src = schema.Source(id="dribbble", label="Dribbble", color="#ea4c89")
        self.assertEqual(src.id, "dribbble")
        self.assertEqual(src.color, "#ea4c89")
    
    def test_to_dict(self):
        src = schema.Source(id="dribbble", label="Dribbble", color="#ea4c89", count=10)
        d = src.to_dict()
        self.assertEqual(d["color"], "#ea4c89")
        self.assertEqual(d["count"], 10)


class TestGallery(unittest.TestCase):
    """Tests for Gallery dataclass."""
    
    def test_create_empty(self):
        gallery = schema.Gallery(concept="planning mode UI")
        self.assertEqual(gallery.concept, "planning mode UI")
        self.assertEqual(len(gallery.categories), 1)  # Auto-added "All"
        self.assertEqual(gallery.categories[0].id, "all")
    
    def test_create_with_refs(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="kanban",
            tags=["productivity", "SaaS"]
        )
        cat = schema.Category(id="kanban", label="Kanban Boards")
        src = schema.Source(id="dribbble", label="Dribbble", color="#ea4c89")
        
        gallery = schema.Gallery(
            concept="planning mode UI",
            categories=[cat],
            sources=[src],
            refs=[ref]
        )
        
        # Auto-adds "All" category and source
        self.assertEqual(gallery.categories[0].id, "all")
        self.assertEqual(gallery.sources[0].id, "all")
        # Tags extracted from refs
        self.assertIn("productivity", gallery.all_tags)
        self.assertIn("SaaS", gallery.all_tags)
    
    def test_update_counts(self):
        ref1 = schema.Reference(url="1", title="1", description="", source="dribbble", category="kanban")
        ref2 = schema.Reference(url="2", title="2", description="", source="dribbble", category="kanban")
        ref3 = schema.Reference(url="3", title="3", description="", source="behance", category="timeline")
        
        cat1 = schema.Category(id="kanban", label="Kanban")
        cat2 = schema.Category(id="timeline", label="Timeline")
        src1 = schema.Source(id="dribbble", label="Dribbble", color="#ea4c89")
        src2 = schema.Source(id="behance", label="Behance", color="#1769ff")
        
        gallery = schema.Gallery(
            concept="test",
            categories=[cat1, cat2],
            sources=[src1, src2],
            refs=[ref1, ref2, ref3]
        )
        gallery.update_counts()
        
        # Check category counts
        all_cat = next(c for c in gallery.categories if c.id == "all")
        kanban_cat = next(c for c in gallery.categories if c.id == "kanban")
        timeline_cat = next(c for c in gallery.categories if c.id == "timeline")
        
        self.assertEqual(all_cat.count, 3)
        self.assertEqual(kanban_cat.count, 2)
        self.assertEqual(timeline_cat.count, 1)
        
        # Check source counts
        dribbble_src = next(s for s in gallery.sources if s.id == "dribbble")
        behance_src = next(s for s in gallery.sources if s.id == "behance")
        
        self.assertEqual(dribbble_src.count, 2)
        self.assertEqual(behance_src.count, 1)
    
    def test_to_json_and_back(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="Desc",
            source="dribbble",
            category="kanban"
        )
        cat = schema.Category(id="kanban", label="Kanban")
        
        gallery = schema.Gallery(
            concept="test",
            categories=[cat],
            refs=[ref],
            tier=2
        )
        
        json_str = gallery.to_json()
        restored = schema.Gallery.from_json(json_str)
        
        self.assertEqual(restored.concept, "test")
        self.assertEqual(restored.tier, 2)
        self.assertEqual(len(restored.refs), 1)
        self.assertEqual(restored.refs[0].title, "Test")


class TestResearchHistory(unittest.TestCase):
    """Tests for ResearchHistory dataclass."""
    
    def test_create(self):
        h = schema.ResearchHistory(
            id="abc123",
            concept="planning mode UI",
            date="2026-04-12T10:30:00Z",
            tier=2,
            ref_count=67,
            gallery_path="galleries/2026-04-12-planning-mode-ui.html",
            sub_patterns=["kanban", "timeline"]
        )
        self.assertEqual(h.id, "abc123")
        self.assertEqual(h.ref_count, 67)
    
    def test_to_dict(self):
        h = schema.ResearchHistory(
            id="abc",
            concept="test",
            date="2026-04-12",
            tier=1,
            ref_count=10,
            gallery_path="test.html"
        )
        d = h.to_dict()
        self.assertEqual(d["id"], "abc")
        self.assertEqual(d["refCount"], 10)


class TestEnvironmentInfo(unittest.TestCase):
    """Tests for EnvironmentInfo dataclass."""
    
    def test_defaults(self):
        env = schema.EnvironmentInfo()
        self.assertFalse(env.playwright_available)
        self.assertEqual(env.detected_tier, 1)
    
    def test_tier_detection(self):
        env = schema.EnvironmentInfo(
            playwright_available=True,
            detected_tier=0
        )
        self.assertTrue(env.playwright_available)
        self.assertEqual(env.detected_tier, 0)
    
    def test_to_dict(self):
        env = schema.EnvironmentInfo(webfetch_available=True, detected_tier=2)
        d = env.to_dict()
        self.assertTrue(d["webfetchAvailable"])
        self.assertEqual(d["detectedTier"], 2)


if __name__ == "__main__":
    unittest.main()
