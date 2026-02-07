"""Application manager that orchestrates job applications."""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from auto_apply.profile_loader import ProfileLoader
from auto_apply.indeed_applier import IndeedApplier
from auto_apply.naukri_applier import NaukriApplier
from auto_apply.remote_board_applier import RemoteBoardApplier
from utils.csv_writer import CSVWriter
from utils.config import (
    CSV_OUTPUT_FILE,
    AUTO_APPLY_ENABLED,
    MAX_APPLICATIONS_PER_RUN,
    APPLY_ONLY_HIGH_PRIORITY,
    PRIORITY_THRESHOLD,
    APPLICATION_STATUS_APPLIED,
    APPLICATION_STATUS_FAILED,
    APPLICATION_STATUS_NEEDS_MANUAL_CHECK,
    APPLICATION_STATUS_SKIPPED,
    METHOD_API,
    METHOD_SELENIUM,
    METHOD_MANUAL
)

logger = logging.getLogger(__name__)


class ApplicationManager:
    """Manages the job application process."""
    
    def __init__(self, csv_file: str = CSV_OUTPUT_FILE, profile_file: str = "data/user_profile.json"):
        """
        Initialize application manager.
        
        Args:
            csv_file: Path to jobs CSV file
            profile_file: Path to user profile JSON file
        """
        self.csv_file = csv_file
        self.csv_writer = CSVWriter(csv_file)
        self.profile_loader = ProfileLoader(profile_file)
        
        # Initialize appliers
        self.appliers = [
            IndeedApplier(self.profile_loader),
            NaukriApplier(self.profile_loader),
            RemoteBoardApplier(self.profile_loader),
        ]
        
        # Application logs directory
        self.logs_dir = "data/application_logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'needs_manual': 0
        }
    
    def get_jobs_to_apply(self) -> List[Dict]:
        """
        Get jobs marked as ready to apply from CSV.
        
        Returns:
            List of job dictionaries
        """
        jobs = self.csv_writer.read_jobs()
        
        # Filter jobs ready to apply
        ready_jobs = []
        for job in jobs:
            ready_to_apply = job.get('ready_to_apply', '').strip().lower()
            applied = job.get('applied', '').strip().lower()
            
            # Skip if already applied
            if applied in ['yes', 'true', '1']:
                continue
            
            # Check if ready to apply
            if ready_to_apply in ['yes', 'true', '1', 'y']:
                # Check priority threshold if enabled
                if APPLY_ONLY_HIGH_PRIORITY:
                    priority_score = job.get('priority_score', '')
                    try:
                        score = float(priority_score) if priority_score else 0
                        if score < PRIORITY_THRESHOLD:
                            continue
                    except (ValueError, TypeError):
                        pass
                
                ready_jobs.append(job)
        
        # Sort by priority score (highest first)
        ready_jobs.sort(
            key=lambda x: float(x.get('priority_score', 0) or 0),
            reverse=True
        )
        
        # Limit by MAX_APPLICATIONS_PER_RUN
        if MAX_APPLICATIONS_PER_RUN > 0:
            ready_jobs = ready_jobs[:MAX_APPLICATIONS_PER_RUN]
        
        return ready_jobs
    
    def find_applier(self, job: Dict) -> Optional[Any]:
        """
        Find appropriate applier for a job.
        
        Args:
            job: Job dictionary
            
        Returns:
            Applier instance or None
        """
        job_url = job.get('url', '')
        source = job.get('source', '')
        
        for applier in self.appliers:
            if applier.can_handle(job_url, source):
                return applier
        
        return None
    
    def apply_to_job(self, job: Dict) -> Dict[str, Any]:
        """
        Apply to a single job.
        
        Args:
            job: Job dictionary
            
        Returns:
            Application result dictionary
        """
        job_url = job.get('url', '')
        job_title = job.get('title', 'Unknown')
        company = job.get('company', 'Unknown')
        
        logger.info(f"Applying to: {job_title} at {company}")
        
        # Find appropriate applier
        applier = self.find_applier(job)
        if not applier:
            result = {
                'success': False,
                'method': METHOD_MANUAL,
                'error': 'No applier found for this job source',
                'error_category': 'Unsupported Source',
                'message': f'No automated applier available for source: {job.get("source", "Unknown")}'
            }
        else:
            # Apply using the applier
            result = applier.apply(job)
        
        # Update job in CSV
        self._update_job_status(job, result)
        
        # Log application
        self._log_application(job, result)
        
        # Update statistics
        self.stats['total_processed'] += 1
        if result.get('success'):
            self.stats['successful'] += 1
        elif result.get('error_category') == 'Unsupported Source':
            self.stats['skipped'] += 1
        elif result.get('error_category') == 'Needs Manual Check':
            self.stats['needs_manual'] += 1
        else:
            self.stats['failed'] += 1
        
        return result
    
    def _update_job_status(self, job: Dict, result: Dict[str, Any]):
        """
        Update job status in CSV.
        
        Args:
            job: Job dictionary
            result: Application result
        """
        job_url = job.get('url', '')
        if not job_url:
            return
        
        updates = {
            'application_method': result.get('method', ''),
            'application_error': result.get('error', '') or '',
        }
        
        if result.get('success'):
            updates['applied'] = 'Yes'
            updates['applied_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updates['status'] = APPLICATION_STATUS_APPLIED
        else:
            error_category = result.get('error_category', '')
            if error_category == 'Unsupported Source':
                updates['status'] = APPLICATION_STATUS_SKIPPED
            elif error_category == 'Needs Manual Check':
                updates['status'] = APPLICATION_STATUS_NEEDS_MANUAL_CHECK
            else:
                updates['status'] = APPLICATION_STATUS_FAILED
        
        # Update CSV
        try:
            self.csv_writer.update_job(job_url, updates)
        except Exception as e:
            logger.error(f"Failed to update job in CSV: {e}")
    
    def _log_application(self, job: Dict, result: Dict[str, Any]):
        """
        Log application attempt to file.
        
        Args:
            job: Job dictionary
            result: Application result
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'job': {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'url': job.get('url', ''),
                'source': job.get('source', '')
            },
            'result': result
        }
        
        log_file = os.path.join(self.logs_dir, f"applications_{datetime.now().strftime('%Y%m%d')}.jsonl")
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write application log: {e}")
    
    def process_applications(self) -> Dict[str, Any]:
        """
        Process all jobs ready to apply.
        
        Returns:
            Summary dictionary with statistics
        """
        if not AUTO_APPLY_ENABLED:
            logger.warning("Auto-apply is disabled in configuration")
            return {
                'success': False,
                'message': 'Auto-apply is disabled. Set AUTO_APPLY_ENABLED = True in config.py',
                'stats': self.stats
            }
        
        # Load user profile
        try:
            self.profile_loader.load()
        except Exception as e:
            logger.error(f"Failed to load user profile: {e}")
            return {
                'success': False,
                'message': f'Failed to load user profile: {e}',
                'stats': self.stats
            }
        
        # Get jobs to apply
        jobs = self.get_jobs_to_apply()
        
        if not jobs:
            logger.info("No jobs marked as ready to apply")
            return {
                'success': True,
                'message': 'No jobs ready to apply',
                'stats': self.stats
            }
        
        logger.info(f"Found {len(jobs)} jobs ready to apply")
        
        # Process each job
        for job in jobs:
            try:
                self.apply_to_job(job)
            except Exception as e:
                logger.error(f"Error applying to job {job.get('url', 'Unknown')}: {e}")
                self.stats['failed'] += 1
        
        # Generate report
        report = self._generate_report()
        
        return {
            'success': True,
            'message': f'Processed {self.stats["total_processed"]} applications',
            'stats': self.stats,
            'report': report
        }
    
    def _generate_report(self) -> str:
        """
        Generate application report.
        
        Returns:
            Report text
        """
        report_lines = [
            "=" * 60,
            "Application Report",
            "=" * 60,
            f"Total Processed: {self.stats['total_processed']}",
            f"Successful: {self.stats['successful']}",
            f"Failed: {self.stats['failed']}",
            f"Skipped: {self.stats['skipped']}",
            f"Needs Manual Check: {self.stats['needs_manual']}",
            "=" * 60,
        ]
        
        report = '\n'.join(report_lines)
        
        # Save report to file
        report_file = os.path.join(
            self.logs_dir,
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return report
