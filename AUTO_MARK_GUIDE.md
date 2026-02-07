# Auto-Mark Jobs as "Ready to Apply" - Guide

## Answer: Do You Need to Mark Manually?

**Short Answer**: Yes, but you can automate it! 

The auto-apply system requires jobs to have `Ready to Apply = Yes` in the CSV. However, you can use the auto-mark script to automatically mark jobs based on criteria instead of doing it manually.

## Option 1: Automatic Marking (Recommended)

Use the script to automatically mark jobs based on criteria:

### Basic Usage
```bash
# Mark top 10 freshest jobs (any priority score)
python3 scripts/auto_mark_ready_to_apply.py --max-jobs 10

# Mark jobs with priority >= 50, max 30 days old
python3 scripts/auto_mark_ready_to_apply.py --min-priority 50 --max-days 30 --max-jobs 10

# Dry run first (see what would be marked)
python3 scripts/auto_mark_ready_to_apply.py --max-jobs 10 --dry-run
```

### Advanced Options
```bash
# Mark top 20 jobs with:
# - Priority >= 50
# - Posted within last 14 days
# - Skills match >= 30%
python3 scripts/auto_mark_ready_to_apply.py \
  --min-priority 50 \
  --max-days 14 \
  --min-skills 30 \
  --max-jobs 20
```

### Full Options
```bash
python3 scripts/auto_mark_ready_to_apply.py --help
```

## Option 2: Manual Marking

If you prefer to review each job manually:

1. Open `data/jobs.csv` in Excel/Google Sheets
2. Sort by `Priority Score` (descending)
3. Review top jobs
4. Set `Ready to Apply = Yes` for jobs you want
5. Save and commit

## Recommended Workflow

### First Time Setup
```bash
# 1. Dry run to see what would be marked
python3 scripts/auto_mark_ready_to_apply.py --max-jobs 10 --dry-run

# 2. If looks good, actually mark them
python3 scripts/auto_mark_ready_to_apply.py --max-jobs 10

# 3. Commit the changes
git add data/jobs.csv
git commit -m "Auto-mark jobs as Ready to Apply"
git push secondary main

# 4. Run auto-apply workflow
# Go to GitHub Actions and trigger the workflow
```

### Regular Use
```bash
# After each scraper run, auto-mark new jobs
python3 scripts/auto_mark_ready_to_apply.py --max-jobs 10 --max-days 7

# Commit and push
git add data/jobs.csv && git commit -m "Mark new jobs ready" && git push secondary main
```

## Criteria Explained

- **Priority Score**: Higher = better match (0-100)
- **Days Since Posted**: Lower = fresher job (0-999)
- **Skills Match %**: Higher = better skills match (0-100)
- **Max Jobs**: Limit how many to mark per run

## Current Status

From your CSV:
- **Total Jobs**: 489
- **Currently Marked**: 0
- **Priority Scores**: Most appear to be empty (0)

**Recommendation**: Since priority scores are empty, use:
```bash
# Mark freshest jobs (any score)
python3 scripts/auto_mark_ready_to_apply.py --max-days 30 --max-jobs 10
```

This will mark the 10 freshest jobs (posted within last 30 days) regardless of priority score.

## After Marking

1. **Commit changes**: `git add data/jobs.csv && git commit -m "Mark jobs ready" && git push secondary main`
2. **Run workflow**: Trigger auto-apply workflow in GitHub Actions
3. **Check results**: Use `./CHECK_IMPACT.sh` to see applied jobs
