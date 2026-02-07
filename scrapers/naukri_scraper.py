"""Naukri.com job scraper."""

import re
import logging
from typing import List, Dict
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NaukriScraper(BaseScraper):
    """Scraper for Naukri.com jobs."""
    
    def __init__(self):
        """Initialize Naukri scraper."""
        super().__init__()
        self.base_url = "https://www.naukri.com"
    
    def scrape(self, keywords: List[str] = None, experience: str = "0-3", location: str = "india", max_results: int = 100) -> List[Dict]:
        """
        Scrape jobs from Naukri.com.
        
        Args:
            keywords: List of search keywords (default: SEARCH_TERMS)
            experience: Experience range (default: 0-3 for fresher–3 years)
            location: Location to search (default: india)
            max_results: Maximum number of results to fetch
            
        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = SEARCH_TERMS
        
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_jobs(keyword, experience, location, max_results)
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs for '{keyword}' in '{location}' on Naukri")
            except Exception as e:
                logger.error(f"Error scraping Naukri for '{keyword}' in '{location}': {e}")
                continue
        
        return all_jobs
    
    def _search_jobs(self, keyword: str, experience: str, location: str, max_results: int) -> List[Dict]:
        """Search for jobs with a specific keyword."""
        jobs = []
        
        # Naukri job search URL - try multiple URL patterns
        params = {
            'k': keyword,
            'l': location.lower(),
            'experience': experience,
            'functionAreaIdGid': '8',  # IT Software
        }
        
        # Try different URL patterns
        url_patterns = [
            f"{self.base_url}/jobs-search?{urlencode(params)}",
            f"{self.base_url}/jobapi/v3/search?{urlencode(params)}",
        ]
        
        response = None
        for url in url_patterns:
            try:
                # Use more realistic headers
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.naukri.com/',
                }
                response = self.get(url, headers=headers)
                if response and response.status_code == 200:
                    break
            except Exception as e:
                logger.debug(f"Naukri: Failed to fetch {url}: {e}")
                continue
        
        if not response:
            logger.warning(f"Naukri: No response for keyword '{keyword}'")
            return jobs
        
        # Check if blocked or redirected
        if hasattr(response, 'url') and response.url:
            if 'login' in response.url.lower() or 'blocked' in response.url.lower():
                logger.warning(f"Naukri: Redirected to login/blocked for keyword '{keyword}'")
                return jobs
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Naukri job listing selectors - try multiple patterns
            job_cards = (
                soup.find_all('article', class_=re.compile(r'jobTuple|jobCard', re.I)) or
                soup.find_all('div', class_=re.compile(r'jobTuple|jobCard|row', re.I)) or
                soup.find_all('div', {'data-job-id': True}) or
                soup.find_all(['div', 'article'], class_=re.compile(r'job|tuple|row', re.I))
            )
            
            # Diagnostic: log what we found
            if len(job_cards) == 0:
                logger.debug(f"Naukri: Found 0 job cards for '{keyword}'. Response length: {len(response.text)} chars")
                # Check for common Naukri structures
                if soup.find('div', class_=re.compile(r'noResults|no-jobs', re.I)):
                    logger.debug(f"Naukri: No results message found for '{keyword}'")
                all_articles = soup.find_all('article')
                logger.debug(f"Naukri: Total articles in page: {len(all_articles)}")
            
            for card in job_cards:
                try:
                    # Extract job title - try multiple selectors
                    title_elem = (
                        card.find('a', class_=re.compile(r'title|jobTitle|job.*title', re.I)) or
                        card.find('a', title=True) or
                        card.find('h2', class_=re.compile(r'title', re.I)) or
                        card.find('h3', class_=re.compile(r'title', re.I)) or
                        card.find('a', href=re.compile(r'/job-details/', re.I)) or
                        card.select_one('a[href*="job-details"]')
                    )
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract company - try multiple selectors
                    company_elem = (
                        card.find('a', class_=re.compile(r'company|compName', re.I)) or
                        card.find('span', class_=re.compile(r'company|compName', re.I)) or
                        card.find('div', class_=re.compile(r'company|compName', re.I)) or
                        card.select_one('[class*="company"]')
                    )
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    # Extract location - try multiple selectors
                    location_elem = (
                        card.find('span', class_=re.compile(r'location|loc', re.I)) or
                        card.find('li', class_=re.compile(r'location|loc', re.I)) or
                        card.find('div', class_=re.compile(r'location|loc', re.I)) or
                        card.select_one('[class*="location"]')
                    )
                    job_location = location_elem.get_text(strip=True) if location_elem else 'India'
                    
                    # Extract URL - try multiple patterns
                    job_url = None
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_url = title_elem['href']
                    else:
                        link = (
                            card.find('a', href=re.compile(r'/job-details/', re.I)) or
                            card.select_one('a[href*="job-details"]')
                        )
                        if link:
                            job_url = link.get('href')
                    
                    if not job_url:
                        continue
                    
                    if not job_url.startswith('http'):
                        job_url = self.base_url + job_url
                    
                    # Extract experience
                    exp_elem = (
                        card.find('span', class_=re.compile(r'exp', re.I)) or
                        card.find('li', class_=re.compile(r'exp', re.I))
                    )
                    experience_req = exp_elem.get_text(strip=True) if exp_elem else ''
                    
                    # Extract description
                    desc_elem = card.find(['p', 'div'], class_=re.compile(r'description|summary', re.I))
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url,
                        'experience': experience_req,
                        'description': description,
                        'posted_date': '',
                        'source': 'Naukri'
                    })
                    
                    if len(jobs) >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching Naukri jobs for '{keyword}': {e}")
            logger.debug(f"Naukri error details: {type(e).__name__}: {str(e)}")
        
        return jobs
