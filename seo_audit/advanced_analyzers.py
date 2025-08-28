from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import urllib.parse
from .models import PageResult
from .utils import is_same_domain, normalize_url


class InternalLinkAnalyzer:
    """Analyzes internal linking structure and identifies orphaned pages"""
    
    def __init__(self):
        self.link_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_link_graph: Dict[str, Set[str]] = defaultdict(set)
        self.all_urls: Set[str] = set()
    
    def add_page_links(self, page_url: str, outbound_links: List[str]) -> None:
        """Add a page and its outbound links to the analysis"""
        self.all_urls.add(page_url)
        
        for link in outbound_links:
            normalized_link = normalize_url(link)
            if normalized_link and is_same_domain(normalized_link, page_url):
                self.link_graph[page_url].add(normalized_link)
                self.reverse_link_graph[normalized_link].add(page_url)
                self.all_urls.add(normalized_link)
    
    def find_orphaned_pages(self, sitemap_urls: Set[str]) -> Set[str]:
        """Find pages that exist in sitemap but have no internal links pointing to them"""
        orphaned = set()
        
        for url in sitemap_urls:
            if url not in self.reverse_link_graph or len(self.reverse_link_graph[url]) == 0:
                orphaned.add(url)
        
        return orphaned
    
    def get_page_authority_metrics(self) -> Dict[str, Dict[str, int]]:
        """Calculate basic authority metrics for pages"""
        metrics = {}
        
        for url in self.all_urls:
            metrics[url] = {
                'inbound_links': len(self.reverse_link_graph[url]),
                'outbound_links': len(self.link_graph[url]),
                'authority_score': self._calculate_authority_score(url)
            }
        
        return metrics
    
    def _calculate_authority_score(self, url: str) -> int:
        """Simple authority score based on inbound links"""
        return len(self.reverse_link_graph[url])
    
    def find_link_depth(self, start_url: str) -> Dict[str, int]:
        """Find the depth of each page from a starting URL using BFS"""
        depths = {start_url: 0}
        queue = deque([start_url])
        
        while queue:
            current_url = queue.popleft()
            current_depth = depths[current_url]
            
            for linked_url in self.link_graph[current_url]:
                if linked_url not in depths:
                    depths[linked_url] = current_depth + 1
                    queue.append(linked_url)
        
        return depths
    
    def get_link_analysis_report(self, sitemap_urls: Set[str], homepage: str) -> Dict[str, any]:
        """Generate comprehensive link analysis report"""
        orphaned_pages = self.find_orphaned_pages(sitemap_urls)
        authority_metrics = self.get_page_authority_metrics()
        depth_analysis = self.find_link_depth(homepage)
        
        # Find pages with high authority (top 10% by inbound links)
        sorted_by_authority = sorted(
            authority_metrics.items(),
            key=lambda x: x[1]['inbound_links'],
            reverse=True
        )
        
        total_pages = len(sorted_by_authority)
        high_authority_pages = sorted_by_authority[:max(1, total_pages // 10)]
        
        # Find deep pages (depth > 3)
        deep_pages = {url: depth for url, depth in depth_analysis.items() if depth > 3}
        
        return {
            'total_pages_analyzed': total_pages,
            'orphaned_pages': list(orphaned_pages),
            'orphaned_count': len(orphaned_pages),
            'high_authority_pages': [(url, metrics['inbound_links']) for url, metrics in high_authority_pages],
            'deep_pages': deep_pages,
            'average_inbound_links': sum(m['inbound_links'] for m in authority_metrics.values()) / total_pages if total_pages > 0 else 0,
            'average_outbound_links': sum(m['outbound_links'] for m in authority_metrics.values()) / total_pages if total_pages > 0 else 0
        }


class IndexabilityAnalyzer:
    """Analyzes page indexability across multiple signals"""
    
    def __init__(self):
        self.indexability_issues = []
    
    def analyze_indexability(self, results: List[PageResult]) -> Dict[str, any]:
        """Analyze indexability signals across all pages"""
        indexability_report = {
            'total_pages': len(results),
            'indexable_pages': 0,
            'non_indexable_pages': 0,
            'conflicting_signals': [],
            'indexability_issues': defaultdict(int)
        }
        
        for result in results:
            issues = self._check_indexability_signals(result)
            
            if issues:
                indexability_report['non_indexable_pages'] += 1
                for issue in issues:
                    indexability_report['indexability_issues'][issue] += 1
                
                if len(issues) > 1:
                    indexability_report['conflicting_signals'].append({
                        'url': result.url,
                        'issues': issues
                    })
            else:
                indexability_report['indexable_pages'] += 1
        
        return indexability_report
    
    def _check_indexability_signals(self, result: PageResult) -> List[str]:
        """Check various indexability signals for conflicts"""
        issues = []
        
        # Check for noindex in meta robots
        if result.noindex:
            issues.append('meta_robots_noindex')
        
        # Check for non-200 status
        if result.status != 200:
            issues.append(f'http_status_{result.status}')
        
        # Check canonical issues
        if not result.canonical:
            issues.append('missing_canonical')
        elif not result.canonical_ok:
            issues.append('canonical_not_accessible')
        
        # Check for redirect chains (if available)
        if hasattr(result, 'redirect_chain') and len(result.redirect_chain) > 1:
            issues.append('redirect_chain')
        
        # Check for blocked by robots (would need robots.txt analysis)
        # This would require additional context about robots.txt rules
        
        return issues


class HreflangAnalyzer:
    """Analyzes hreflang implementation for international sites"""
    
    def __init__(self):
        self.hreflang_data: Dict[str, Dict[str, str]] = {}
    
    def add_hreflang_data(self, url: str, hreflang_links: Dict[str, str]) -> None:
        """Add hreflang data for a URL"""
        self.hreflang_data[url] = hreflang_links
    
    def analyze_hreflang_consistency(self) -> Dict[str, any]:
        """Analyze hreflang for reciprocal linking and consistency"""
        analysis = {
            'total_pages_with_hreflang': len(self.hreflang_data),
            'reciprocal_issues': [],
            'missing_x_default': [],
            'duplicate_languages': [],
            'invalid_language_codes': []
        }
        
        # Check for reciprocal linking
        for url, hreflang_links in self.hreflang_data.items():
            for lang_code, target_url in hreflang_links.items():
                # Check if target URL has reciprocal hreflang back to original
                if target_url in self.hreflang_data:
                    target_hreflang = self.hreflang_data[target_url]
                    
                    # Find the language code that should point back to original URL
                    original_lang = self._detect_url_language(url)
                    if original_lang and original_lang in target_hreflang:
                        if target_hreflang[original_lang] != url:
                            analysis['reciprocal_issues'].append({
                                'url': url,
                                'target_url': target_url,
                                'issue': 'non_reciprocal_hreflang'
                            })
            
            # Check for x-default
            if 'x-default' not in hreflang_links:
                analysis['missing_x_default'].append(url)
            
            # Check for duplicate language codes
            seen_languages = set()
            for lang_code in hreflang_links.keys():
                if lang_code in seen_languages:
                    analysis['duplicate_languages'].append({
                        'url': url,
                        'language': lang_code
                    })
                seen_languages.add(lang_code)
        
        return analysis
    
    def _detect_url_language(self, url: str) -> Optional[str]:
        """Simple URL-based language detection"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated language detection
        path = urllib.parse.urlparse(url).path.lower()
        
        common_lang_patterns = {
            '/en/': 'en',
            '/fr/': 'fr',
            '/de/': 'de',
            '/es/': 'es',
            '/it/': 'it'
        }
        
        for pattern, lang in common_lang_patterns.items():
            if pattern in path:
                return lang
        
        return None


class StructuredDataAnalyzer:
    """Analyzes structured data implementation"""
    
    def __init__(self):
        self.structured_data: Dict[str, List[Dict]] = {}
    
    def add_structured_data(self, url: str, json_ld_data: List[Dict]) -> None:
        """Add structured data found on a page"""
        self.structured_data[url] = json_ld_data
    
    def analyze_structured_data(self) -> Dict[str, any]:
        """Analyze structured data implementation across the site"""
        analysis = {
            'total_pages_with_data': len(self.structured_data),
            'schema_types': defaultdict(int),
            'pages_by_schema_type': defaultdict(list),
            'missing_required_properties': [],
            'validation_errors': []
        }
        
        for url, json_ld_list in self.structured_data.items():
            for json_ld in json_ld_list:
                schema_type = json_ld.get('@type', 'Unknown')
                analysis['schema_types'][schema_type] += 1
                analysis['pages_by_schema_type'][schema_type].append(url)
                
                # Basic validation
                validation_issues = self._validate_schema(json_ld, schema_type)
                if validation_issues:
                    analysis['validation_errors'].append({
                        'url': url,
                        'schema_type': schema_type,
                        'issues': validation_issues
                    })
        
        return analysis
    
    def _validate_schema(self, schema_data: Dict, schema_type: str) -> List[str]:
        """Basic schema validation"""
        issues = []
        
        # Common required properties by schema type
        required_properties = {
            'Organization': ['name'],
            'Person': ['name'],
            'Article': ['headline', 'author'],
            'Product': ['name', 'description'],
            'LocalBusiness': ['name', 'address']
        }
        
        if schema_type in required_properties:
            for required_prop in required_properties[schema_type]:
                if required_prop not in schema_data:
                    issues.append(f'missing_{required_prop}')
        
        return issues