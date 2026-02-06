"""LinkedIn job scraper."""

import re
import logging
from typing import List, Dict
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS, INDIA_LOCATIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn jobs."""
    
    def __init__(self):
        """Initialize LinkedIn scraper."""
        super().__init__()
        self.base_url = "https://www.linkedin.com/jobs/search"
    
    def scrape(self, keywords: List[str] = None, location: str = "India", max_results: int = 100) -> List[Dict]:
        """
        Scrape jobs from LinkedIn.
        
        Args:
            keywords: List of search keywords (default: SEARCH_TERMS)
            location: Location to search (default: India)
            max_results: Maximum number of results to fetch
            
        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = SEARCH_TERMS
        
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_jobs(keyword, location, max_results)
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs for '{keyword}' on LinkedIn")
            except Exception as e:
                logger.error(f"Error scraping LinkedIn for '{keyword}': {e}")
                continue
        
        return all_jobs
    
    def _search_jobs(self, keyword: str, location: str, max_results: int) -> List[Dict]:
        """Search for jobs with a specific keyword."""
        jobs = []
        
        # LinkedIn job search URL
        params = {
            'keywords': keyword,
            'location': location,
            'f_TPR': 'r86400',  # Past 24 hours
            'f_E': '2,3',  # Entry and Associate level
            'start': 0
        }
        
        url = f"{self.base_url}?{urlencode(params)}"
        
        try:
            response = self.get(url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # LinkedIn uses different structures - try multiple selectors
            job_cards = soup.find_all(['div', 'li'], class_=re.compile(r'job|result|card', re.I))
            
            for card in job_cards:
                try:
                    # Extract job title
                    title_elem = (
                        card.find('a', class_=re.compile(r'title|job-title', re.I)) or
                        card.find('h3', class_=re.compile(r'title', re.I)) or
                        card.find('span', class_=re.compile(r'title', re.I))
                    )
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract company
                    company_elem = (
                        card.find('a', class_=re.compile(r'company', re.I)) or
                        card.find('h4', class_=re.compile(r'company', re.I)) or
                        card.find('span', class_=re.compile(r'company', re.I))
                    )
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    # Extract location
                    location_elem = (
                        card.find('span', class_=re.compile(r'location', re.I)) or
                        card.find('div', class_=re.compile(r'location', re.I))
                    )
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract URL
                    link = title_elem.find('a', href=True) if title_elem.name != 'a' else title_elem
                    if link and link.get('href'):
                        job_url = link['href']
                        if not job_url.startswith('http'):
                            job_url = 'https://www.linkedin.com' + job_url
                    else:
                        continue
                    
                    # Extract description snippet
                    desc_elem = card.find(['p', 'div'], class_=re.compile(r'description|snippet', re.I))
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url,
                        'experience': '',
                        'description': description,
                        'posted_date': '',
                        'source': 'LinkedIn'
                    })
                    
                    if len(jobs) >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
        
        return jobs
