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

# Your technical skills for job matching (used in priority scoring)
# Extracted from resume - comprehensive list for accurate job matching
YOUR_SKILLS = [
    # Programming Languages
    "C++",
    "Java",
    "Java 8",
    "Java 11",
    "Java 17",
    "Java 21",
    "Python",
    "Python 3",
    "Python 3.10",
    "Python 3.11",
    "Python 3.12",
    "Python 3.13",
    "SQL",
    "HTML",
    "CSS",
    # Backend Frameworks & APIs
    "Spring Boot",
    "Spring",
    "SpringBoot",
    "Django",
    "Flask",
    "REST APIs",
    "RESTful APIs",
    # Cloud & AWS Services
    "AWS",
    "EC2",
    "S3",
    "Aurora",
    "Aurora MySQL",
    "AWS Glue",
    "AWS infrastructure",
    # DevOps & Infrastructure
    "Docker",
    "Kubernetes",
    "K8s",
    "CI/CD",
    "Kafka",
    "Kafka Streams",
    "Kafka Connect",
    "Load Balancers",
    "Auto Scaling",
    "Auto Scaling Groups",
    "SFTP",
    "Chronos",
    "Cron",
    "Redis",
    # Databases
    "PostgreSQL",
    "MySQL",
    # ML/NLP
    "SpaCy",
    "NLTK",
    "Natural Language Toolkit",
    "NLP",
    "Natural Language Processing",
    "Named Entity Recognition",
    "NER",
    "Regular Expressions",
    "Regex",
    # Frontend/Mobile
    "Flutter",
    # Tools & Platforms
    "Linux",
    "Linux Kernel",
    "Git",
    "GitHub",
    "GitLab",
    "Figma",
    "Google PlayStore",
    "DialogFlow",
    # System Design & Architecture
    "System Design",
    "API Design",
    "Data Modeling",
    "Schema Design",
    "Backend Development",
    "High Performance APIs",
    "Low Latency Systems",
    "Microservices",
    "Distributed Systems",
    "Event-Driven Architecture",
    # Web & Data
    "Web Scraping",
    "BeautifulSoup",
    "Data Scraping",
    # Testing & QA
    "QA Automation",
    "Load Testing",
    "Unit Testing",
    # Other Skills
    "Chatbot Development",
    "Quantitative Finance",
    "Algorithmic Trading",
    "Competitive Programming",
]

# Auto-apply settings
AUTO_APPLY_ENABLED = False  # Master switch for auto-apply functionality
APPLY_DELAY_MIN = 30  # Minimum delay between applications (seconds)
APPLY_DELAY_MAX = 120  # Maximum delay between applications (seconds)
MAX_APPLICATIONS_PER_RUN = 10  # Maximum number of applications per run (rate limiting)
SELENIUM_ENABLED = True  # Enable/disable Selenium fallback for complex forms
CAPTCHA_SERVICE = None  # Optional CAPTCHA solving service (e.g., "2captcha", "anticaptcha")
APPLY_ONLY_HIGH_PRIORITY = False  # If True, only apply to jobs above priority threshold
PRIORITY_THRESHOLD = 50  # Minimum priority score to auto-apply (if APPLY_ONLY_HIGH_PRIORITY is True)

# Application status values
APPLICATION_STATUS_READY = "Ready to Apply"
APPLICATION_STATUS_APPLYING = "Applying"
APPLICATION_STATUS_APPLIED = "Applied"
APPLICATION_STATUS_FAILED = "Failed"
APPLICATION_STATUS_NEEDS_MANUAL_CHECK = "Needs Manual Check"
APPLICATION_STATUS_SKIPPED = "Skipped"

# Application error categories
ERROR_FORM_NOT_FOUND = "Form Not Found"
ERROR_LOGIN_REQUIRED = "Login Required"
ERROR_CAPTCHA = "CAPTCHA"
ERROR_RATE_LIMITED = "Rate Limited"
ERROR_NETWORK = "Network Error"
ERROR_INVALID_DATA = "Invalid Data"
ERROR_UNKNOWN = "Unknown Error"

# Application method values
METHOD_API = "API"
METHOD_SELENIUM = "Selenium"
METHOD_MANUAL = "Manual"
