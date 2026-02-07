"""Himalayas job scraper (best-effort RSS)."""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logger = logging.getLogger(__name__)


class HimalayasScraper(BaseScraper):
    """
    Scraper for Himalayas.

    Note:
        Himalayas may change/limit access. This scraper tries a couple of RSS URLs.
    """

    def __init__(self):
        super().__init__()
        self.rss_candidates = [
            "https://himalayas.app/jobs/rss",
            "https://himalayas.app/jobs.rss",
        ]

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        if keywords is None:
            keywords = SEARCH_TERMS

        resp = None
        for url in self.rss_candidates:
            resp = self.get(url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
            if resp and resp.text:
                break

        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "xml")
        items = soup.find_all("item")
        if not items:
            return []

        jobs: List[Dict] = []
        # Removed early keyword filtering - let main JobFilter handle it

        for item in items:
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()
            posted = (item.findtext("pubDate") or "").strip()

            jobs.append(
                {
                    "title": title,
                    "company": "",
                    "location": "Remote",
                    "url": url,
                    "experience": "",
                    "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                    "posted_date": posted,
                    "source": "Himalayas",
                }
            )

            if len(jobs) >= max_results:
                break

        return jobs

