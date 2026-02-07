"""Selenium-based fallback for complex job application forms."""

import os
import time
import random
import logging
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from auto_apply.profile_loader import ProfileLoader
from auto_apply.utils import human_like_delay, get_random_user_agent
from utils.config import SELENIUM_ENABLED, BROWSER_PAGE_LOAD_TIMEOUT

logger = logging.getLogger(__name__)


class SeleniumFallback:
    """Selenium-based application handler for complex forms."""
    
    def __init__(self, profile_loader: ProfileLoader):
        """
        Initialize Selenium fallback.
        
        Args:
            profile_loader: ProfileLoader instance
        """
        self.profile_loader = profile_loader
        self.profile_data = profile_loader.get_form_data()
        self.driver: Optional[webdriver.Chrome] = None
        self.screenshot_dir = "data/application_logs/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def _setup_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Setup Chrome WebDriver.
        
        Args:
            headless: Run browser in headless mode
            
        Returns:
            Configured Chrome WebDriver
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and CSS for faster loading (optional)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            driver.set_page_load_timeout(BROWSER_PAGE_LOAD_TIMEOUT)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def _take_screenshot(self, filename: str) -> str:
        """
        Take screenshot of current page.
        
        Args:
            filename: Screenshot filename
            
        Returns:
            Path to screenshot file
        """
        if not self.driver:
            return ""
        
        try:
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            self.driver.save_screenshot(screenshot_path)
            return screenshot_path
        except Exception as e:
            logger.warning(f"Failed to take screenshot: {e}")
            return ""
    
    def _human_like_type(self, element, text: str):
        """
        Type text in a human-like manner.
        
        Args:
            element: Selenium WebElement
            text: Text to type
        """
        element.clear()
        for char in text:
            element.send_keys(char)
            human_like_delay(0.05, 0.02)  # Small delay between keystrokes
    
    def _find_and_fill_field(
        self,
        field_name: str,
        value: str,
        field_type: str = 'text',
        selectors: Optional[list] = None
    ) -> bool:
        """
        Find and fill a form field.
        
        Args:
            field_name: Name or ID of field
            value: Value to fill
            field_type: Type of field (text, select, etc.)
            selectors: List of CSS selectors to try
            
        Returns:
            True if field was found and filled
        """
        if not self.driver:
            return False
        
        if not selectors:
            # Default selectors to try
            selectors = [
                f'input[name="{field_name}"]',
                f'input[id="{field_name}"]',
                f'textarea[name="{field_name}"]',
                f'textarea[id="{field_name}"]',
                f'select[name="{field_name}"]',
                f'select[id="{field_name}"]',
                f'#{field_name}',
                f'[name="{field_name}"]',
            ]
        
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                human_like_delay(0.3, 0.2)
                
                if field_type == 'select':
                    select = Select(element)
                    try:
                        select.select_by_value(value)
                    except:
                        try:
                            select.select_by_visible_text(value)
                        except:
                            return False
                else:
                    # Click first to focus
                    element.click()
                    human_like_delay(0.2, 0.1)
                    self._human_like_type(element, value)
                
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        return False
    
    def _upload_resume(self, resume_path: str, selectors: Optional[list] = None) -> bool:
        """
        Upload resume file.
        
        Args:
            resume_path: Path to resume file
            selectors: List of CSS selectors for file input
            
        Returns:
            True if upload was successful
        """
        if not self.driver or not os.path.exists(resume_path):
            return False
        
        if not selectors:
            selectors = [
                'input[type="file"]',
                'input[accept*="pdf"]',
                'input[accept*="doc"]',
                'input[name*="resume"]',
                'input[id*="resume"]',
                'input[name*="cv"]',
                'input[id*="cv"]',
            ]
        
        for selector in selectors:
            try:
                file_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                file_input.send_keys(os.path.abspath(resume_path))
                human_like_delay(0.5, 0.2)
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        
        return False
    
    def _click_submit_button(self, selectors: Optional[list] = None) -> bool:
        """
        Click submit/apply button.
        
        Args:
            selectors: List of CSS selectors for submit button
            
        Returns:
            True if button was clicked
        """
        if not self.driver:
            return False
        
        if not selectors:
            selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Apply")',
                'button:contains("Submit")',
                'a:contains("Apply")',
                '[class*="apply"]',
                '[id*="apply"]',
                '[class*="submit"]',
                '[id*="submit"]',
            ]
        
        for selector in selectors:
            try:
                # Try XPath for text-based selection
                if ':contains(' in selector:
                    xpath = f"//button[contains(text(), 'Apply')] | //button[contains(text(), 'Submit')]"
                    try:
                        button = self.driver.find_element(By.XPATH, xpath)
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        human_like_delay(0.3, 0.2)
                        button.click()
                        return True
                    except:
                        continue
                else:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    human_like_delay(0.3, 0.2)
                    button.click()
                    return True
            except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
                continue
        
        return False
    
    def apply(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to job using Selenium.
        
        Args:
            job: Job dictionary
            
        Returns:
            Application result dictionary
        """
        if not SELENIUM_ENABLED:
            return {
                'success': False,
                'method': 'Selenium',
                'error': 'Selenium is disabled',
                'error_category': 'Configuration',
                'message': 'Selenium fallback is disabled in configuration'
            }
        
        job_url = job.get('url', '')
        if not job_url:
            return {
                'success': False,
                'method': 'Selenium',
                'error': 'No job URL provided',
                'error_category': 'Invalid Data',
                'message': 'Job URL is required'
            }
        
        try:
            self.driver = self._setup_driver(headless=True)
            self.driver.get(job_url)
            
            # Wait for page to load
            time.sleep(2 + random.uniform(0, 2))
            
            # Take initial screenshot
            screenshot_file = f"application_{job.get('company', 'unknown').replace(' ', '_')}_{int(time.time())}.png"
            self._take_screenshot(screenshot_file)
            
            # Try to fill common form fields
            filled_fields = 0
            
            # Name fields
            if self._find_and_fill_field('name', self.profile_data.get('full_name', '')):
                filled_fields += 1
            if self._find_and_fill_field('first_name', self.profile_data.get('first_name', '')):
                filled_fields += 1
            if self._find_and_fill_field('last_name', self.profile_data.get('last_name', '')):
                filled_fields += 1
            
            # Contact fields
            if self._find_and_fill_field('email', self.profile_data.get('email', ''), 'email'):
                filled_fields += 1
            if self._find_and_fill_field('phone', self.profile_data.get('phone', ''), 'tel'):
                filled_fields += 1
            
            # Resume upload
            resume_path = self.profile_data.get('resume_path')
            if resume_path:
                self._upload_resume(resume_path)
            
            # Check if we found any fields
            if filled_fields == 0:
                return {
                    'success': False,
                    'method': 'Selenium',
                    'error': 'No form fields found',
                    'error_category': 'Form Not Found',
                    'message': 'Could not locate application form fields',
                    'screenshot': screenshot_file
                }
            
            # Try to submit
            human_like_delay(1, 0.5)
            if self._click_submit_button():
                # Wait a bit to see if submission was successful
                time.sleep(3)
                
                # Take final screenshot
                final_screenshot = f"submitted_{screenshot_file}"
                self._take_screenshot(final_screenshot)
                
                # Check for success indicators
                current_url = self.driver.current_url
                page_source = self.driver.page_source.lower()
                
                success_indicators = ['thank you', 'application received', 'success', 'submitted']
                has_success = any(indicator in page_source for indicator in success_indicators)
                
                return {
                    'success': has_success,
                    'method': 'Selenium',
                    'error': None if has_success else 'Submission uncertain',
                    'error_category': None if has_success else 'Unknown Error',
                    'message': 'Application submitted via Selenium' if has_success else 'Application submitted but status uncertain',
                    'screenshot': final_screenshot,
                    'filled_fields': filled_fields
                }
            else:
                return {
                    'success': False,
                    'method': 'Selenium',
                    'error': 'Could not find submit button',
                    'error_category': 'Form Not Found',
                    'message': 'Form fields filled but submit button not found',
                    'screenshot': screenshot_file,
                    'filled_fields': filled_fields
                }
        
        except WebDriverException as e:
            logger.error(f"Selenium error: {e}")
            return {
                'success': False,
                'method': 'Selenium',
                'error': str(e),
                'error_category': 'Unknown Error',
                'message': f'Selenium error: {e}'
            }
        except Exception as e:
            logger.error(f"Unexpected error in Selenium fallback: {e}")
            return {
                'success': False,
                'method': 'Selenium',
                'error': str(e),
                'error_category': 'Unknown Error',
                'message': f'Unexpected error: {e}'
            }
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
