"""Scrapers that are gated behind login / strong anti-bot protections.

These are intentionally disabled by default to avoid breaking runs.
Enable via `ENABLE_GATED_SCRAPERS = True` in `utils/config.py` and be prepared
to maintain them (HTML changes, blocking, ToS constraints).
"""

import logging
from typing import List, Dict

from scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class _GatedScraper(BaseScraper):
    name = "Gated"

    def scrape(self, *args, **kwargs) -> List[Dict]:
        logger.warning(
            f"{self.name}: scraper is disabled by default (login/anti-bot gated). "
            f"Enable `ENABLE_GATED_SCRAPERS=True` and implement site-specific logic."
        )
        return []


class WellfoundScraper(_GatedScraper):
    name = "Wellfound"


class CutshortScraper(_GatedScraper):
    name = "Cutshort"


class InstahyreScraper(_GatedScraper):
    name = "Instahyre"


class HiristIIMJobsScraper(_GatedScraper):
    name = "Hirist/iimjobs"


class ArcScraper(_GatedScraper):
    name = "Arc.dev"


class FlexJobsScraper(_GatedScraper):
    name = "FlexJobs"

