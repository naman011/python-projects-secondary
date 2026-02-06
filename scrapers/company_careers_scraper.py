"""Company career pages scraper - PRIMARY SOURCE."""

import json
import os
import re
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.browser_fallback import BrowserCareerFallback
from utils.config import (
    SEARCH_TERMS,
    USE_BROWSER_FALLBACK,
    BROWSER_MAX_COMPANIES,
)
from utils.failure_reporter import FailureReporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyCareersScraper(BaseScraper):
    """Scraper for company career pages - most reliable source."""
    
    def __init__(self, companies_file: str = "data/companies.json"):
        """
        Initialize the company careers scraper.
        
        Args:
            companies_file: Path to companies JSON file
        """
        super().__init__()
        # Validate and normalize file path to prevent path traversal
        if not companies_file or not isinstance(companies_file, str):
            companies_file = "data/companies.json"
        # Normalize path and ensure it's within project directory
        companies_file = os.path.normpath(companies_file)
        if companies_file.startswith('..') or os.path.isabs(companies_file):
            logger.warning(f"Invalid companies file path: {companies_file}. Using default.")
            companies_file = "data/companies.json"
        self.companies_file = companies_file
        self.companies = self._load_companies()
        self.failures: List[Dict] = []
        self.failure_reporter = FailureReporter()
        self.browser_fallback = BrowserCareerFallback(enabled=USE_BROWSER_FALLBACK)
        self._browser_companies_used = 0
    
    def _load_companies(self) -> Dict:
        """Load companies from JSON file."""
        try:
            if not os.path.exists(self.companies_file):
                logger.error(f"Companies file not found: {self.companies_file}")
                return {}
            with open(self.companies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.error("Companies file does not contain a valid dictionary")
                    return {}
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing companies JSON file: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading companies file: {e}")
            return {}
    
    def _extract_text(self, element) -> str:
        """Extract text from BeautifulSoup element."""
        if element:
            return element.get_text(strip=True)
        return ""
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalize URL to absolute URL with validation."""
        if not url or not isinstance(url, str):
            return ""
        
        url = url.strip()
        if not url:
            return ""
        
        # Already absolute URL
        if url.startswith(('http://', 'https://')):
            # Basic validation
            try:
                parsed = urlparse(url)
                if parsed.netloc:  # Has a valid domain
                    return url
            except Exception:
                pass
            return ""
        
        # Validate base_url
        if not base_url or not isinstance(base_url, str):
            return ""
        
        try:
            # Use urljoin for proper URL joining
            absolute_url = urljoin(base_url, url)
            # Validate the result
            parsed = urlparse(absolute_url)
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                return absolute_url
        except Exception as e:
            logger.warning(f"Error normalizing URL {url} with base {base_url}: {e}")
        
        return ""
    
    def _scrape_greenhouse(self, company_name: str, career_url: str, search_terms: List[str]) -> List[Dict]:
        """
        Scrape Greenhouse-based career pages.
        
        Args:
            company_name: Company name
            career_url: Career page URL
            search_terms: Search terms to filter jobs
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Greenhouse API endpoint
            # Try to find the board token from the page
            response = self.get(career_url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for Greenhouse board token
            script_tags = soup.find_all('script')
            board_token = None
            
            for script in script_tags:
                if script.string:
                    # Look for board token in script
                    match = re.search(r'boardToken["\']?\s*[:=]\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        board_token = match.group(1)
                        break
            
            if not board_token:
                # Try alternative: look for data attributes or API calls
                # Many Greenhouse sites use /api/v1/boards/{board}/jobs
                # Try to extract from page structure
                api_match = re.search(r'/api/v1/boards/([^/]+)', response.text)
                if api_match:
                    board_token = api_match.group(1)
            
            if board_token:
                # Fetch jobs from Greenhouse API
                api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
                api_response = self.get(api_url)
                
                if api_response:
                    try:
                        data = api_response.json()
                        if not isinstance(data, dict):
                            raise ValueError("Invalid API response format")
                        for job in data.get('jobs', []):
                            if not isinstance(job, dict):
                                continue
                            title = str(job.get('title', '')).strip()
                            if not title:
                                continue
                            locations = job.get('locations', [])
                            if isinstance(locations, list):
                                location = ', '.join([str(loc.get('name', '')) for loc in locations if isinstance(loc, dict)])
                            else:
                                location = ''
                            job_url = str(job.get('absolute_url', '')).strip()
                            
                            # Check if job matches search terms
                            title_lower = title.lower()
                            if any(term.lower() in title_lower for term in search_terms):
                                jobs.append({
                                    'title': title,
                                    'company': str(company_name),
                                    'location': location,
                                    'url': job_url,
                                    'experience': '',
                                    'description': str(job.get('content', '')),
                                    'posted_date': '',
                                    'source': str(company_name)
                                })
                    except (json.JSONDecodeError, ValueError, KeyError) as e:
                        logger.warning(f"Error parsing Greenhouse API for {company_name}: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error parsing Greenhouse API for {company_name}: {e}")
            
            # Fallback: scrape HTML directly
            if not jobs:
                job_elements = soup.find_all(['a', 'div'], class_=re.compile(r'job|position|opening', re.I))
                
                for element in job_elements:
                    title_elem = element.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'title|name', re.I))
                    if not title_elem:
                        title_elem = element
                    
                    title = self._extract_text(title_elem)
                    if not title:
                        continue
                    
                    # Check if matches search terms
                    title_lower = title.lower()
                    if not any(term.lower() in title_lower for term in search_terms):
                        continue
                    
                    # Extract location
                    location_elem = element.find(['span', 'div'], class_=re.compile(r'location', re.I))
                    location = self._extract_text(location_elem) if location_elem else ''
                    
                    # Extract URL
                    link = element.find('a', href=True) if element.name != 'a' else element
                    if link and link.get('href'):
                        job_url = self._normalize_url(link['href'], career_url)
                    else:
                        job_url = career_url
                    
                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'url': job_url,
                        'experience': '',
                        'description': '',
                        'posted_date': '',
                        'source': company_name
                    })
        
        except Exception as e:
            logger.error(f"Error scraping Greenhouse for {company_name}: {e}")
        
        return jobs
    
    def _scrape_lever(self, company_name: str, career_url: str, search_terms: List[str]) -> List[Dict]:
        """
        Scrape Lever-based career pages.
        
        Args:
            company_name: Company name
            career_url: Career page URL
            search_terms: Search terms to filter jobs
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Lever API endpoint
            # Extract team from URL or try common patterns
            response = self.get(career_url)
            if not response:
                return jobs
            
            # Try Lever API
            api_url = career_url.rstrip('/') + '/api/postings'
            api_response = self.get(api_url)
            
            if api_response:
                try:
                    data = api_response.json()
                    if not isinstance(data, list):
                        raise ValueError("Invalid API response format")
                    for job in data:
                        if not isinstance(job, dict):
                            continue
                        title = str(job.get('text', '')).strip()
                        if not title:
                            continue
                        categories = job.get('categories', {})
                        if isinstance(categories, dict):
                            locations = categories.get('location', [])
                            if isinstance(locations, list):
                                location = ', '.join([str(loc) for loc in locations])
                            else:
                                location = ''
                        else:
                            location = ''
                        job_url = str(job.get('hostedUrl', '') or job.get('applyUrl', '')).strip()
                        if job_url and not job_url.startswith('http'):
                            job_url = self._normalize_url(job_url, career_url)
                        
                        title_lower = title.lower()
                        if any(term.lower() in title_lower for term in search_terms):
                            jobs.append({
                                'title': title,
                                'company': str(company_name),
                                'location': location,
                                'url': job_url,
                                'experience': '',
                                'description': str(job.get('descriptionPlain', '')),
                                'posted_date': str(job.get('createdAt', '')),
                                'source': str(company_name)
                            })
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"Error parsing Lever API for {company_name}: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error parsing Lever API for {company_name}: {e}")
            
            # Fallback: scrape HTML
            if not jobs:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_elements = soup.find_all(['a', 'div'], class_=re.compile(r'posting|job', re.I))
                
                for element in job_elements:
                    title_elem = element.find(['h3', 'h4', 'h5', 'span'], class_=re.compile(r'title|name', re.I))
                    if not title_elem:
                        title_elem = element
                    
                    title = self._extract_text(title_elem)
                    if not title:
                        continue
                    
                    title_lower = title.lower()
                    if not any(term.lower() in title_lower for term in search_terms):
                        continue
                    
                    location_elem = element.find(['span', 'div'], class_=re.compile(r'location', re.I))
                    location = self._extract_text(location_elem) if location_elem else ''
                    
                    link = element.find('a', href=True) if element.name != 'a' else element
                    if link and link.get('href'):
                        job_url = self._normalize_url(link['href'], career_url)
                    else:
                        job_url = career_url
                    
                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'url': job_url,
                        'experience': '',
                        'description': '',
                        'posted_date': '',
                        'source': company_name
                    })
        
        except Exception as e:
            logger.error(f"Error scraping Lever for {company_name}: {e}")
        
        return jobs
    
    def _scrape_custom(self, company_name: str, career_url: str, search_terms: List[str]) -> List[Dict]:
        """
        Scrape custom HTML career pages.
        
        Args:
            company_name: Company name
            career_url: Career page URL
            search_terms: Search terms to filter jobs
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            response = self.get(career_url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common patterns for job listings
            # Look for links, divs, or list items that might contain jobs
            job_selectors = [
                'a[href*="job"]',
                'a[href*="career"]',
                'a[href*="position"]',
                'div.job',
                'div.position',
                'div.opening',
                'li.job',
                'li.position',
                'article.job',
                '[class*="job"]',
                '[class*="position"]',
                '[class*="opening"]',
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                job_elements.extend(elements)
            
            # Remove duplicates
            seen = set()
            unique_elements = []
            for elem in job_elements:
                elem_id = id(elem)
                if elem_id not in seen:
                    seen.add(elem_id)
                    unique_elements.append(elem)
            
            for element in unique_elements:
                # Extract title
                title_elem = (
                    element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], class_=re.compile(r'title|name|heading', re.I)) or
                    element.find('span', class_=re.compile(r'title|name', re.I)) or
                    element.find('a') or
                    element
                )
                
                title = self._extract_text(title_elem)
                if not title or len(title) < 5:  # Skip very short titles
                    continue
                
                # Check if matches search terms
                title_lower = title.lower()
                if not any(term.lower() in title_lower for term in search_terms):
                    continue
                
                # Extract location
                location = ''
                location_elem = element.find(['span', 'div', 'p'], class_=re.compile(r'location|city|place', re.I))
                if location_elem:
                    location = self._extract_text(location_elem)
                else:
                    # Try to find location in nearby elements
                    parent = element.parent
                    if parent:
                        loc_elem = parent.find(['span', 'div'], class_=re.compile(r'location', re.I))
                        if loc_elem:
                            location = self._extract_text(loc_elem)
                
                # Extract URL
                link = element if element.name == 'a' else element.find('a', href=True)
                if link and link.get('href'):
                    job_url = self._normalize_url(link['href'], career_url)
                else:
                    job_url = career_url
                
                # Extract description if available
                desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|summary', re.I))
                description = self._extract_text(desc_elem) if desc_elem else ''
                
                jobs.append({
                    'title': title,
                    'company': company_name,
                    'location': location,
                    'url': job_url,
                    'experience': '',
                    'description': description,
                    'posted_date': '',
                    'source': company_name
                })
        
        except Exception as e:
            logger.error(f"Error scraping custom page for {company_name}: {e}")
        
        return jobs
    
    def scrape_company(self, company_name: str, company_info: Dict) -> List[Dict]:
        """
        Scrape jobs from a single company.
        
        Args:
            company_name: Company name
            company_info: Company information dictionary
            
        Returns:
            List of job dictionaries
        """
        if not company_name or not isinstance(company_name, str):
            return []
        
        if not company_info or not isinstance(company_info, dict):
            return []
        
        career_url = str(company_info.get('career_url', '')).strip()
        scraper_type = str(company_info.get('scraper_type', 'custom')).lower()
        search_terms = company_info.get('search_terms', SEARCH_TERMS)
        
        if not career_url or not career_url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid career URL for {company_name}: {career_url}")
            self.failures.append(
                {
                    "company": company_name,
                    "career_url": career_url,
                    "scraper_type": scraper_type,
                    "stage": "validate",
                    "error": "invalid_career_url",
                }
            )
            return []
        
        if not isinstance(search_terms, list):
            search_terms = SEARCH_TERMS
        
        logger.info(f"Scraping {company_name} ({scraper_type})...")
        
        try:
            if scraper_type == 'greenhouse':
                return self._scrape_greenhouse(company_name, career_url, search_terms)
            elif scraper_type == 'lever':
                return self._scrape_lever(company_name, career_url, search_terms)
            elif scraper_type == 'workday':
                # Workday is complex, treat as custom for now
                return self._scrape_custom(company_name, career_url, search_terms)
            else:
                return self._scrape_custom(company_name, career_url, search_terms)
        except Exception as e:
            logger.error(f"Error in scrape_company for {company_name}: {e}")
            self.failures.append(
                {
                    "company": company_name,
                    "career_url": career_url,
                    "scraper_type": scraper_type,
                    "stage": "scrape",
                    "error": str(e),
                }
            )
            return []

    def scrape_company_with_fallback(
        self, company_name: str, company_info: Dict
    ) -> List[Dict]:
        """Scrape a company, and if no jobs via HTML, optionally try browser fallback."""
        jobs = self.scrape_company(company_name, company_info)

        # If we already have jobs or browser fallback is disabled/exhausted, return.
        if jobs or not self.browser_fallback.enabled:
            return jobs

        if self._browser_companies_used >= BROWSER_MAX_COMPANIES:
            return jobs

        career_url = str(company_info.get("career_url", "")).strip()
        scraper_type = str(company_info.get("scraper_type", "custom")).lower()
        search_terms = company_info.get("search_terms", SEARCH_TERMS)

        # Basic sanity check
        if not career_url.startswith(("http://", "https://")):
            return jobs

        try:
            self._browser_companies_used += 1
            browser_jobs = self.browser_fallback.scrape_company(
                company_name, career_url, search_terms
            )
            if browser_jobs:
                # Mark previous zero_jobs failure, if any, as browser_success
                for item in self.failures:
                    if (
                        item.get("company") == company_name
                        and item.get("stage") == "result"
                        and item.get("error") == "zero_jobs"
                    ):
                        item["error"] = "browser_success"
                return browser_jobs
        except Exception as e:
            logger.warning(
                "Browser fallback failed for %s (%s): %s", company_name, career_url, e
            )
            self.failures.append(
                {
                    "company": company_name,
                    "career_url": career_url,
                    "scraper_type": scraper_type,
                    "stage": "browser",
                    "error": str(e),
                }
            )

        return jobs
    
    def scrape(self) -> List[Dict]:
        """
        Scrape jobs from all companies.
        
        Returns:
            List of all job dictionaries
        """
        all_jobs = []
        
        for company_name, company_info in self.companies.items():
            try:
                jobs = self.scrape_company_with_fallback(company_name, company_info)
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs at {company_name}")
                if len(jobs) == 0:
                    # record a soft failure so you can tune URLs/scraper types later
                    self.failures.append(
                        {
                            "company": company_name,
                            "career_url": str(company_info.get("career_url", "")),
                            "scraper_type": str(company_info.get("scraper_type", "")),
                            "stage": "result",
                            "error": "zero_jobs",
                        }
                    )
            except Exception as e:
                logger.error(f"Error scraping {company_name}: {e}")
                self.failures.append(
                    {
                        "company": company_name,
                        "career_url": str(company_info.get("career_url", "")),
                        "scraper_type": str(company_info.get("scraper_type", "")),
                        "stage": "loop",
                        "error": str(e),
                    }
                )
                continue
        
        try:
            self.failure_reporter.write(self.failures)
            logger.info(f"Wrote failure report: {self.failure_reporter.output_file}")
        except Exception as e:
            logger.warning(f"Failed writing failure report: {e}")
        
        return all_jobs
