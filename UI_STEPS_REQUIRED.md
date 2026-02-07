# Steps Completed vs. UI Steps Required

## ✅ Completed Automatically

### Git Operations
- ✅ Created branch: `auto-apply-feature`
- ✅ Committed all auto-apply code (22 files, 3332+ lines)
- ✅ Pushed branch to remote: `secondary/auto-apply-feature`
- ✅ Branch is now available at: `https://github.com/naman011/python-projects-secondary/tree/auto-apply-feature`

### Files Created/Modified
All code and configuration files are in place:
- Auto-apply module (`auto_apply/`)
- GitHub Actions workflow (`.github/workflows/auto-apply-jobs.yml`)
- Documentation files
- Configuration updates

## 🔧 Steps That Must Be Done Through GitHub UI

### 1. Set Up GitHub Secrets (REQUIRED)

**Location**: Repository Settings → Secrets and variables → Actions

**Steps**:
1. Go to: `https://github.com/naman011/python-projects-secondary/settings/secrets/actions`
2. Click **"New repository secret"**
3. Create secret:
   - **Name**: `USER_PROFILE_JSON` (exact name, case-sensitive)
   - **Value**: Copy entire contents of your `data/user_profile.json` file
4. Click **"Add secret"**

**Important**: 
- Secret name must be exactly: `USER_PROFILE_JSON`
- Value must be valid JSON
- This is required for the workflow to run

### 2. Verify Workflow File (RECOMMENDED)

**Location**: Actions tab

**Steps**:
1. Go to: `https://github.com/naman011/python-projects-secondary/actions`
2. Check that **"Auto-Apply to Jobs"** workflow appears in the list
3. If not visible, ensure you're viewing the `auto-apply-feature` branch

### 3. Test Workflow (RECOMMENDED)

**Location**: Actions tab → Auto-Apply to Jobs → Run workflow

**Steps**:
1. Go to: `https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml`
2. Click **"Run workflow"** button (top right)
3. Configure:
   - **Branch**: `auto-apply-feature`
   - **Dry run mode**: ✅ (checked - for testing)
   - **Max applications**: `1` (for testing)
   - **Skip CSV commit**: ✅ (checked - for testing)
4. Click **"Run workflow"**
5. Monitor the run in the Actions tab

### 4. Adjust Workflow Schedule (OPTIONAL)

**Location**: Edit workflow file in GitHub UI or locally

**Current Schedule**: Daily at 9 AM UTC

**To Change**:
- Option A: Edit `.github/workflows/auto-apply-jobs.yml` in GitHub UI
- Option B: Edit locally and push changes

**To Disable Schedule** (manual-only mode):
- Comment out the `schedule` section in the workflow file

### 5. Enable/Disable Workflow (OPTIONAL)

**Location**: Actions tab → Auto-Apply to Jobs → ... (three dots)

**To Disable**:
1. Go to Actions tab
2. Click on "Auto-Apply to Jobs" workflow
3. Click **"..."** (three dots) → **"Disable workflow"**

**To Re-enable**:
1. Same location
2. Click **"..."** → **"Enable workflow"**

### 6. Monitor Workflow Runs (ONGOING)

**Location**: Actions tab

**What to Check**:
- Workflow run status (success/failure)
- Application logs in artifacts
- CSV updates in main branch
- Error messages in workflow logs

## 📋 Quick Checklist

- [ ] Set up `USER_PROFILE_JSON` secret in GitHub
- [ ] Verify workflow appears in Actions tab
- [ ] Test workflow with dry-run mode
- [ ] Review workflow logs for any errors
- [ ] Mark jobs as "Ready to Apply" in CSV (on main branch)
- [ ] Run workflow manually first (without dry-run)
- [ ] Monitor results and adjust if needed
- [ ] Enable schedule if satisfied

## 🔗 Important Links

- **Repository**: `https://github.com/naman011/python-projects-secondary`
- **Auto-Apply Branch**: `https://github.com/naman011/python-projects-secondary/tree/auto-apply-feature`
- **Workflow File**: `https://github.com/naman011/python-projects-secondary/blob/auto-apply-feature/.github/workflows/auto-apply-jobs.yml`
- **Secrets Settings**: `https://github.com/naman011/python-projects-secondary/settings/secrets/actions`
- **Actions Tab**: `https://github.com/naman011/python-projects-secondary/actions`

## ⚠️ Important Notes

1. **Secrets Setup is Critical**: Without `USER_PROFILE_JSON` secret, the workflow will fail
2. **Branch Context**: Workflow runs on `auto-apply-feature` branch but reads CSV from `main` branch
3. **First Run**: Always test with dry-run mode first
4. **CSV Location**: Jobs CSV is in `main` branch, auto-apply updates it there
5. **Remote**: All operations are on `secondary` remote (naman011/python-projects-secondary)

## 🆘 Troubleshooting

### Workflow Not Visible
- Ensure you're viewing the `auto-apply-feature` branch
- Check that workflow file exists in `.github/workflows/` directory

### Secret Not Found Error
- Verify secret name is exactly `USER_PROFILE_JSON`
- Check secret exists in repository settings
- Ensure workflow has access to secrets

### Workflow Fails
- Check workflow logs for detailed error messages
- Verify all dependencies are in `requirements.txt`
- Test locally first: `python apply_jobs.py --dry-run`
