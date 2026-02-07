"""Additional remote job board scrapers.

Includes: Otta, Jobspresso, Dynamite Jobs, Working Nomads, RemoteSource,
No Visa Jobs, World Teams, Remote Rebellion, Y Combinator Jobs, Flexa,
Remote.co, DailyRemote, remote.io, RemoteHub, Remoters.me, JustRemote,
SkipTheDrive, Growmotely, Remotewx, Pangian.
"""

import logging
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from scrapers.base_scraper import BaseScraper
from utils.config import SEARCH_TERMS

logger = logging.getLogger(__name__)


class OttaScraper(BaseScraper):
    """Scraper for Otta (startup jobs, many remote)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://otta.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        if keywords is None:
            keywords = SEARCH_TERMS

        jobs: List[Dict] = []
        # Otta uses search API - try to scrape search results
        for keyword in keywords[:3]:  # Limit to avoid too many requests
            try:
                # Try search page
                search_url = f"{self.base_url}/jobs?q={keyword.replace(' ', '+')}"
                resp = self.get(search_url)
                if not resp:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                # Otta structure may vary - try common patterns
                job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|card|listing", re.I))

                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title|name", re.I))
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        if not title or len(title) < 5:
                            continue

                        link = card.find("a", href=True)
                        url = link["href"] if link else ""
                        if url and not url.startswith("http"):
                            url = self.base_url + url

                        company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                        company = company_elem.get_text(strip=True) if company_elem else ""

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": "Remote",
                            "url": url or self.base_url,
                            "experience": "",
                            "description": "",
                            "posted_date": "",
                            "source": "Otta",
                        })

                        if len(jobs) >= max_results:
                            break
                    except Exception as e:
                        logger.debug(f"Otta: Error parsing job card: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Otta: Error searching '{keyword}': {e}")
                continue

        return jobs


class JobspressoScraper(BaseScraper):
    """Scraper for Jobspresso (remote jobs)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://jobspresso.co"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            # Try RSS feed first
            rss_url = f"{self.base_url}/feed/"
            resp = self.get(rss_url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
            if resp and resp.text:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")

                for item in items[:max_results]:
                    try:
                        title = (item.findtext("title") or "").strip()
                        url = (item.findtext("link") or "").strip()
                        description = (item.findtext("description") or "").strip()
                        posted = (item.findtext("pubDate") or "").strip()

                        # Extract company from title if format is "Job Title at Company"
                        company = ""
                        if " at " in title:
                            parts = title.split(" at ", 1)
                            if len(parts) == 2:
                                title = parts[0].strip()
                                company = parts[1].strip()

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": "Remote",
                            "url": url,
                            "experience": "",
                            "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                            "posted_date": posted,
                            "source": "Jobspresso",
                        })
                    except Exception as e:
                        logger.debug(f"Jobspresso: Error parsing item: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Jobspresso: Error scraping: {e}")

        return jobs


