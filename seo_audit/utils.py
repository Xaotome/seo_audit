import urllib.parse
import re
from typing import List, Optional, Set
from urllib.robotparser import RobotFileParser


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragment and ensuring scheme"""
    if not url:
        return url
        
    # Remove fragment
    url = urllib.parse.urldefrag(url)[0]
    
    # Add scheme if missing
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        
    return url


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same domain"""
    try:
        domain1 = urllib.parse.urlparse(url1).netloc.lower()
        domain2 = urllib.parse.urlparse(url2).netloc.lower()
        return domain1 == domain2
    except:
        return False


def is_internal_link(href: str, base_url: str) -> bool:
    """Check if a link is internal to the domain"""
    try:
        absolute_url = urllib.parse.urljoin(base_url, href)
        return is_same_domain(absolute_url, base_url)
    except:
        return False


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        return urllib.parse.urlparse(url).netloc
    except:
        return ""


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def count_words(text: str) -> int:
    """Count words in text content"""
    if not text:
        return 0
    
    # Simple word count - split by whitespace
    words = text.split()
    # Filter out very short "words" that are likely not meaningful
    meaningful_words = [w for w in words if len(w) >= 2]
    return len(meaningful_words)


def get_robots_parser(domain: str) -> Optional[RobotFileParser]:
    """Get robots.txt parser for domain"""
    try:
        robots_url = urllib.parse.urljoin(domain, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp
    except:
        return None


def is_allowed_by_robots(url: str, user_agent: str, robots_parser: Optional[RobotFileParser]) -> bool:
    """Check if URL is allowed by robots.txt"""
    if not robots_parser:
        return True
    
    try:
        return robots_parser.can_fetch(user_agent, url)
    except:
        return True


def get_crawl_delay(user_agent: str, robots_parser: Optional[RobotFileParser]) -> Optional[float]:
    """Get crawl delay from robots.txt"""
    if not robots_parser:
        return None
    
    try:
        delay = robots_parser.crawl_delay(user_agent)
        return float(delay) if delay else None
    except:
        return None


def deduplicate_urls(urls: List[str]) -> List[str]:
    """Remove duplicate URLs after normalization"""
    seen = set()
    result = []
    
    for url in urls:
        normalized = normalize_url(url)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    
    return result


def filter_urls_by_domain(urls: List[str], allowed_domain: str) -> List[str]:
    """Filter URLs to only include those from allowed domain"""
    return [url for url in urls if is_same_domain(url, allowed_domain)]


def is_valid_url(url: str) -> bool:
    """Check if URL is valid and has proper scheme"""
    try:
        parsed = urllib.parse.urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except:
        return False