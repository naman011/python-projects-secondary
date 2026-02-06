"""Remote OK job scraper (public JSON API)."""

import logging
from typing import List, Dict, Optional

from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logger = logging.getLogger(__name__)


class RemoteOKScraper(BaseScraper):
    """Scraper for Remote OK using the public JSON endpoint."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://remoteok.com/api"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        """
        Scrape Remote OK jobs.

        Notes:
            Remote OK API returns a JSON array. The first element is metadata.
        """
        if keywords is None:
            keywords = SEARCH_TERMS

        resp = self.get(self.api_url, headers={"Accept": "application/json"})
        if not resp:
            return []

        try:
            data = resp.json()
        except Exception as e:
            logger.warning(f"Remote OK: failed to parse JSON: {e}")
            return []

        if not isinstance(data, list) or not data:
            return []

        # First element is metadata in Remote OK API
        items = [x for x in data[1:] if isinstance(x, dict)]

        jobs: List[Dict] = []
        keyword_l = [k.lower() for k in keywords if k]

        for item in items:
            title = str(item.get("position") or "").strip()
            company = str(item.get("company") or "").strip()
            url = str(item.get("url") or item.get("apply_url") or "").strip()
            description = str(item.get("description") or "").strip()
            tags = item.get("tags") or []
            tags_text = " ".join([str(t) for t in tags]) if isinstance(tags, list) else str(tags)

            haystack = f"{title} {description} {tags_text}".lower()
            if keyword_l and not any(k in haystack for k in keyword_l):
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": "Remote",
                    "url": url,
                    "experience": "",
                    "description": description,
                    "posted_date": "",
                    "source": "RemoteOK",
                }
            )

            if len(jobs) >= max_results:
                break

        return jobs

