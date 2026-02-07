"""Configuration settings for the job scraper."""

# Search terms for tech roles (product/startup friendly, 0–3 years)
SEARCH_TERMS = [
    # Core SWE
    "software engineer",
    "software developer",
    "software development engineer",
    "sde",
    "sde 1",
    "sde i",
    "junior software engineer",
    "graduate software engineer",
    # Backend / frontend / full stack
    "backend engineer",
    "backend developer",
    "frontend engineer",
    "frontend developer",
    "full stack engineer",
    "fullstack engineer",
    "full stack developer",
    # Platform / devops / sre
    "platform engineer",
    "devops engineer",
    "site reliability engineer",
    "sre",
    # Data / ml
    "data engineer",
    "analytics engineer",
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    # Mobile
    "android engineer",
    "android developer",
    "ios engineer",
    "ios developer",
    "mobile engineer",
    "mobile developer",
]

# Location filters - India, Remote, and Gulf countries
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
    # Gulf countries / UAE
    "dubai",
    "uae",
    "united arab emirates",
    "abu dhabi",
    "saudi arabia",
    "riyadh",
    "qatar",
    "doha",
    "kuwait",
    "bahrain",
    "oman",
    "muscat",
    "gulf",
    "middle east",
]

# Additional locations to search in job boards (LinkedIn, Naukri, Indeed)
SEARCH_LOCATIONS = [
    "India",
    "Dubai, United Arab Emirates",
    "UAE",
    "Saudi Arabia",
    "Qatar",
    "Kuwait",
    "Bahrain",
    "Oman",
]

# Experience levels to include (fresher – 3 years)
EXPERIENCE_LEVELS = [
    "fresher",
    "0 years",
    "0-1 years",
    "0-2 years",
    "0-3 years",
    "1 year",
    "1 years",
    "1-2 years",
    "1-3 years",
    "2 years",
    "2-3 years",
    "3 years",
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

# Extra job boards (some are gated behind login/anti-bot and are disabled by default)
ENABLE_GATED_SCRAPERS = False

# Filter diagnostics - set to True to log why jobs are filtered out
ENABLE_FILTER_LOGGING = False
