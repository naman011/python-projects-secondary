# Workflow Not Visible - Fix Instructions

## Issue

The "Auto-Apply to Jobs" workflow is not appearing in the Actions tab because GitHub only shows workflows from the **default branch** (usually `main`).

## Solution Options

### Option 1: Access Workflow Directly via URL (Easiest)

You can access and run the workflow directly using this URL:

**Direct Workflow URL:**
```
https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml
```

**Steps:**
1. Go to the URL above
2. Click **"Run workflow"** button (top right)
3. Select branch: `auto-apply-feature`
4. Configure options and run

### Option 2: Add Workflow File to Main Branch (Recommended)

To make the workflow appear in the Actions tab, we need to add the workflow file to the `main` branch as well. The workflow will still run from the `auto-apply-feature` branch code.

**Steps:**
1. Switch to main branch locally
2. Copy the workflow file to main branch
3. Commit and push
4. Workflow will now appear in Actions tab

### Option 3: Merge Workflow File to Main (Alternative)

Merge just the workflow file (not the code) to main branch so it appears in Actions tab.

## Quick Fix - Add Workflow to Main Branch

Run these commands:

```bash
# Switch to main branch
git checkout main

# Copy workflow file from auto-apply-feature branch
git checkout auto-apply-feature -- .github/workflows/auto-apply-jobs.yml

# Commit to main branch
git add .github/workflows/auto-apply-jobs.yml
git commit -m "Add auto-apply workflow file to main branch for Actions visibility"

# Push to main
git push secondary main
```

After this, the workflow will appear in the Actions tab!

## Why This Happens

GitHub Actions shows workflows in the Actions tab only if:
- The workflow file exists in the **default branch** (main/master)
- The workflow has been run at least once

Even though the workflow file is in `auto-apply-feature`, GitHub's UI only scans the default branch for workflow discovery.

## After Adding to Main

Once the workflow file is in main:
1. Go to Actions tab
2. You'll see "Auto-Apply to Jobs" workflow
3. Click on it
4. Click "Run workflow"
5. Select branch: `auto-apply-feature` (this is important - it will use the code from that branch)
6. Configure and run

## Important Note

Even though the workflow file is in `main`, when you run it and select branch `auto-apply-feature`, it will:
- Use the code from `auto-apply-feature` branch
- Use the workflow definition from `auto-apply-feature` branch (if different)
- This maintains the separation we want

## Alternative: Direct URL Access

If you prefer not to add the workflow to main, you can always access it directly:

**Workflow Runs:**
```
https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml
```

**Run Workflow:**
```
https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml?query=is%3Afailure
```

Then click "Run workflow" button.
