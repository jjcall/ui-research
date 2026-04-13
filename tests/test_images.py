"""Tests for images module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib import images


class TestExtractOgImage(unittest.TestCase):
    """Tests for extract_og_image function."""
    
    def test_extracts_og_image(self):
        html = '''
        <html>
        <head>
            <meta property="og:image" content="https://example.com/image.jpg">
        </head>
        </html>
        '''
        result = images.extract_og_image(html)
        self.assertEqual(result, "https://example.com/image.jpg")
    
    def test_extracts_og_image_reverse_order(self):
        html = '''
        <html>
        <head>
            <meta content="https://example.com/image.jpg" property="og:image">
        </head>
        </html>
        '''
        result = images.extract_og_image(html)
        self.assertEqual(result, "https://example.com/image.jpg")
    
    def test_extracts_twitter_image(self):
        html = '''
        <html>
        <head>
            <meta name="twitter:image" content="https://example.com/twitter.jpg">
        </head>
        </html>
        '''
        result = images.extract_og_image(html)
        self.assertEqual(result, "https://example.com/twitter.jpg")
    
    def test_prefers_og_over_twitter(self):
        html = '''
        <html>
        <head>
            <meta property="og:image" content="https://example.com/og.jpg">
            <meta name="twitter:image" content="https://example.com/twitter.jpg">
        </head>
        </html>
        '''
        result = images.extract_og_image(html)
        self.assertEqual(result, "https://example.com/og.jpg")
    
    def test_returns_none_when_missing(self):
        html = '<html><head></head></html>'
        result = images.extract_og_image(html)
        self.assertIsNone(result)


class TestExtractImagesFromHtml(unittest.TestCase):
    """Tests for extract_images_from_html function."""
    
    def test_extracts_img_tags(self):
        html = '''
        <html>
        <body>
            <img src="https://example.com/image1.jpg">
            <img src="https://example.com/image2.png">
        </body>
        </html>
        '''
        result = images.extract_images_from_html(html)
        self.assertEqual(len(result), 2)
        self.assertIn("https://example.com/image1.jpg", result)
    
    def test_handles_relative_urls(self):
        html = '<img src="/images/photo.jpg">'
        result = images.extract_images_from_html(html, "https://example.com")
        self.assertEqual(len(result), 1)
        self.assertIn("example.com", result[0])
    
    def test_extracts_data_src(self):
        html = '<img data-src="https://example.com/lazy.jpg">'
        result = images.extract_images_from_html(html)
        self.assertIn("https://example.com/lazy.jpg", result)
    
    def test_excludes_data_urls(self):
        html = '<img src="data:image/png;base64,abc123">'
        result = images.extract_images_from_html(html)
        self.assertEqual(len(result), 0)


class TestFilterImagesByCdn(unittest.TestCase):
    """Tests for filter_images_by_cdn function."""
    
    def test_filters_dribbble_cdn(self):
        image_list = [
            "https://cdn.dribbble.com/userupload/abc.jpg",
            "https://example.com/other.jpg"
        ]
        result = images.filter_images_by_cdn(image_list, "dribbble")
        self.assertEqual(len(result), 1)
        self.assertIn("dribbble", result[0])
    
    def test_returns_all_when_no_patterns(self):
        image_list = ["https://example.com/a.jpg", "https://example.com/b.jpg"]
        result = images.filter_images_by_cdn(image_list, "unknown")
        self.assertEqual(len(result), 2)


class TestIsValidImageUrl(unittest.TestCase):
    """Tests for is_valid_image_url function."""
    
    def test_valid_jpg(self):
        self.assertTrue(images.is_valid_image_url("https://example.com/image.jpg"))
    
    def test_valid_png(self):
        self.assertTrue(images.is_valid_image_url("https://example.com/image.png"))
    
    def test_valid_webp(self):
        self.assertTrue(images.is_valid_image_url("https://example.com/image.webp"))
    
    def test_cdn_without_extension(self):
        self.assertTrue(images.is_valid_image_url("https://cdn.dribbble.com/abc123"))
    
    def test_invalid_empty(self):
        self.assertFalse(images.is_valid_image_url(""))
        self.assertFalse(images.is_valid_image_url(None))
    
    def test_invalid_non_http(self):
        self.assertFalse(images.is_valid_image_url("file:///local/image.jpg"))


class TestNormalizeImageUrl(unittest.TestCase):
    """Tests for normalize_image_url function."""
    
    def test_adds_https_to_protocol_relative(self):
        result = images.normalize_image_url("//example.com/image.jpg")
        self.assertEqual(result, "https://example.com/image.jpg")
    
    def test_preserves_https(self):
        url = "https://example.com/image.jpg"
        result = images.normalize_image_url(url)
        self.assertEqual(result, url)
    
    def test_handles_empty(self):
        self.assertEqual(images.normalize_image_url(""), "")
        self.assertIsNone(images.normalize_image_url(None))


class TestGetContentTypeFromUrl(unittest.TestCase):
    """Tests for get_content_type_from_url function."""
    
    def test_png(self):
        self.assertEqual(images.get_content_type_from_url("image.png"), "image/png")
    
    def test_gif(self):
        self.assertEqual(images.get_content_type_from_url("image.gif"), "image/gif")
    
    def test_webp(self):
        self.assertEqual(images.get_content_type_from_url("image.webp"), "image/webp")
    
    def test_svg(self):
        self.assertEqual(images.get_content_type_from_url("image.svg"), "image/svg+xml")
    
    def test_default_jpeg(self):
        self.assertEqual(images.get_content_type_from_url("image.unknown"), "image/jpeg")


class TestEncodeImageToBase64(unittest.TestCase):
    """Tests for encode_image_to_base64 function."""
    
    def test_encodes_data(self):
        data = b"test image data"
        result = images.encode_image_to_base64(data)
        self.assertTrue(result.startswith("data:image/png;base64,"))
    
    def test_custom_content_type(self):
        data = b"test"
        result = images.encode_image_to_base64(data, "image/jpeg")
        self.assertTrue(result.startswith("data:image/jpeg;base64,"))


class TestExtractRedditImages(unittest.TestCase):
    """Tests for extract_reddit_images function."""
    
    def test_extracts_imgur(self):
        html = 'Check out https://imgur.com/abc123 and https://i.imgur.com/xyz789.jpg'
        result = images.extract_reddit_images(html)
        self.assertEqual(len(result), 2)
    
    def test_extracts_redd_it(self):
        html = 'Posted at https://i.redd.it/abc123.png'
        result = images.extract_reddit_images(html)
        self.assertEqual(len(result), 1)
        self.assertIn("i.redd.it", result[0])
    
    def test_adds_extension_to_imgur(self):
        html = 'https://imgur.com/abc123'
        result = images.extract_reddit_images(html)
        self.assertTrue(result[0].endswith(".jpg"))


class TestFindBestImage(unittest.TestCase):
    """Tests for find_best_image function."""
    
    def test_prefers_og_image(self):
        html = '''
        <html>
        <head>
            <meta property="og:image" content="https://example.com/og.jpg">
        </head>
        <body>
            <img src="https://example.com/other.jpg">
        </body>
        </html>
        '''
        result = images.find_best_image(html, "https://example.com", "product")
        self.assertEqual(result, "https://example.com/og.jpg")
    
    def test_falls_back_to_first_image(self):
        html = '<html><body><img src="https://example.com/first.jpg"></body></html>'
        result = images.find_best_image(html, "https://example.com", "product")
        self.assertEqual(result, "https://example.com/first.jpg")
    
    def test_returns_none_when_no_images(self):
        html = '<html><body><p>No images here</p></body></html>'
        result = images.find_best_image(html, "https://example.com", "product")
        self.assertIsNone(result)


class TestExtractSrcsetImages(unittest.TestCase):
    """Tests for extract_srcset_images function."""
    
    def test_extracts_srcset_with_widths(self):
        html = '<img srcset="small.jpg 400w, medium.jpg 800w, large.jpg 1200w">'
        result = images.extract_srcset_images(html)
        self.assertEqual(len(result), 3)
        # Should be sorted by width descending
        self.assertEqual(result[0]["width"], 1200)
        self.assertIn("large.jpg", result[0]["url"])
    
    def test_handles_srcset_without_widths(self):
        html = '<img srcset="image.jpg 1x, image@2x.jpg 2x">'
        result = images.extract_srcset_images(html)
        self.assertEqual(len(result), 2)
    
    def test_resolves_relative_urls(self):
        html = '<img srcset="/images/photo.jpg 800w">'
        result = images.extract_srcset_images(html, "https://example.com")
        self.assertIn("example.com", result[0]["url"])


class TestScoreImageUrl(unittest.TestCase):
    """Tests for score_image_url function."""
    
    def test_cdn_gets_boost(self):
        url = "https://cdn.dribbble.com/userupload/image.jpg"
        score = images.score_image_url(url, "dribbble")
        self.assertGreater(score, 0.5)
    
    def test_thumbnail_gets_penalty(self):
        url = "https://example.com/image_thumb.jpg"
        score = images.score_image_url(url)
        self.assertLess(score, 0.5)
    
    def test_large_indicator_gets_boost(self):
        url = "https://example.com/image_large.jpg"
        score = images.score_image_url(url)
        self.assertGreater(score, 0.5)
    
    def test_icon_gets_penalty(self):
        url = "https://example.com/icons/logo.png"
        score = images.score_image_url(url)
        self.assertLess(score, 0.5)


class TestIsLikelyIcon(unittest.TestCase):
    """Tests for _is_likely_icon function."""
    
    def test_avatar_is_icon(self):
        self.assertTrue(images._is_likely_icon("/avatars/user.png"))
    
    def test_icon_path_is_icon(self):
        self.assertTrue(images._is_likely_icon("/icons/menu.svg"))
    
    def test_favicon_is_icon(self):
        self.assertTrue(images._is_likely_icon("/favicon.ico"))
    
    def test_small_dimension_is_icon(self):
        # Test underscored small dimension
        self.assertTrue(images._is_likely_icon("/image_thumb.png"))
    
    def test_regular_image_not_icon(self):
        self.assertFalse(images._is_likely_icon("/images/hero-banner.jpg"))


class TestConstructYoutubeThumbnail(unittest.TestCase):
    """Tests for construct_youtube_thumbnail function."""
    
    def test_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = images.construct_youtube_thumbnail(url)
        self.assertIn("dQw4w9WgXcQ", result)
        self.assertIn("i.ytimg.com", result)
    
    def test_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = images.construct_youtube_thumbnail(url)
        self.assertIn("dQw4w9WgXcQ", result)
    
    def test_invalid_url_returns_none(self):
        url = "https://www.youtube.com/channel/UCxyz"
        result = images.construct_youtube_thumbnail(url)
        self.assertIsNone(result)


class TestGetSourceColor(unittest.TestCase):
    """Tests for get_source_color function."""
    
    def test_dribbble_color(self):
        color = images.get_source_color("dribbble")
        self.assertEqual(color, "#ea4c89")
    
    def test_unknown_source_default(self):
        color = images.get_source_color("unknown_source")
        self.assertEqual(color, "#666666")


class TestGetFallbackImageForSource(unittest.TestCase):
    """Tests for get_fallback_image_for_source function."""
    
    def test_youtube_fallback(self):
        url = "https://www.youtube.com/watch?v=abc123xyz00"
        result = images.get_fallback_image_for_source(url, "youtube")
        self.assertIn("i.ytimg.com", result)
    
    def test_unknown_source_returns_none(self):
        url = "https://example.com/page"
        result = images.get_fallback_image_for_source(url, "product")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
