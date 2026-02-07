# Commands to Check Scraper & Auto-Apply Impact

## Quick Check (All-in-One)
```bash
./CHECK_IMPACT.sh
```

## Step-by-Step Commands

### 1. Pull Latest Changes
```bash
git pull secondary main
```

### 2. Check Git Status
```bash
git status
git log --oneline -10
```

### 3. Check Jobs CSV
```bash
# File info
ls -lh data/jobs.csv

# Total jobs count
python3 -c "import csv; print('Total jobs:', len(list(csv.DictReader(open('data/jobs.csv')))))"

# Applied jobs
python3 << 'EOF'
import csv
with open('data/jobs.csv', 'r') as f:
    rows = list(csv.DictReader(f))
    applied = [r for r in rows if r.get('Applied', '').strip().lower() == 'yes']
    print(f"Applied jobs: {len(applied)}")
    for job in applied:
        print(f"  - {job.get('Job Title')} at {job.get('Company')}")
        print(f"    Method: {job.get('Application Method')}")
        print(f"    Date: {job.get('Applied Date')}")
EOF
```

### 4. Check Application Status
```bash
python3 << 'EOF'
import csv
with open('data/jobs.csv', 'r') as f:
    rows = list(csv.DictReader(f))
    
    # Ready to apply
    ready = [r for r in rows if r.get('Ready to Apply', '').strip().lower() == 'yes']
    print(f"Ready to Apply: {len(ready)}")
    
    # Application methods
    methods = {}
    for r in rows:
        method = r.get('Application Method', '').strip()
        if method:
            methods[method] = methods.get(method, 0) + 1
    
    print("\nApplication Methods:")
    for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count}")
    
    # Errors
    errors = [r for r in rows if r.get('Application Error', '').strip()]
    print(f"\nJobs with errors: {len(errors)}")
    for job in errors[:5]:
        print(f"  - {job.get('Job Title')}: {job.get('Application Error')}")
EOF
```

### 5. View Specific Job Details
```bash
# View all columns for a specific company
python3 << 'EOF'
import csv
company = "Indeed"  # Change this
with open('data/jobs.csv', 'r') as f:
    rows = list(csv.DictReader(f))
    matches = [r for r in rows if company.lower() in r.get('Company', '').lower()]
    print(f"Jobs from {company}: {len(matches)}")
    for job in matches[:3]:
        print(f"\n{job.get('Job Title')}")
        print(f"  Company: {job.get('Company')}")
        print(f"  URL: {job.get('Job URL')}")
        print(f"  Applied: {job.get('Applied')}")
        print(f"  Method: {job.get('Application Method')}")
EOF
```

### 6. Check GitHub Actions Status
```bash
# Open in browser
open https://github.com/naman011/python-projects-secondary/actions

# Or use GitHub CLI (if installed)
gh run list --workflow=auto-apply-jobs.yml --limit 5
gh run list --workflow=job-scraper-hourly.yml --limit 5
```

### 7. View CSV Changes
```bash
# See what changed in jobs.csv
git diff HEAD data/jobs.csv | head -50

# See last commit changes
git show HEAD:data/jobs.csv | head -20
```

### 8. Check Workflow Logs
```bash
# View workflow files
ls -la .github/workflows/

# Check for artifacts (if downloaded)
ls -la artifacts/ 2>/dev/null
```

## Summary Commands

```bash
# Quick summary
echo "=== QUICK SUMMARY ===" && \
python3 << 'EOF'
import csv
with open('data/jobs.csv', 'r') as f:
    rows = list(csv.DictReader(f))
    applied = len([r for r in rows if r.get('Applied', '').strip().lower() == 'yes'])
    ready = len([r for r in rows if r.get('Ready to Apply', '').strip().lower() == 'yes'])
    print(f"Total jobs: {len(rows)}")
    print(f"Applied: {applied}")
    print(f"Ready to apply: {ready}")
EOF
```

## Current Status (from last check)
- **Total Jobs**: 489
- **Applied Jobs**: 0
- **Ready to Apply**: 0
- **Last Modified**: Check with `ls -lh data/jobs.csv`
