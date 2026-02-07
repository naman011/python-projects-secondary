"""We Work Remotely job scraper (RSS feed)."""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(BaseScraper):
    """Scraper for We Work Remotely using the Programming category RSS feed."""

    def __init__(self):
        super().__init__()
        self.rss_url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        if keywords is None:
            keywords = SEARCH_TERMS

        resp = self.get(self.rss_url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
        if not resp:
            return []

        soup = BeautifulSoup(resp.text, "xml")
        items = soup.find_all("item")

        jobs: List[Dict] = []
        # Removed early keyword filtering - let main JobFilter handle it

        for item in items:
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            description = (item.findtext("description") or "").strip()

            # Typical title looks like: "Company: Job title"
            company = ""
            job_title = title
            if ":" in title:
                left, right = title.split(":", 1)
                if left and right:
                    company = left.strip()
                    job_title = right.strip()

            jobs.append(
                {
                    "title": job_title,
                    "company": company,
                    "location": "Remote",
                    "url": url,
                    "experience": "",
                    "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                    "posted_date": (item.findtext("pubDate") or "").strip(),
                    "source": "WeWorkRemotely",
                }
            )

            if len(jobs) >= max_results:
                break

        return jobs

