"""Remotive job scraper (public JSON API)."""

import logging
from typing import List, Dict, Optional

from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logger = logging.getLogger(__name__)


class RemotiveScraper(BaseScraper):
    """Scraper for Remotive using their public API."""

    def __init__(self):
        super().__init__()
        self.api_url = "https://remotive.com/api/remote-jobs"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        if keywords is None:
            keywords = SEARCH_TERMS

        resp = self.get(self.api_url, headers={"Accept": "application/json"})
        if not resp:
            return []

        try:
            payload = resp.json()
        except Exception as e:
            logger.warning(f"Remotive: failed to parse JSON: {e}")
            return []

        items = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(items, list):
            return []

        jobs: List[Dict] = []
        keyword_l = [k.lower() for k in keywords if k]

        for item in items:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or "").strip()
            company = str(item.get("company_name") or "").strip()
            url = str(item.get("url") or "").strip()
            description = str(item.get("description") or "").strip()
            location = str(item.get("candidate_required_location") or "Remote").strip()
            posted = str(item.get("publication_date") or "").strip()

            haystack = f"{title} {description}".lower()
            if keyword_l and not any(k in haystack for k in keyword_l):
                continue

            jobs.append(
                {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": url,
                    "experience": "",
                    "description": description,
                    "posted_date": posted,
                    "source": "Remotive",
                }
            )

            if len(jobs) >= max_results:
                break

        return jobs

