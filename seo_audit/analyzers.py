import re
import time
import requests
import urllib.parse
from typing import List, Dict, Optional, Tuple
from selectolax.parser import HTMLParser

from .models import PageResult, AuditConfig, HeadingItem
from .utils import (
    clean_text, count_words, is_internal_link, 
    normalize_url, is_same_domain
)


class PageAnalyzer:
    """Analyzes individual pages for SEO issues"""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def analyze_page(self, url: str) -> PageResult:
        """Perform complete SEO analysis of a page"""
        result = PageResult(url=url)
        
        try:
            start_time = time.time()
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=self.config.follow_redirects
            )
            response_time = int((time.time() - start_time) * 1000)
            
            result.status = response.status_code
            result.response_ms = response_time
            
            if response.status_code >= 400:
                result.issues.append(f"HTTP {response.status_code}")
                return result
            
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                result.issues.append("Contenu non-HTML")
                return result
            
            # Store response data for analysis
            html_content = response.text
            result.html_size = len(html_content.encode('utf-8'))
            
            # Check compression
            result.is_compressed = 'gzip' in response.headers.get('Content-Encoding', '')
            
            # Store cache headers
            result.cache_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() in ['cache-control', 'expires', 'etag', 'last-modified']
            }
            
            # Parse HTML and run checks
            self._analyze_html_content(html_content, url, result)
            
        except requests.exceptions.Timeout:
            result.issues.append("Timeout de la requête")
        except requests.exceptions.RequestException as e:
            result.issues.append(f"Erreur de requête: {str(e)}")
        except Exception as e:
            result.issues.append(f"Erreur d'analyse: {str(e)}")
        
        return result
    
    def _analyze_html_content(self, html_content: str, url: str, result: PageResult) -> None:
        """Analyze HTML content for SEO issues"""
        tree = HTMLParser(html_content)
        
        # Title analysis
        self._analyze_title(tree, result)
        
        # Meta description analysis
        self._analyze_meta_description(tree, result)
        
        # H1 analysis
        self._analyze_h1_tags(tree, result)
        
        # Heading structure analysis
        self._analyze_heading_structure(tree, result)
        
        # Canonical analysis
        self._analyze_canonical(tree, url, result)
        
        # Meta robots analysis
        self._analyze_meta_robots(tree, result)
        
        # Images analysis
        self._analyze_images(tree, result)
        
        # Links analysis
        self._analyze_links(tree, url, result)
        
        # Content analysis
        self._analyze_content(tree, result)
        
        # Hreflang analysis (V1 feature)
        self._analyze_hreflang(tree, result)
        
        # Structured data analysis (V1 feature)
        self._analyze_structured_data(html_content, result)
    
    def _analyze_title(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze page title"""
        title_nodes = tree.css('title')
        
        if not title_nodes:
            result.issues.append("Titre manquant")
            return
        
        title_text = clean_text(title_nodes[0].text())
        result.title = title_text
        result.title_len = len(title_text) if title_text else 0
        
        if not title_text:
            result.issues.append("Titre vide")
        elif result.title_len < 10:
            result.issues.append("Titre trop court (< 10 caractères)")
        elif result.title_len > 65:
            result.issues.append("Titre trop long (> 65 caractères)")
    
    def _analyze_meta_description(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze meta description"""
        meta_desc_nodes = tree.css('meta[name="description"]')
        
        if not meta_desc_nodes:
            result.issues.append("Meta description manquante")
            return
        
        content = meta_desc_nodes[0].attributes.get('content', '').strip()
        result.meta_desc = content
        result.meta_desc_len = len(content) if content else 0
        
        if not content:
            result.issues.append("Meta description vide")
        elif result.meta_desc_len < 50:
            result.issues.append("Meta description trop courte (< 50 caractères)")
        elif result.meta_desc_len > 160:
            result.issues.append("Meta description trop longue (> 160 caractères)")
    
    def _analyze_h1_tags(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze H1 tags"""
        h1_nodes = tree.css('h1')
        result.h1_count = len(h1_nodes)
        
        if result.h1_count == 0:
            result.issues.append("H1 manquant")
        elif result.h1_count > 1:
            result.issues.append(f"Balises H1 multiples ({result.h1_count})")
    
    def _analyze_canonical(self, tree: HTMLParser, url: str, result: PageResult) -> None:
        """Analyze canonical tag"""
        canonical_nodes = tree.css('link[rel="canonical"]')
        
        if not canonical_nodes:
            result.issues.append("URL canonique manquante")
            return
        
        canonical_href = canonical_nodes[0].attributes.get('href', '').strip()
        if not canonical_href:
            result.issues.append("URL canonique vide")
            return
        
        # Convert to absolute URL
        canonical_url = urllib.parse.urljoin(url, canonical_href)
        result.canonical = canonical_url
        
        # Check if canonical is accessible
        try:
            response = self.session.head(canonical_url, timeout=10, allow_redirects=True)
            result.canonical_ok = response.status_code == 200
            
            if not result.canonical_ok:
                result.issues.append(f"L'URL canonique retourne {response.status_code}")
        except:
            result.canonical_ok = False
            result.issues.append("URL canonique non accessible")
        
        # Check for self-referential issues
        if urllib.parse.urldefrag(canonical_url)[0] == urllib.parse.urldefrag(url)[0]:
            # This is correct self-canonical
            pass
        else:
            # Non-self canonical, could be legitimate or an issue
            result.issues.append("URL canonique externe")
    
    def _analyze_meta_robots(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze meta robots tag"""
        robots_nodes = tree.css('meta[name="robots"]')
        
        if robots_nodes:
            robots_content = robots_nodes[0].attributes.get('content', '').lower()
            result.robots_meta = robots_content
            
            result.noindex = 'noindex' in robots_content
            result.nofollow = 'nofollow' in robots_content
            
            if result.noindex:
                result.issues.append("Directive noindex trouvée")
            if result.nofollow:
                result.issues.append("Directive nofollow trouvée")
    
    def _analyze_images(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze images for alt attributes"""
        img_nodes = tree.css('img')
        
        for img in img_nodes:
            alt = img.attributes.get('alt')
            if alt is None or alt.strip() == '':
                result.img_no_alt += 1
        
        if result.img_no_alt > 0:
            result.issues.append(f"{result.img_no_alt} images sans texte alt")
    
    def _analyze_links(self, tree: HTMLParser, url: str, result: PageResult) -> None:
        """Analyze internal and external links"""
        link_nodes = tree.css('a[href]')
        
        for link in link_nodes:
            href = link.attributes.get('href', '').strip()
            
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            
            if is_internal_link(href, url):
                result.links_internal += 1
            else:
                result.links_external += 1
    
    def _analyze_content(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze page content"""
        # Remove script and style content
        for script in tree.css('script'):
            script.decompose()
        for style in tree.css('style'):
            style.decompose()
        
        # Get body text or fallback to full text
        body_nodes = tree.css('body')
        if body_nodes:
            text_content = clean_text(body_nodes[0].text())
        else:
            text_content = clean_text(tree.text())
        
        result.word_count = count_words(text_content)
        
        if result.word_count < 150:
            result.issues.append("Nombre de mots insuffisant (< 150 mots)")
    
    def _analyze_hreflang(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze hreflang attributes (V1 feature)"""
        hreflang_nodes = tree.css('link[rel="alternate"][hreflang]')
        result.hreflang_count = len(hreflang_nodes)
    
    def _analyze_structured_data(self, html_content: str, result: PageResult) -> None:
        """Analyze structured data (V1 feature)"""
        # Look for JSON-LD structured data
        jsonld_pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(jsonld_pattern, html_content, re.DOTALL | re.IGNORECASE)
        result.structured_data_count = len(matches)
    
    def _analyze_heading_structure(self, tree: HTMLParser, result: PageResult) -> None:
        """Analyze heading hierarchy structure (H1-H6)"""
        headings = []
        
        # Get all heading elements and their positions in the document
        all_headings_elements = []
        
        # Collect all headings with their DOM positions
        for level in range(1, 7):  # H1 to H6
            heading_nodes = tree.css(f'h{level}')
            for heading in heading_nodes:
                text = clean_text(heading.text()).strip()
                if text:  # Only include non-empty headings
                    all_headings_elements.append((level, text[:100], heading))
        
        # Create HeadingItem objects with sequential positions
        for position, (level, text, element) in enumerate(all_headings_elements):
            headings.append(HeadingItem(
                level=level,
                text=text,
                position=position
            ))
        
        result.headings_structure = headings
        
        # Analyze hierarchy for issues
        self._validate_heading_hierarchy(headings, result)
    
    def _validate_heading_hierarchy(self, headings: List[HeadingItem], result: PageResult) -> None:
        """Validate heading hierarchy and report issues"""
        if not headings:
            result.headings_hierarchy_issues.append("Aucun titre trouvé")
            result.issues.append("Aucun titre trouvé")
            return
        
        issues = []
        
        # Check if first heading is H1
        if headings[0].level != 1:
            issues.append(f"Le premier titre est H{headings[0].level}, devrait être H1")
        
        # Check for missing H1
        h1_headings = [h for h in headings if h.level == 1]
        if not h1_headings:
            issues.append("Aucun titre H1 trouvé")
        elif len(h1_headings) > 1:
            issues.append(f"Plusieurs titres H1 trouvés ({len(h1_headings)})")
        
        # Check hierarchy skips
        prev_level = 0
        for heading in headings:
            current_level = heading.level
            
            # Skip level validation (e.g., H1 -> H3 without H2)
            if prev_level > 0 and current_level > prev_level + 1:
                issues.append(f"Saut de niveau de titre: H{prev_level} → H{current_level} (H{prev_level + 1} manquant)")
            
            prev_level = current_level
        
        # Check for empty headings
        empty_headings = [h for h in headings if not h.text.strip()]
        if empty_headings:
            issues.append(f"{len(empty_headings)} titres vides trouvés")
        
        # Check for very long headings
        long_headings = [h for h in headings if len(h.text) > 70]
        if long_headings:
            issues.append(f"{len(long_headings)} titres trop longs (>70 caractères)")
        
        # Store hierarchy-specific issues
        result.headings_hierarchy_issues = issues
        
        # Add significant issues to main issues list
        for issue in issues:
            if any(keyword in issue.lower() for keyword in ['no h1', 'multiple h1', 'skip', 'no headings']):
                result.issues.append(f"Structure des titres: {issue}")


class RedirectAnalyzer:
    """Analyzes redirect chains and patterns (V1 feature)"""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent
        })
    
    def analyze_redirects(self, url: str) -> Tuple[List[str], List[str]]:
        """Analyze redirect chain for a URL"""
        redirect_chain = []
        issues = []
        
        try:
            # Don't follow redirects initially to build chain manually
            response = self.session.get(url, allow_redirects=False, timeout=self.config.timeout)
            current_url = url
            redirect_chain.append(current_url)
            
            # Follow redirect chain manually
            while response.status_code in [301, 302, 303, 307, 308] and len(redirect_chain) < 10:
                location = response.headers.get('Location')
                if not location:
                    issues.append("Redirection sans en-tête Location")
                    break
                
                # Resolve relative URLs
                next_url = urllib.parse.urljoin(current_url, location)
                
                # Check for redirect loops
                if next_url in redirect_chain:
                    issues.append("Boucle de redirection détectée")
                    break
                
                redirect_chain.append(next_url)
                current_url = next_url
                
                try:
                    response = self.session.get(
                        current_url, 
                        allow_redirects=False, 
                        timeout=self.config.timeout
                    )
                except:
                    issues.append("Chaîne de redirection interrompue")
                    break
            
            # Analyze chain for issues
            if len(redirect_chain) > 1:
                if len(redirect_chain) > 3:
                    issues.append(f"Chaîne de redirection longue ({len(redirect_chain)} étapes)")
                
                # Check for HTTP/HTTPS mix
                schemes = [urllib.parse.urlparse(u).scheme for u in redirect_chain]
                if len(set(schemes)) > 1:
                    issues.append("HTTP/HTTPS mélangé dans la chaîne de redirection")
        
        except Exception as e:
            issues.append(f"Erreur d'analyse des redirections: {str(e)}")
        
        return redirect_chain, issues