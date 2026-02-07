#!/usr/bin/env python3
"""Main script to scrape jobs from company career pages."""

import sys
import logging
from scrapers.company_careers_scraper import CompanyCareersScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.naukri_scraper import NaukriScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.remoteok_scraper import RemoteOKScraper
from scrapers.weworkremotely_scraper import WeWorkRemotelyScraper
from scrapers.remotive_scraper import RemotiveScraper
from scrapers.himalayas_scraper import HimalayasScraper
from scrapers.gated_scrapers import (
    WellfoundScraper,
    CutshortScraper,
    InstahyreScraper,
    HiristIIMJobsScraper,
    ArcScraper,
    FlexJobsScraper,
)
from filters.job_filter import JobFilter
from utils.csv_writer import CSVWriter
from utils.config import CSV_HISTORY_DIR, ENABLE_GATED_SCRAPERS, SEARCH_LOCATIONS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to orchestrate job scraping."""
    print("=" * 60)
    print("Job Scraper - Company Career Pages")
    print("=" * 60)
    print()
    
    # Initialize components
    try:
        company_scraper = CompanyCareersScraper()
        linkedin_scraper = LinkedInScraper()
        naukri_scraper = NaukriScraper()
        indeed_scraper = IndeedScraper()
        remoteok_scraper = RemoteOKScraper()
        wwr_scraper = WeWorkRemotelyScraper()
        remotive_scraper = RemotiveScraper()
        himalayas_scraper = HimalayasScraper()

        gated_scrapers = []
        if ENABLE_GATED_SCRAPERS:
            gated_scrapers = [
                WellfoundScraper(),
                CutshortScraper(),
                InstahyreScraper(),
                HiristIIMJobsScraper(),
                ArcScraper(),
                FlexJobsScraper(),
            ]
        job_filter = JobFilter()
        csv_writer = CSVWriter()
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        print(f"Error: Failed to initialize scraper components: {e}")
        return
    
    # Get existing URLs to avoid duplicates
    try:
        existing_urls = csv_writer.get_existing_urls()
        print(f"Found {len(existing_urls)} existing jobs in CSV (for deduplication)")
        print()
    except Exception as e:
        logger.warning(f"Error reading existing CSV: {e}")
        existing_urls = set()
        print("Starting fresh (could not read existing CSV)")
        print()
    
    # Scrape jobs from all sources
    all_jobs = []
    scraper_stats = {}  # Track jobs per scraper before filtering
    
    # 1. Company career pages (primary source)
    print("1. Scraping company career pages...")
    print("-" * 60)
    try:
        company_jobs = company_scraper.scrape()
        all_jobs.extend(company_jobs)
        scraper_stats['Company Career Pages'] = len(company_jobs)
        print(f"   Found {len(company_jobs)} jobs from company career pages")
    except Exception as e:
        logger.error(f"Error scraping company career pages: {e}")
        scraper_stats['Company Career Pages'] = 0
        print(f"   Error: {e}")
    print()
    
    # 2. LinkedIn (search multiple locations: India + Gulf countries)
    print("2. Scraping LinkedIn...")
    print("-" * 60)
    try:
        linkedin_jobs = []
        for location in SEARCH_LOCATIONS:
            try:
                location_jobs = linkedin_scraper.scrape(location=location, max_results=50)
                linkedin_jobs.extend(location_jobs)
                logger.info(f"LinkedIn: Found {len(location_jobs)} jobs in {location}")
            except Exception as e:
                logger.warning(f"LinkedIn: Error searching {location}: {e}")
                continue
        all_jobs.extend(linkedin_jobs)
        scraper_stats['LinkedIn'] = len(linkedin_jobs)
        print(f"   Found {len(linkedin_jobs)} jobs from LinkedIn (across {len(SEARCH_LOCATIONS)} locations)")
    except Exception as e:
        logger.error(f"Error scraping LinkedIn: {e}")
        scraper_stats['LinkedIn'] = 0
        print(f"   Error: {e}")
    print()
    
    # 3. Naukri (search multiple locations: India + Gulf countries)
    print("3. Scraping Naukri...")
    print("-" * 60)
    try:
        naukri_jobs = []
        # Naukri primarily serves India, but also search for Gulf countries
        for location in SEARCH_LOCATIONS:
            try:
                # For Naukri, use location name directly
                location_jobs = naukri_scraper.scrape(location=location.lower(), max_results=50)
                naukri_jobs.extend(location_jobs)
                logger.info(f"Naukri: Found {len(location_jobs)} jobs in {location}")
            except Exception as e:
                logger.warning(f"Naukri: Error searching {location}: {e}")
                continue
        all_jobs.extend(naukri_jobs)
        scraper_stats['Naukri'] = len(naukri_jobs)
        print(f"   Found {len(naukri_jobs)} jobs from Naukri (across {len(SEARCH_LOCATIONS)} locations)")
    except Exception as e:
        logger.error(f"Error scraping Naukri: {e}")
        scraper_stats['Naukri'] = 0
        print(f"   Error: {e}")
    print()
    
    # 4. Indeed (search multiple locations: India + Gulf countries)
    print("4. Scraping Indeed...")
    print("-" * 60)
    try:
        indeed_jobs = []
        for location in SEARCH_LOCATIONS:
            try:
                location_jobs = indeed_scraper.scrape(location=location, max_results=50)
                indeed_jobs.extend(location_jobs)
                logger.info(f"Indeed: Found {len(location_jobs)} jobs in {location}")
            except Exception as e:
                logger.warning(f"Indeed: Error searching {location}: {e}")
                continue
        all_jobs.extend(indeed_jobs)
        scraper_stats['Indeed'] = len(indeed_jobs)
        print(f"   Found {len(indeed_jobs)} jobs from Indeed (across {len(SEARCH_LOCATIONS)} locations)")
    except Exception as e:
        logger.error(f"Error scraping Indeed: {e}")
        scraper_stats['Indeed'] = 0
        print(f"   Error: {e}")
    print()

    # 5. RemoteOK
    print("5. Scraping RemoteOK...")
    print("-" * 60)
    try:
        remoteok_jobs = remoteok_scraper.scrape(max_results=100)
        all_jobs.extend(remoteok_jobs)
        scraper_stats['RemoteOK'] = len(remoteok_jobs)
        print(f"   Found {len(remoteok_jobs)} jobs from RemoteOK")
    except Exception as e:
        logger.error(f"Error scraping RemoteOK: {e}")
        scraper_stats['RemoteOK'] = 0
        print(f"   Error: {e}")
    print()

    # 6. We Work Remotely
    print("6. Scraping We Work Remotely...")
    print("-" * 60)
    try:
        wwr_jobs = wwr_scraper.scrape(max_results=100)
        all_jobs.extend(wwr_jobs)
        scraper_stats['We Work Remotely'] = len(wwr_jobs)
        print(f"   Found {len(wwr_jobs)} jobs from We Work Remotely")
    except Exception as e:
        logger.error(f"Error scraping We Work Remotely: {e}")
        scraper_stats['We Work Remotely'] = 0
        print(f"   Error: {e}")
    print()

    # 7. Remotive
    print("7. Scraping Remotive...")
    print("-" * 60)
    try:
        remotive_jobs = remotive_scraper.scrape(max_results=100)
        all_jobs.extend(remotive_jobs)
        scraper_stats['Remotive'] = len(remotive_jobs)
        print(f"   Found {len(remotive_jobs)} jobs from Remotive")
    except Exception as e:
        logger.error(f"Error scraping Remotive: {e}")
        scraper_stats['Remotive'] = 0
        print(f"   Error: {e}")
    print()

    # 8. Himalayas
    print("8. Scraping Himalayas...")
    print("-" * 60)
    try:
        himalayas_jobs = himalayas_scraper.scrape(max_results=100)
        all_jobs.extend(himalayas_jobs)
        scraper_stats['Himalayas'] = len(himalayas_jobs)
        print(f"   Found {len(himalayas_jobs)} jobs from Himalayas")
    except Exception as e:
        logger.error(f"Error scraping Himalayas: {e}")
        scraper_stats['Himalayas'] = 0
        print(f"   Error: {e}")
    print()

    # 9. Gated sources (disabled by default)
    if gated_scrapers:
        print("9. Scraping gated sources (enabled)...")
        print("-" * 60)
        for scraper in gated_scrapers:
            try:
                jobs = scraper.scrape(max_results=50)
                all_jobs.extend(jobs)
                scraper_name = scraper.__class__.__name__
                scraper_stats[scraper_name] = len(jobs)
                print(f"   Found {len(jobs)} jobs from {scraper_name}")
            except Exception as e:
                logger.error(f"Error scraping {scraper.__class__.__name__}: {e}")
                scraper_stats[scraper.__class__.__name__] = 0
                print(f"   Error: {e}")
        print()
    
    print("=" * 60)
    print(f"Total jobs scraped from all sources: {len(all_jobs)}")
    print("=" * 60)
    print()
    
    # Display diagnostics: jobs per scraper BEFORE filtering
    print("DIAGNOSTICS - Jobs found per scraper (BEFORE filtering):")
    print("-" * 60)
    for scraper_name, count in sorted(scraper_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {scraper_name:30s}: {count:4d} jobs")
    print("-" * 60)
    print()
    
    if not all_jobs:
        print("No jobs found. This could be due to:")
        print("- Network connectivity issues")
        print("- Company career pages may have changed structure")
        print("- All companies may be temporarily unavailable")
        return
    
    # Filter jobs
    print("Filtering jobs (India/Remote, Tech roles, 0-3 years experience)...")
    print("-" * 60)
    try:
        filtered_jobs = job_filter.filter_jobs(all_jobs)
    except Exception as e:
        logger.error(f"Error filtering jobs: {e}")
        print(f"Error: Filtering failed: {e}")
        return
    
    print(f"Jobs after filtering: {len(filtered_jobs)} (removed {len(all_jobs) - len(filtered_jobs)})")
    
    # Track which scrapers' jobs passed filtering
    filtered_stats = {}
    for job in filtered_jobs:
        source = job.get('source', 'Unknown')
        filtered_stats[source] = filtered_stats.get(source, 0) + 1
    
    print()
    print("DIAGNOSTICS - Jobs per source AFTER filtering:")
    print("-" * 60)
    for source, count in sorted(filtered_stats.items(), key=lambda x: x[1], reverse=True):
        before = scraper_stats.get(source, 0)
        if before > 0:
            pct = (count / before) * 100
            print(f"  {source:30s}: {count:4d} jobs ({pct:5.1f}% of {before} scraped)")
        else:
            print(f"  {source:30s}: {count:4d} jobs")
    print("-" * 60)
    print()
    
    if not filtered_jobs:
        print("No jobs matched the filter criteria.")
        print("Try adjusting search terms or location filters in utils/config.py")
        return
    
    # Remove duplicates based on URL
    print("Removing duplicates...")
    unique_jobs = []
    seen_urls = set(existing_urls)  # Start with existing URLs
    
    for job in filtered_jobs:
        if not job or not isinstance(job, dict):
            continue
        job_url = str(job.get('url', '') or '').strip()
        if job_url and job_url not in seen_urls:
            seen_urls.add(job_url)
            unique_jobs.append(job)
    
    new_jobs_count = len(unique_jobs)
    print(f"New unique jobs: {new_jobs_count}")
    print()
    
    if new_jobs_count == 0:
        print("No new jobs found. All jobs are already in the CSV.")
        return
    
    # Write to CSV (main aggregate file)
    print(f"Writing {new_jobs_count} jobs to CSV...")
    timestamped_file = None
    try:
        csv_writer.write_jobs(unique_jobs, mode='a' if existing_urls else 'w')

        # Also write a per-run timestamped CSV snapshot into a history folder
        try:
            timestamped_file = csv_writer.write_timestamped_jobs(unique_jobs, CSV_HISTORY_DIR)
        except Exception as e:
            logger.warning(f"Error writing timestamped CSV snapshot: {e}")
    except Exception as e:
        logger.error(f"Error writing to CSV: {e}")
        print(f"Error: Failed to write to CSV: {e}")
        return
    
    print()
    print("=" * 60)
    print("Scraping completed successfully!")
    print(f"Total new jobs added: {new_jobs_count}")
    print(f"CSV file: {csv_writer.output_file}")
    if timestamped_file:
        print(f"Timestamped CSV snapshot: {timestamped_file}")
    print("=" * 60)
    print()
    print("Open the CSV file in Excel or Google Sheets to view jobs.")
    print("Click on the 'Job URL' column to apply directly!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)
