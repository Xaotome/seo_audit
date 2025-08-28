from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class HeadingItem:
    """Represents a heading element with its level and text"""
    level: int  # 1-6 for H1-H6
    text: str
    position: int  # Position in the document (order of appearance)


@dataclass
class PageResult:
    """Data model for SEO page audit results"""
    url: str
    status: Optional[int] = None
    response_ms: Optional[int] = None
    title: Optional[str] = None
    title_len: int = 0
    meta_desc: Optional[str] = None
    meta_desc_len: int = 0
    h1_count: int = 0
    canonical: Optional[str] = None
    canonical_ok: bool = False
    robots_meta: Optional[str] = None
    noindex: bool = False
    nofollow: bool = False
    img_no_alt: int = 0
    links_internal: int = 0
    links_external: int = 0
    word_count: int = 0
    issues: List[str] = field(default_factory=list)
    
    # Heading structure analysis
    headings_structure: List[HeadingItem] = field(default_factory=list)
    headings_hierarchy_issues: List[str] = field(default_factory=list)
    
    # V1 features
    redirect_chain: List[str] = field(default_factory=list)
    hreflang_count: int = 0
    structured_data_count: int = 0
    html_size: int = 0
    is_compressed: bool = False
    cache_headers: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    crawled_at: datetime = field(default_factory=datetime.now)


@dataclass 
class AuditConfig:
    """Configuration for SEO audit"""
    domain: str
    max_pages: int = 100
    max_depth: int = 3
    rate_limit: float = 1.0  # requests per second
    timeout: int = 15
    user_agent: str = "SEO-AuditBot/0.1"
    follow_redirects: bool = True
    check_js_rendering: bool = False
    include_images: bool = True
    output_format: str = "csv"  # csv, json, html
    output_file: Optional[str] = None


@dataclass
class AuditSummary:
    """Summary statistics for the audit"""
    total_pages: int = 0
    pages_with_issues: int = 0
    avg_response_time: float = 0.0
    total_issues: int = 0
    common_issues: Dict[str, int] = field(default_factory=dict)
    status_codes: Dict[int, int] = field(default_factory=dict)
    
    def add_result(self, result: PageResult):
        """Add a page result to the summary"""
        self.total_pages += 1
        if result.issues:
            self.pages_with_issues += 1
            self.total_issues += len(result.issues)
            
        if result.response_ms:
            # Update avg response time
            self.avg_response_time = (
                (self.avg_response_time * (self.total_pages - 1) + result.response_ms) 
                / self.total_pages
            )
            
        if result.status:
            self.status_codes[result.status] = self.status_codes.get(result.status, 0) + 1
            
        for issue in result.issues:
            self.common_issues[issue] = self.common_issues.get(issue, 0) + 1