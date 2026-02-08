#!/usr/bin/env python3
"""Test to see if update_job() clears Ready to Apply field."""

from utils.csv_writer import CSVWriter
import csv

print("=" * 80)
print("TESTING update_job() - Does it preserve 'Ready to Apply'?")
print("=" * 80)

# Read a job that's marked as ready
csv_writer = CSVWriter('data/jobs.csv')
jobs = csv_writer.read_jobs()

# Find a job marked as ready
ready_job = None
for job in jobs:
    if job.get('ready_to_apply', '').strip().lower() == 'yes':
        ready_job = job
        break

if not ready_job:
    print("No job marked as ready found!")
    exit(1)

print(f"\nBefore update:")
print(f"  Title: {ready_job.get('title', '')[:50]}")
print(f"  ready_to_apply: '{ready_job.get('ready_to_apply', '')}'")
print(f"  URL: {ready_job.get('url', '')[:60]}")

# Simulate what update_job() does
job_url = ready_job.get('url', '')
updates = {
    'application_method': 'TEST',
    'application_error': 'TEST ERROR',
    'status': 'Failed'
}

print(f"\nSimulating update_job() with:")
print(f"  updates: {updates}")

# Read all jobs
all_jobs = csv_writer.read_jobs()

# Find and update the job (same logic as update_job)
updated = False
for job in all_jobs:
    if job.get('url', '').strip() == job_url.strip():
        print(f"\nFound job to update:")
        print(f"  Before update - ready_to_apply: '{job.get('ready_to_apply', '')}'")
        job.update(updates)
        print(f"  After update - ready_to_apply: '{job.get('ready_to_apply', '')}'")
        updated = True
        break

if updated:
    # Check what write_jobs would do
    print(f"\nChecking what write_jobs() would do:")
    from utils.csv_writer import CSVWriter
    
    # Create a test CSV writer
    test_writer = CSVWriter('data/jobs_test.csv')
    
    # Write the updated jobs
    test_writer.write_jobs(all_jobs, mode='w')
    
    # Read back and check
    written_jobs = test_writer.read_jobs()
    for job in written_jobs:
        if job.get('url', '').strip() == job_url.strip():
            print(f"  After write_jobs() - ready_to_apply: '{job.get('ready_to_apply', '')}'")
            print(f"  After write_jobs() - status: '{job.get('status', '')}'")
            break
    
    # Clean up
    import os
    if os.path.exists('data/jobs_test.csv'):
        os.remove('data/jobs_test.csv')
    
    print("\n✅ Test complete - check if ready_to_apply was preserved")
