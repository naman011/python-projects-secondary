"""Base scraper class with common utilities."""

import time
import random
import logging
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from fake_useragent import UserAgent
from utils.config import REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, MAX_RETRIES, TIMEOUT
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers with common utilities."""
    
    def __init__(self):
        """Initialize the base scraper."""
        self.session = requests.Session()
        # Reasonable retry strategy at the HTTPAdapter level for flaky networks
        try:
            retry = Retry(
                total=2,
                connect=2,
                read=2,
                status=2,
                backoff_factor=0.5,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset(["GET", "POST", "HEAD"]),
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
        except Exception:
            # If urllib3 API changes, continue without adapter retries
            pass
        self.ua = UserAgent()
        self._update_user_agent()
    
    def _update_user_agent(self):
        """Update the user agent for the session."""
        try:
            user_agent = self.ua.random
            self.session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
        except Exception as e:
            logger.warning(f"Failed to get random user agent: {e}. Using default.")
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
    
    def _rate_limit(self):
        """Add a random delay between requests to be respectful."""
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
    
    def _make_request(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Optional[requests.Response]:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        if headers:
            request_headers = {**self.session.headers, **headers}
        else:
            request_headers = self.session.headers
        
        for attempt in range(MAX_RETRIES):
            try:
                self._rate_limit()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=request_headers,
                    timeout=TIMEOUT,
                    # ensure SSL verification is on; users can override via kwargs
                    verify=kwargs.pop("verify", True),
                    **kwargs
                )
                
                # Don't waste retries on hard failures where retry won't help
                if response.status_code in (401, 403, 404):
                    logger.warning(f"Non-retriable HTTP {response.status_code}: {url}")
                    return None

                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {url} - {e}"
                )
                # Don't retry on 404s surfaced as exceptions
                if isinstance(e, requests.exceptions.HTTPError):
                    try:
                        status = e.response.status_code if e.response is not None else None
                        if status in (401, 403, 404):
                            return None
                    except Exception:
                        pass
                if attempt < MAX_RETRIES - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch {url} after {MAX_RETRIES} attempts")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                else:
                    return None
        
        return None
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Convenience method for GET requests."""
        return self._make_request(url, method='GET', **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Convenience method for POST requests."""
        return self._make_request(url, method='POST', **kwargs)
    
    @abstractmethod
    def scrape(self, *args, **kwargs):
        """Abstract method to be implemented by subclasses."""
        pass
