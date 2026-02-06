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
    
    def scrape(self, keywords: List[str] = None, experience: str = "0-1", max_results: int = 100) -> List[Dict]:
        """
        Scrape jobs from Naukri.com.
        
        Args:
            keywords: List of search keywords (default: SEARCH_TERMS)
            experience: Experience range (default: 0-1 for fresher/1+ years)
            max_results: Maximum number of results to fetch
            
        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = SEARCH_TERMS
        
        all_jobs = []
        
        for keyword in keywords:
            try:
                jobs = self._search_jobs(keyword, experience, max_results)
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs for '{keyword}' on Naukri")
            except Exception as e:
                logger.error(f"Error scraping Naukri for '{keyword}': {e}")
                continue
        
        return all_jobs
    
    def _search_jobs(self, keyword: str, experience: str, max_results: int) -> List[Dict]:
        """Search for jobs with a specific keyword."""
        jobs = []
        
        # Naukri job search URL
        search_url = f"{self.base_url}/jobapi/v3/search"
        
        # Naukri uses POST requests with form data
        # For simplicity, we'll try scraping the search results page
        params = {
            'k': keyword,
            'l': 'india',
            'experience': experience,
            'functionAreaIdGid': '8',  # IT Software
        }
        
        url = f"{self.base_url}/jobs-search?{urlencode(params)}"
        
        try:
            response = self.get(url)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Naukri job listing selectors
            job_cards = soup.find_all(['div', 'article'], class_=re.compile(r'job|tuple|row', re.I))
            
            for card in job_cards:
                try:
                    # Extract job title
                    title_elem = (
                        card.find('a', class_=re.compile(r'title|jobTitle', re.I)) or
                        card.find('h2', class_=re.compile(r'title', re.I)) or
                        card.find('a', href=re.compile(r'/job-details/', re.I))
                    )
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 5:
                        continue
                    
                    # Extract company
                    company_elem = (
                        card.find('a', class_=re.compile(r'company', re.I)) or
                        card.find('span', class_=re.compile(r'company', re.I)) or
                        card.find('div', class_=re.compile(r'company', re.I))
                    )
                    company = company_elem.get_text(strip=True) if company_elem else ''
                    
                    # Extract location
                    location_elem = (
                        card.find('span', class_=re.compile(r'location', re.I)) or
                        card.find('li', class_=re.compile(r'location', re.I)) or
                        card.find('div', class_=re.compile(r'location', re.I))
                    )
                    job_location = location_elem.get_text(strip=True) if location_elem else 'India'
                    
                    # Extract URL
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_url = title_elem['href']
                        if not job_url.startswith('http'):
                            job_url = self.base_url + job_url
                    else:
                        link = card.find('a', href=re.compile(r'/job-details/', re.I))
                        if link:
                            job_url = link['href']
                            if not job_url.startswith('http'):
                                job_url = self.base_url + job_url
                        else:
                            continue
                    
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
            logger.error(f"Error searching Naukri jobs: {e}")
        
        return jobs
