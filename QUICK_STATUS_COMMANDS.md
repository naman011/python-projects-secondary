# Quick Status Check Commands

## Pull Latest Changes
```bash
git pull secondary main
```

## Check Git Status
```bash
git status
```

## View Recent Commands
```bash
git log --oneline -10
```

## Check Jobs CSV Status
```bash
# File info
ls -lh data/jobs.csv

# Total jobs
wc -l data/jobs.csv

# Applied jobs count
grep -c ",Applied," data/jobs.csv

# Jobs ready to apply
grep -c "Ready to Apply" data/jobs.csv

# View applied jobs
grep -i "Applied" data/jobs.csv | head -10
```

## Detailed Job Analysis
```bash
# View all columns for applied jobs
grep -i "Applied" data/jobs.csv | cut -d',' -f1-22

# Check application methods
cut -d',' -f19 data/jobs.csv | sort | uniq -c

# Check application errors
grep "Application Error" data/jobs.csv | grep -v "^$"

# Count by status
cut -d',' -f21 data/jobs.csv | sort | uniq -c
```

## Check GitHub Actions
```bash
# View workflow runs (in browser)
open https://github.com/naman011/python-projects-secondary/actions

# Or check locally
gh run list --workflow=auto-apply-jobs.yml
gh run list --workflow=job-scraper-hourly.yml
```

## View CSV in Readable Format
```bash
# View first few jobs
head -5 data/jobs.csv | column -t -s','

# Search for specific company
grep -i "company_name" data/jobs.csv

# View jobs with errors
grep "Application Error" data/jobs.csv
```

## Check Workflow Artifacts
```bash
# List workflow files
ls -la .github/workflows/

# Check for any log files
find . -name "*.log" -type f
```

## Quick Summary Script
```bash
./CHECK_IMPACT.sh
```
