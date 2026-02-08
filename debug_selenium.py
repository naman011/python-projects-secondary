#!/usr/bin/env python3
"""Debug script to see what Selenium sees on a job page."""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from auto_apply.utils import get_random_user_agent

def debug_job_page(job_url: str, headless: bool = False):
    """Debug what Selenium sees on a job page."""
    
    print("=" * 80)
    print(f"DEBUGGING JOB PAGE: {job_url}")
    print("=" * 80)
    print()
    
    # Setup driver
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("1. Loading page...")
        driver.get(job_url)
        print(f"   ✅ Page loaded")
        print(f"   Current URL: {driver.current_url}")
        print()
        
        # Wait a bit for dynamic content
        print("2. Waiting for dynamic content (5 seconds)...")
        time.sleep(5)
        print()
        
        # Check page title
        print("3. Page Information:")
        print(f"   Title: {driver.title[:80]}")
        print(f"   URL: {driver.current_url}")
        print()
        
        # Check for login requirements
        print("4. Checking for login requirements...")
        page_source_lower = driver.page_source.lower()
        login_indicators = [
            'sign in', 'log in', 'login', 'create account', 'register',
            'you must be logged in', 'please sign in'
        ]
        found_login = [ind for ind in login_indicators if ind in page_source_lower]
        if found_login:
            print(f"   ⚠️  LOGIN REQUIRED - Found indicators: {found_login[:3]}")
        else:
            print("   ✅ No obvious login requirement")
        print()
        
        # Check for redirects
        if driver.current_url != job_url:
            print(f"   ⚠️  PAGE REDIRECTED")
            print(f"   Original: {job_url[:60]}")
            print(f"   Current:  {driver.current_url[:60]}")
        print()
        
        # Find all form elements
        print("5. Searching for form elements...")
        forms = driver.find_elements(By.TAG_NAME, 'form')
        print(f"   Found {len(forms)} <form> elements")
        
        if forms:
            for i, form in enumerate(forms, 1):
                print(f"\n   Form {i}:")
                form_id = form.get_attribute('id') or 'no-id'
                form_action = form.get_attribute('action') or 'no-action'
                form_method = form.get_attribute('method') or 'GET'
                print(f"      ID: {form_id}")
                print(f"      Action: {form_action[:60]}")
                print(f"      Method: {form_method}")
                
                # Find all inputs in this form
                inputs = form.find_elements(By.TAG_NAME, 'input')
                textareas = form.find_elements(By.TAG_NAME, 'textarea')
                selects = form.find_elements(By.TAG_NAME, 'select')
                
                print(f"      Inputs: {len(inputs)}")
                for inp in inputs[:10]:  # Show first 10
                    inp_type = inp.get_attribute('type') or 'text'
                    inp_name = inp.get_attribute('name') or 'no-name'
                    inp_id = inp.get_attribute('id') or 'no-id'
                    inp_placeholder = inp.get_attribute('placeholder') or ''
                    print(f"         - type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder[:30]}")
                
                if len(inputs) > 10:
                    print(f"         ... and {len(inputs) - 10} more inputs")
                
                print(f"      Textareas: {len(textareas)}")
                print(f"      Selects: {len(selects)}")
        else:
            print("   ❌ No <form> elements found")
        
        print()
        
        # Find all input elements (even outside forms)
        print("6. Searching for ALL input elements on page...")
        all_inputs = driver.find_elements(By.TAG_NAME, 'input')
        print(f"   Found {len(all_inputs)} total <input> elements")
        
        if all_inputs:
            print("\n   Input fields found:")
            for inp in all_inputs[:20]:  # Show first 20
                inp_type = inp.get_attribute('type') or 'text'
                inp_name = inp.get_attribute('name') or ''
                inp_id = inp.get_attribute('id') or ''
                inp_class = inp.get_attribute('class') or ''
                inp_placeholder = inp.get_attribute('placeholder') or ''
                
                # Only show visible inputs
                try:
                    if inp.is_displayed():
                        print(f"      - type={inp_type:10} name={inp_name:20} id={inp_id:20} placeholder={inp_placeholder[:30]}")
                except:
                    pass
        
        print()
        
        # Check for iframes
        print("7. Checking for iframes...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"   Found {len(iframes)} iframes")
        if iframes:
            print("   ⚠️  Forms might be inside iframes!")
            for i, iframe in enumerate(iframes[:5], 1):
                iframe_src = iframe.get_attribute('src') or 'no-src'
                print(f"      Iframe {i}: {iframe_src[:60]}")
        print()
        
        # Take screenshot
        print("8. Taking screenshot...")
        screenshot_path = f"debug_screenshot_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        print(f"   ✅ Screenshot saved: {screenshot_path}")
        print()
        
        # Check page source for common patterns
        print("9. Analyzing page content...")
        page_text = driver.page_source.lower()
        
        # Check for common application-related text
        application_keywords = [
            'apply', 'application', 'submit', 'resume', 'cv', 'cover letter',
            'phone', 'email', 'name', 'experience', 'skills'
        ]
        found_keywords = [kw for kw in application_keywords if kw in page_text]
        print(f"   Found keywords: {found_keywords[:10]}")
        print()
        
        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Forms found: {len(forms)}")
        print(f"Total inputs: {len(all_inputs)}")
        print(f"Iframes: {len(iframes)}")
        print(f"Login required: {'Yes' if found_login else 'No'}")
        print(f"Redirected: {'Yes' if driver.current_url != job_url else 'No'}")
        print()
        
        if len(forms) == 0 and len(all_inputs) == 0:
            print("❌ ISSUE: No forms or input fields found!")
            print("   Possible reasons:")
            print("   - Page requires login")
            print("   - Page redirected to external site")
            print("   - Form is loaded via JavaScript (needs more wait time)")
            print("   - Form is in an iframe")
        elif len(forms) == 0 and len(all_inputs) > 0:
            print("⚠️  Inputs found but no <form> tag")
            print("   Form might be submitted via JavaScript")
        else:
            print("✅ Forms found - check selectors above")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 debug_selenium.py <job_url> [headless]")
        print("Example: python3 debug_selenium.py 'https://in.indeed.com/viewjob?jk=...'")
        sys.exit(1)
    
    job_url = sys.argv[1]
    headless = len(sys.argv) > 2 and sys.argv[2].lower() == 'headless'
    
    debug_job_page(job_url, headless=headless)
