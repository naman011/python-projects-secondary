"""Configuration settings for the job scraper."""

# Search terms for Software Engineer roles
SEARCH_TERMS = [
    "software engineer",
    "sde",
    "software developer",
    "backend engineer",
    "full stack engineer",
    "frontend engineer",
    "fullstack engineer",
    "software development engineer"
]

# Location filters - India and Remote
# NOTE: filtering by location in code is now OPTIONAL; see JobFilter.filter_job.
# This list is still useful if you want to re-enable strict location filtering.
INDIA_LOCATIONS = [
    "india",
    "remote",
    "work from home",
    "wfh",
    "bangalore",
    "bengaluru",
    "mumbai",
    "delhi",
    "hyderabad",
    "pune",
    "chennai",
    "gurgaon",
    "gurugram",
    "noida",
    "kolkata",
    "ahmedabad",
]

# Experience levels to include
EXPERIENCE_LEVELS = [
    "fresher",
    "0 years",
    "0-1 years",
    "1+ years",
    "1-2 years",
    "1-3 years"
]

# Roles to exclude (internships)
EXCLUDE_KEYWORDS = [
    "intern",
    "internship"
]

# Scraping settings
REQUEST_DELAY_MIN = 1  # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = 3  # Maximum delay between requests (seconds)
MAX_RETRIES = 3  # Maximum retry attempts for failed requests
TIMEOUT = 30  # Request timeout in seconds

# Browser-based scraping (JS-heavy career sites) - optional
USE_BROWSER_FALLBACK = True  # Try headless browser when HTML scraper finds zero jobs
BROWSER_MAX_COMPANIES = 10  # Max number of companies per run to hit with browser
BROWSER_PAGE_LOAD_TIMEOUT = 40  # Seconds to wait for page load in browser

# CSV output settings
CSV_OUTPUT_FILE = "data/jobs.csv"

# Directory to store per-run timestamped CSV snapshots
# Example file name: data/job_runs/jobs_20260206_150000.csv
CSV_HISTORY_DIR = "data/job_runs"

MAX_DESCRIPTION_LENGTH = 500  # Truncate description if longer