class DynamiteJobsScraper(BaseScraper):
    """Scraper for Dynamite Jobs."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://dynamitejobs.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            # Try jobs listing page
            jobs_url = f"{self.base_url}/remote-jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|card", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True) or title_elem if title_elem.name == "a" else None
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "DynamiteJobs",
                    })
                except Exception as e:
                    logger.debug(f"DynamiteJobs: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"DynamiteJobs: Error scraping: {e}")

        return jobs


class WorkingNomadsScraper(BaseScraper):
    """Scraper for Working Nomads."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.workingnomads.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            # Try RSS feed
            rss_url = f"{self.base_url}/jobs.rss"
            resp = self.get(rss_url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
            if resp and resp.text:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")

                for item in items[:max_results]:
                    try:
                        title = (item.findtext("title") or "").strip()
                        url = (item.findtext("link") or "").strip()
                        description = (item.findtext("description") or "").strip()
                        posted = (item.findtext("pubDate") or "").strip()

                        jobs.append({
                            "title": title,
                            "company": "",
                            "location": "Remote",
                            "url": url,
                            "experience": "",
                            "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                            "posted_date": posted,
                            "source": "WorkingNomads",
                        })
                    except Exception as e:
                        logger.debug(f"WorkingNomads: Error parsing item: {e}")
                        continue
        except Exception as e:
            logger.warning(f"WorkingNomads: Error scraping: {e}")

        return jobs


class RemoteSourceScraper(BaseScraper):
    """Scraper for RemoteSource."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remotesource.io"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article", "li"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True) or (title_elem if title_elem.name == "a" else None)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "RemoteSource",
                    })
                except Exception as e:
                    logger.debug(f"RemoteSource: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"RemoteSource: Error scraping: {e}")

        return jobs


class NoVisaJobsScraper(BaseScraper):
    """Scraper for No Visa Jobs."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://novisajobs.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "NoVisaJobs",
                    })
                except Exception as e:
                    logger.debug(f"NoVisaJobs: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"NoVisaJobs: Error scraping: {e}")

        return jobs


class WorldTeamsScraper(BaseScraper):
    """Scraper for World Teams."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://worldteams.io"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "WorldTeams",
                    })
                except Exception as e:
                    logger.debug(f"WorldTeams: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"WorldTeams: Error scraping: {e}")

        return jobs


class RemoteRebellionScraper(BaseScraper):
    """Scraper for Remote Rebellion."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remoterebellion.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "RemoteRebellion",
                    })
                except Exception as e:
                    logger.debug(f"RemoteRebellion: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"RemoteRebellion: Error scraping: {e}")

        return jobs


class YCombinatorJobsScraper(BaseScraper):
    """Scraper for Y Combinator Jobs (startup jobs, many remote)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.workatastartup.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|card", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title|name", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True) or (title_elem if title_elem.name == "a" else None)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "YCombinatorJobs",
                    })
                except Exception as e:
                    logger.debug(f"YCombinatorJobs: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"YCombinatorJobs: Error scraping: {e}")

        return jobs


class FlexaScraper(BaseScraper):
    """Scraper for Flexa (flexible/remote jobs)."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://flexa.careers"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "Flexa",
                    })
                except Exception as e:
                    logger.debug(f"Flexa: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Flexa: Error scraping: {e}")

        return jobs


