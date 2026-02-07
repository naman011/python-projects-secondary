# Auto-Apply System Documentation

## Overview

The auto-apply system allows you to automatically apply to jobs that have been scraped and marked as "ready to apply" in the CSV file. The system uses a hybrid approach: it first attempts to apply via API/HTTP requests, and falls back to Selenium browser automation for complex forms.

## Features

- **Hybrid Application Strategy**: API-first approach with Selenium fallback
- **Multi-Platform Support**: Indeed, Naukri, and 20+ remote job boards
- **Manual Review Workflow**: Mark jobs as "Ready to Apply" in CSV before auto-applying
- **Comprehensive Logging**: All application attempts are logged with detailed information
- **Error Handling**: Graceful error handling with categorization
- **Rate Limiting**: Configurable delays between applications to avoid detection
- **Status Tracking**: CSV is updated with application status, method, and errors

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create User Profile

Copy the template and fill in your details:

```bash
cp data/user_profile.json.template data/user_profile.json
```

Edit `data/user_profile.json` with your:
- Personal information (name, email, phone, LinkedIn, etc.)
- Education history
- Work experience
- Skills
- Resume file path
- Cover letter template (optional)

**Important**: The `data/user_profile.json` file contains sensitive information. Do NOT commit it to git. It should be in `.gitignore`.

### 3. Configure Auto-Apply Settings

Edit `utils/config.py` to configure auto-apply behavior:

```python
# Auto-apply settings
AUTO_APPLY_ENABLED = True  # Enable auto-apply
APPLY_DELAY_MIN = 30  # Minimum delay between applications (seconds)
APPLY_DELAY_MAX = 120  # Maximum delay between applications (seconds)
MAX_APPLICATIONS_PER_RUN = 10  # Maximum applications per run
SELENIUM_ENABLED = True  # Enable Selenium fallback
APPLY_ONLY_HIGH_PRIORITY = False  # Only apply to high-priority jobs
PRIORITY_THRESHOLD = 50  # Minimum priority score (if APPLY_ONLY_HIGH_PRIORITY is True)
```

### 4. Install Chrome/Chromium (for Selenium)

Selenium requires Chrome or Chromium to be installed on your system:

