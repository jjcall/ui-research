"""Tests for render module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import render, schema


class TestRenderGallery(unittest.TestCase):
    """Tests for render_gallery function."""
    
    def test_renders_basic_gallery(self):
        gallery = schema.Gallery(
            concept="planning mode UI",
            categories=[schema.Category(id="kanban", label="Kanban Boards")],
            refs=[schema.Reference(
                url="https://dribbble.com/shots/123",
                title="Linear Project Board",
                description="Clean kanban with drag handles",
                source="dribbble",
                category="kanban",
            )],
        )
        
        html = render.render_gallery(gallery)
        
        self.assertIn("planning mode UI", html)
        self.assertIn("Linear Project Board", html)
        self.assertIn("Kanban Boards", html)
    
    def test_includes_script_with_data(self):
        gallery = schema.Gallery(
            concept="test",
            refs=[schema.Reference(
                url="https://example.com",
                title="Test",
                description="",
                source="dribbble",
                category="test"
            )]
        )
        
        html = render.render_gallery(gallery)
        
        self.assertIn("const data =", html)
        self.assertIn('"concept": "test"', html)
    
    def test_includes_styling(self):
        gallery = schema.Gallery(concept="test")
        html = render.render_gallery(gallery)
        
        self.assertIn("<style>", html)
        self.assertIn(".sidebar", html)
        self.assertIn(".ref-item", html)


class TestEscapeHtml(unittest.TestCase):
    """Tests for escape_html function."""
    
    def test_escapes_angle_brackets(self):
        self.assertEqual(render.escape_html("<script>"), "&lt;script&gt;")
    
    def test_escapes_ampersand(self):
        self.assertEqual(render.escape_html("A & B"), "A &amp; B")
    
    def test_escapes_quotes(self):
        self.assertEqual(render.escape_html('"test"'), "&quot;test&quot;")
        self.assertEqual(render.escape_html("'test'"), "&#39;test&#39;")


class TestGenerateStats(unittest.TestCase):
    """Tests for generate_stats function."""
    
    def test_includes_total(self):
        gallery = schema.Gallery(
            concept="test",
            refs=[
                schema.Reference(url="1", title="1", description="", source="dribbble", category="a"),
                schema.Reference(url="2", title="2", description="", source="dribbble", category="a")
            ]
        )
        
        stats = render.generate_stats(gallery)
        
        self.assertIn("Total: 2 references", stats)
    
    def test_includes_source_breakdown(self):
        gallery = schema.Gallery(
            concept="test",
            refs=[
                schema.Reference(url="1", title="1", description="", source="dribbble", category="a"),
                schema.Reference(url="2", title="2", description="", source="behance", category="a")
            ]
        )
        
        stats = render.generate_stats(gallery)
        
        self.assertIn("Sources:", stats)
        self.assertIn("Dribbble: 1", stats)
        self.assertIn("Behance: 1", stats)


class TestRenderReferenceCard(unittest.TestCase):
    """Tests for render_reference_card function."""
    
    def test_basic_card(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test Title",
            description="Test description",
            source="dribbble",
            source_label="Dribbble",
            category="test"
        )
        
        html = render.render_reference_card(ref)
        
        self.assertIn("Test Title", html)
        self.assertIn("Test description", html)
        self.assertIn("Dribbble", html)
        self.assertIn("https://example.com", html)
    
    def test_with_primary_tag(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="test",
            primary_tag="Must Read"
        )
        
        html = render.render_reference_card(ref)
        
        self.assertIn("Must Read", html)
        self.assertIn("ref-tag", html)
    
    def test_with_image(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="test",
            image_url="https://example.com/image.jpg"
        )
        
        html = render.render_reference_card(ref, show_image=True)
        
        self.assertIn("ref-image", html)
        self.assertIn("https://example.com/image.jpg", html)
    
    def test_without_image_flag(self):
        ref = schema.Reference(
            url="https://example.com",
            title="Test",
            description="",
            source="dribbble",
            category="test",
            image_url="https://example.com/image.jpg"
        )
        
        html = render.render_reference_card(ref, show_image=False)
        
        self.assertNotIn("ref-image", html)


class TestGetSourceColor(unittest.TestCase):
    """Tests for get_source_color function."""
    
    def test_dribbble(self):
        self.assertEqual(render.get_source_color("dribbble"), "#ea4c89")
    
    def test_behance(self):
        self.assertEqual(render.get_source_color("behance"), "#1769ff")
    
    def test_unknown(self):
        self.assertEqual(render.get_source_color("unknown"), "#666666")


class TestRenderSidebar(unittest.TestCase):
    """Tests for render_sidebar function."""
    
    def test_renders_categories(self):
        gallery = schema.Gallery(
            concept="test",
            categories=[
                schema.Category(id="kanban", label="Kanban", count=5),
                schema.Category(id="timeline", label="Timeline", count=3)
            ]
        )
        
        html = render.render_sidebar(gallery)
        
        self.assertIn("Kanban", html)
        self.assertIn("Timeline", html)
        self.assertIn("5", html)
        self.assertIn("3", html)


class TestRenderSourceChips(unittest.TestCase):
    """Tests for render_source_chips function."""
    
    def test_renders_sources(self):
        gallery = schema.Gallery(
            concept="test",
            sources=[
                schema.Source(id="dribbble", label="Dribbble", color="#ea4c89", count=10),
                schema.Source(id="behance", label="Behance", color="#1769ff", count=5)
            ]
        )
        
        html = render.render_source_chips(gallery)
        
        self.assertIn("Dribbble", html)
        self.assertIn("Behance", html)
        self.assertIn("#ea4c89", html)


class TestRenderTagChips(unittest.TestCase):
    """Tests for render_tag_chips function."""
    
    def test_renders_tags(self):
        tags = ["productivity", "SaaS", "dark-mode"]
        
        html = render.render_tag_chips(tags)
        
        self.assertIn("productivity", html)
        self.assertIn("SaaS", html)
        self.assertIn("dark-mode", html)
    
    def test_limits_to_15(self):
        tags = [f"xtag-{i:02d}" for i in range(20)]
        
        html = render.render_tag_chips(tags)
        
        # Should have first 15 (xtag-00 through xtag-14) but not later ones
        self.assertIn("xtag-00", html)
        self.assertIn("xtag-14", html)
        self.assertNotIn("xtag-15", html)
        self.assertNotIn("xtag-19", html)


class TestGetDefaultOutputPath(unittest.TestCase):
    """Tests for get_default_output_path function."""
    
    def test_creates_safe_filename(self):
        path = render.get_default_output_path("Planning Mode UI")
        
        self.assertTrue(str(path).endswith(".html"))
        self.assertIn("planning-mode-ui", str(path).lower())
    
    def test_sanitizes_special_chars(self):
        path = render.get_default_output_path("Test/With\\Special:Chars")
        
        # Should not contain special characters
        filename = path.name
        self.assertNotIn("/", filename)
        self.assertNotIn("\\", filename)
        self.assertNotIn(":", filename)
    
    def test_truncates_long_names(self):
        long_name = "A" * 100
        path = render.get_default_output_path(long_name)
        
        # Filename should be reasonable length
        self.assertLess(len(path.name), 70)


if __name__ == "__main__":
    unittest.main()
