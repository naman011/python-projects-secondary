#!/usr/bin/env python3
"""Test script to check auto-apply logic without running the full application."""

import csv
import sys

def test_csv_reading():
    """Test how CSV is read and if Ready to Apply is preserved."""
    print("=" * 80)
    print("TEST 1: Reading CSV and checking 'Ready to Apply' field")
    print("=" * 80)
    
    try:
        with open('data/jobs.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            jobs = list(reader)
        
        print(f"Total jobs in CSV: {len(jobs)}")
        
        # Check how many have "Ready to Apply" = "Yes"
        ready_count = 0
        empty_count = 0
        no_count = 0
        
        sample_ready = []
        
        for job in jobs:
            ready = job.get('Ready to Apply', '').strip()
            if ready.lower() == 'yes':
                ready_count += 1
                if len(sample_ready) < 5:
                    sample_ready.append({
                        'title': job.get('Job Title', '')[:50],
                        'ready': ready,
                        'url': job.get('Job URL', '')[:60]
                    })
            elif ready.lower() == 'no':
                no_count += 1
            else:
                empty_count += 1
        
        print(f"\n'Ready to Apply' status:")
        print(f"  Yes: {ready_count}")
        print(f"  No: {no_count}")
        print(f"  Empty: {empty_count}")
        
        if sample_ready:
            print(f"\nSample jobs marked as 'Yes':")
            for i, job in enumerate(sample_ready, 1):
                print(f"  {i}. {job['title']}")
                print(f"     Ready: '{job['ready']}'")
                print(f"     URL: {job['url']}")
        
        return ready_count > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_writer_logic():
    """Test how CSVWriter converts column names."""
    print("\n" + "=" * 80)
    print("TEST 2: Testing CSVWriter.read_jobs() logic")
    print("=" * 80)
    
    try:
        from utils.csv_writer import CSVWriter
        
        csv_writer = CSVWriter('data/jobs.csv')
        jobs = csv_writer.read_jobs()
        
        print(f"Jobs read via CSVWriter: {len(jobs)}")
        
        # Check ready_to_apply field (lowercase with underscore)
        ready_count = 0
        sample_ready = []
        
        for job in jobs:
            ready = job.get('ready_to_apply', '').strip()
            if ready.lower() == 'yes':
                ready_count += 1
                if len(sample_ready) < 5:
                    sample_ready.append({
                        'title': job.get('title', '')[:50],
                        'ready': ready,
                        'url': job.get('url', '')[:60]
                    })
        
        print(f"\nJobs with ready_to_apply='yes': {ready_count}")
        
        if sample_ready:
            print(f"\nSample jobs with ready_to_apply='yes':")
            for i, job in enumerate(sample_ready, 1):
                print(f"  {i}. {job['title']}")
                print(f"     ready_to_apply: '{job['ready']}'")
                print(f"     URL: {job['url']}")
        
        return ready_count > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_application_manager_logic():
    """Test ApplicationManager.get_jobs_to_apply() logic."""
    print("\n" + "=" * 80)
    print("TEST 3: Testing ApplicationManager.get_jobs_to_apply() logic")
    print("=" * 80)
    
    try:
        # Simulate the logic from application_manager.py
        from utils.csv_writer import CSVWriter
        
        csv_writer = CSVWriter('data/jobs.csv')
        jobs = csv_writer.read_jobs()
        
        # Filter jobs ready to apply (same logic as ApplicationManager)
        ready_jobs = []
        for job in jobs:
            ready_to_apply = job.get('ready_to_apply', '').strip().lower()
            applied = job.get('applied', '').strip().lower()
            
            # Skip if already applied
            if applied in ['yes', 'true', '1']:
                continue
            
            # Check if ready to apply
            if ready_to_apply in ['yes', 'true', '1', 'y']:
                ready_jobs.append(job)
        
        print(f"Jobs found by ApplicationManager logic: {len(ready_jobs)}")
        
        if ready_jobs:
            print(f"\nSample jobs that would be processed:")
            for i, job in enumerate(ready_jobs[:10], 1):
                print(f"  {i}. {job.get('title', 'Unknown')[:50]}")
                print(f"     Company: {job.get('company', 'Unknown')[:40]}")
                print(f"     ready_to_apply: '{job.get('ready_to_apply', '')}'")
                print(f"     applied: '{job.get('applied', '')}'")
                print(f"     URL: {job.get('url', '')[:60]}")
                print()
        
        return len(ready_jobs) > 0
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AUTO-APPLY LOGIC DIAGNOSTIC TEST")
    print("=" * 80)
    print()
    
    test1 = test_csv_reading()
    test2 = test_csv_writer_logic()
    test3 = test_application_manager_logic()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (CSV Reading): {'PASS' if test1 else 'FAIL'}")
    print(f"Test 2 (CSVWriter Logic): {'PASS' if test2 else 'FAIL'}")
    print(f"Test 3 (ApplicationManager Logic): {'PASS' if test3 else 'FAIL'}")
    print()
    
    if not test1:
        print("❌ ISSUE: CSV doesn't have jobs marked as 'Ready to Apply = Yes'")
    elif not test2:
        print("❌ ISSUE: CSVWriter.read_jobs() is not reading 'Ready to Apply' correctly")
    elif not test3:
        print("❌ ISSUE: ApplicationManager.get_jobs_to_apply() is not finding ready jobs")
    else:
        print("✅ All tests passed! The logic should work correctly.")
    
    sys.exit(0 if (test1 and test2 and test3) else 1)
