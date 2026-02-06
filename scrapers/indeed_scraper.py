"""Indeed.com job scraper."""

import re
import logging
from typing import List, Dict
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com jobs."""
    
    def __init__(self):
        """Initialize Indeed scraper."""
        super().__init__()
        self.base_url = "https://in.indeed.com"
    
    def scrape(self, keywords: List[str] = None, location: str = "India", max_results: int = 100) -> List[Dict]:
        """
        Scrape jobs from Indeed.
        
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
                logger.info(f"Found {len(jobs)} jobs for '{keyword}' on Indeed")
            except Exception as e:
                logger.error(f"Error scraping Indeed for '{keyword}': {e}")
                continue
        
        return all_jobs
    
    def _search_jobs(self, keyword: str, location: str, max_results: int) -> List[Dict]:
        """Search for jobs with a specific keyword."""
        jobs = []
        
        # Indeed job search URL
        params = {
            'q': keyword,
            'l': location,
            'fromage': '1',  # Past 24 hours
            'explvl': 'entry_level',  # Entry level
        }
        
        url = f"{self.base_url}/jobs?{urlencode(params)}"
        
        try:
            response = self.get(url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Indeed job card selectors
            job_cards = soup.find_all(['div', 'a'], class_=re.compile(r'job|result', re.I))
            
            for card in job_cards:
                try:
                    # Extract job title
                    title_elem = (
                        card.find('a', class_=re.compile(r'title|jobTitle', re.I)) or
                        card.find('h2', class_=re.compile(r'title', re.I)) or
                        card.find('a', href=re.compile(r'/viewjob', re.I))
                    )
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract company
                    company_elem = (
                        card.find('span', class_=re.compile(r'company', re.I)) or
                        card.find('div', class_=re.compile(r'company', re.I)) or
                        card.find('a', class_=re.compile(r'company', re.I))
                    )
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    # Extract location
                    location_elem = (
                        card.find('div', class_=re.compile(r'location', re.I)) or
                        card.find('span', class_=re.compile(r'location', re.I))
                    )
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract URL
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_url = title_elem['href']
                        if not job_url.startswith('http'):
                            job_url = self.base_url + job_url
                    else:
                        link = card.find('a', href=re.compile(r'/viewjob', re.I))
                        if link:
                            job_url = link['href']
                            if not job_url.startswith('http'):
                                job_url = self.base_url + job_url
                        else:
                            continue
                    
                    # Extract description snippet
                    desc_elem = card.find(['div', 'span'], class_=re.compile(r'summary|snippet', re.I))
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    # Extract posted date
                    date_elem = card.find('span', class_=re.compile(r'date', re.I))
                    posted_date = date_elem.get_text(strip=True) if date_elem else ''
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'url': job_url,
                        'experience': '',
                        'description': description,
                        'posted_date': posted_date,
                        'source': 'Indeed'
                    })
                    
                    if len(jobs) >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error parsing job card: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching Indeed jobs: {e}")
        
        return jobs
