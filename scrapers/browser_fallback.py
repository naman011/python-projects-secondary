"""Headless browser fallback for JS-heavy career sites.

Uses Selenium (if installed) to render the careers page, then parses the
resulting HTML with BeautifulSoup using heuristics similar to _scrape_custom.
"""

import logging
from typing import List, Dict

from bs4 import BeautifulSoup

from utils.config import (
    SEARCH_TERMS,
    BROWSER_PAGE_LOAD_TIMEOUT,
)

logger = logging.getLogger(__name__)


class BrowserCareerFallback:
    """Optional Selenium-based fallback for career pages that need JS."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._webdriver = None

        if not self.enabled:
            return

        try:
            # Import here so selenium remains an optional dependency at import time
            from selenium import webdriver  # type: ignore
            from selenium.webdriver.chrome.options import Options  # type: ignore
            from selenium.webdriver.chrome.service import Service  # type: ignore
            from webdriver_manager.chrome import ChromeDriverManager  # type: ignore

            self._webdriver_mod = webdriver
            self._options_mod = Options
            self._service_mod = Service
            self._driver_manager_mod = ChromeDriverManager
        except Exception as e:
            logger.warning(
                "Selenium/browser fallback not available (import error): %s", e
            )
            self.enabled = False

    def _get_driver(self):
        if self._webdriver is not None:
            return self._webdriver

        if not self.enabled:
            return None

        try:
            options = self._options_mod()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            service = self._service_mod(self._driver_manager_mod().install())
            driver = self._webdriver_mod.Chrome(service=service, options=options)
            driver.set_page_load_timeout(BROWSER_PAGE_LOAD_TIMEOUT)
            self._webdriver = driver
            return driver
        except Exception as e:
            logger.warning("Failed to start headless browser: %s", e)
            self.enabled = False
            return None

    def close(self) -> None:
        if self._webdriver is not None:
            try:
                self._webdriver.quit()
            except Exception:
                pass
            self._webdriver = None

    def _extract_jobs_from_html(
        self, html: str, company_name: str, career_url: str, search_terms: List[str]
    ) -> List[Dict]:
        """Heuristic extraction of jobs from rendered HTML."""
        soup = BeautifulSoup(html, "html.parser")
        jobs: List[Dict] = []

        job_selectors = [
            'a[href*="job"]',
            'a[href*="careers"]',
            'a[href*="position"]',
            "div.job",
            "div.position",
            "div.opening",
            "li.job",
            "li.position",
            "article.job",
            '[class*="job"]',
            '[class*="career"]',
            '[class*="opening"]',
        ]

        job_elements = []
        for selector in job_selectors:
            job_elements.extend(soup.select(selector))

        seen_ids = set()
        for element in job_elements:
            elem_id = id(element)
            if elem_id in seen_ids:
                continue
            seen_ids.add(elem_id)

            # Title
            title_elem = (
                element.find(
                    ["h1", "h2", "h3", "h4", "h5", "h6"],
                    class_=lambda c: c and any(
                        k in c.lower() for k in ("title", "name", "heading")
                    ),
                )
                or element.find("span", class_=lambda c: c and "title" in c.lower())
                or element.find("a")
                or element
            )
            title = title_elem.get_text(strip=True) if title_elem else ""
            if not title or len(title) < 5:
                continue

            title_lower = title.lower()
            if not any(term.lower() in title_lower for term in search_terms):
                continue

            # URL
            link = element if element.name == "a" else element.find("a", href=True)
            job_url = career_url
            if link and link.get("href"):
                href = link["href"].strip()
                if href.startswith(("http://", "https://")):
                    job_url = href

            # Location
            loc_elem = (
                element.find(
                    ["span", "div", "p"],
                    class_=lambda c: c
                    and any(k in c.lower() for k in ("location", "city", "place")),
                )
                or element.parent.find(
                    ["span", "div"],
                    class_=lambda c: c and "location" in c.lower(),
                )
                if element.parent
                else None
            )
            location = loc_elem.get_text(strip=True) if loc_elem else ""

            # Description
            desc_elem = element.find(
                ["p", "div"],
                class_=lambda c: c
                and any(k in c.lower() for k in ("description", "summary", "details")),
            )
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            jobs.append(
                {
                    "title": title,
                    "company": company_name,
                    "location": location,
                    "url": job_url,
                    "experience": "",
                    "description": description,
                    "posted_date": "",
                    "source": company_name,
                }
            )

        return jobs

    def scrape_company(
        self,
        company_name: str,
        career_url: str,
        search_terms: List[str] = None,
    ) -> List[Dict]:
        """Use a headless browser to try to extract jobs for a single company."""
        if not self.enabled:
            return []

        if search_terms is None:
            search_terms = SEARCH_TERMS

        driver = self._get_driver()
        if driver is None:
            return []

        logger.info("Browser fallback: loading %s (%s)", company_name, career_url)
        try:
            driver.get(career_url)
        except Exception as e:
            logger.warning("Browser fallback failed to load %s: %s", career_url, e)
            return []

        # Try a simple scroll to trigger lazy-loading
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass

        try:
            html = driver.page_source
        except Exception as e:
            logger.warning("Browser fallback: could not get page_source for %s: %s", career_url, e)
            return []

        jobs = self._extract_jobs_from_html(html, company_name, career_url, search_terms)
        logger.info("Browser fallback: found %d jobs at %s", len(jobs), company_name)
        return jobs

