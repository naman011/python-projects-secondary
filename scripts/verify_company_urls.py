#!/usr/bin/env python3
"""
Script to verify and update company career URLs.
This script will check URLs and help identify which ones need updating.
"""

import json
import requests
from urllib.parse import urlparse
import time
from typing import Dict, List, Tuple

def verify_url(url: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Verify if a URL is accessible.
    Returns (is_valid, status_message)
    """
    if not url or not url.startswith(('http://', 'https://')):
        return False, "Invalid URL format"
    
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True, f"OK ({response.status_code})"
        elif response.status_code in [301, 302, 303, 307, 308]:
            # Redirect - might be OK, but could indicate URL change
            return True, f"Redirect ({response.status_code})"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)[:50]}"
    except Exception as e:
        return False, f"Unexpected: {str(e)[:50]}"

def check_url_issues(url: str) -> List[str]:
    """Check for common URL issues."""
    issues = []
    
    if url.startswith('http://'):
        issues.append("Uses HTTP (should be HTTPS)")
    
    if 'linkedin.com' in url.lower():
        issues.append("LinkedIn redirect (should use direct careers page)")
    
    if 'lnkd.in' in url.lower():
        issues.append("LinkedIn short link (should use direct careers page)")
    
    parsed = urlparse(url)
    if not parsed.netloc:
        issues.append("Invalid domain")
    
    return issues

def main():
    """Main function to verify company URLs."""
    companies_file = "data/companies.json"
    
    print("=" * 80)
    print("Company Career URL Verification")
    print("=" * 80)
    print()
    
    # Load companies
    with open(companies_file, 'r') as f:
        companies = json.load(f)
    
    total = len(companies)
    print(f"Total companies: {total}\n")
    
    # Track results
    verified = []
    needs_update = []
    issues_found = []
    
    print("Verifying URLs (this may take a while)...\n")
    
    for i, (company_name, company_info) in enumerate(companies.items(), 1):
        url = company_info.get('career_url', '')
        
        print(f"[{i}/{total}] {company_name}")
        print(f"  URL: {url}")
        
        # Check for issues
        url_issues = check_url_issues(url)
        if url_issues:
            print(f"  ⚠️  Issues: {', '.join(url_issues)}")
            issues_found.append({
                'company': company_name,
                'url': url,
                'issues': url_issues
            })
        
        # Verify URL
        is_valid, status = verify_url(url)
        
        if is_valid:
            print(f"  ✅ {status}")
            verified.append(company_name)
        else:
            print(f"  ❌ {status}")
            needs_update.append({
                'company': company_name,
                'url': url,
                'status': status,
                'issues': url_issues
            })
        
        print()
        time.sleep(0.5)  # Rate limiting
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Verified: {len(verified)}")
    print(f"❌ Needs Update: {len(needs_update)}")
    print(f"⚠️  Has Issues: {len(issues_found)}")
    print()
    
    if needs_update:
        print("COMPANIES NEEDING URL UPDATES:")
        print("-" * 80)
        for item in needs_update:
            print(f"  • {item['company']}")
            print(f"    Current: {item['url']}")
            print(f"    Status: {item['status']}")
            if item['issues']:
                print(f"    Issues: {', '.join(item['issues'])}")
            print()
    
    if issues_found:
        print("COMPANIES WITH URL ISSUES (but accessible):")
        print("-" * 80)
        for item in issues_found:
            print(f"  • {item['company']}")
            print(f"    URL: {item['url']}")
            print(f"    Issues: {', '.join(item['issues'])}")
            print()
    
    # Save report
    report = {
        'verified': verified,
        'needs_update': needs_update,
        'issues_found': issues_found,
        'total': total
    }
    
    with open('data/url_verification_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: data/url_verification_report.json")

if __name__ == "__main__":
    main()
