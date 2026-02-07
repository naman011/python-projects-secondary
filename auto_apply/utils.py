"""Utility functions for auto-apply module."""

import time
import random
import logging
from typing import Optional, Dict, Any
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

# Initialize user agent generator
ua = UserAgent()


def random_delay(min_seconds: float, max_seconds: float):
    """
    Sleep for a random duration between min and max seconds.
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def get_random_user_agent() -> str:
    """
    Get a random user agent string.
    
    Returns:
        Random user agent string
    """
    try:
        return ua.random
    except Exception:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def human_like_delay(base_delay: float = 0.5, variance: float = 0.3):
    """
    Add a human-like delay with some variance.
    
    Args:
        base_delay: Base delay in seconds
        variance: Variance factor (0-1)
    """
    delay = base_delay + random.uniform(-base_delay * variance, base_delay * variance)
    delay = max(0.1, delay)  # Ensure minimum delay
    time.sleep(delay)


def extract_form_fields(html: str) -> Dict[str, Any]:
    """
    Extract form fields from HTML.
    
    Args:
        html: HTML content
        
    Returns:
        Dictionary of form fields
    """
    from bs4 import BeautifulSoup
    
    form_fields = {}
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all input fields
    inputs = soup.find_all(['input', 'textarea', 'select'])
    for inp in inputs:
        name = inp.get('name') or inp.get('id')
        if name:
            field_type = inp.get('type', 'text')
            form_fields[name] = {
                'type': field_type,
                'required': inp.has_attr('required'),
                'value': inp.get('value', ''),
                'placeholder': inp.get('placeholder', '')
            }
    
    return form_fields


def detect_captcha(html: str) -> bool:
    """
    Detect if page contains CAPTCHA.
    
    Args:
        html: HTML content
        
    Returns:
        True if CAPTCHA is detected
    """
    captcha_indicators = [
        'captcha',
        'recaptcha',
        'hcaptcha',
        'cloudflare',
        'challenge',
        'verify you are human'
    ]
    
    html_lower = html.lower()
    return any(indicator in html_lower for indicator in captcha_indicators)


def detect_login_required(html: str, url: str) -> bool:
    """
    Detect if login is required to apply.
    
    Args:
        html: HTML content
        url: Page URL
        
    Returns:
        True if login appears to be required
    """
    login_indicators = [
        'sign in',
        'log in',
        'login',
        'create account',
        'register',
        'authentication required'
    ]
    
    html_lower = html.lower()
    url_lower = url.lower()
    
    # Check for login indicators
    has_login_text = any(indicator in html_lower for indicator in login_indicators)
    
    # Check URL for login paths
    login_paths = ['/login', '/signin', '/auth', '/account']
    has_login_path = any(path in url_lower for path in login_paths)
    
    return has_login_text or has_login_path


def format_phone_number(phone: str) -> str:
    """
    Format phone number for form submission.
    
    Args:
        phone: Phone number string
        
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format based on length
    if len(digits) >= 10:
        # Assume Indian format: +91-XXXXXXXXXX
        if digits.startswith('91') and len(digits) == 12:
            return f"+{digits[:2]}-{digits[2:]}"
        elif len(digits) == 10:
            return f"+91-{digits}"
        else:
            return phone  # Return as-is if can't format
    
    return phone


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address
        
    Returns:
        True if email appears valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
