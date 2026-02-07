# Quick Start Guide - Auto-Apply

## 🚀 Immediate Action Items

### 1. Add "Ready to Apply" Column to CSV (If Missing)

Your CSV might not have the new columns yet. Here's how to add them:

**Option A: Using Python (Recommended)**
```bash
# This will add the missing columns automatically
python -c "
import csv
from utils.csv_writer import CSVWriter

writer = CSVWriter()
jobs = writer.read_jobs()
# Add default values for new columns
for job in jobs:
    if 'ready_to_apply' not in job:
        job['ready_to_apply'] = 'No'
    if 'application_method' not in job:
        job['application_method'] = ''
    if 'application_error' not in job:
        job['application_error'] = ''
writer.write_jobs(jobs, mode='w')
print('CSV updated with new columns')
"
```

**Option B: Manual Edit**
1. Open `data/jobs.csv` in Excel/Google Sheets
2. Add these columns at the end:
   - `Ready to Apply`
   - `Application Method`
   - `Application Error`
3. Fill `Ready to Apply` with "No" for all existing rows
4. Save and commit

### 2. Mark Jobs to Apply (5 minutes)

1. Open `data/jobs.csv`
2. Sort by `Priority Score` (descending) - highest first
3. Review top 5-10 jobs
4. For jobs you want to apply to:
   - Set `Ready to Apply` = `Yes`
   - Review job description
   - Check if it matches your profile
5. Save the file

**Start Small**: Mark only 1-2 jobs for your first test!

### 3. Test with Dry-Run (2 minutes)

1. Go to: https://github.com/naman011/python-projects-secondary/actions
2. Click **"Auto-Apply to Jobs"**
3. Click **"Run workflow"** (top right)
4. Settings:
   - Branch: `auto-apply-feature` ⚠️
   - Dry run: ✅ CHECKED
   - Max applications: `1`
   - Skip CSV commit: ✅ CHECKED
5. Click **"Run workflow"**
6. Wait 2-3 minutes
7. Check the run - should show what would be applied

### 4. First Real Application (5 minutes)

If dry-run looks good:

1. Mark 1 job as "Ready to Apply"
2. Run workflow again:
   - Branch: `auto-apply-feature`
   - Dry run: ❌ UNCHECKED
   - Max applications: `1`
   - Skip CSV commit: ❌ UNCHECKED
3. Wait for completion
4. Check CSV - job should show `Applied = Yes`

### 5. Verify Results

Check `data/jobs.csv`:
- `Applied` column: Should be "Yes" if successful
- `Application Method`: Shows "API" or "Selenium"
- `Application Error`: Empty if successful, error message if failed
- `Status`: "Applied", "Failed", or "Needs Manual Check"

## ⚡ Quick Checklist

- [ ] CSV has "Ready to Apply" column (add if missing)
- [ ] Mark 1-2 jobs as "Ready to Apply"
- [ ] Test with dry-run workflow
- [ ] Review dry-run results
- [ ] Run first real application
- [ ] Check CSV for application status
- [ ] Scale up if successful

## 🎯 Current Status

✅ GitHub Secret configured
✅ Workflow visible in Actions
✅ Ready to start applying!

## 📍 Where to Go

- **Mark Jobs**: Edit `data/jobs.csv` locally or on GitHub
- **Run Workflow**: https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml
- **Check Results**: View `data/jobs.csv` on main branch

## 💡 Pro Tips

1. **Start with 1 job** - test the system first
2. **Use dry-run** - always test before real applications
3. **Check logs** - download artifacts to see details
4. **Review CSV** - verify applications were recorded
5. **Monitor closely** - watch the first few runs

## 🆘 Need Help?

- Check `NEXT_STEPS.md` for detailed instructions
- Review workflow logs for errors
- Check CSV `Application Error` column for issues

---

**Ready? Start with Step 1: Add columns to CSV (if needed), then mark jobs and test!**
