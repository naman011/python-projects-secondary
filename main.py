#!/usr/bin/env python3
"""Main script to scrape jobs from company career pages."""

import sys
import logging
from scrapers.company_careers_scraper import CompanyCareersScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.naukri_scraper import NaukriScraper
from scrapers.indeed_scraper import IndeedScraper
from filters.job_filter import JobFilter
from utils.csv_writer import CSVWriter
from utils.config import CSV_HISTORY_DIR

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
    
    # 1. Company career pages (primary source)
    print("1. Scraping company career pages...")
    print("-" * 60)
    try:
        company_jobs = company_scraper.scrape()
        all_jobs.extend(company_jobs)
        print(f"   Found {len(company_jobs)} jobs from company career pages")
    except Exception as e:
        logger.error(f"Error scraping company career pages: {e}")
        print(f"   Error: {e}")
    print()
    
    # 2. LinkedIn
    print("2. Scraping LinkedIn...")
    print("-" * 60)
    try:
        linkedin_jobs = linkedin_scraper.scrape(max_results=50)
        all_jobs.extend(linkedin_jobs)
        print(f"   Found {len(linkedin_jobs)} jobs from LinkedIn")
    except Exception as e:
        logger.error(f"Error scraping LinkedIn: {e}")
        print(f"   Error: {e}")
    print()
    
    # 3. Naukri
    print("3. Scraping Naukri...")
    print("-" * 60)
    try:
        naukri_jobs = naukri_scraper.scrape(max_results=50)
        all_jobs.extend(naukri_jobs)
        print(f"   Found {len(naukri_jobs)} jobs from Naukri")
    except Exception as e:
        logger.error(f"Error scraping Naukri: {e}")
        print(f"   Error: {e}")
    print()
    
    # 4. Indeed
    print("4. Scraping Indeed...")
    print("-" * 60)
    try:
        indeed_jobs = indeed_scraper.scrape(max_results=50)
        all_jobs.extend(indeed_jobs)
        print(f"   Found {len(indeed_jobs)} jobs from Indeed")
    except Exception as e:
        logger.error(f"Error scraping Indeed: {e}")
        print(f"   Error: {e}")
    print()
    
    print("=" * 60)
    print(f"Total jobs scraped from all sources: {len(all_jobs)}")
    print("=" * 60)
    print()
    
    if not all_jobs:
        print("No jobs found. This could be due to:")
        print("- Network connectivity issues")
        print("- Company career pages may have changed structure")
        print("- All companies may be temporarily unavailable")
        return
    
    # Filter jobs
    print("Filtering jobs (India/Remote, Software Engineer, Fresher/1+ years)...")
    try:
        filtered_jobs = job_filter.filter_jobs(all_jobs)
    except Exception as e:
        logger.error(f"Error filtering jobs: {e}")
        print(f"Error: Filtering failed: {e}")
        return
    
    print(f"Jobs after filtering: {len(filtered_jobs)}")
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
