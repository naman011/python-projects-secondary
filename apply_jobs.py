#!/usr/bin/env python3
"""CLI entry point for auto-apply system."""

import sys
import argparse
import logging
from auto_apply.application_manager import ApplicationManager
from utils.config import AUTO_APPLY_ENABLED

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Auto-apply to jobs marked as ready in CSV'
    )
    parser.add_argument(
        '--csv',
        type=str,
        default='data/jobs.csv',
        help='Path to jobs CSV file (default: data/jobs.csv)'
    )
    parser.add_argument(
        '--profile',
        type=str,
        default='data/user_profile.json',
        help='Path to user profile JSON file (default: data/user_profile.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode - show what would be applied without actually applying'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if auto-apply is enabled
    if not AUTO_APPLY_ENABLED:
        print("=" * 60)
        print("WARNING: Auto-apply is disabled")
        print("=" * 60)
        print("To enable auto-apply, set AUTO_APPLY_ENABLED = True in utils/config.py")
        print()
        response = input("Do you want to continue anyway? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Exiting.")
            sys.exit(0)
    
    print("=" * 60)
    print("Job Auto-Apply System")
    print("=" * 60)
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No applications will be submitted")
        print()
    
    # Initialize application manager
    try:
        manager = ApplicationManager(csv_file=args.csv, profile_file=args.profile)
    except Exception as e:
        logger.error(f"Failed to initialize application manager: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    
    if args.dry_run:
        # Just show what would be applied
        jobs = manager.get_jobs_to_apply()
        print(f"Found {len(jobs)} jobs ready to apply:")
        print("-" * 60)
        for idx, job in enumerate(jobs, 1):
            print(f"{idx}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"   URL: {job.get('url', '')}")
            print(f"   Source: {job.get('source', 'Unknown')}")
            print(f"   Priority Score: {job.get('priority_score', 'N/A')}")
            print()
        
        print(f"Total: {len(jobs)} jobs would be processed")
        return
    
    # Process applications
    try:
        result = manager.process_applications()
        
        print()
        print("=" * 60)
        print("Application Summary")
        print("=" * 60)
        print(result.get('message', 'Completed'))
        print()
        
        stats = result.get('stats', {})
        print("Statistics:")
        print(f"  Total Processed: {stats.get('total_processed', 0)}")
        print(f"  Successful: {stats.get('successful', 0)}")
        print(f"  Failed: {stats.get('failed', 0)}")
        print(f"  Skipped: {stats.get('skipped', 0)}")
        print(f"  Needs Manual Check: {stats.get('needs_manual', 0)}")
        print()
        
        if result.get('report'):
            print(result['report'])
        
        print("=" * 60)
        print("Check the CSV file for updated application statuses")
        print("Check data/application_logs/ for detailed logs")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nApplication process interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing applications: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
