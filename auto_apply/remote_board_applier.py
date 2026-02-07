"""Generic handler for remote job board applications."""

import logging
from typing import Dict, Any, List
from urllib.parse import urlparse
from auto_apply.base_applier import BaseApplier
from auto_apply.selenium_fallback import SeleniumFallback
from auto_apply.profile_loader import ProfileLoader
from auto_apply.utils import detect_login_required, detect_captcha
from utils.config import (
    METHOD_API,
    METHOD_SELENIUM,
    ERROR_FORM_NOT_FOUND,
    ERROR_LOGIN_REQUIRED,
    ERROR_CAPTCHA
)

logger = logging.getLogger(__name__)


class RemoteBoardApplier(BaseApplier):
    """Generic handler for remote job board applications."""
    
    # List of remote job board domains
    REMOTE_BOARDS = [
        'remoteok.io',
        'weworkremotely.com',
        'remotive.io',
        'himalayas.app',
        'otta.com',
        'jobspresso.co',
        'dynamitejobs.com',
        'workingnomads.co',
        'remotesource.io',
        'novisajobs.com',
        'worldteams.io',
        'remoterebellion.com',
        'ycombinator.com',
        'flexa.work',
        'remote.co',
        'dailyremote.com',
        'remote.io',
        'remotehub.com',
        'remoters.me',
        'justremote.co',
        'skipthedrive.com',
        'growmotely.com',
        'remotewx.com',
        'pangian.com',
    ]
    
    def __init__(self, profile_loader: ProfileLoader):
        """Initialize remote board applier."""
        super().__init__(profile_loader)
        self.selenium_fallback = SeleniumFallback(profile_loader)
    
    def can_handle(self, job_url: str, source: str) -> bool:
        """Check if this applier can handle the URL."""
        if not job_url:
            return False
        
        parsed = urlparse(job_url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain matches any remote board
        return any(board in domain for board in self.REMOTE_BOARDS)
    
    def apply(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to remote job board job.
        
        Most remote boards have simpler application forms.
        Try API first, fall back to Selenium if needed.
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
        
        # If API failed due to form complexity, try Selenium
        if not result.get('success') and result.get('error_category') == ERROR_FORM_NOT_FOUND:
            logger.info(f"API approach failed for {job_url}, trying Selenium fallback")
            selenium_result = self.selenium_fallback.apply(job)
            return selenium_result
        
        return result
    
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
        
        # Check for CAPTCHA
        if detect_captcha(html):
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'CAPTCHA detected',
                'error_category': ERROR_CAPTCHA,
                'message': 'CAPTCHA detected. Manual intervention required or use Selenium.'
            }
        
        # Check for login requirement
        if detect_login_required(html, job_url):
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Login required',
                'error_category': ERROR_LOGIN_REQUIRED,
                'message': 'Login required to apply'
            }
        
        # Try to find application form
        form = self._find_application_form(html)
        if not form:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Application form not found',
                'error_category': ERROR_FORM_NOT_FOUND,
                'message': 'Could not locate application form'
            }
        
        # Try to extract form action and method
        form_action = form.get('action', '')
        form_method = form.get('method', 'GET').upper()
        
        if not form_action:
            # Form might use JavaScript submission
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Form uses JavaScript submission',
                'error_category': ERROR_FORM_NOT_FOUND,
                'message': 'Form requires JavaScript. Trying Selenium fallback.'
            }
        
        # Build form URL
        from urllib.parse import urljoin
        form_url = urljoin(job_url, form_action)
        
        # Extract form fields
        form_data = self._extract_form_data(form, html)
        
        # Submit form
        if form_method == 'POST':
            submit_response = self._make_request(
                form_url,
                method='POST',
                data=form_data
            )
        else:
            submit_response = self._make_request(
                form_url,
                method='GET',
                params=form_data
            )
        
        if not submit_response:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Form submission failed',
                'error_category': 'Network Error',
                'message': 'Failed to submit application form'
            }
        
        # Check response for success indicators
        response_text = submit_response.text.lower()
        success_indicators = ['thank you', 'application received', 'success', 'submitted', 'applied']
        has_success = any(indicator in response_text for indicator in success_indicators)
        
        if has_success or submit_response.status_code == 200:
            return {
                'success': True,
                'method': METHOD_API,
                'error': None,
                'error_category': None,
                'message': 'Application submitted successfully via API'
            }
        else:
            return {
                'success': False,
                'method': METHOD_API,
                'error': 'Submission status uncertain',
                'error_category': 'Unknown Error',
                'message': f'Form submitted but success not confirmed (status: {submit_response.status_code})'
            }
    
    def _extract_form_data(self, form, html: str) -> Dict[str, str]:
        """
        Extract form data to submit.
        
        Args:
            form: BeautifulSoup form element
            html: Full HTML content
            
        Returns:
            Dictionary of form field values
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        form_data = {}
        profile = self.profile_data
        
        # Find all input fields in form
        inputs = form.find_all(['input', 'textarea', 'select'])
        
        for inp in inputs:
            name = inp.get('name') or inp.get('id')
            if not name:
                continue
            
            field_type = inp.get('type', 'text').lower()
            
            # Skip submit buttons and hidden fields we don't need
            if field_type in ['submit', 'button', 'reset']:
                continue
            
            # Map common field names to profile data
            name_lower = name.lower()
            
            if 'email' in name_lower:
                form_data[name] = profile.get('email', '')
            elif 'name' in name_lower or 'fullname' in name_lower:
                form_data[name] = profile.get('full_name', '')
            elif 'first' in name_lower and 'name' in name_lower:
                form_data[name] = profile.get('first_name', '')
            elif 'last' in name_lower and 'name' in name_lower:
                form_data[name] = profile.get('last_name', '')
            elif 'phone' in name_lower or 'tel' in name_lower:
                form_data[name] = profile.get('phone', '')
            elif 'location' in name_lower or 'city' in name_lower:
                form_data[name] = profile.get('location', '')
            elif 'linkedin' in name_lower:
                form_data[name] = profile.get('linkedin_url', '')
            elif 'github' in name_lower or 'portfolio' in name_lower:
                form_data[name] = profile.get('github_url', '')
            elif 'resume' in name_lower or 'cv' in name_lower:
                # File uploads need special handling
                continue
            elif 'cover' in name_lower or 'letter' in name_lower or 'message' in name_lower:
                # Use cover letter if available
                cover_letter = self.profile_loader.get_cover_letter_text(
                    job.get('company', ''),
                    job.get('title', '')
                )
                form_data[name] = cover_letter
            elif 'experience' in name_lower or 'years' in name_lower:
                form_data[name] = str(profile.get('years_of_experience', ''))
            elif 'skills' in name_lower:
                form_data[name] = profile.get('skills', '')
            else:
                # Use default value if present
                default_value = inp.get('value', '')
                if default_value:
                    form_data[name] = default_value
        
        return form_data
