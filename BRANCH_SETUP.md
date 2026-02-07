# Branch Setup Instructions

## What Was Created

All auto-apply code has been implemented. To complete the setup, you need to:

## Step 1: Create the Auto-Apply Branch

Since git operations require permissions, create the branch manually:

```bash
# Make sure you're on main branch and have committed/stashed your changes
git checkout main

# Create and switch to new branch
git checkout -b auto-apply-feature

# Add all auto-apply files
git add .
git commit -m "Add auto-apply functionality with GitHub Actions workflow"

# Push to remote
git push -u origin auto-apply-feature
```

## Step 2: Verify Files Are in Place

The following files should be in the `auto-apply-feature` branch:

### Auto-Apply Code:
- `auto_apply/` - Complete auto-apply module
- `apply_jobs.py` - CLI entry point
- `data/user_profile.json.template` - Profile template

### GitHub Actions:
- `.github/workflows/auto-apply-jobs.yml` - Auto-apply workflow
- `scripts/generate_profile_from_secrets.py` - Secrets handler

### Documentation:
- `AUTO_APPLY_README.md` - Local usage guide
- `docs/AUTO_APPLY_SETUP.md` - GitHub Actions setup guide
- `README.md` - Updated with workflow info

## Step 3: Set Up GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Create secret:
   - **Name**: `USER_PROFILE_JSON`
   - **Value**: Copy entire contents of your `data/user_profile.json` file
5. Click **Add secret**

## Step 4: Test the Workflow

1. Go to **Actions** tab in GitHub
2. Select **Auto-Apply to Jobs** workflow
3. Click **Run workflow**
4. Select:
   - **Branch**: `auto-apply-feature`
   - **Dry run mode**: ✅ (checked)
   - **Max applications**: `1`
5. Click **Run workflow**

## Step 5: Monitor and Adjust

- Check workflow logs for any errors
- Adjust schedule in `.github/workflows/auto-apply-jobs.yml` if needed
- Test with actual applications once satisfied

## Branch Strategy

### Main Branch
- Contains only job scraping code
- Workflow: `job-scraper-hourly.yml`
- Purpose: Scrape jobs, update CSV

### Auto-Apply Branch
- Contains auto-apply code + job scraping code
- Workflow: `auto-apply-jobs.yml`
- Purpose: Apply to jobs, update CSV with application statuses

## Workflow Independence

✅ **Separate branches**: Code isolation
✅ **Separate triggers**: Independent scheduling
✅ **Separate failures**: One doesn't affect the other
✅ **Manual control**: Can pause/resume independently

## Next Steps

1. ✅ Create branch (Step 1 above)
2. ✅ Set up GitHub Secrets (Step 3)
3. ✅ Test workflow (Step 4)
4. ✅ Mark jobs as "Ready to Apply" in CSV
5. ✅ Run workflow manually first
6. ✅ Enable schedule if satisfied

## Troubleshooting

### Branch Creation Issues
- Ensure you have write access to repository
- Check that you're on the correct remote
- Verify branch doesn't already exist

### Workflow Not Appearing
- Ensure workflow file is committed to `auto-apply-feature` branch
- Check file is in `.github/workflows/` directory
- Verify YAML syntax is correct

### Secrets Not Working
- Verify secret name is exactly `USER_PROFILE_JSON`
- Check JSON is valid (use JSON validator)
- Ensure workflow has access to secrets

## Support

For detailed setup instructions, see:
- [Auto-Apply Setup Guide](docs/AUTO_APPLY_SETUP.md)
- [Auto-Apply README](AUTO_APPLY_README.md)
