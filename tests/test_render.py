"""Tests for render module."""

import sys
import unittest
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import render, schema


class TestGetGalleryTemplate(unittest.TestCase):
    """Tests for get_gallery_template function."""
    
    def test_loads_template_file(self):
        template = render.get_gallery_template()
        
        self.assertIn("<!DOCTYPE html>", template)
        self.assertIn("GALLERY_DATA", template)
        self.assertIn("{{CONCEPT}}", template)
    
    def test_template_has_data_marker(self):
        template = render.get_gallery_template()
        
        self.assertIn("/*GALLERY_DATA*/", template)
        self.assertIn("/*END_GALLERY_DATA*/", template)
    
    def test_template_is_valid_html_structure(self):
        template = render.get_gallery_template()
        
        self.assertIn("<html", template)
        self.assertIn("</html>", template)
        self.assertIn("<head>", template)
        self.assertIn("<body>", template)


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
    
    def test_injects_data_at_marker(self):
        gallery = schema.Gallery(
            concept="test concept",
            refs=[schema.Reference(
                url="https://example.com",
                title="Test Title",
                description="Test desc",
                source="dribbble",
                category="test"
            )]
        )
        
        html = render.render_gallery(gallery)
        
        # Should have injected JSON data between markers
        match = re.search(r'/\*GALLERY_DATA\*/(.*?)/\*END_GALLERY_DATA\*/', html, re.DOTALL)
        self.assertIsNotNone(match)
        
        # Parse the injected data
        data = json.loads(match.group(1))
        self.assertEqual(data["concept"], "test concept")
        self.assertEqual(len(data["refs"]), 1)
        self.assertEqual(data["refs"][0]["title"], "Test Title")
    
    def test_replaces_concept_placeholder(self):
        gallery = schema.Gallery(concept="My Research Topic")
        html = render.render_gallery(gallery)
        
        # Title should be replaced
        self.assertIn("<title>My Research Topic", html)
        # Original placeholder should not appear
        self.assertNotIn("{{CONCEPT}}", html)
    
    def test_escapes_concept_in_title(self):
        gallery = schema.Gallery(concept="Test <script> & Stuff")
        html = render.render_gallery(gallery)
        
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp;", html)
    
    def test_includes_all_gallery_data(self):
        gallery = schema.Gallery(
            concept="comprehensive test",
            categories=[
                schema.Category(id="all", label="All", count=2),
                schema.Category(id="cat1", label="Category 1", count=1)
            ],
            sources=[
                schema.Source(id="all", label="All", color="#666666", count=1),
                schema.Source(id="dribbble", label="Dribbble", color="#ea4c89", count=1)
            ],
            refs=[
                schema.Reference(
                    url="https://dribbble.com/shots/1",
                    title="Ref 1",
                    description="Description",
                    source="dribbble",
                    category="cat1",
                    tags=["tag1", "tag2"],
                    url_quality=0.9
                )
            ],
            all_tags=["tag1", "tag2"],
            tier=2
        )
        
        html = render.render_gallery(gallery)
        match = re.search(r'/\*GALLERY_DATA\*/(.*?)/\*END_GALLERY_DATA\*/', html, re.DOTALL)
        data = json.loads(match.group(1))
        
        self.assertEqual(data["concept"], "comprehensive test")
        self.assertEqual(len(data["categories"]), 2)
        self.assertEqual(len(data["sources"]), 2)
        # First source is "All"
        self.assertEqual(data["sources"][0]["id"], "all")
        # Second source is Dribbble with correct color
        self.assertEqual(data["sources"][1]["color"], "#ea4c89")
        self.assertEqual(data["allTags"], ["tag1", "tag2"])
        self.assertEqual(data["tier"], 2)
    
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
    
    def test_handles_empty_string(self):
        self.assertEqual(render.escape_html(""), "")
    
    def test_handles_no_special_chars(self):
        self.assertEqual(render.escape_html("normal text"), "normal text")


class TestSaveGallery(unittest.TestCase):
    """Tests for save_gallery function."""
    
    def test_creates_output_directory(self):
        import tempfile
        import shutil
        
        tmpdir = tempfile.mkdtemp()
        try:
            output_path = Path(tmpdir) / "nested" / "dir" / "gallery.html"
            
            gallery = schema.Gallery(concept="test")
            result = render.save_gallery(gallery, output_path)
            
            self.assertTrue(output_path.exists())
            self.assertEqual(result, output_path)
            
            content = output_path.read_text()
            self.assertIn("test", content)
        finally:
            shutil.rmtree(tmpdir)
    
    def test_writes_valid_html(self):
        import tempfile
        import shutil
        
        tmpdir = tempfile.mkdtemp()
        try:
            output_path = Path(tmpdir) / "gallery.html"
            
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
            render.save_gallery(gallery, output_path)
            
            content = output_path.read_text()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("</html>", content)
        finally:
            shutil.rmtree(tmpdir)


class TestGetDefaultOutputPath(unittest.TestCase):
    """Tests for get_default_output_path function."""
    
    def test_creates_safe_filename(self):
        path = render.get_default_output_path("Planning Mode UI")
        
        self.assertTrue(str(path).endswith(".html"))
        self.assertIn("planning-mode-ui", str(path).lower())
    
    def test_uses_design_research_output_directory(self):
        path = render.get_default_output_path("Test Concept")
        
        self.assertIn(".design-research-output", str(path))
    
    def test_sanitizes_special_chars(self):
        path = render.get_default_output_path("Test/With\\Special:Chars")
        
        filename = path.name
        self.assertNotIn("/", filename)
        self.assertNotIn("\\", filename)
        self.assertNotIn(":", filename)
    
    def test_truncates_long_names(self):
        long_name = "A" * 100
        path = render.get_default_output_path(long_name)
        
        self.assertLess(len(path.name), 70)
    
    def test_includes_date_in_filename(self):
        from datetime import datetime
        
        path = render.get_default_output_path("test")
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.assertIn(today, path.name)


if __name__ == "__main__":
    unittest.main()
