# Git Commands to Check Auto-Apply Status

## 🎯 Quick Status Check

```bash
# You're on main branch - pull latest
git pull secondary main

# Check if CSV has application results
python3 << 'EOF'
import csv
with open('data/jobs.csv', 'r') as f:
    reader = csv.DictReader(f)
    jobs = list(reader)
    applied = [j for j in jobs if j.get('Applied', '').strip().lower() in ['yes', 'true', '1']]
    ready = [j for j in jobs if j.get('Ready to Apply', '').strip().lower() in ['yes', 'true', '1']]
    failed = [j for j in jobs if j.get('Status', '') == 'Failed']
    
    print(f"Total jobs: {len(jobs)}")
    print(f"Ready to Apply: {len(ready)}")
    print(f"Applied: {len(applied)}")
    print(f"Failed: {len(failed)}")
    
    if applied:
        print(f"\n✅ Successfully Applied Jobs:")
        for i, job in enumerate(applied[:10], 1):
            print(f"{i}. {job.get('Company')} - {job.get('Job Title')}")
            print(f"   Method: {job.get('Application Method')}")
            print(f"   Date: {job.get('Applied Date')}")
            print()
EOF
```

## 📍 Branch & Files

### Branch: `main`
```bash
git checkout main
git pull secondary main
```

### File to Check: `data/jobs.csv`
```bash
# View CSV
cat data/jobs.csv | head -20

# Or open in editor
open data/jobs.csv  # macOS
code data/jobs.csv  # VS Code
```

## 🔍 Check Workflow Completion

### 1. Check for Auto-Apply Commits
```bash
# Look for commits with [auto-apply] in message
git log --oneline --all --grep="\[auto-apply\]" -10

# If no results, workflow may not have committed yet
```

### 2. Check CSV File Changes
```bash
# See when CSV was last modified
git log --oneline -10 -- data/jobs.csv

# See what changed in last commit
git show HEAD --stat -- data/jobs.csv
```

### 3. Check Workflow Status (GitHub)
**Go to**: `https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml`

**Look for**:
- Latest run status (green/red/yellow)
- "Commit updated CSV" step - did it run?
- Any error messages in logs

## 📊 Detailed Status Check

```bash
# Full status check
git pull secondary main

python3 << 'EOF'
import csv
from collections import Counter

with open('data/jobs.csv', 'r') as f:
    reader = csv.DictReader(f)
    jobs = list(reader)

applied = [j for j in jobs if j.get('Applied', '').strip().lower() in ['yes', 'true', '1']]
failed = [j for j in jobs if j.get('Status', '') == 'Failed']
needs_check = [j for j in jobs if j.get('Status', '') == 'Needs Manual Check']
ready = [j for j in jobs if j.get('Ready to Apply', '').strip().lower() in ['yes', 'true', '1']]

print("=" * 60)
print("AUTO-APPLY STATUS")
print("=" * 60)
print(f"Total jobs in CSV: {len(jobs)}")
print(f"Ready to Apply: {len(ready)}")
print(f"Successfully Applied: {len(applied)}")
print(f"Failed: {len(failed)}")
print(f"Needs Manual Check: {len(needs_check)}")
print()

if applied:
    print("Application Methods:")
    methods = Counter(j.get('Application Method', 'Unknown') for j in applied)
    for method, count in methods.items():
        print(f"  {method}: {count}")
    print()
    
    print("First 10 Applied Jobs:")
    for i, job in enumerate(applied[:10], 1):
        print(f"{i}. {job.get('Company', 'Unknown')} - {job.get('Job Title', 'Unknown')}")
        print(f"   URL: {job.get('Job URL', '')}")
        print(f"   Method: {job.get('Application Method', 'N/A')}")
        print(f"   Date: {job.get('Applied Date', 'N/A')}")
        print()

if failed:
    print("Failed Applications (first 5):")
    for i, job in enumerate(failed[:5], 1):
        print(f"{i}. {job.get('Company', 'Unknown')} - {job.get('Job Title', 'Unknown')}")
        print(f"   Error: {job.get('Application Error', 'Unknown error')}")
        print()
EOF
```

## ⚠️ If Applied = 0

**Possible Reasons**:
1. **Workflow still running** - Check GitHub Actions
2. **No jobs marked** - Jobs need `Ready to Apply = Yes`
3. **Workflow failed** - Check workflow logs
4. **CSV not committed** - Workflow may have failed before commit

**Check These**:
```bash
# 1. Check if any jobs are marked as ready
grep -c ',Yes,' data/jobs.csv | grep "Ready to Apply"

# 2. Check workflow commits
git log --oneline --all --grep="auto-apply" -5

# 3. Check GitHub Actions (manual check)
# Go to: https://github.com/naman011/python-projects-secondary/actions
```

## 🔗 Direct Links

- **Workflow**: `https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml`
- **CSV**: `https://github.com/naman011/python-projects-secondary/blob/main/data/jobs.csv`
- **Latest Run**: Check Actions tab for most recent run

## 💡 Quick Commands Summary

```bash
# 1. Update CSV columns (if missing)
python3 scripts/update_csv_columns.py

# 2. Pull latest changes
git pull secondary main

# 3. Check applied jobs count
python3 -c "import csv; f=open('data/jobs.csv'); r=csv.DictReader(f); jobs=list(r); print(f\"Applied: {sum(1 for j in jobs if j.get('Applied','').strip().lower() in ['yes','true','1'])}\")"

# 4. Check workflow commits
git log --oneline --all --grep="\[auto-apply\]" -5
```
