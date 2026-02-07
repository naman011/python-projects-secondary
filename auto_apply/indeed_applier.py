"""Indeed.com job application handler."""

import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from auto_apply.base_applier import BaseApplier
from auto_apply.selenium_fallback import SeleniumFallback
from auto_apply.profile_loader import ProfileLoader
from auto_apply.utils import detect_login_required
from utils.config import METHOD_API, METHOD_SELENIUM, ERROR_FORM_NOT_FOUND, ERROR_LOGIN_REQUIRED

logger = logging.getLogger(__name__)


class IndeedApplier(BaseApplier):
    """Handler for Indeed.com job applications."""
    
    def __init__(self, profile_loader: ProfileLoader):
        """Initialize Indeed applier."""
        super().__init__(profile_loader)
        self.selenium_fallback = SeleniumFallback(profile_loader)
        self.base_url = "https://www.indeed.com"
    
    def can_handle(self, job_url: str, source: str) -> bool:
        """Check if this applier can handle the URL."""
        if source and source.lower() == 'indeed':
            return True
        url_lower = job_url.lower()
        return 'indeed.com' in url_lower or 'indeed.co' in url_lower
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from Indeed URL."""
        # Indeed URLs can be: /viewjob?jk=JOB_ID or /jobs/view/JOB_ID
        match = re.search(r'jk=([^&]+)', url)
        if match:
            return match.group(1)
        match = re.search(r'/jobs/view/([^/?]+)', url)
        if match:
            return match.group(1)
        return None
    
    def _find_apply_button(self, html: str) -> Optional[Dict]:
        """Find apply button/link in HTML."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Common Indeed apply button selectors
        apply_selectors = [
            'a[href*="apply"]',
            'button[id*="apply"]',
            'a[id*="apply"]',
            'button[class*="apply"]',
            'a[class*="apply"]',
            'a:contains("Apply")',
            'button:contains("Apply")',
        ]
        
        for selector in apply_selectors:
            if ':contains(' in selector:
                # Use XPath-like search
                elements = soup.find_all('a', string=re.compile('Apply', re.I))
                if elements:
                    href = elements[0].get('href', '')
                    if href:
                        return {'type': 'link', 'href': href, 'element': elements[0]}
            else:
                element = soup.select_one(selector)
                if element:
                    href = element.get('href', '')
                    if href:
                        return {'type': 'link', 'href': href, 'element': element}
                    # Check if it's a button that triggers JS
                    onclick = element.get('onclick', '')
                    if onclick:
                        return {'type': 'button', 'element': element, 'onclick': onclick}
        
        return None
    
    def apply(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to Indeed job.
        
        Indeed typically redirects to external company sites or uses their own form.
        We'll try to find the application form, otherwise fall back to Selenium.
        """
        job_url = job.get('url', '')
        if not job_url:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'No job URL provided',
                'error_category': 'Invalid Data',
                'message': 'Job URL is required'
            }
        
        # Try API approach first
        result = self._try_api_apply(job_url, job)
        if result.get('success') or result.get('error_category') == ERROR_FORM_NOT_FOUND:
            return result
        
        # Fall back to Selenium
        logger.info(f"API approach failed for {job_url}, trying Selenium fallback")
        selenium_result = self.selenium_fallback.apply(job)
        return selenium_result
    
    def _try_api_apply(self, job_url: str, job: Dict) -> Dict[str, Any]:
        """Try to apply via API/HTTP requests."""
        # Get job page
        page_result = self._get_page_content(job_url)
        if not page_result:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Failed to load job page',
                'error_category': 'Network Error',
                'message': 'Could not fetch job page'
            }
        
        # page_result is a tuple of (html, response)
        html, response = page_result
        
        # Check for login requirement
        if detect_login_required(html, job_url):
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Login required',
                'error_category': ERROR_LOGIN_REQUIRED,
                'message': 'Indeed requires login to apply'
            }
        
        # Find apply button
        apply_info = self._find_apply_button(html)
        if not apply_info:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Apply button not found',
                'error_category': ERROR_FORM_NOT_FOUND,
                'message': 'Could not locate application form or apply button'
            }
        
        # Indeed often redirects to external sites or uses complex forms
        # For now, indicate that Selenium fallback is needed
        return {
            'success': False,
            'method': METHOD_API,
            'error': 'Complex form requires Selenium',
            'error_category': ERROR_FORM_NOT_FOUND,
            'message': 'Indeed application form requires browser automation'
        }
