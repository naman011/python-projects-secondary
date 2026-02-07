# Auto-Apply GitHub Actions Setup Guide

This guide explains how to set up the auto-apply workflow in GitHub Actions.

## Overview

The auto-apply workflow runs independently from the job scraping workflow:
- **Job Scraping**: Runs every 2 hours, scrapes jobs, updates CSV (main branch)
- **Auto-Apply**: Runs daily (or manually), applies to jobs, updates CSV (auto-apply-feature branch)

## Prerequisites

1. Repository with job scraping workflow already set up
2. `auto-apply-feature` branch created with auto-apply code
3. GitHub repository with Actions enabled

## Step 1: Create Auto-Apply Branch

If you haven't already, create the auto-apply branch:

```bash
git checkout -b auto-apply-feature
git push -u origin auto-apply-feature
```

## Step 2: Set Up GitHub Secrets

### 2.1 Navigate to Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### 2.2 Add User Profile Secret

Create a secret named `USER_PROFILE_JSON`:

1. **Name**: `USER_PROFILE_JSON`
2. **Value**: Copy the entire contents of your `data/user_profile.json` file
   - Open `data/user_profile.json` locally
   - Copy all JSON content
   - Paste into the secret value field

**Example structure:**
```json
{
  "personal_info": {
    "full_name": "Your Name",
    "email": "your.email@example.com",
    "phone": "+91-XXXXXXXXXX",
    ...
  },
  "education": [...],
  "work_experience": [...],
  ...
}
```

### 2.3 Verify Secret

- Secret name must be exactly: `USER_PROFILE_JSON`
- Secret value should be valid JSON
- Click **Add secret** to save

## Step 3: Enable Workflow

### 3.1 Workflow File Location

The workflow file is located at:
```
.github/workflows/auto-apply-jobs.yml
```

### 3.2 Verify Workflow

1. Go to **Actions** tab in your repository
2. You should see "Auto-Apply to Jobs" workflow
3. If not visible, ensure the file is committed to `auto-apply-feature` branch

## Step 4: Configure Schedule (Optional)

The workflow runs daily at 9 AM UTC by default. To change or disable:

1. Edit `.github/workflows/auto-apply-jobs.yml`
2. Modify the `schedule` section:

```yaml
on:
  schedule:
    # Run daily at 9 AM UTC
    - cron: "0 9 * * *"
    # Or disable by commenting out:
    # - cron: "0 9 * * *"
```

### Common Schedule Examples

- **Daily at 9 AM UTC**: `"0 9 * * *"`
- **Every 12 hours**: `"0 */12 * * *"`
- **Weekdays only**: `"0 9 * * 1-5"`
- **Twice daily**: `"0 9,21 * * *"`

## Step 5: Manual Workflow Trigger

### 5.1 Trigger from GitHub UI

1. Go to **Actions** tab
2. Select **Auto-Apply to Jobs** workflow
3. Click **Run workflow**
4. Configure options:
   - **Dry run mode**: Test without applying (recommended first time)
   - **Max applications**: Limit number of applications (default: 10)
   - **Skip CSV commit**: Don't commit updates (for testing)
5. Click **Run workflow**

### 5.2 Workflow Options

- **Dry Run**: Shows what would be applied without actually applying
- **Max Applications**: Limits how many jobs to process per run
- **Skip CSV Commit**: Useful for testing - doesn't update main branch

## Step 6: Monitor Workflow

### 6.1 View Workflow Runs

1. Go to **Actions** tab
2. Click on **Auto-Apply to Jobs**
3. View run history and logs

### 6.2 Check Logs

- Click on a workflow run
- Expand steps to see detailed logs
- Look for errors or warnings

### 6.3 Download Artifacts

After each run, download:
- Application logs (`data/application_logs/`)
- CSV backup (`data/jobs.csv.backup`)

## Step 7: Pause/Resume Workflow

### Pause Auto-Apply

**Option 1: Disable Schedule**
```yaml
on:
  # schedule:
  #   - cron: "0 9 * * *"  # Commented out
  workflow_dispatch:
    ...
```

**Option 2: Disable Workflow**
1. Go to **Actions** → **Auto-Apply to Jobs**
2. Click **...** (three dots) → **Disable workflow**

**Option 3: Manual Only**
- Remove `schedule` section entirely
- Keep only `workflow_dispatch`

### Resume Auto-Apply

1. Re-enable schedule in workflow file
2. Or enable workflow in GitHub UI
3. Or trigger manually via `workflow_dispatch`

## Troubleshooting

### Error: "USER_PROFILE_JSON not set"

**Solution**: 
- Verify secret is named exactly `USER_PROFILE_JSON`
- Check secret exists in repository settings
- Ensure workflow has access to secrets

### Error: "Invalid JSON in USER_PROFILE_JSON"

**Solution**:
- Validate JSON syntax (use JSON validator)
- Ensure no trailing commas
- Check for special characters that need escaping

### Error: "CSV file not found"

**Solution**:
- Ensure job scraping workflow has run at least once
- Check that `data/jobs.csv` exists in main branch
- Verify workflow checkout paths

### Error: "Merge conflict detected"

**Solution**:
- Job scraping and auto-apply ran simultaneously
- Manually resolve conflict in `data/jobs.csv`
- Re-run auto-apply workflow

### Workflow Not Appearing

**Solution**:
- Ensure workflow file is in `.github/workflows/` directory
- Check file is committed to `auto-apply-feature` branch
- Verify YAML syntax is correct

### Applications Not Working

**Solution**:
1. Check application logs in artifacts
2. Review `Application Error` column in CSV
3. Test locally first: `python apply_jobs.py --dry-run`
4. Check that jobs are marked as "Ready to Apply" in CSV

## Security Best Practices

1. **Never commit `user_profile.json`** to repository
2. **Use GitHub Secrets** for all sensitive data
3. **Review workflow logs** regularly
4. **Limit workflow permissions** (already configured)
5. **Monitor for suspicious activity**

## Workflow Independence

The auto-apply workflow is completely independent:

- ✅ **Separate branch**: Code in `auto-apply-feature` branch
- ✅ **Separate triggers**: Can run independently
- ✅ **Separate failures**: One workflow failure doesn't affect the other
- ✅ **Manual control**: Can pause/resume independently

## Testing Workflow

### First Time Setup

1. **Test with dry-run**:
   - Trigger workflow manually
   - Enable "Dry run mode"
   - Review output

2. **Test with 1 job**:
   - Mark 1 job as "Ready to Apply" in CSV
   - Run workflow with `max_applications: 1`
   - Verify CSV updates

3. **Test full workflow**:
   - Mark multiple jobs
   - Run workflow normally
   - Check logs and CSV updates

## Advanced Configuration

### Custom Environment Variables

Edit workflow to add custom variables:

```yaml
env:
  AUTO_APPLY_ENABLED: 'true'
  MAX_APPLICATIONS_PER_RUN: '10'
  APPLY_DELAY_MIN: '30'
  APPLY_DELAY_MAX: '120'
```

### Resume File Handling

If you need to handle resume files:

1. Encode resume as base64
2. Store in GitHub Secret: `RESUME_BASE64`
3. Decode in workflow step
4. Save to `data/` directory

## Support

For issues:
1. Check workflow logs
2. Review application logs in artifacts
3. Test locally with `apply_jobs.py`
4. Check CSV for error messages

## Next Steps

After setup:
1. ✅ Test with dry-run
2. ✅ Mark jobs as "Ready to Apply"
3. ✅ Run workflow manually first
4. ✅ Monitor results
5. ✅ Enable schedule if satisfied
