# Workflow File Branch Strategy

## Answer: Push to MAIN Branch

**The workflow file should be committed to the `main` branch** for GitHub Actions visibility.

## Why Main Branch?

1. **GitHub Actions Visibility**: Workflows only appear in the Actions tab if they exist on the default branch (`main`)
2. **Workflow Discovery**: GitHub scans the default branch to discover workflows
3. **Code Separation**: The workflow file can be on `main`, but it checks out `auto-apply-feature` branch for the actual code

## Current Setup

- **Workflow file location**: `.github/workflows/auto-apply-jobs.yml`
- **Should be on**: `main` branch ✅
- **Code it runs**: From `auto-apply-feature` branch (checked out in workflow)

## How to Commit Workflow Changes

### If you're on main branch (current):
```bash
# 1. Make sure file is saved
# 2. Check status
git status

# 3. Add and commit
git add .github/workflows/auto-apply-jobs.yml
git commit -m "Update auto-apply workflow configuration"
git push secondary main
```

### Optional: Sync to auto-apply-feature branch
If you want the workflow file on both branches:
```bash
# After committing to main, optionally sync to auto-apply-feature
git checkout auto-apply-feature
git checkout main -- .github/workflows/auto-apply-jobs.yml
git add .github/workflows/auto-apply-jobs.yml
git commit -m "Sync workflow file from main"
git push secondary auto-apply-feature
git checkout main  # Switch back to main
```

## Important Notes

- **Main branch is primary**: The workflow file on `main` is what GitHub Actions uses for visibility
- **Code separation**: Even though workflow is on `main`, it runs code from `auto-apply-feature` branch
- **Workflow definition**: When you run the workflow and select branch `auto-apply-feature`, it uses the workflow definition from that branch (if different)

## Current Status

- ✅ You're on `main` branch
- ✅ Workflow file exists on `main`
- ⚠️ If you made changes, save the file first, then commit
