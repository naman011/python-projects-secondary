"""CSV writer for job output with clickable URLs."""

import csv
import os
import re
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse
from utils.config import CSV_OUTPUT_FILE, MAX_DESCRIPTION_LENGTH


class CSVWriter:
    """Write jobs to CSV file with clickable URLs."""
    
    def __init__(self, output_file: str = CSV_OUTPUT_FILE):
        """
        Initialize CSV writer.
        
        Args:
            output_file: Path to output CSV file
        """
        self.output_file = output_file
        self.fieldnames = [
            'Job Title',
            'Company',
            'Location',
            'Experience Required',
            'Job URL',
            'Posted Date',
            'Source',
            'Description',
            'Priority Score',
            'Days Since Posted',
            'Freshness',
            'Salary',
            'Deadline',
            'Days Until Deadline',
            'Skills Match %',
            'Ready to Apply',
            'Applied',
            'Applied Date',
            'Application Method',
            'Application Error',
            'Status',
            'Notes'
        ]
    
    def _sanitize_csv_value(self, value: str) -> str:
        """
        Sanitize CSV value to prevent CSV injection attacks.
        Excel/Google Sheets interpret =, +, -, @ as formula starters.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized value
        """
        if not value:
            return ""
        
        # Convert to string if not already
        value = str(value)
        
        # If value starts with formula characters, prefix with tab
        if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
            return "'" + value
        
        return value
    
    def _truncate_description(self, description: str) -> str:
        """
        Truncate description if too long.
        
        Args:
            description: Job description
            
        Returns:
            Truncated description
        """
        if not description:
            return ""
        
        description = str(description)
        
        if len(description) > MAX_DESCRIPTION_LENGTH:
            return description[:MAX_DESCRIPTION_LENGTH] + "..."
        
        return description
    
    def _format_url(self, url: str) -> str:
        """
        Format URL to be clickable in CSV.
        
        Args:
            url: Job URL
            
        Returns:
            Formatted URL
        """
        if not url:
            return ""
        
        url = str(url).strip()
        
        # Basic URL validation
        if not url or len(url) > 2048:  # Max URL length
            return ""
        
        # Ensure URL is complete
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Basic validation - check for valid URL pattern
        # More lenient pattern to allow various URL formats
        try:
            parsed = urlparse(url)
            # Check if it has a scheme and netloc
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                return url
        except Exception:
            pass
        
        # If URL doesn't pass validation, sanitize and return
        return self._sanitize_csv_value(url)
    
    def write_jobs(self, jobs: List[Dict], mode: str = 'w'):
        """
        Write jobs to CSV file.
        
        Args:
            jobs: List of job dictionaries
            mode: File write mode ('w' for overwrite, 'a' for append)
        """
        # Create data directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        file_exists = os.path.exists(self.output_file) and mode == 'a'
        
        with open(self.output_file, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            
            # Write header if new file
            if not file_exists:
                writer.writeheader()
            
            # Write jobs
            for job in jobs:
                if not job or not isinstance(job, dict):
                    continue
                
                # Handle new columns with defaults for backward compatibility
                priority_score = job.get('priority_score', '')
                days_since_posted = job.get('days_since_posted', '')
                freshness = job.get('freshness', '')
                salary = job.get('salary', '')
                deadline = job.get('deadline', '')
                days_until_deadline = job.get('days_until_deadline', '')
                skills_match_pct = job.get('skills_match_pct', '')
                
                # Automatically mark all new jobs as "Ready to Apply = Yes"
                # Only preserve existing value if job already has it set
                ready_to_apply = job.get('ready_to_apply', '')
                if not ready_to_apply or ready_to_apply.strip() == '':
                    ready_to_apply = 'Yes'  # Auto-mark new jobs
                else:
                    ready_to_apply = ready_to_apply.strip()  # Preserve existing value
                
                row = {
                    'Job Title': self._sanitize_csv_value(job.get('title', '') or ''),
                    'Company': self._sanitize_csv_value(job.get('company', '') or ''),
                    'Location': self._sanitize_csv_value(job.get('location', '') or ''),
                    'Experience Required': self._sanitize_csv_value(job.get('experience', '') or ''),
                    'Job URL': self._format_url(job.get('url', '')),
                    'Posted Date': self._sanitize_csv_value(job.get('posted_date', '') or ''),
                    'Source': self._sanitize_csv_value(job.get('source', '') or ''),
                    'Description': self._truncate_description(job.get('description', '') or ''),
                    'Priority Score': self._sanitize_csv_value(str(priority_score) if priority_score != '' else ''),
                    'Days Since Posted': self._sanitize_csv_value(str(days_since_posted) if days_since_posted != '' else ''),
                    'Freshness': self._sanitize_csv_value(str(freshness) if freshness else ''),
                    'Salary': self._sanitize_csv_value(str(salary) if salary else ''),
                    'Deadline': self._sanitize_csv_value(str(deadline) if deadline else ''),
                    'Days Until Deadline': self._sanitize_csv_value(str(days_until_deadline) if days_until_deadline is not None else ''),
                    'Skills Match %': self._sanitize_csv_value(str(skills_match_pct) if skills_match_pct != '' else ''),
                    'Ready to Apply': self._sanitize_csv_value(ready_to_apply),
                    'Applied': self._sanitize_csv_value(job.get('applied', 'No') or 'No'),
                    'Applied Date': self._sanitize_csv_value(job.get('applied_date', '') or ''),
                    'Application Method': self._sanitize_csv_value(job.get('application_method', '') or ''),
                    'Application Error': self._sanitize_csv_value(job.get('application_error', '') or ''),
                    'Status': self._sanitize_csv_value(job.get('status', 'Not Applied') or 'Not Applied'),
                    'Notes': self._sanitize_csv_value(job.get('notes', '') or '')
                }
                writer.writerow(row)

    def write_timestamped_jobs(self, jobs: List[Dict], directory: str) -> str:
        """
        Write jobs to a new CSV file whose name includes the current timestamp.

        Args:
            jobs: List of job dictionaries
            directory: Directory where timestamped CSV should be created

        Returns:
            Path to the created CSV file
        """
        if not jobs:
            return ""

        # Ensure directory exists
        os.makedirs(directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(directory, f"jobs_{timestamp}.csv")

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()

            for job in jobs:
                if not job or not isinstance(job, dict):
                    continue

                # Handle new columns with defaults for backward compatibility
                priority_score = job.get('priority_score', '')
                days_since_posted = job.get('days_since_posted', '')
                freshness = job.get('freshness', '')
                salary = job.get('salary', '')
                deadline = job.get('deadline', '')
                days_until_deadline = job.get('days_until_deadline', '')
                skills_match_pct = job.get('skills_match_pct', '')
                
                # Automatically mark all new jobs as "Ready to Apply = Yes"
                # Only preserve existing value if job already has it set
                ready_to_apply = job.get('ready_to_apply', '')
                if not ready_to_apply or ready_to_apply.strip() == '':
                    ready_to_apply = 'Yes'  # Auto-mark new jobs
                else:
                    ready_to_apply = ready_to_apply.strip()  # Preserve existing value

                row = {
                    'Job Title': self._sanitize_csv_value(job.get('title', '') or ''),
                    'Company': self._sanitize_csv_value(job.get('company', '') or ''),
                    'Location': self._sanitize_csv_value(job.get('location', '') or ''),
                    'Experience Required': self._sanitize_csv_value(job.get('experience', '') or ''),
                    'Job URL': self._format_url(job.get('url', '')),
                    'Posted Date': self._sanitize_csv_value(job.get('posted_date', '') or ''),
                    'Source': self._sanitize_csv_value(job.get('source', '') or ''),
                    'Description': self._truncate_description(job.get('description', '') or ''),
                    'Priority Score': self._sanitize_csv_value(str(priority_score) if priority_score != '' else ''),
                    'Days Since Posted': self._sanitize_csv_value(str(days_since_posted) if days_since_posted != '' else ''),
                    'Freshness': self._sanitize_csv_value(str(freshness) if freshness else ''),
                    'Salary': self._sanitize_csv_value(str(salary) if salary else ''),
                    'Deadline': self._sanitize_csv_value(str(deadline) if deadline else ''),
                    'Days Until Deadline': self._sanitize_csv_value(str(days_until_deadline) if days_until_deadline is not None else ''),
                    'Skills Match %': self._sanitize_csv_value(str(skills_match_pct) if skills_match_pct != '' else ''),
                    'Ready to Apply': self._sanitize_csv_value(ready_to_apply),
                    'Applied': self._sanitize_csv_value(job.get('applied', 'No') or 'No'),
                    'Applied Date': self._sanitize_csv_value(job.get('applied_date', '') or ''),
                    'Application Method': self._sanitize_csv_value(job.get('application_method', '') or ''),
                    'Application Error': self._sanitize_csv_value(job.get('application_error', '') or ''),
                    'Status': self._sanitize_csv_value(job.get('status', 'Not Applied') or 'Not Applied'),
                    'Notes': self._sanitize_csv_value(job.get('notes', '') or '')
                }
                writer.writerow(row)

        return output_path
    
    def append_jobs(self, jobs: List[Dict]):
        """
        Append jobs to existing CSV file.
        
        Args:
            jobs: List of job dictionaries
        """
        self.write_jobs(jobs, mode='a')
    
    def get_existing_urls(self) -> set:
        """
        Get set of existing job URLs from CSV to avoid duplicates.
        
        Returns:
            Set of existing job URLs
        """
        existing_urls = set()
        
        if not os.path.exists(self.output_file):
            return existing_urls
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    url = row.get('Job URL', '').strip()
                    if url:
                        existing_urls.add(url)
        except Exception as e:
            print(f"Error reading existing CSV: {e}")
        
        return existing_urls
