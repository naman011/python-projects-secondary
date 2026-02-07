#!/usr/bin/env python3
"""
Script to test company career URLs and identify broken links.
"""

import json
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError, URLError as TimeoutError
import time
from typing import Dict, List, Tuple
import sys
import ssl

# Create SSL context that doesn't verify certificates (for testing)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def test_url(url: str, timeout: int = 10) -> Tuple[bool, str, int]:
    """
    Test if a URL is accessible using urllib.
    Returns (is_valid, status_message, status_code)
    """
    if not url or not url.startswith(('http://', 'https://')):
        return False, "Invalid URL format", 0
    
    try:
        # Create request with User-Agent to avoid blocking
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Try to open URL
        response = urlopen(req, timeout=timeout, context=ssl_context)
        status_code = response.getcode()
        final_url = response.geturl()
        
        if status_code == 200:
            if final_url != url:
                return True, f"OK (redirects to {final_url[:60]}...)", status_code
            return True, f"OK", status_code
        elif status_code in [301, 302, 303, 307, 308]:
            return True, f"Redirect ({status_code})", status_code
        elif status_code == 403:
            return False, f"Forbidden (may require login/bot protection)", status_code
        elif status_code == 404:
            return False, f"Not Found", status_code
        else:
            return False, f"HTTP {status_code}", status_code
    except HTTPError as e:
        status_code = e.code
        if status_code == 403:
            return False, f"Forbidden (may require login/bot protection)", status_code
        elif status_code == 404:
            return False, f"Not Found", status_code
        else:
            return False, f"HTTP {status_code}", status_code
    except URLError as e:
        error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
        if 'timed out' in error_msg.lower() or 'timeout' in error_msg.lower():
            return False, "Timeout", 0
        elif 'SSL' in error_msg or 'certificate' in error_msg.lower():
            return False, "SSL Error", 0
        elif 'Connection refused' in error_msg or 'connection' in error_msg.lower():
            return False, "Connection Error", 0
        else:
            return False, f"Error: {error_msg[:50]}", 0
    except Exception as e:
        return False, f"Unexpected: {str(e)[:50]}", 0

def main():
    """Main function to test company URLs."""
    companies_file = "data/companies.json"
    
    print("=" * 80)
    print("Company Career URL Testing")
    print("=" * 80)
    print()
    
    # Load companies
    try:
        with open(companies_file, 'r') as f:
            companies = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {companies_file} not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {companies_file}: {e}")
        sys.exit(1)
    
    total = len(companies)
    print(f"Total companies: {total}\n")
    print("Testing URLs (this may take a while)...\n")
    
    # Track results
    working = []
    broken = []
    redirects = []
    errors = []
    
    for i, (company_name, company_info) in enumerate(companies.items(), 1):
        url = company_info.get('career_url', '')
        
        print(f"[{i}/{total}] {company_name}")
        print(f"  URL: {url}")
        
        # Test URL
        is_valid, status, code = test_url(url)
        
        if is_valid:
            if "Redirect" in status:
                print(f"  ⚠️  {status} (HTTP {code})")
                redirects.append({
                    'company': company_name,
                    'url': url,
                    'status': status,
                    'code': code
                })
            else:
                print(f"  ✅ {status}")
            working.append(company_name)
        else:
            print(f"  ❌ {status}")
            broken.append({
                'company': company_name,
                'url': url,
                'status': status,
                'code': code
            })
            errors.append(company_name)
        
        print()
        time.sleep(0.3)  # Rate limiting to avoid overwhelming servers
    
    # Summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"✅ Working: {len(working)} ({len(working)/total*100:.1f}%)")
    print(f"⚠️  Redirects: {len(redirects)}")
    print(f"❌ Broken/Errors: {len(broken)} ({len(broken)/total*100:.1f}%)")
    print()
    
    if broken:
        print("BROKEN URLs NEEDING FIXES:")
        print("-" * 80)
        for item in broken:
            print(f"  • {item['company']}")
            print(f"    URL: {item['url']}")
            print(f"    Status: {item['status']}")
            if item['code']:
                print(f"    HTTP Code: {item['code']}")
            print()
    
    if redirects:
        print("URLS WITH REDIRECTS (may need update):")
        print("-" * 80)
        for item in redirects[:10]:  # Show first 10
            print(f"  • {item['company']}")
            print(f"    URL: {item['url']}")
            print(f"    Status: {item['status']}")
            print()
        if len(redirects) > 10:
            print(f"  ... and {len(redirects) - 10} more")
        print()
    
    # Save detailed report
    report = {
        'total': total,
        'working': working,
        'broken': broken,
        'redirects': redirects,
        'summary': {
            'working_count': len(working),
            'broken_count': len(broken),
            'redirects_count': len(redirects),
            'working_percentage': round(len(working)/total*100, 1),
            'broken_percentage': round(len(broken)/total*100, 1)
        }
    }
    
    report_file = 'data/url_test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved to: {report_file}")
    print()
    
    if broken:
        print("⚠️  ACTION REQUIRED: Fix broken URLs before running the scraper.")
        return 1
    else:
        print("✅ All URLs are working! Ready to scrape.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
