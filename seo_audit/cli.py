#!/usr/bin/env python3
"""
SEO Audit Tool - Command Line Interface
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Optional

from .models import AuditConfig
from .audit_engine import SEOAuditEngine
from .utils import normalize_url


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print("\n🛑 Audit interrupted by user")
    sys.exit(0)


def progress_callback(current: int, total: int, url: str) -> None:
    """Display progress information"""
    percentage = (current / total) * 100
    print(f"[{current}/{total}] ({percentage:.1f}%) Analyzing: {url}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Professional SEO Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com
  %(prog)s https://example.com --limit 500 --format json
  %(prog)s https://example.com --rate-limit 2.0 --timeout 30
  %(prog)s https://example.com --output my_audit --format html
        """
    )
    
    # Required arguments
    parser.add_argument(
        'domain',
        help='Domain to audit (e.g., https://example.com)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of pages to audit (default: 100)'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='Maximum crawling depth (default: 3)'
    )
    
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=1.0,
        help='Requests per second (default: 1.0)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=15,
        help='Request timeout in seconds (default: 15)'
    )
    
    parser.add_argument(
        '--user-agent',
        default='SEO-AuditBot/0.1',
        help='User agent string (default: SEO-AuditBot/0.1)'
    )
    
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'html'],
        default='csv',
        help='Output format (default: csv)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file name (without extension)'
    )
    
    parser.add_argument(
        '--no-redirects',
        action='store_true',
        help='Do not follow redirects'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip image analysis'
    )
    
    parser.add_argument(
        '--js-rendering',
        action='store_true',
        help='Enable JavaScript rendering (requires playwright)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='SEO Audit Tool 0.1.0'
    )
    
    return parser


def validate_domain(domain: str) -> str:
    """Validate and normalize domain"""
    if not domain:
        raise ValueError("Domain cannot be empty")
    
    # Add protocol if missing
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    return normalize_url(domain)


def create_config_from_args(args) -> AuditConfig:
    """Create AuditConfig from command line arguments"""
    domain = validate_domain(args.domain)
    
    config = AuditConfig(
        domain=domain,
        max_pages=args.limit,
        max_depth=args.depth,
        rate_limit=args.rate_limit,
        timeout=args.timeout,
        user_agent=args.user_agent,
        follow_redirects=not args.no_redirects,
        check_js_rendering=args.js_rendering,
        include_images=not args.no_images,
        output_format=args.format,
        output_file=args.output
    )
    
    return config


def print_header():
    """Print tool header"""
    print("""
🔍 SEO Audit Tool v0.1.0
========================
Professional SEO analysis tool for websites
""")


def print_config_summary(config: AuditConfig):
    """Print configuration summary"""
    print(f"""
🔧 Configuration:
   • Domain: {config.domain}
   • Max pages: {config.max_pages}
   • Rate limit: {config.rate_limit} req/s
   • Timeout: {config.timeout}s
   • Follow redirects: {config.follow_redirects}
   • Output format: {config.output_format}
   • JavaScript rendering: {config.check_js_rendering}
""")


def main():
    """Main CLI entry point"""
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create configuration
        config = create_config_from_args(args)
        
        # Print header and configuration
        if not args.verbose:
            print_header()
            print_config_summary(config)
        
        # Create audit engine
        audit_engine = SEOAuditEngine(config)
        
        # Validate configuration
        if not audit_engine.validate_config():
            sys.exit(1)
        
        # Run the audit
        callback = progress_callback if args.verbose else None
        results = audit_engine.run_audit(progress_callback=callback)
        
        if not results:
            print("⚠️  No pages were analyzed. Please check the domain and try again.")
            sys.exit(1)
        
        # Print progress summary
        audit_engine.print_progress_summary()
        
        # Export results
        audit_engine.export_results(config.output_file)
        
        # Print top issues
        top_issues = audit_engine.get_top_issues(5)
        if top_issues:
            print("\n🚨 Top 5 Issues:")
            for i, (issue, count) in enumerate(top_issues, 1):
                print(f"   {i}. {issue}: {count} pages")
        
        # Print performance insights
        perf_insights = audit_engine.get_performance_insights()
        if perf_insights:
            print(f"\n⚡ Performance Insights:")
            print(f"   • Average response time: {perf_insights['avg_response_time']:.0f}ms")
            print(f"   • Slow pages (>3s): {len(perf_insights['slow_pages'])}")
            print(f"   • Large pages (>500KB): {len(perf_insights['large_pages'])}")
            print(f"   • Low content pages: {len(perf_insights['low_content_pages'])}")
        
        print("\n✅ SEO audit completed successfully!")
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Audit interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()