- **macOS**: `brew install --cask google-chrome` or `brew install chromium`
- **Linux**: `sudo apt-get install chromium-browser` or `sudo apt-get install google-chrome-stable`
- **Windows**: Download from [Google Chrome](https://www.google.com/chrome/)

The `webdriver-manager` package will automatically download and manage the ChromeDriver.

## Usage

### Step 1: Mark Jobs as Ready to Apply

Open `data/jobs.csv` in Excel, Google Sheets, or any CSV editor. For jobs you want to apply to, set the `Ready to Apply` column to `Yes`.

You can filter and sort jobs by:
- Priority Score (higher is better)
- Freshness (newer jobs first)
- Skills Match %
- Company tier

### Step 2: Run Auto-Apply

#### Basic Usage

```bash
python apply_jobs.py
```

#### Advanced Options

```bash
# Dry run (see what would be applied without actually applying)
python apply_jobs.py --dry-run

# Use custom CSV file
python apply_jobs.py --csv path/to/jobs.csv

# Use custom profile file
python apply_jobs.py --profile path/to/user_profile.json

# Verbose logging
python apply_jobs.py --verbose
```

### Step 3: Review Results

After running, check:

1. **CSV File** (`data/jobs.csv`):
   - `Applied` column: Shows if application was successful
   - `Application Method`: Shows method used (API, Selenium, or Manual)
   - `Application Error`: Shows error message if application failed
   - `Status`: Current application status

2. **Application Logs** (`data/application_logs/`):
   - `applications_YYYYMMDD.jsonl`: Detailed JSON logs of each application
   - `report_YYYYMMDD_HHMMSS.txt`: Summary report
   - `screenshots/`: Screenshots from Selenium applications

## Application Statuses

- **Applied**: Successfully submitted application
- **Failed**: Application failed (check `Application Error` column)
- **Needs Manual Check**: Status uncertain, requires manual verification
- **Skipped**: Job source not supported or intentionally skipped
- **Not Applied**: Not yet processed

## Error Categories

- **Form Not Found**: Could not locate application form
- **Login Required**: Requires account login (e.g., LinkedIn, Naukri)
- **CAPTCHA**: CAPTCHA detected (requires manual intervention)
- **Rate Limited**: Too many requests (wait and retry later)
- **Network Error**: Connection issues
- **Invalid Data**: Form validation failed
- **Unknown Error**: Unexpected error

## Supported Job Boards

### Fully Supported (API + Selenium)
- RemoteOK
- We Work Remotely
- Remotive
- Himalayas
- Otta
- Jobspresso
- Dynamite Jobs
- Working Nomads
- And 15+ other remote job boards

### Partially Supported (Selenium Only)
- Indeed (often redirects to external sites)
- Naukri (requires login in most cases)

### Not Supported (Manual Application Required)
- LinkedIn (requires login and has strict anti-automation)
- Company career pages (too diverse, use manual application)

## Limitations & Considerations

### Technical Limitations

1. **Dynamic Forms**: Some forms use JavaScript that requires Selenium
2. **File Uploads**: Resume uploads work but may need manual verification
3. **Multi-Step Applications**: Complex multi-step forms may not complete fully
4. **CAPTCHA**: CAPTCHA challenges require manual intervention

### Detection Risks

1. **Rate Limiting**: Applying too quickly may trigger rate limits
2. **Account Suspension**: Some platforms may detect automation and suspend accounts
3. **IP Blocking**: Excessive requests may result in temporary IP blocks

### Legal/Ethical Considerations

1. **Terms of Service**: Some platforms prohibit automation (check ToS)
2. **Spam Detection**: Mass applications may be flagged as spam
3. **Quality vs Quantity**: Focus on quality applications over quantity

### Best Practices

1. **Start Small**: Test with 1-2 jobs first
2. **Review Before Applying**: Always review jobs before marking as "Ready to Apply"
3. **Monitor Success Rates**: Check application logs regularly
4. **Respect Rate Limits**: Use conservative delay settings
5. **Manual Follow-up**: Some applications may need manual follow-up

## Troubleshooting

### "Profile file not found"

Make sure you've created `data/user_profile.json` from the template:
```bash
cp data/user_profile.json.template data/user_profile.json
```

### "Selenium WebDriver error"

1. Make sure Chrome/Chromium is installed
2. Check internet connection (webdriver-manager needs to download driver)
3. Try running with `--verbose` to see detailed error messages

### "No jobs ready to apply"

1. Check that `Ready to Apply` column is set to `Yes` in CSV
2. Verify jobs haven't already been applied (check `Applied` column)
3. If `APPLY_ONLY_HIGH_PRIORITY` is enabled, check priority scores

### "Application failed: Login required"

Some platforms (like Naukri, LinkedIn) require login. Options:
1. Apply manually through the platform
2. Configure account credentials (advanced, not implemented yet)
3. Use Selenium with saved login session (advanced)

### "CAPTCHA detected"

CAPTCHA challenges require manual intervention:
1. Apply manually through browser
2. Use a CAPTCHA solving service (configure in `config.py`)
3. Wait and retry later (some CAPTCHAs are temporary)

## Advanced Configuration

### Custom Application Delays

Edit `utils/config.py`:
```python
APPLY_DELAY_MIN = 60  # More conservative
APPLY_DELAY_MAX = 180
```

### Priority-Based Filtering

Only apply to high-priority jobs:
```python
APPLY_ONLY_HIGH_PRIORITY = True
PRIORITY_THRESHOLD = 70  # Only jobs with score >= 70
```

### Disable Selenium

If you only want API-based applications:
```python
SELENIUM_ENABLED = False
```

## File Structure

```
auto_apply/
├── __init__.py
├── profile_loader.py          # Load user profile
├── base_applier.py            # Base applier class
├── indeed_applier.py          # Indeed handler
├── naukri_applier.py         # Naukri handler
├── remote_board_applier.py   # Remote boards handler
├── selenium_fallback.py      # Selenium automation
├── application_manager.py    # Main orchestrator
└── utils.py                  # Helper functions

data/
├── user_profile.json          # Your application data (gitignored)
├── user_profile.json.template # Template file
├── jobs.csv                   # Jobs with application status
└── application_logs/          # Application logs and reports
    ├── applications_*.jsonl
    ├── report_*.txt
    └── screenshots/
```

## Security Notes

1. **Never commit `user_profile.json`** - It contains sensitive personal information
2. **Review application logs** - They may contain personal data
3. **Use secure storage** - Consider encrypting `user_profile.json` for production use
4. **Monitor account activity** - Check your accounts regularly for suspicious activity

## Support

For issues or questions:
1. Check application logs in `data/application_logs/`
2. Review error messages in CSV `Application Error` column
3. Run with `--verbose` flag for detailed logging
4. Check that all dependencies are installed correctly

## Future Enhancements

Potential improvements:
- Account credential management for platforms requiring login
- CAPTCHA solving service integration
- Email notification on application status
- Application tracking dashboard
- Resume customization per job
- Cover letter generation using AI
