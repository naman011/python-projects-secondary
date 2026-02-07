# Git Commands to Check Auto-Apply Status

## 📍 Which Branch to Checkout

### For CSV Updates (Application Statuses)
**Branch**: `main`
- CSV file is updated on main branch
- Contains application statuses, errors, and results

### For Code/Logs (If Committed)
**Branch**: `auto-apply-feature`
- Contains auto-apply code
- Application logs are usually in artifacts (not committed)

## 🔧 Git Commands

### 1. Check CSV Updates on Main Branch

```bash
# Switch to main branch
git checkout main

# Pull latest changes (to get CSV updates from workflow)
git pull secondary main

# View CSV file
cat data/jobs.csv | head -20

# Or open in your editor
code data/jobs.csv  # VS Code
# or
open data/jobs.csv  # Default app (macOS)
```

### 2. Check Recent Commits (CSV Updates)

```bash
# On main branch
git checkout main
git pull secondary main

# See recent commits (look for [auto-apply] in message)
git log --oneline -10

# See what changed in last commit
git show HEAD --stat

# See CSV changes in last commit
git show HEAD:data/jobs.csv | head -20
```

### 3. Filter CSV for Applied Jobs

```bash
# On main branch
git checkout main
git pull secondary main

# Count successful applications
grep -c ',Yes,' data/jobs.csv || echo "No successful applications found"

# Show jobs that were applied
grep ',Yes,' data/jobs.csv | head -10

# Show failed applications
grep ',Failed,' data/jobs.csv | head -10

# Count by status
echo "Applied: $(grep -c ',Applied,' data/jobs.csv || echo 0)"
echo "Failed: $(grep -c ',Failed,' data/jobs.csv || echo 0)"
echo "Needs Manual Check: $(grep -c ',Needs Manual Check,' data/jobs.csv || echo 0)"
```

### 4. View CSV with Better Formatting

```bash
# Install csvkit for better CSV viewing (optional)
# pip install csvkit

# View CSV as table
csvlook data/jobs.csv | head -20

# Or use Python
python3 << 'EOF'
import csv
from collections import Counter

with open('data/jobs.csv', 'r') as f:
    reader = csv.DictReader(f)
    jobs = list(reader)

print(f"Total jobs: {len(jobs)}")
print(f"\nApplied: {sum(1 for j in jobs if j.get('Applied', '').strip().lower() == 'yes')}")
print(f"Failed: {sum(1 for j in jobs if j.get('Status', '') == 'Failed')}")
print(f"Needs Manual Check: {sum(1 for j in jobs if j.get('Status', '') == 'Needs Manual Check')}")

print("\nApplication Methods:")
methods = Counter(j.get('Application Method', '') for j in jobs if j.get('Applied', '').strip().lower() == 'yes')
for method, count in methods.items():
    if method:
        print(f"  {method}: {count}")

print("\nTop 10 Applied Jobs:")
applied = [j for j in jobs if j.get('Applied', '').strip().lower() == 'yes']
for i, job in enumerate(applied[:10], 1):
    print(f"{i}. {job.get('Company', 'Unknown')} - {job.get('Job Title', 'Unknown')}")
    print(f"   Method: {job.get('Application Method', 'N/A')}")
    print(f"   Date: {job.get('Applied Date', 'N/A')}")
EOF
```

### 5. Compare CSV Before/After

```bash
# On main branch
git checkout main
git pull secondary main

# See what changed in CSV in last commit
git diff HEAD~1 HEAD -- data/jobs.csv | head -50

# Or see changes in last 5 commits
git log -5 --oneline -- data/jobs.csv
```

### 6. Check Workflow Code (If Needed)

```bash
# Switch to auto-apply-feature branch
git checkout auto-apply-feature
git pull secondary auto-apply-feature

# View application logs directory (if committed)
ls -la data/application_logs/ 2>/dev/null || echo "Logs not in git (check artifacts)"
```

## 📊 Quick Status Check Script

Create a script to quickly check status:

```bash
# Save as check_status.sh
cat > check_status.sh << 'EOF'
#!/bin/bash

echo "=== Auto-Apply Status Check ==="
echo ""

# Switch to main and pull
git checkout main > /dev/null 2>&1
git pull secondary main > /dev/null 2>&1

# Count applications
TOTAL=$(wc -l < data/jobs.csv)
APPLIED=$(grep -c ',Yes,' data/jobs.csv 2>/dev/null || echo "0")
FAILED=$(grep -c ',Failed,' data/jobs.csv 2>/dev/null || echo "0")
NEEDS_CHECK=$(grep -c ',Needs Manual Check,' data/jobs.csv 2>/dev/null || echo "0")

echo "📊 Statistics:"
echo "  Total jobs in CSV: $((TOTAL - 1))"  # Subtract header
echo "  Successfully Applied: $APPLIED"
echo "  Failed: $FAILED"
echo "  Needs Manual Check: $NEEDS_CHECK"
echo ""

# Check last commit
echo "📝 Last CSV Update:"
git log -1 --oneline --format="  %h - %s (%ar)" -- data/jobs.csv

echo ""
echo "✅ Check GitHub Actions for detailed logs:"
echo "   https://github.com/naman011/python-projects-secondary/actions"
EOF

chmod +x check_status.sh
./check_status.sh
```

## 🎯 Recommended Workflow

### Quick Check (30 seconds)
```bash
git checkout main
git pull secondary main
grep -c ',Yes,' data/jobs.csv
```

### Detailed Check (2 minutes)
```bash
git checkout main
git pull secondary main
python3 << 'EOF'
import csv
with open('data/jobs.csv', 'r') as f:
    reader = csv.DictReader(f)
    jobs = list(reader)
    applied = [j for j in jobs if j.get('Applied', '').strip().lower() == 'yes']
    print(f"Applied: {len(applied)}/{len(jobs)}")
    for job in applied[:5]:
        print(f"  - {job.get('Company')}: {job.get('Job Title')}")
EOF
```

## 📁 Files to Check

### On Main Branch:
- `data/jobs.csv` - **Main file to check** - Contains all application statuses

### On Auto-Apply-Feature Branch:
- `auto_apply/` - Application code
- `apply_jobs.py` - CLI script
- `data/application_logs/` - May contain logs (if committed)

### In GitHub Actions Artifacts (Not in Git):
- `data/application_logs/applications_*.jsonl` - Detailed logs
- `data/application_logs/report_*.txt` - Summary report
- `data/application_logs/screenshots/` - Screenshots

## 🔗 Quick Reference

```bash
# 1. Check CSV on main branch
git checkout main && git pull secondary main && cat data/jobs.csv | grep ',Yes,' | wc -l

# 2. See last commit that updated CSV
git log --oneline -5 -- data/jobs.csv

# 3. View CSV changes
git show HEAD:data/jobs.csv | head -20
```

## 💡 Pro Tip

For the easiest view, use Excel/Google Sheets:
1. `git checkout main && git pull secondary main`
2. Open `data/jobs.csv` in Excel/Sheets
3. Filter by `Applied = Yes` column
4. Sort by `Applied Date` (newest first)
