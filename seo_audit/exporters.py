import json
import csv
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from .models import PageResult, AuditSummary


class DataExporter:
    """Handles export of audit results to various formats"""
    
    def __init__(self):
        pass
    
    def export_to_csv(self, results: List[PageResult], output_file: str) -> None:
        """Export results to CSV format"""
        if not results:
            return
        
        # Define CSV columns
        fieldnames = [
            'url', 'status', 'response_ms', 'title', 'title_len',
            'meta_desc', 'meta_desc_len', 'h1_count', 'canonical',
            'canonical_ok', 'robots_meta', 'noindex', 'nofollow',
            'img_no_alt', 'links_internal', 'links_external', 'word_count',
            'html_size', 'is_compressed', 'hreflang_count', 'structured_data_count',
            'issues', 'crawled_at'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = {
                    'url': result.url,
                    'status': result.status,
                    'response_ms': result.response_ms,
                    'title': result.title,
                    'title_len': result.title_len,
                    'meta_desc': result.meta_desc,
                    'meta_desc_len': result.meta_desc_len,
                    'h1_count': result.h1_count,
                    'canonical': result.canonical,
                    'canonical_ok': result.canonical_ok,
                    'robots_meta': result.robots_meta,
                    'noindex': result.noindex,
                    'nofollow': result.nofollow,
                    'img_no_alt': result.img_no_alt,
                    'links_internal': result.links_internal,
                    'links_external': result.links_external,
                    'word_count': result.word_count,
                    'html_size': result.html_size,
                    'is_compressed': result.is_compressed,
                    'hreflang_count': result.hreflang_count,
                    'structured_data_count': result.structured_data_count,
                    'issues': '; '.join(result.issues),
                    'crawled_at': result.crawled_at.isoformat()
                }
                writer.writerow(row)
    
    def export_to_json(self, results: List[PageResult], output_file: str) -> None:
        """Export results to JSON format"""
        json_data = {
            'audit_timestamp': datetime.now().isoformat(),
            'total_pages': len(results),
            'results': []
        }
        
        for result in results:
            result_dict = {
                'url': result.url,
                'status': result.status,
                'response_ms': result.response_ms,
                'title': result.title,
                'title_len': result.title_len,
                'meta_desc': result.meta_desc,
                'meta_desc_len': result.meta_desc_len,
                'h1_count': result.h1_count,
                'canonical': result.canonical,
                'canonical_ok': result.canonical_ok,
                'robots_meta': result.robots_meta,
                'noindex': result.noindex,
                'nofollow': result.nofollow,
                'img_no_alt': result.img_no_alt,
                'links_internal': result.links_internal,
                'links_external': result.links_external,
                'word_count': result.word_count,
                'html_size': result.html_size,
                'is_compressed': result.is_compressed,
                'hreflang_count': result.hreflang_count,
                'structured_data_count': result.structured_data_count,
                'redirect_chain': result.redirect_chain,
                'cache_headers': result.cache_headers,
                'issues': result.issues,
                'crawled_at': result.crawled_at.isoformat()
            }
            json_data['results'].append(result_dict)
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
    
    def export_to_pandas(self, results: List[PageResult]) -> pd.DataFrame:
        """Export results to pandas DataFrame"""
        if not results:
            return pd.DataFrame()
        
        data = []
        for result in results:
            row = {
                'url': result.url,
                'status': result.status,
                'response_ms': result.response_ms,
                'title': result.title,
                'title_len': result.title_len,
                'meta_desc': result.meta_desc,
                'meta_desc_len': result.meta_desc_len,
                'h1_count': result.h1_count,
                'canonical': result.canonical,
                'canonical_ok': result.canonical_ok,
                'robots_meta': result.robots_meta,
                'noindex': result.noindex,
                'nofollow': result.nofollow,
                'img_no_alt': result.img_no_alt,
                'links_internal': result.links_internal,
                'links_external': result.links_external,
                'word_count': result.word_count,
                'html_size': result.html_size,
                'is_compressed': result.is_compressed,
                'hreflang_count': result.hreflang_count,
                'structured_data_count': result.structured_data_count,
                'issues_count': len(result.issues),
                'issues': '; '.join(result.issues),
                'crawled_at': result.crawled_at
            }
            data.append(row)
        
        return pd.DataFrame(data)


class ReportGenerator:
    """Generates human-readable reports"""
    
    def __init__(self):
        self.exporter = DataExporter()
    
    def generate_summary_report(self, results: List[PageResult], summary: AuditSummary) -> str:
        """Generate a text summary report"""
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append("SEO AUDIT SUMMARY REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Overview
        report_lines.append("OVERVIEW")
        report_lines.append("-" * 20)
        report_lines.append(f"Total pages analyzed: {summary.total_pages}")
        report_lines.append(f"Pages with issues: {summary.pages_with_issues}")
        report_lines.append(f"Issue rate: {(summary.pages_with_issues / summary.total_pages * 100):.1f}%")
        report_lines.append(f"Average response time: {summary.avg_response_time:.0f}ms")
        report_lines.append(f"Total issues found: {summary.total_issues}")
        report_lines.append("")
        
        # Status codes
        if summary.status_codes:
            report_lines.append("HTTP STATUS CODES")
            report_lines.append("-" * 20)
            for status, count in sorted(summary.status_codes.items()):
                percentage = (count / summary.total_pages * 100)
                report_lines.append(f"{status}: {count} pages ({percentage:.1f}%)")
            report_lines.append("")
        
        # Top issues
        if summary.common_issues:
            report_lines.append("TOP 10 ISSUES")
            report_lines.append("-" * 20)
            sorted_issues = sorted(
                summary.common_issues.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            for issue, count in sorted_issues:
                percentage = (count / summary.total_pages * 100)
                report_lines.append(f"{issue}: {count} pages ({percentage:.1f}%)")
            report_lines.append("")
        
        # Performance insights
        report_lines.append("PERFORMANCE INSIGHTS")
        report_lines.append("-" * 20)
        
        if results:
            # Response time analysis
            response_times = [r.response_ms for r in results if r.response_ms]
            if response_times:
                slow_pages = [r for r in results if r.response_ms and r.response_ms > 3000]
                report_lines.append(f"Pages loading >3s: {len(slow_pages)}")
                
            # Content analysis
            low_content_pages = [r for r in results if r.word_count < 150]
            report_lines.append(f"Pages with low word count: {len(low_content_pages)}")
            
            # SEO basics
            no_title_pages = [r for r in results if not r.title]
            no_meta_desc_pages = [r for r in results if not r.meta_desc]
            no_h1_pages = [r for r in results if r.h1_count == 0]
            
            report_lines.append(f"Pages missing title: {len(no_title_pages)}")
            report_lines.append(f"Pages missing meta description: {len(no_meta_desc_pages)}")
            report_lines.append(f"Pages missing H1: {len(no_h1_pages)}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def generate_html_report(self, results: List[PageResult], summary: AuditSummary, output_file: str) -> None:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SEO Audit Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background: #ecf0f1; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .issues {{ background: #e74c3c; color: white; padding: 10px; border-radius: 3px; }}
                .success {{ background: #27ae60; color: white; padding: 10px; border-radius: 3px; }}
                .warning {{ background: #f39c12; color: white; padding: 10px; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #34495e; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .url {{ max-width: 300px; word-wrap: break-word; }}
                .issues-cell {{ max-width: 200px; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SEO Audit Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total pages:</strong> {summary.total_pages}</p>
                <p><strong>Pages with issues:</strong> {summary.pages_with_issues}</p>
                <p><strong>Issue rate:</strong> {(summary.pages_with_issues / summary.total_pages * 100):.1f}%</p>
                <p><strong>Average response time:</strong> {summary.avg_response_time:.0f}ms</p>
                <p><strong>Total issues:</strong> {summary.total_issues}</p>
            </div>
            
            <h2>Page Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Response Time</th>
                        <th>Title Length</th>
                        <th>Meta Desc Length</th>
                        <th>H1 Count</th>
                        <th>Word Count</th>
                        <th>Issues</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for result in results:
            status_class = "success" if result.status == 200 else ("warning" if result.status < 400 else "issues")
            issues_text = "; ".join(result.issues) if result.issues else "No issues"
            
            html_content += f"""
                    <tr>
                        <td class="url">{result.url}</td>
                        <td><span class="{status_class}">{result.status or 'N/A'}</span></td>
                        <td>{result.response_ms or 'N/A'}ms</td>
                        <td>{result.title_len}</td>
                        <td>{result.meta_desc_len}</td>
                        <td>{result.h1_count}</td>
                        <td>{result.word_count}</td>
                        <td class="issues-cell">{issues_text}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)