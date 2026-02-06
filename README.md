# Job Scraper Tool

A free Python-based job scraper that focuses on **company career pages** (the most reliable source) to find Software Engineer positions in India and Remote locations. Perfect for freshers and candidates with 1+ years of experience.

## Features

- ✅ **Free**: No paid APIs, uses only free web scraping methods
- ✅ **Multiple Sources**: Scrapes from company career pages, LinkedIn, Naukri, and Indeed
- ✅ **Comprehensive**: Includes both fresher and 1+ years experience positions
- ✅ **Clickable Links**: CSV contains direct application URLs
- ✅ **Manual Execution**: Run anytime you want
- ✅ **Deduplication**: Automatically removes duplicate jobs
- ✅ **Multiple Formats**: Supports Greenhouse, Lever, Workday, and custom HTML career pages
- ✅ **80+ Companies**: Pre-configured list of top tech companies in India

## Requirements

- Python 3.7 or higher
- Internet connection

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the main script:

```bash
python main.py
```

The script will:
1. Scrape jobs from multiple sources:
   - Company career pages (80+ companies)
   - LinkedIn jobs
   - Naukri.com
   - Indeed.com
2. Filter jobs for:
   - Location: India or Remote
   - Role: Software Engineer, SDE, Software Developer, etc.
   - Experience: Fresher (0 years) or 1+ years
3. Remove duplicates
4. Save results to `data/jobs.csv`

### Automated hourly runs (GitHub Actions)

This project is set up to run automatically **every hour** using **GitHub Actions**:

- Workflow file: `.github/workflows/job-scraper-hourly.yml`
- Trigger: `cron: "0 * * * *"` (hourly), plus manual runs from the **Actions** tab
- On each run it:
  - Installs dependencies
  - Runs `python main.py`
  - Uploads the latest CSVs as an artifact

Each run produces:

- An aggregate CSV: `data/jobs.csv`
- A timestamped snapshot in `data/job_runs/`, for example: `data/job_runs/jobs_20260206_153000.csv`

To use this automation:

1. Push the repo (with the workflow file) to GitHub.
2. Open the repository’s **Actions** tab and ensure workflows are enabled.
3. The workflow named **“Job scraper (hourly)”** will run every hour.
4. For each run, you can download the CSVs from the run’s **Artifacts** section.

## Output

The results are saved in `data/jobs.csv` with the following columns:

- **Job Title**: Position title
- **Company**: Company name
- **Location**: Job location (India/Remote/City)
- **Experience Required**: Experience level
- **Job URL**: Clickable link for direct application
- **Posted Date**: Date when job was posted (if available)
- **Source**: Company name
- **Description**: Job description (truncated if too long)

Open the CSV file in Excel or Google Sheets. The **Job URL** column contains clickable links that you can click to apply directly!

## Adding More Companies

To add more companies, edit `data/companies.json`:

```json
{
  "Company Name": {
    "career_url": "https://company.com/careers",
    "scraper_type": "greenhouse|lever|workday|custom",
    "search_terms": ["software engineer", "sde"]
  }
}
```

**Scraper Types:**
- `greenhouse`: For companies using Greenhouse (e.g., Razorpay, Swiggy)
- `lever`: For companies using Lever
- `workday`: For companies using Workday
- `custom`: For custom HTML career pages (most companies)

## Configuration

You can customize search terms, locations, and other settings in `utils/config.py`:

- `SEARCH_TERMS`: Job titles to search for
- `INDIA_LOCATIONS`: Location keywords to match
- `EXPERIENCE_LEVELS`: Experience levels to include
- `REQUEST_DELAY_MIN/MAX`: Rate limiting delays

## How It Works

1. **Base Scraper** (`scrapers/base_scraper.py`): Provides common utilities like rate limiting, retry logic, and user-agent rotation

2. **Company Careers Scraper** (`scrapers/company_careers_scraper.py`): 
   - Scrapes company career pages (80+ companies)
   - Supports multiple formats (Greenhouse, Lever, custom HTML)
   - Extracts job details (title, location, URL, description)

3. **LinkedIn Scraper** (`scrapers/linkedin_scraper.py`):
   - Scrapes LinkedIn job listings
   - Searches for Software Engineer positions in India
   - Filters for entry and associate level positions

4. **Naukri Scraper** (`scrapers/naukri_scraper.py`):
   - Scrapes Naukri.com job listings
   - India's largest job portal
   - Focuses on IT Software roles

5. **Indeed Scraper** (`scrapers/indeed_scraper.py`):
   - Scrapes Indeed.com job listings
   - Searches for Software Engineer positions
   - Filters for entry-level positions

6. **Job Filter** (`filters/job_filter.py`):
   - Filters by location (India/Remote)
   - Filters by role (Software Engineer, SDE, etc.)
   - Includes freshers and 1+ years experience
   - Excludes internships

7. **CSV Writer** (`utils/csv_writer.py`):
   - Writes jobs to CSV with clickable URLs
   - Handles deduplication
   - Formats URLs properly

## Notes

- The scraper respects rate limits and includes delays between requests
- Some companies may block scrapers - the script will continue with other companies
- Career page structures may change - you may need to update scrapers for specific companies
- The script appends new jobs to existing CSV (won't duplicate existing jobs)

## Troubleshooting

**No jobs found?**
- Check your internet connection
- Some company career pages may have changed structure
- Try running again (some pages may be temporarily unavailable)

**Import errors?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`

**CSV file not created?**
- The `data/` directory will be created automatically
- Check file permissions in the project directory

## License

See LICENSE file for details.

## Contributing

Feel free to add more companies to `data/companies.json` or improve the scrapers!
