#!/bin/bash

echo "=========================================="
echo "Checking Scraper & Auto-Apply Impact"
echo "=========================================="
echo ""

# 1. Pull latest changes
echo "1. Pulling latest changes from remote..."
git pull secondary main
echo ""

# 2. Check git status
echo "2. Checking git status..."
git status
echo ""

# 3. Check recent commits
echo "3. Recent commits:"
git log --oneline -10
echo ""

# 4. Check if jobs.csv was updated
echo "4. Checking jobs.csv updates..."
if [ -f "data/jobs.csv" ]; then
    echo "  - File exists"
    echo "  - Last modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" data/jobs.csv)"
    echo "  - Total lines: $(wc -l < data/jobs.csv)"
    echo "  - File size: $(du -h data/jobs.csv | cut -f1)"
else
    echo "  - File not found"
fi
echo ""

# 5. Check applied jobs count
echo "5. Checking applied jobs..."
if [ -f "data/jobs.csv" ]; then
    echo "  - Jobs marked as 'Applied': $(grep -c ',Applied,' data/jobs.csv || echo 0)"
    echo "  - Jobs with 'Application Method': $(grep -c 'Application Method' data/jobs.csv || echo 0)"
    echo "  - Jobs with 'Ready to Apply': $(grep -c 'Ready to Apply' data/jobs.csv || echo 0)"
    echo "  - Jobs with errors: $(grep -c 'Application Error' data/jobs.csv | grep -v '^$' || echo 0)"
fi
echo ""

# 6. Show sample of applied jobs
echo "6. Sample of applied jobs (last 5):"
if [ -f "data/jobs.csv" ]; then
    grep -i "Applied" data/jobs.csv | tail -5 | cut -d',' -f1-5
fi
echo ""

# 7. Check for workflow artifacts
echo "7. Checking for workflow artifacts..."
if [ -d ".github/workflows" ]; then
    echo "  - Workflow files found"
    ls -la .github/workflows/
fi
echo ""

# 8. Check data directory
echo "8. Data directory contents:"
ls -lh data/ 2>/dev/null | head -10
echo ""

# 9. Check for log files
echo "9. Checking for log files..."
find . -name "*.log" -type f 2>/dev/null | head -5
echo ""

echo "=========================================="
echo "Summary:"
echo "=========================================="
echo "To view detailed results:"
echo "  - View jobs.csv: cat data/jobs.csv | less"
echo "  - Filter applied jobs: grep -i 'Applied' data/jobs.csv"
echo "  - Check GitHub Actions: https://github.com/naman011/python-projects-secondary/actions"
echo ""
