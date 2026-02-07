#!/bin/bash

echo "=== Cleaning Up Unstaged Files ==="
echo ""

# 1. Update .gitignore (already done)
echo "✅ .gitignore updated (sensitive files now ignored)"
echo ""

# 2. Remove files that belong on auto-apply-feature branch
echo "Removing files from wrong branch..."
if [ -f "apply_jobs.py" ]; then
    rm apply_jobs.py
    echo "  ✅ Removed apply_jobs.py (belongs on auto-apply-feature branch)"
fi

if [ -d "scripts" ]; then
    rm -rf scripts/
    echo "  ✅ Removed scripts/ (belongs on auto-apply-feature branch)"
fi
echo ""

# 3. Show what's left
echo "Remaining files:"
git status --short | grep "^??" | head -15
echo ""

echo "Options:"
echo "1. Commit documentation files (recommended)"
echo "2. Keep everything local (no commit)"
echo ""
echo "To commit docs, run:"
echo "  git add *.md CHECK_WORKFLOW_STATUS.sh .gitignore"
echo "  git commit -m 'Add auto-apply documentation'"
echo "  git push secondary main"
