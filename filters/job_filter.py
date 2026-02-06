"""Job filtering logic for location, role, and experience."""

import re
from typing import Dict, List, Optional
from utils.config import (
    SEARCH_TERMS,
    INDIA_LOCATIONS,
    EXPERIENCE_LEVELS,
    EXCLUDE_KEYWORDS
)


class JobFilter:
    """Filter jobs based on location, role, and experience criteria."""
    
    def __init__(self):
        """Initialize the job filter."""
        self.search_terms = [term.lower() for term in SEARCH_TERMS]
        self.locations = [loc.lower() for loc in INDIA_LOCATIONS]
        self.experience_levels = [exp.lower() for exp in EXPERIENCE_LEVELS]
        self.exclude_keywords = [kw.lower() for kw in EXCLUDE_KEYWORDS]
    
    def matches_role(self, job_title: str, job_description: str = "") -> bool:
        """
        Check if job matches Software Engineer role.
        
        Args:
            job_title: Job title
            job_description: Job description (optional)
            
        Returns:
            True if job matches role criteria
        """
        text = f"{job_title} {job_description}".lower()
        
        # Check if any search term is in the text
        for term in self.search_terms:
            if term in text:
                return True
        
        return False
    
    def matches_location(self, location: str) -> bool:
        """
        Check if job location matches India or Remote.
        
        Args:
            location: Job location string
            
        Returns:
            True if location matches India/Remote criteria
        """
        if not location:
            return False
        
        location_lower = location.lower()
        
        # Check if location contains any of the India/Remote keywords
        for loc in self.locations:
            if loc in location_lower:
                return True
        
        return False
    
    def is_experience_eligible(self, job_title: str, job_description: str = "") -> bool:
        """
        Check if job is eligible based on experience (fresher or 1+ years).
        Excludes internships.
        
        Args:
            job_title: Job title
            job_description: Job description (optional)
            
        Returns:
            True if job is eligible (fresher or 1+ years, not internship)
        """
        text = f"{job_title} {job_description}".lower()
        
        # Exclude internships
        for exclude_kw in self.exclude_keywords:
            if exclude_kw in text:
                # Allow if it's explicitly "full-time" or "permanent"
                if "full-time" in text or "permanent" in text:
                    continue
                return False
        
        # Check for experience requirements
        # Look for patterns like "0-1 years", "1+ years", "fresher", etc.
        experience_patterns = [
            r'\b(0|zero)\s*(to|-)?\s*[1-2]\s*(years?|yrs?)\b',
            r'\b[1-5]\+\s*(years?|yrs?)\b',
            r'\b[1-5]\s*(to|-)\s*[1-9]\s*(years?|yrs?)\b',
            r'\bfresher\b',
            r'\bentry\s*level\b',
            r'\bjunior\b',
        ]
        
        # If no explicit experience mentioned, assume it's eligible
        has_experience_mention = any(re.search(pattern, text) for pattern in experience_patterns)
        
        if not has_experience_mention:
            # If no experience mentioned, include it (might be fresher or 1+)
            return True
        
        # Check if it matches our experience levels
        for exp_level in self.experience_levels:
            if exp_level in text:
                return True
        
        # Check for patterns that indicate too much experience (e.g., "4+ years", "senior")
        senior_patterns = [
            r'\b[4-9]\+\s*(years?|yrs?)\b',
            r'\b(1[0-9]|[2-9][0-9])\+\s*(years?|yrs?)\b',
            r'\bsenior\b',
            r'\blead\b',
            r'\bprincipal\b',
            r'\barchitect\b',
        ]
        
        # If it's clearly senior level, exclude it
        for pattern in senior_patterns:
            if re.search(pattern, text):
                return False
        
        # If experience is mentioned but doesn't match our criteria, check if it's reasonable
        # Look for "1 year", "2 years", etc. (1-3 years is acceptable)
        reasonable_exp = re.search(r'\b([1-3])\s*(years?|yrs?)\b', text)
        if reasonable_exp:
            return True
        
        # Default: include if no clear exclusion
        return True
    
    def filter_job(self, job: Dict) -> bool:
        """
        Filter a job based on all criteria.
        
        Args:
            job: Job dictionary with keys: title, company, location, description, etc.
            
        Returns:
            True if job passes all filters
        """
        if not job or not isinstance(job, dict):
            return False
        
        job_title = str(job.get('title', '') or '').lower()
        job_location = str(job.get('location', '') or '')
        job_description = str(job.get('description', '') or '').lower()
        
        # Check role match (keep this strict)
        if not self.matches_role(job_title, job_description):
            return False

        # TEMPORARILY relax location filtering to avoid dropping valid jobs.
        # Many company career pages don't include explicit "India"/city strings
        # in the location field, or use separate filters that we don't see here.
        #
        # If you want to re-enable strict location filtering later, uncomment:
        #
        # if not self.matches_location(job_location):
        #     return False

        # Keep experience-based exclusion (we only drop clear senior roles
        # and internships; everything else is allowed).
        if not self.is_experience_eligible(job_title, job_description):
            return False

        return True
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter a list of jobs.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Filtered list of jobs
        """
        return [job for job in jobs if self.filter_job(job)]
