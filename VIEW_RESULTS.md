# Where to View Auto-Apply Results

## 🎯 Quick Access Links

### 1. Workflow Run Status & Logs
**Location**: GitHub Actions Tab
**URL**: `https://github.com/naman011/python-projects-secondary/actions`

**Steps**:
1. Go to the Actions tab
2. Click on **"Auto-Apply to Jobs"** workflow
3. Click on the latest run (should be at the top)
4. View the run status and step-by-step logs

**What to Check**:
- ✅ Green checkmark = Run completed successfully
- ❌ Red X = Run failed (check logs for errors)
- 🟡 Yellow circle = Run in progress

### 2. Application Summary in Workflow
**Location**: Workflow Run → Summary Section

**What You'll See**:
- Total jobs processed
- Successful applications
- Failed applications
- Skipped applications
- Needs manual check count

**How to View**:
1. Open the workflow run
2. Scroll to the bottom
3. Look for "Generate summary" step output
4. Or check the "Summary" section at the top of the run page

### 3. CSV File Updates (Main Branch)
**Location**: `data/jobs.csv` on main branch
**URL**: `https://github.com/naman011/python-projects-secondary/blob/main/data/jobs.csv`

**What Changed**:
- `Applied` column: Shows "Yes" for successful applications
- `Application Method`: Shows "API" or "Selenium"
- `Application Error`: Shows error message if failed
- `Status`: Shows "Applied", "Failed", "Needs Manual Check", or "Skipped"
- `Applied Date`: Timestamp of application

**How to View**:
1. Go to main branch
2. Open `data/jobs.csv`
3. Filter/sort by:
   - `Applied = Yes` (successful)
   - `Status = Applied` (successful)
   - `Status = Failed` (failed applications)
   - `Application Error` (not empty = has errors)

**In Excel/Google Sheets**:
- Filter by `Applied` column = "Yes"
- Sort by `Applied Date` (newest first)
- Check `Application Error` column for any issues

### 4. Download Application Logs (Artifacts)
**Location**: Workflow Run → Artifacts Section

**What's Included**:
- `data/application_logs/` folder with:
  - `applications_YYYYMMDD.jsonl` - Detailed JSON logs for each application
  - `report_YYYYMMDD_HHMMSS.txt` - Summary report
  - `screenshots/` - Screenshots from Selenium applications (if any)

**How to Download**:
1. Go to workflow run page
2. Scroll to bottom
3. Find **"Artifacts"** section
4. Click on artifact name (e.g., `auto-apply-logs-123456`)
5. Click **"Download"** button
6. Extract the ZIP file

**What to Check in Logs**:
- Each application attempt with timestamp
- Success/failure status
- Error messages
- Application method used
- Job details (title, company, URL)

### 5. Detailed Application Report
**Location**: Downloaded artifacts → `data/application_logs/report_*.txt`

**Contains**:
```
============================================================
Application Report
============================================================
Total Processed: 100
Successful: 45
Failed: 30
Skipped: 15
Needs Manual Check: 10
============================================================
```

### 6. JSON Logs (Detailed)
**Location**: Downloaded artifacts → `data/application_logs/applications_YYYYMMDD.jsonl`

**Format**: One JSON object per line
**Contains**:
- Timestamp
- Job details (title, company, URL, source)
- Application result (success, method, error, etc.)

**How to View**:
- Open in text editor
- Or use JSON viewer online
- Or parse with Python script

## 📊 Quick Statistics Check

### Option 1: GitHub CSV View
1. Go to: `https://github.com/naman011/python-projects-secondary/blob/main/data/jobs.csv`
2. Use browser search (Ctrl+F / Cmd+F):
   - Search for: `,Yes,` (to find Applied = Yes)
   - Search for: `,Failed,` (to find failed applications)

### Option 2: Download and Analyze Locally
```bash
# Download CSV
# Then use Python to analyze:
python3 << EOF
import csv
from collections import Counter

with open('data/jobs.csv', 'r') as f:
    reader = csv.DictReader(f)
    jobs = list(reader)

applied = [j for j in jobs if j.get('Applied', '').strip().lower() == 'yes']
failed = [j for j in jobs if j.get('Status', '') == 'Failed']
needs_check = [j for j in jobs if j.get('Status', '') == 'Needs Manual Check']

print(f"Total jobs: {len(jobs)}")
print(f"Applied: {len(applied)}")
print(f"Failed: {len(failed)}")
print(f"Needs Manual Check: {len(needs_check)}")
print(f"\nApplication Methods:")
print(Counter(j.get('Application Method', '') for j in applied))
EOF
```

## 🔍 What to Look For

### Success Indicators ✅
- `Applied = Yes` in CSV
- `Status = Applied` in CSV
- `Application Method` shows "API" or "Selenium"
- `Application Error` is empty
- `Applied Date` has timestamp

### Failure Indicators ❌
- `Status = Failed` in CSV
- `Application Error` column has error message
- Common errors:
  - "Login Required" - Platform needs account
  - "Form Not Found" - Couldn't find application form
  - "CAPTCHA" - CAPTCHA detected
  - "Rate Limited" - Too many requests

### Needs Review ⚠️
- `Status = Needs Manual Check` - Uncertain status
- Check logs for details
- May need manual verification

## 📍 Direct Links

- **Workflow Runs**: `https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml`
- **CSV File**: `https://github.com/naman011/python-projects-secondary/blob/main/data/jobs.csv`
- **Latest Commit**: Check main branch for `[auto-apply]` commit message

## 🎯 Recommended Review Process

1. **Check Workflow Status** (2 min)
   - Go to Actions tab
   - Verify run completed successfully
   - Check summary statistics

2. **Download Artifacts** (1 min)
   - Download application logs
   - Extract ZIP file

3. **Review CSV** (5 min)
   - Open `data/jobs.csv`
   - Filter by `Applied = Yes`
   - Review successful applications
   - Check `Application Error` for failures

4. **Review Logs** (10 min)
   - Open `report_*.txt` for summary
   - Check `applications_*.jsonl` for details
   - Identify patterns in failures

5. **Take Action** (as needed)
   - Manual application for failed jobs
   - Adjust settings if needed
   - Mark more jobs for next run

## 💡 Pro Tips

1. **Use CSV Filters**: In Excel/Sheets, filter by `Applied` column to see only successful applications
2. **Sort by Date**: Sort by `Applied Date` to see most recent applications first
3. **Check Error Patterns**: Group failures by `Application Error` to identify common issues
4. **Review Screenshots**: If Selenium was used, check screenshots folder for visual confirmation
5. **Monitor Rate Limits**: If many "Rate Limited" errors, reduce `MAX_APPLICATIONS_PER_RUN`

## 🆘 Troubleshooting

### Can't See CSV Updates
- Check if workflow completed successfully
- Verify commit was made to main branch
- Look for `[auto-apply]` in commit message
- Refresh the page

### Artifacts Not Available
- Artifacts are retained for 30 days
- Check if workflow run completed
- Artifacts are only created if workflow runs to completion

### No Applications Found
- Check if jobs are marked as "Ready to Apply" = "Yes"
- Verify CSV has the column
- Check workflow logs for "No jobs ready to apply" message

---

**Start Here**: Go to Actions tab → Latest run → Check summary and download artifacts!
