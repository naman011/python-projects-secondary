# Next Steps - Auto-Apply System

## ✅ Completed
- [x] GitHub Secret `USER_PROFILE_JSON` added
- [x] Workflow is visible in Actions tab
- [x] Branch `auto-apply-feature` created and pushed

## 🎯 Immediate Next Steps

### Step 1: Mark Jobs as "Ready to Apply" in CSV

**Location**: `data/jobs.csv` (on main branch)

**Steps**:
1. Open `data/jobs.csv` in Excel, Google Sheets, or any CSV editor
2. Find the `Ready to Apply` column
3. For jobs you want to apply to, set the value to `Yes`
4. Save the file
5. Commit and push to main branch (if you edited locally)

**Tips**:
- Start with 1-2 jobs for testing
- Filter by Priority Score (higher is better)
- Check Freshness (newer jobs are better)
- Review job descriptions before marking

**Example**:
```
Job Title,Company,Location,...,Ready to Apply,...
Software Engineer,Company A,Bangalore,...,Yes,...
Backend Developer,Company B,Remote,...,Yes,...
```

### Step 2: Test Workflow with Dry-Run (RECOMMENDED FIRST)

**Location**: GitHub Actions tab

**Steps**:
1. Go to: `https://github.com/naman011/python-projects-secondary/actions`
2. Click on **"Auto-Apply to Jobs"** workflow
3. Click **"Run workflow"** button (top right)
4. Configure:
   - **Branch**: `auto-apply-feature` ⚠️ (IMPORTANT - must select this)
   - **Dry run mode**: ✅ (checked)
   - **Max applications**: `1` (for testing)
   - **Skip CSV commit**: ✅ (checked - for testing)
5. Click **"Run workflow"**
6. Wait for workflow to complete (check the run)

**What to check**:
- Workflow completes without errors
- Logs show what would be applied
- No actual applications are submitted

### Step 3: Review Dry-Run Results

**Check**:
1. Go to workflow run logs
2. Review the output:
   - Which jobs would be applied to
   - What data would be submitted
   - Any errors or warnings
3. Download artifacts (if available) to see detailed logs

**If everything looks good**, proceed to Step 4.
**If there are issues**, review and fix before proceeding.

### Step 4: Run First Real Application (Test with 1 Job)

**Steps**:
1. Mark only **1 job** as "Ready to Apply" in CSV
2. Go to Actions → Auto-Apply to Jobs
3. Click **"Run workflow"**
4. Configure:
   - **Branch**: `auto-apply-feature`
   - **Dry run mode**: ❌ (unchecked - this is real)
   - **Max applications**: `1`
   - **Skip CSV commit**: ❌ (unchecked - allow CSV update)
5. Click **"Run workflow"**
6. Monitor the run

**What happens**:
- System will attempt to apply to the job
- CSV will be updated with application status
- Logs will show success/failure

### Step 5: Verify Application Status

**Check CSV Updates**:
1. Go to main branch: `data/jobs.csv`
2. Find the job you applied to
3. Check these columns:
   - `Applied`: Should be "Yes" if successful
   - `Application Method`: Shows "API" or "Selenium"
   - `Application Error`: Shows error if failed
   - `Status`: Shows "Applied", "Failed", or "Needs Manual Check"

**Check Logs**:
1. Download workflow artifacts
2. Review `data/application_logs/` folder
3. Check for any errors or warnings

### Step 6: Scale Up (If First Test Succeeded)

**Steps**:
1. Mark more jobs as "Ready to Apply" (5-10 jobs)
2. Run workflow again with:
   - **Max applications**: `5` or `10`
   - **Dry run mode**: ❌ (unchecked)
3. Monitor results
4. Gradually increase if successful

### Step 7: Enable Scheduled Runs (Optional)

**Current Schedule**: Daily at 9 AM UTC

**To Enable**:
- Schedule is already enabled in workflow
- It will run automatically daily
- You can disable it if you prefer manual-only

**To Disable Schedule**:
1. Edit `.github/workflows/auto-apply-jobs.yml`
2. Comment out the `schedule` section
3. Commit and push

## 📊 Monitoring & Maintenance

### Daily Checks (If Scheduled Enabled)
- Review workflow runs in Actions tab
- Check CSV for new application statuses
- Review any errors in logs

### Weekly Review
- Download application logs
- Review success/failure rates
- Adjust settings if needed
- Update user profile if information changes

### Monthly Review
- Analyze which job boards work best
- Review application success rates
- Update skills/experience in profile
- Adjust priority thresholds if needed

## ⚙️ Configuration Options

### Adjust Application Limits

Edit `utils/config.py`:
```python
MAX_APPLICATIONS_PER_RUN = 10  # Change this
APPLY_DELAY_MIN = 30  # Minimum delay between applications
APPLY_DELAY_MAX = 120  # Maximum delay between applications
```

### Priority Filtering

To only apply to high-priority jobs:
```python
APPLY_ONLY_HIGH_PRIORITY = True
PRIORITY_THRESHOLD = 70  # Only jobs with score >= 70
```

### Disable Selenium (API Only)

```python
SELENIUM_ENABLED = False
```

## 🚨 Important Reminders

1. **Always test with dry-run first** for new configurations
2. **Start small** - test with 1-2 jobs before scaling
3. **Monitor closely** for the first few runs
4. **Review CSV regularly** to see application statuses
5. **Check logs** if applications fail unexpectedly
6. **Update profile** if your information changes

## 🔗 Quick Links

- **Actions Tab**: `https://github.com/naman011/python-projects-secondary/actions`
- **Workflow**: `https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml`
- **Secrets**: `https://github.com/naman011/python-projects-secondary/settings/secrets/actions`
- **CSV File**: `https://github.com/naman011/python-projects-secondary/blob/main/data/jobs.csv`

## ❓ Troubleshooting

### Workflow Fails
- Check workflow logs for error messages
- Verify `USER_PROFILE_JSON` secret is set correctly
- Ensure CSV file exists in main branch
- Check that jobs are marked as "Ready to Apply"

### Applications Not Working
- Check `Application Error` column in CSV
- Review application logs in artifacts
- Some platforms may require manual application
- Check if login is required (Naukri, LinkedIn)

### CSV Not Updating
- Verify workflow has write permissions
- Check for merge conflicts
- Ensure "Skip CSV commit" is unchecked
- Review workflow logs for commit errors

## 📝 Checklist

- [ ] Mark 1-2 jobs as "Ready to Apply" in CSV
- [ ] Test workflow with dry-run mode
- [ ] Review dry-run results
- [ ] Run first real application (1 job)
- [ ] Verify application status in CSV
- [ ] Check application logs
- [ ] Scale up to more jobs if successful
- [ ] Monitor scheduled runs (if enabled)
- [ ] Review and adjust settings as needed

## 🎉 You're Ready!

Start with Step 1: Mark jobs in CSV and test with dry-run. Good luck with your job applications!
