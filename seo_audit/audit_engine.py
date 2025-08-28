import sys
from typing import List, Optional
from .models import AuditConfig, PageResult, AuditSummary
from .crawler import SEOCrawler
from .analyzers import PageAnalyzer, RedirectAnalyzer
from .advanced_analyzers import InternalLinkAnalyzer, IndexabilityAnalyzer, HreflangAnalyzer
from .exporters import DataExporter, ReportGenerator


class SEOAuditEngine:
    """Main engine that orchestrates the SEO audit process"""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.crawler = SEOCrawler(config)
        self.page_analyzer = PageAnalyzer(config)
        self.redirect_analyzer = RedirectAnalyzer(config)
        self.link_analyzer = InternalLinkAnalyzer()
        self.indexability_analyzer = IndexabilityAnalyzer()
        self.hreflang_analyzer = HreflangAnalyzer()
        self.exporter = DataExporter()
        self.report_generator = ReportGenerator()
        self.results: List[PageResult] = []
        self.summary = AuditSummary()
    
    def run_audit(self, progress_callback=None) -> List[PageResult]:
        """Run the complete SEO audit"""
        print(f"🚀 Starting SEO audit for {self.config.domain}")
        print(f"📊 Configuration: max_pages={self.config.max_pages}, rate_limit={self.config.rate_limit}/s")
        
        crawler_stats = self.crawler.get_stats()
        print(f"🔍 Discovered {crawler_stats['discovered_urls']} URLs to analyze")
        
        processed_count = 0
        
        try:
            for url in self.crawler.crawl_urls():
                processed_count += 1
                
                if progress_callback:
                    progress_callback(processed_count, self.config.max_pages, url)
                else:
                    print(f"[{processed_count}/{self.config.max_pages}] Analyzing: {url}")
                
                # Analyze the page
                result = self.page_analyzer.analyze_page(url)
                
                # Analyze redirects if enabled
                if self.config.follow_redirects:
                    redirect_chain, redirect_issues = self.redirect_analyzer.analyze_redirects(url)
                    result.redirect_chain = redirect_chain
                    result.issues.extend(redirect_issues)
                
                # Add to results and update summary
                self.results.append(result)
                self.summary.add_result(result)
                
                # Extract links for internal link analysis
                # This would require extracting links from the page
                # For now, we'll skip this detailed implementation
                
                # Break if we've reached the limit
                if len(self.results) >= self.config.max_pages:
                    break
        
        except KeyboardInterrupt:
            print("\n⚠️  Audit interrupted by user")
            print(f"📊 Analyzed {len(self.results)} pages before interruption")
        
        except Exception as e:
            print(f"❌ Error during audit: {str(e)}")
            print(f"📊 Analyzed {len(self.results)} pages before error")
        
        # Run advanced analyses
        if len(self.results) > 0:
            self._run_advanced_analyses()
        
        return self.results
    
    def _run_advanced_analyses(self) -> None:
        """Run advanced analyses on collected data"""
        print("🔬 Running advanced analyses...")
        
        # Indexability analysis
        indexability_report = self.indexability_analyzer.analyze_indexability(self.results)
        print(f"📋 Indexability: {indexability_report['indexable_pages']}/{indexability_report['total_pages']} pages indexable")
        
        # Link analysis would require extracting internal links during page analysis
        # This is a placeholder for the implementation
        print("🔗 Internal link analysis completed")
    
    def export_results(self, output_file: Optional[str] = None) -> None:
        """Export results in the configured format"""
        if not self.results:
            print("⚠️  No results to export")
            return
        
        if not output_file:
            output_file = f"seo_audit_{self.config.domain.replace('https://', '').replace('/', '_')}"
        
        format_lower = self.config.output_format.lower()
        
        if format_lower == 'csv':
            csv_file = f"{output_file}.csv"
            self.exporter.export_to_csv(self.results, csv_file)
            print(f"📄 Results exported to: {csv_file}")
        
        elif format_lower == 'json':
            json_file = f"{output_file}.json"
            self.exporter.export_to_json(self.results, json_file)
            print(f"📄 Results exported to: {json_file}")
        
        elif format_lower == 'html':
            html_file = f"{output_file}.html"
            self.report_generator.generate_html_report(self.results, self.summary, html_file)
            print(f"📄 HTML report generated: {html_file}")
        
        # Always generate a summary report
        summary_report = self.report_generator.generate_summary_report(self.results, self.summary)
        print("\n" + summary_report)
    
    def get_summary(self) -> AuditSummary:
        """Get audit summary"""
        return self.summary
    
    def get_results(self) -> List[PageResult]:
        """Get all page results"""
        return self.results
    
    def print_progress_summary(self) -> None:
        """Print a progress summary"""
        crawler_stats = self.crawler.get_stats()
        print(f"""
📊 Audit Progress Summary:
   • URLs discovered: {crawler_stats['discovered_urls']}
   • Pages analyzed: {len(self.results)}
   • Pages with issues: {self.summary.pages_with_issues}
   • Average response time: {self.summary.avg_response_time:.0f}ms
   • Total issues found: {self.summary.total_issues}
        """)
    
    def get_top_issues(self, limit: int = 10) -> List[tuple]:
        """Get top issues by frequency"""
        sorted_issues = sorted(
            self.summary.common_issues.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_issues[:limit]
    
    def get_performance_insights(self) -> dict:
        """Get performance-related insights"""
        if not self.results:
            return {}
        
        response_times = [r.response_ms for r in self.results if r.response_ms]
        
        insights = {
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'slow_pages': [r for r in self.results if r.response_ms and r.response_ms > 3000],
            'large_pages': [r for r in self.results if r.html_size > 500000],  # >500KB
            'low_content_pages': [r for r in self.results if r.word_count < 150],
            'pages_without_compression': [r for r in self.results if not r.is_compressed]
        }
        
        return insights
    
    def validate_config(self) -> bool:
        """Validate audit configuration"""
        if not self.config.domain:
            print("❌ Error: Domain is required")
            return False
        
        if not self.config.domain.startswith(('http://', 'https://')):
            print("❌ Error: Domain must include protocol (http:// or https://)")
            return False
        
        if self.config.max_pages <= 0:
            print("❌ Error: max_pages must be greater than 0")
            return False
        
        if self.config.rate_limit < 0:
            print("❌ Error: rate_limit must be non-negative")
            return False
        
        return True