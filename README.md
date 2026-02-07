# Job Scraper & Auto-Apply System

Automated job scraping and application system for tech roles in India and remote positions.

## Features

- **Job Scraping**: Scrapes jobs from 30+ sources (company career pages, LinkedIn, Naukri, Indeed, remote job boards)
- **Smart Filtering**: Filters by location (India/Remote/Gulf), tech roles, and experience (0-3 years)
- **Priority Scoring**: Scores jobs based on recency, company quality, salary, and skills match
- **Auto-Apply**: Automatically applies to jobs marked as ready (optional, separate workflow)

## Project Structure

### Branches

- **`main`**: Job scraping code and workflows
- **`auto-apply-feature`**: Auto-apply functionality (separate branch for safety)

### Workflows

#### 1. Job Scraping Workflow
- **File**: `.github/workflows/job-scraper-hourly.yml`
- **Trigger**: Every 2 hours (scheduled) + manual
- **Purpose**: Scrapes jobs and updates `data/jobs.csv`
- **Branch**: `main`

#### 2. Auto-Apply Workflow
- **File**: `.github/workflows/auto-apply-jobs.yml`
- **Trigger**: Daily at 9 AM UTC (scheduled) + manual
- **Purpose**: Applies to jobs marked as "Ready to Apply"
- **Branch**: `auto-apply-feature`
- **Setup**: See [Auto-Apply Setup Guide](docs/AUTO_APPLY_SETUP.md)

## Quick Start

### Job Scraping

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run scraper locally**:
   ```bash
   python main.py
   ```

3. **View results**:
   - Open `data/jobs.csv` in Excel/Google Sheets
   - Jobs are sorted by priority score

### Auto-Apply (Optional)

1. **Set up user profile**:
   ```bash
   cp data/user_profile.json.template data/user_profile.json
   # Edit with your details
   ```

2. **Mark jobs to apply**:
   - Open `data/jobs.csv`
   - Set `Ready to Apply` column to `Yes` for desired jobs

3. **Run auto-apply**:
   ```bash
   python apply_jobs.py --dry-run  # Test first
   python apply_jobs.py            # Actually apply
   ```

4. **GitHub Actions setup**: See [Auto-Apply Setup Guide](docs/AUTO_APPLY_SETUP.md)

## Documentation

- **Auto-Apply README**: [AUTO_APPLY_README.md](AUTO_APPLY_README.md) - Local usage guide
- **GitHub Actions Setup**: [docs/AUTO_APPLY_SETUP.md](docs/AUTO_APPLY_SETUP.md) - Workflow setup guide

## Configuration

Edit `utils/config.py` to customize:
- Search terms and locations
- Experience levels
- Priority scoring weights
- Auto-apply settings

## Workflow Independence

The two workflows are completely independent:

- ✅ **Separate branches**: Code isolation
- ✅ **Separate triggers**: Can run independently  
- ✅ **Separate failures**: One doesn't affect the other
- ✅ **Manual control**: Pause/resume independently

## Safety Features

- **Manual Review**: Mark jobs before auto-applying
- **Dry Run Mode**: Test without applying
- **Rate Limiting**: Configurable delays between applications
- **Error Handling**: Comprehensive error tracking
- **CSV Backup**: Automatic backups before updates

## License

See [LICENSE](LICENSE) file.
