"""Naukri.com job application handler."""

import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urljoin
from auto_apply.base_applier import BaseApplier
from auto_apply.selenium_fallback import SeleniumFallback
from auto_apply.profile_loader import ProfileLoader
from auto_apply.utils import detect_login_required
from utils.config import METHOD_API, METHOD_SELENIUM, ERROR_FORM_NOT_FOUND, ERROR_LOGIN_REQUIRED

logger = logging.getLogger(__name__)


class NaukriApplier(BaseApplier):
    """Handler for Naukri.com job applications."""
    
    def __init__(self, profile_loader: ProfileLoader):
        """Initialize Naukri applier."""
        super().__init__(profile_loader)
        self.selenium_fallback = SeleniumFallback(profile_loader)
        self.base_url = "https://www.naukri.com"
    
    def can_handle(self, job_url: str, source: str) -> bool:
        """Check if this applier can handle the URL."""
        if source and source.lower() == 'naukri':
            return True
        url_lower = job_url.lower()
        return 'naukri.com' in url_lower
    
    def apply(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to Naukri job.
        
        Naukri typically requires login and uses their own application system.
        We'll try API first, then fall back to Selenium.
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
        
        # Check for login requirement (Naukri almost always requires login)
        if detect_login_required(html, job_url):
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Login required',
                'error_category': ERROR_LOGIN_REQUIRED,
                'message': 'Naukri requires login to apply. Please apply manually or configure account credentials.'
            }
        
        # Try to find application form
        form = self._find_application_form(html)
        if not form:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Application form not found',
                'error_category': ERROR_FORM_NOT_FOUND,
                'message': 'Could not locate application form. Naukri may require login.'
            }
        
        # Naukri forms are typically complex and require authentication
        # For now, indicate that Selenium fallback or manual application is needed
        return {
            'success': False,
            'method': METHOD_API,
            'error': 'Complex form requires Selenium or login',
            'error_category': ERROR_FORM_NOT_FOUND,
            'message': 'Naukri application form requires browser automation or manual login'
        }
