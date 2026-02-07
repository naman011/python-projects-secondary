#!/usr/bin/env python3
"""
Script to automatically mark jobs as "Ready to Apply" based on criteria.
This helps avoid manual marking of jobs.
"""

import csv
import sys
from typing import List, Dict
from datetime import datetime

def auto_mark_jobs(
    csv_file: str = "data/jobs.csv",
    min_priority_score: float = 50.0,
    max_days_old: int = 30,
    min_skills_match: float = 0.0,
    max_jobs_to_mark: int = 10,
    exclude_already_applied: bool = True,
    exclude_already_marked: bool = True
) -> Dict:
    """
    Automatically mark jobs as "Ready to Apply" based on criteria.
    
    Args:
        csv_file: Path to jobs CSV file
        min_priority_score: Minimum priority score to mark (0-100)
        max_days_old: Maximum days since posted (fresher jobs preferred)
        min_skills_match: Minimum skills match percentage (0-100)
        max_jobs_to_mark: Maximum number of jobs to mark in one run
        exclude_already_applied: Skip jobs already applied to
        exclude_already_marked: Skip jobs already marked as ready
    
    Returns:
        Dictionary with statistics
    """
    
    # Read jobs
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            jobs = list(reader)
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)
    
    if not jobs:
        print("❌ No jobs found in CSV")
        sys.exit(1)
    
    print("=" * 80)
    print("Auto-Mark Jobs as 'Ready to Apply'")
    print("=" * 80)
    print(f"\nCriteria:")
    print(f"  - Minimum Priority Score: {min_priority_score}")
    print(f"  - Maximum Days Old: {max_days_old}")
    print(f"  - Minimum Skills Match: {min_skills_match}%")
    print(f"  - Max Jobs to Mark: {max_jobs_to_mark}")
    print()
    
    # Filter and score jobs
    eligible_jobs = []
    
    for job in jobs:
        # Skip if already applied
        if exclude_already_applied and job.get('Applied', '').strip().lower() in ['yes', 'true', '1']:
            continue
        
        # Skip if already marked
        if exclude_already_marked and job.get('Ready to Apply', '').strip().lower() in ['yes', 'true', '1']:
            continue
        
        # Parse priority score
        priority_str = job.get('Priority Score', '').strip()
        try:
            priority = float(priority_str) if priority_str else 0.0
        except (ValueError, TypeError):
            priority = 0.0
        
        # Parse days since posted
        days_str = job.get('Days Since Posted', '').strip()
        try:
            days_old = int(days_str) if days_str else 999
        except (ValueError, TypeError):
            days_old = 999
        
        # Parse skills match
        skills_str = job.get('Skills Match %', '').strip()
        try:
            skills_match = float(skills_str.replace('%', '').strip()) if skills_str else 0.0
        except (ValueError, TypeError):
            skills_match = 0.0
        
        # If all scores are empty/zero, use a default score based on other factors
        if priority == 0.0 and days_old == 999 and skills_match == 0.0:
            # Give default eligibility - mark if it has a valid URL and title
            has_url = bool(job.get('Job URL', '').strip())
            has_title = bool(job.get('Job Title', '').strip())
            if has_url and has_title:
                # Default eligible - will be sorted by other factors
                priority = 50.0  # Default priority
                days_old = 0     # Assume fresh if no data
                skills_match = 50.0  # Default match
        
        # Check criteria (relaxed for empty data)
        if priority >= min_priority_score and days_old <= max_days_old and skills_match >= min_skills_match:
            eligible_jobs.append({
                'job': job,
                'priority': priority,
                'days_old': days_old,
                'skills_match': skills_match,
                'score': priority + (100 - days_old) * 0.1 + skills_match * 0.1  # Combined score
            })
    
    # Sort by combined score (highest first)
    eligible_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit to max_jobs_to_mark
    jobs_to_mark = eligible_jobs[:max_jobs_to_mark]
    
    print(f"Found {len(eligible_jobs)} eligible jobs")
    print(f"Marking top {len(jobs_to_mark)} jobs as 'Ready to Apply'\n")
    
    # Mark jobs
    marked_count = 0
    for item in jobs_to_mark:
        job = item['job']
        job['Ready to Apply'] = 'Yes'
        marked_count += 1
        print(f"✅ Marked: {job.get('Job Title', 'N/A')[:50]} at {job.get('Company', 'N/A')}")
        print(f"   Priority: {item['priority']:.1f}, Days Old: {item['days_old']}, Skills Match: {item['skills_match']:.1f}%")
    
    # Write back to CSV
    if marked_count > 0:
        fieldnames = list(jobs[0].keys())
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(jobs)
        
        print(f"\n✅ Successfully marked {marked_count} jobs as 'Ready to Apply'")
        print(f"📄 Updated: {csv_file}")
    else:
        print("\n⚠️  No jobs matched the criteria")
    
    return {
        'total_jobs': len(jobs),
        'eligible': len(eligible_jobs),
        'marked': marked_count
    }

def main():
    """Main function with configurable options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-mark jobs as Ready to Apply')
    parser.add_argument('--min-priority', type=float, default=0.0,
                       help='Minimum priority score (default: 0.0 - mark all)')
    parser.add_argument('--max-days', type=int, default=90,
                       help='Maximum days since posted (default: 90)')
    parser.add_argument('--min-skills', type=float, default=0.0,
                       help='Minimum skills match percentage (default: 0.0)')
    parser.add_argument('--max-jobs', type=int, default=10,
                       help='Maximum jobs to mark (default: 10)')
    parser.add_argument('--csv', type=str, default='data/jobs.csv',
                       help='Path to jobs CSV file (default: data/jobs.csv)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be marked without actually marking')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
        # Temporarily redirect output to see what would be marked
        stats = auto_mark_jobs(
            csv_file=args.csv,
            min_priority_score=args.min_priority,
            max_days_old=args.max_days,
            min_skills_match=args.min_skills,
            max_jobs_to_mark=args.max_jobs
        )
        print(f"\n📊 Would mark {stats['marked']} jobs")
        return
    
    # Actually mark jobs
    stats = auto_mark_jobs(
        csv_file=args.csv,
        min_priority_score=args.min_priority,
        max_days_old=args.max_days,
        min_skills_match=args.min_skills,
        max_jobs_to_mark=args.max_jobs
    )
    
    print(f"\n📊 Summary:")
    print(f"  Total jobs: {stats['total_jobs']}")
    print(f"  Eligible: {stats['eligible']}")
    print(f"  Marked: {stats['marked']}")

if __name__ == "__main__":
    main()
