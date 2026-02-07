#!/bin/bash

echo "=== Auto-Apply Workflow Status Check ==="
echo ""

# Check CSV status
echo "📊 CSV Status:"
TOTAL=$(tail -n +2 data/jobs.csv | wc -l | tr -d ' ')
READY=$(grep -c ',Yes,' data/jobs.csv 2>/dev/null | grep -v "Ready to Apply" || echo "0")
APPLIED=$(grep -c ',Yes,' data/jobs.csv 2>/dev/null | grep "Applied" || echo "0")

echo "  Total jobs: $TOTAL"
echo "  Ready to Apply: $(python3 -c "import csv; f=open('data/jobs.csv'); r=csv.DictReader(f); jobs=list(r); print(sum(1 for j in jobs if j.get('Ready to Apply','').strip().lower() in ['yes','true','1']))")"
echo "  Applied: $(python3 -c "import csv; f=open('data/jobs.csv'); r=csv.DictReader(f); jobs=list(r); print(sum(1 for j in jobs if j.get('Applied','').strip().lower() in ['yes','true','1']))")"
echo ""

# Check for auto-apply commits
echo "📝 Recent Commits:"
git log --oneline -10 --all --grep="\[auto-apply\]" 2>/dev/null | head -5
if [ $? -ne 0 ] || [ -z "$(git log --oneline -10 --all --grep='\[auto-apply\]' 2>/dev/null)" ]; then
    echo "  ⚠️  No [auto-apply] commits found"
    echo "  This means workflow may not have completed or committed changes"
fi
echo ""

# Check CSV file commits
echo "📄 Recent CSV Updates:"
git log --oneline -5 -- data/jobs.csv | head -3
echo ""

echo "🔗 Check GitHub Actions:"
echo "  https://github.com/naman011/python-projects-secondary/actions/workflows/auto-apply-jobs.yml"
echo ""
echo "💡 If workflow completed but Applied=0:"
echo "  1. Check if jobs were marked as 'Ready to Apply = Yes'"
echo "  2. Check workflow logs for errors"
echo "  3. Download artifacts to see detailed logs"
