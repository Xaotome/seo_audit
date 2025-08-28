import unittest
from seo_audit.utils import (
    normalize_url, is_same_domain, is_internal_link,
    extract_domain, clean_text, count_words, deduplicate_urls,
    filter_urls_by_domain, is_valid_url
)


class TestUtils(unittest.TestCase):
    
    def test_normalize_url(self):
        """Test URL normalization"""
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        self.assertEqual(normalize_url("http://example.com"), "http://example.com")
        self.assertEqual(normalize_url("https://example.com#fragment"), "https://example.com")
        self.assertEqual(normalize_url(""), "")
    
    def test_is_same_domain(self):
        """Test domain comparison"""
        self.assertTrue(is_same_domain("https://example.com", "https://example.com/page"))
        self.assertTrue(is_same_domain("http://example.com", "https://example.com"))
        self.assertFalse(is_same_domain("https://example.com", "https://other.com"))
        self.assertFalse(is_same_domain("", "https://example.com"))
    
    def test_is_internal_link(self):
        """Test internal link detection"""
        base_url = "https://example.com"
        self.assertTrue(is_internal_link("/page", base_url))
        self.assertTrue(is_internal_link("https://example.com/page", base_url))
        self.assertFalse(is_internal_link("https://other.com/page", base_url))
        self.assertFalse(is_internal_link("mailto:test@example.com", base_url))
    
    def test_extract_domain(self):
        """Test domain extraction"""
        self.assertEqual(extract_domain("https://example.com/page"), "example.com")
        self.assertEqual(extract_domain("http://sub.example.com"), "sub.example.com")
        self.assertEqual(extract_domain("invalid-url"), "")
    
    def test_clean_text(self):
        """Test text cleaning"""
        self.assertEqual(clean_text("  Hello   world  "), "Hello world")
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text("Line 1\n\nLine 2"), "Line 1 Line 2")
    
    def test_count_words(self):
        """Test word counting"""
        self.assertEqual(count_words("Hello world"), 2)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("a"), 0)  # Too short
        self.assertEqual(count_words("Hello, world! How are you?"), 4)
    
    def test_deduplicate_urls(self):
        """Test URL deduplication"""
        urls = [
            "https://example.com",
            "https://example.com/",
            "https://example.com#fragment",
            "https://example.com/page"
        ]
        result = deduplicate_urls(urls)
        self.assertEqual(len(result), 2)  # Should remove duplicates
    
    def test_filter_urls_by_domain(self):
        """Test URL filtering by domain"""
        urls = [
            "https://example.com/page1",
            "https://other.com/page2",
            "https://example.com/page3"
        ]
        result = filter_urls_by_domain(urls, "https://example.com")
        self.assertEqual(len(result), 2)
        self.assertIn("https://example.com/page1", result)
        self.assertIn("https://example.com/page3", result)
    
    def test_is_valid_url(self):
        """Test URL validation"""
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://example.com"))
        self.assertFalse(is_valid_url("example.com"))
        self.assertFalse(is_valid_url(""))
        self.assertFalse(is_valid_url("invalid-url"))


if __name__ == '__main__':
    unittest.main()