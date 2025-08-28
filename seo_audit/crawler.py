import time
import requests
import urllib.parse
from collections import deque
from typing import List, Set, Optional, Iterator
from xml.etree import ElementTree as ET
from urllib.robotparser import RobotFileParser

from .models import AuditConfig
from .utils import (
    normalize_url, is_same_domain, deduplicate_urls, 
    filter_urls_by_domain, is_valid_url, get_robots_parser,
    is_allowed_by_robots, get_crawl_delay
)


class URLDiscovery:
    """Handles URL discovery from sitemaps and page crawling"""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def discover_from_sitemap(self, domain: str) -> List[str]:
        """Discover URLs from sitemap.xml"""
        urls = set()
        
        # Common sitemap locations
        sitemap_urls = [
            urllib.parse.urljoin(domain, '/sitemap.xml'),
            urllib.parse.urljoin(domain, '/sitemap_index.xml'),
            urllib.parse.urljoin(domain, '/sitemaps.xml')
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(
                    sitemap_url, 
                    timeout=self.config.timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200 and 'xml' in response.headers.get('Content-Type', ''):
                    sitemap_urls_found = self._parse_sitemap(response.text, domain)
                    urls.update(sitemap_urls_found)
                    
            except Exception:
                continue
        
        return list(urls)
    
    def _parse_sitemap(self, xml_content: str, domain: str) -> Set[str]:
        """Parse XML sitemap content"""
        urls = set()
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'xhtml': 'http://www.w3.org/1999/xhtml'
            }
            
            # Check if it's a sitemap index
            sitemap_elements = root.findall('.//sm:sitemap', namespaces)
            if sitemap_elements:
                # This is a sitemap index, fetch individual sitemaps
                for sitemap_elem in sitemap_elements:
                    loc_elem = sitemap_elem.find('sm:loc', namespaces)
                    if loc_elem is not None and loc_elem.text:
                        nested_urls = self._fetch_nested_sitemap(loc_elem.text.strip())
                        urls.update(nested_urls)
            else:
                # This is a regular sitemap, extract URLs
                url_elements = root.findall('.//sm:url/sm:loc', namespaces)
                for url_elem in url_elements:
                    if url_elem.text:
                        url = url_elem.text.strip()
                        if is_same_domain(url, domain):
                            urls.add(normalize_url(url))
        
        except ET.ParseError:
            pass
        
        return urls
    
    def _fetch_nested_sitemap(self, sitemap_url: str) -> Set[str]:
        """Fetch and parse nested sitemap"""
        urls = set()
        
        try:
            response = self.session.get(
                sitemap_url,
                timeout=self.config.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                nested_urls = self._parse_sitemap(response.text, self.config.domain)
                urls.update(nested_urls)
        
        except Exception:
            pass
        
        return urls
    
    def discover_from_page(self, url: str) -> List[str]:
        """Discover URLs from a webpage's links"""
        urls = []
        
        try:
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                urls = self._extract_links_from_html(response.text, url)
        
        except Exception:
            pass
        
        return urls
    
    def _extract_links_from_html(self, html_content: str, base_url: str) -> List[str]:
        """Extract internal links from HTML content"""
        from selectolax.parser import HTMLParser
        
        urls = []
        tree = HTMLParser(html_content)
        
        # Extract links from <a> tags
        for link in tree.css('a[href]'):
            href = link.attributes.get('href', '').strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                absolute_url = urllib.parse.urljoin(base_url, href)
                if is_same_domain(absolute_url, self.config.domain):
                    urls.append(normalize_url(absolute_url))
        
        return deduplicate_urls(urls)


class SEOCrawler:
    """Main crawler class that manages the crawling process"""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.discovered_urls: Set[str] = set()
        self.crawled_urls: Set[str] = set()
        self.url_queue = deque()
        self.robots_parser = get_robots_parser(config.domain)
        self.discovery = URLDiscovery(config)
        self.last_request_time = 0
        
        # Get crawl delay from robots.txt or use configured rate limit
        robots_delay = get_crawl_delay(config.user_agent, self.robots_parser)
        if robots_delay:
            self.crawl_delay = robots_delay
        else:
            self.crawl_delay = 1.0 / config.rate_limit if config.rate_limit > 0 else 0
    
    def initialize_urls(self) -> None:
        """Initialize URL queue with sitemap URLs or homepage"""
        # Try to get URLs from sitemap first
        sitemap_urls = self.discovery.discover_from_sitemap(self.config.domain)
        
        if sitemap_urls:
            # Filter and limit URLs from sitemap
            filtered_urls = filter_urls_by_domain(sitemap_urls, self.config.domain)
            for url in filtered_urls[:self.config.max_pages]:
                self._add_url_to_queue(url)
        else:
            # Fallback to homepage
            homepage = normalize_url(self.config.domain)
            self._add_url_to_queue(homepage)
    
    def _add_url_to_queue(self, url: str) -> None:
        """Add URL to crawl queue if not already discovered"""
        if url not in self.discovered_urls and is_valid_url(url):
            if is_allowed_by_robots(url, self.config.user_agent, self.robots_parser):
                self.discovered_urls.add(url)
                self.url_queue.append(url)
    
    def _respect_rate_limit(self) -> None:
        """Implement rate limiting between requests"""
        if self.crawl_delay > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.crawl_delay:
                time.sleep(self.crawl_delay - elapsed)
        
        self.last_request_time = time.time()
    
    def get_next_url(self) -> Optional[str]:
        """Get next URL to crawl"""
        if not self.url_queue or len(self.crawled_urls) >= self.config.max_pages:
            return None
        
        return self.url_queue.popleft()
    
    def mark_url_crawled(self, url: str) -> None:
        """Mark URL as crawled"""
        self.crawled_urls.add(url)
    
    def discover_more_urls(self, url: str) -> None:
        """Discover more URLs from the current page"""
        if len(self.discovered_urls) >= self.config.max_pages:
            return
        
        try:
            page_urls = self.discovery.discover_from_page(url)
            for page_url in page_urls:
                if len(self.discovered_urls) < self.config.max_pages:
                    self._add_url_to_queue(page_url)
                else:
                    break
        except Exception:
            pass
    
    def crawl_urls(self) -> Iterator[str]:
        """Iterator that yields URLs to crawl"""
        self.initialize_urls()
        
        while True:
            url = self.get_next_url()
            if not url:
                break
            
            self._respect_rate_limit()
            yield url
            
            self.mark_url_crawled(url)
            
            # Discover more URLs from this page for depth crawling
            if len(self.crawled_urls) < self.config.max_pages:
                self.discover_more_urls(url)
    
    def get_stats(self) -> dict:
        """Get crawling statistics"""
        return {
            'discovered_urls': len(self.discovered_urls),
            'crawled_urls': len(self.crawled_urls),
            'remaining_urls': len(self.url_queue),
            'crawl_delay': self.crawl_delay
        }