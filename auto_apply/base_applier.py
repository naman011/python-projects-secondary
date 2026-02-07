"""Base applier class with common utilities for job applications."""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Tuple
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from auto_apply.profile_loader import ProfileLoader
from auto_apply.utils import (
    random_delay,
    get_random_user_agent,
    human_like_delay
)
from auto_apply.utils import detect_captcha, detect_login_required
from utils.config import (
    APPLY_DELAY_MIN,
    APPLY_DELAY_MAX,
    ERROR_CAPTCHA,
    ERROR_LOGIN_REQUIRED,
    ERROR_NETWORK,
    ERROR_UNKNOWN,
    TIMEOUT
)

logger = logging.getLogger(__name__)


class BaseApplier(ABC):
    """Base class for all job application handlers."""
    
    def __init__(self, profile_loader: ProfileLoader):
        """
        Initialize base applier.
        
        Args:
            profile_loader: ProfileLoader instance with user data
        """
        self.profile_loader = profile_loader
        self.profile_data = profile_loader.get_form_data()
        self.session = requests.Session()
        self._update_user_agent()
        self.last_request_time = 0
    
    def _update_user_agent(self):
        """Update session user agent."""
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        min_delay = APPLY_DELAY_MIN
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last + random.uniform(0, 5)
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting and error handling.
        
        Args:
            url: URL to request
            method: HTTP method
            params: Query parameters
            data: Request data
            headers: Additional headers
            **kwargs: Additional request arguments
            
        Returns:
            Response object or None if failed
        """
        self._rate_limit()
        
        request_headers = {**self.session.headers}
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=TIMEOUT,
                allow_redirects=True,
                **kwargs
            )
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            return None
    
    def _get_page_content(self, url: str) -> Optional[Tuple[str, requests.Response]]:
        """
        Get page content and check for common issues.
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple of (html_content, response) or None if failed
        """
        response = self._make_request(url)
        if not response:
            return None
        
        if response.status_code != 200:
            logger.warning(f"Non-200 status code: {response.status_code} for {url}")
            return None
        
        html = response.text
        
        # Check for CAPTCHA
        if detect_captcha(html):
            logger.warning(f"CAPTCHA detected on {url}")
            return None  # Return None to indicate failure
        
        # Check for login requirement
        if detect_login_required(html, url):
            logger.warning(f"Login required on {url}")
            return None  # Return None to indicate failure
        
        return html, response
    
    def _find_application_form(self, html: str) -> Optional[BeautifulSoup]:
        """
        Find application form in HTML.
        
        Args:
            html: HTML content
            
        Returns:
            BeautifulSoup element of form or None
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try common form selectors
        form_selectors = [
            'form[action*="apply"]',
            'form[action*="application"]',
            'form[id*="apply"]',
            'form[class*="apply"]',
            'form',
        ]
        
        for selector in form_selectors:
            form = soup.select_one(selector)
            if form:
                return form
        
        return None
    
    def _fill_form_field(self, field, value: str, field_type: str = 'text'):
        """
        Fill a form field with value.
        
        Args:
            field: BeautifulSoup element
            value: Value to fill
            field_type: Type of field
        """
        if field_type in ['text', 'email', 'tel', 'url']:
            if field.name == 'input':
                field['value'] = value
            elif field.name == 'textarea':
                field.string = value
        elif field_type == 'select':
            # Try to select option by value or text
            options = field.find_all('option')
            for option in options:
                if option.get('value') == value or option.text.strip() == value:
                    option['selected'] = 'selected'
                    break
    
    @abstractmethod
    def can_handle(self, job_url: str, source: str) -> bool:
        """
        Check if this applier can handle the given job URL.
        
        Args:
            job_url: Job application URL
            source: Job source (e.g., 'Indeed', 'Naukri')
            
        Returns:
            True if this applier can handle the URL
        """
        pass
    
    @abstractmethod
    def apply(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to a job.
        
        Args:
            job: Job dictionary with title, company, url, etc.
            
        Returns:
            Dictionary with application result:
            {
                'success': bool,
                'method': 'API' or 'Selenium',
                'error': str or None,
                'error_category': str or None,
                'message': str
            }
        """
        pass
    
    def verify_application(self, job_url: str) -> bool:
        """
        Verify if application was successful (optional implementation).
        
        Args:
            job_url: Job URL
            
        Returns:
            True if application appears successful
        """
        # Default implementation - can be overridden
        return True