class RemoteCoScraper(BaseScraper):
    """Scraper for Remote.co."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remote.co"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            # Try RSS feed
            rss_url = f"{self.base_url}/remote-jobs/feed/"
            resp = self.get(rss_url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
            if resp and resp.text:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")

                for item in items[:max_results]:
                    try:
                        title = (item.findtext("title") or "").strip()
                        url = (item.findtext("link") or "").strip()
                        description = (item.findtext("description") or "").strip()
                        posted = (item.findtext("pubDate") or "").strip()

                        jobs.append({
                            "title": title,
                            "company": "",
                            "location": "Remote",
                            "url": url,
                            "experience": "",
                            "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                            "posted_date": posted,
                            "source": "Remote.co",
                        })
                    except Exception as e:
                        logger.debug(f"Remote.co: Error parsing item: {e}")
                        continue
            else:
                # Fallback to HTML scraping
                jobs_url = f"{self.base_url}/remote-jobs"
                resp = self.get(jobs_url)
                if resp:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

                    for card in job_cards[:max_results]:
                        try:
                            title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                            if not title_elem:
                                continue

                            title = title_elem.get_text(strip=True)
                            if not title:
                                continue

                            link = card.find("a", href=True)
                            url = link["href"] if link and link.get("href") else ""
                            if url and not url.startswith("http"):
                                url = self.base_url + url

                            jobs.append({
                                "title": title,
                                "company": "",
                                "location": "Remote",
                                "url": url or self.base_url,
                                "experience": "",
                                "description": "",
                                "posted_date": "",
                                "source": "Remote.co",
                            })
                        except Exception as e:
                            logger.debug(f"Remote.co: Error parsing card: {e}")
                            continue
        except Exception as e:
            logger.warning(f"Remote.co: Error scraping: {e}")

        return jobs


class DailyRemoteScraper(BaseScraper):
    """Scraper for DailyRemote."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://dailyremote.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/remote-jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|card", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "DailyRemote",
                    })
                except Exception as e:
                    logger.debug(f"DailyRemote: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"DailyRemote: Error scraping: {e}")

        return jobs


class RemoteIoScraper(BaseScraper):
    """Scraper for remote.io."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remote.io"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "remote.io",
                    })
                except Exception as e:
                    logger.debug(f"remote.io: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"remote.io: Error scraping: {e}")

        return jobs


class RemoteHubScraper(BaseScraper):
    """Scraper for RemoteHub."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remotehub.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/remote-jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "RemoteHub",
                    })
                except Exception as e:
                    logger.debug(f"RemoteHub: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"RemoteHub: Error scraping: {e}")

        return jobs


class RemotersMeScraper(BaseScraper):
    """Scraper for Remoters.me."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remoters.me"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "Remoters.me",
                    })
                except Exception as e:
                    logger.debug(f"Remoters.me: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Remoters.me: Error scraping: {e}")

        return jobs


class JustRemoteScraper(BaseScraper):
    """Scraper for JustRemote."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://justremote.co"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/remote-jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing|card", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "JustRemote",
                    })
                except Exception as e:
                    logger.debug(f"JustRemote: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"JustRemote: Error scraping: {e}")

        return jobs


class SkipTheDriveScraper(BaseScraper):
    """Scraper for SkipTheDrive."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.skipthedrive.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            # Try RSS feed
            rss_url = f"{self.base_url}/feed/"
            resp = self.get(rss_url, headers={"Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8"})
            if resp and resp.text:
                soup = BeautifulSoup(resp.text, "xml")
                items = soup.find_all("item")

                for item in items[:max_results]:
                    try:
                        title = (item.findtext("title") or "").strip()
                        url = (item.findtext("link") or "").strip()
                        description = (item.findtext("description") or "").strip()
                        posted = (item.findtext("pubDate") or "").strip()

                        jobs.append({
                            "title": title,
                            "company": "",
                            "location": "Remote",
                            "url": url,
                            "experience": "",
                            "description": BeautifulSoup(description, "html.parser").get_text(" ", strip=True),
                            "posted_date": posted,
                            "source": "SkipTheDrive",
                        })
                    except Exception as e:
                        logger.debug(f"SkipTheDrive: Error parsing item: {e}")
                        continue
        except Exception as e:
            logger.warning(f"SkipTheDrive: Error scraping: {e}")

        return jobs


class GrowmotelyScraper(BaseScraper):
    """Scraper for Growmotely."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://growmotely.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "Growmotely",
                    })
                except Exception as e:
                    logger.debug(f"Growmotely: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Growmotely: Error scraping: {e}")

        return jobs


class RemotewxScraper(BaseScraper):
    """Scraper for Remotewx."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://remotewx.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "Remotewx",
                    })
                except Exception as e:
                    logger.debug(f"Remotewx: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Remotewx: Error scraping: {e}")

        return jobs


class PangianScraper(BaseScraper):
    """Scraper for Pangian."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://pangian.com"

    def scrape(self, keywords: Optional[List[str]] = None, max_results: int = 200) -> List[Dict]:
        jobs: List[Dict] = []
        try:
            jobs_url = f"{self.base_url}/remote-jobs"
            resp = self.get(jobs_url)
            if not resp:
                return jobs

            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all(["div", "article"], class_=re.compile(r"job|listing", re.I))

            for card in job_cards[:max_results]:
                try:
                    title_elem = card.find(["h2", "h3", "a"], class_=re.compile(r"title", re.I))
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue

                    link = card.find("a", href=True)
                    url = link["href"] if link and link.get("href") else ""
                    if url and not url.startswith("http"):
                        url = self.base_url + url

                    company_elem = card.find(["div", "span"], class_=re.compile(r"company", re.I))
                    company = company_elem.get_text(strip=True) if company_elem else ""

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": "Remote",
                        "url": url or self.base_url,
                        "experience": "",
                        "description": "",
                        "posted_date": "",
                        "source": "Pangian",
                    })
                except Exception as e:
                    logger.debug(f"Pangian: Error parsing card: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Pangian: Error scraping: {e}")

        return jobs
