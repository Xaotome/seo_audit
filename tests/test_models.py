import unittest
from datetime import datetime
from seo_audit.models import PageResult, AuditConfig, AuditSummary


class TestModels(unittest.TestCase):
    
    def test_page_result_initialization(self):
        """Test PageResult initialization"""
        result = PageResult(url="https://example.com")
        self.assertEqual(result.url, "https://example.com")
        self.assertIsNone(result.status)
        self.assertEqual(result.issues, [])
        self.assertIsInstance(result.crawled_at, datetime)
    
    def test_page_result_with_data(self):
        """Test PageResult with data"""
        result = PageResult(
            url="https://example.com",
            status=200,
            title="Test Page",
            title_len=9,
            issues=["Missing meta description"]
        )
        
        self.assertEqual(result.status, 200)
        self.assertEqual(result.title, "Test Page")
        self.assertEqual(result.title_len, 9)
        self.assertEqual(len(result.issues), 1)
    
    def test_audit_config_defaults(self):
        """Test AuditConfig default values"""
        config = AuditConfig(domain="https://example.com")
        self.assertEqual(config.domain, "https://example.com")
        self.assertEqual(config.max_pages, 100)
        self.assertEqual(config.rate_limit, 1.0)
        self.assertEqual(config.timeout, 15)
        self.assertTrue(config.follow_redirects)
        self.assertFalse(config.check_js_rendering)
    
    def test_audit_config_custom_values(self):
        """Test AuditConfig with custom values"""
        config = AuditConfig(
            domain="https://example.com",
            max_pages=500,
            rate_limit=2.0,
            timeout=30,
            follow_redirects=False
        )
        
        self.assertEqual(config.max_pages, 500)
        self.assertEqual(config.rate_limit, 2.0)
        self.assertEqual(config.timeout, 30)
        self.assertFalse(config.follow_redirects)
    
    def test_audit_summary_initialization(self):
        """Test AuditSummary initialization"""
        summary = AuditSummary()
        self.assertEqual(summary.total_pages, 0)
        self.assertEqual(summary.pages_with_issues, 0)
        self.assertEqual(summary.avg_response_time, 0.0)
        self.assertEqual(summary.total_issues, 0)
        self.assertEqual(summary.common_issues, {})
        self.assertEqual(summary.status_codes, {})
    
    def test_audit_summary_add_result(self):
        """Test adding results to AuditSummary"""
        summary = AuditSummary()
        
        # Add first result
        result1 = PageResult(
            url="https://example.com/page1",
            status=200,
            response_ms=500,
            issues=["Missing meta description", "Title too short"]
        )
        summary.add_result(result1)
        
        self.assertEqual(summary.total_pages, 1)
        self.assertEqual(summary.pages_with_issues, 1)
        self.assertEqual(summary.avg_response_time, 500.0)
        self.assertEqual(summary.total_issues, 2)
        self.assertEqual(summary.status_codes[200], 1)
        self.assertEqual(summary.common_issues["Missing meta description"], 1)
        
        # Add second result
        result2 = PageResult(
            url="https://example.com/page2",
            status=404,
            response_ms=300,
            issues=["HTTP 404"]
        )
        summary.add_result(result2)
        
        self.assertEqual(summary.total_pages, 2)
        self.assertEqual(summary.pages_with_issues, 2)
        self.assertEqual(summary.avg_response_time, 400.0)  # (500 + 300) / 2
        self.assertEqual(summary.total_issues, 3)
        self.assertEqual(summary.status_codes[200], 1)
        self.assertEqual(summary.status_codes[404], 1)
        
        # Add result with no issues
        result3 = PageResult(
            url="https://example.com/page3",
            status=200,
            response_ms=200,
            issues=[]
        )
        summary.add_result(result3)
        
        self.assertEqual(summary.total_pages, 3)
        self.assertEqual(summary.pages_with_issues, 2)  # Still 2, this one has no issues
        self.assertAlmostEqual(summary.avg_response_time, 333.33, places=1)  # (500 + 300 + 200) / 3


if __name__ == '__main__':
    unittest.main()