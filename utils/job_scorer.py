"""Job scoring system for prioritizing opportunities."""

import json
import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional, List
from utils.salary_extractor import SalaryExtractor
from utils.deadline_extractor import DeadlineExtractor
from utils.config import YOUR_SKILLS

logger = logging.getLogger(__name__)


class JobScorer:
    """Calculate priority scores for jobs based on multiple factors."""
    
    def __init__(self, companies_metadata_file: str = "data/companies_metadata.json"):
        """
        Initialize job scorer.
        
        Args:
            companies_metadata_file: Path to companies metadata JSON file
        """
        self.companies_metadata = self._load_companies_metadata(companies_metadata_file)
        self.salary_extractor = SalaryExtractor()
        self.deadline_extractor = DeadlineExtractor()
        self.user_skills = [skill.lower() for skill in YOUR_SKILLS] if YOUR_SKILLS else []
    
    def _load_companies_metadata(self, filepath: str) -> Dict:
        """Load companies metadata from JSON file."""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Companies metadata file not found: {filepath}. Using empty dict.")
                return {}
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading companies metadata: {e}. Using empty dict.")
            return {}
    
    def _parse_posted_date(self, posted_date: str) -> Optional[datetime]:
        """
        Parse posted date string to datetime object.
        
        Handles various date formats:
        - "2024-01-15"
        - "Jan 15, 2024"
        - "15/01/2024"
        - "2 days ago", "1 week ago" (relative)
        """
        if not posted_date:
            return None
        
        posted_date = str(posted_date).strip()
        
        # Try common date formats
        date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(posted_date, fmt)
            except ValueError:
                continue
        
        # Try relative dates like "2 days ago", "1 week ago"
        from datetime import timedelta
        relative_patterns = [
            (r'(\d+)\s*days?\s*ago', lambda m: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(m.group(1)))),
            (r'(\d+)\s*weeks?\s*ago', lambda m: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(weeks=int(m.group(1)))),
            (r'(\d+)\s*months?\s*ago', lambda m: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=int(m.group(1)) * 30)),
        ]
        for pattern, func in relative_patterns:
            match = re.search(pattern, posted_date.lower())
            if match:
                try:
                    return func(match)
                except Exception:
                    continue
        
        return None
    
    def _calculate_days_since_posted(self, posted_date: str) -> Optional[int]:
        """Calculate days since job was posted."""
        parsed_date = self._parse_posted_date(posted_date)
        if not parsed_date:
            return None
        
        delta = datetime.now() - parsed_date
        return max(0, delta.days)
    
    def _get_freshness_indicator(self, days_since_posted: Optional[int]) -> str:
        """
        Get freshness indicator based on days since posted.
        
        Args:
            days_since_posted: Number of days since job was posted
            
        Returns:
            Freshness indicator: "Fresh" (<1 day), "Recent" (1-7 days), "Recent" (8-14 days), "Old" (>14 days)
        """
        if days_since_posted is None:
            return "Unknown"
        
        if days_since_posted <= 1:
            return "Fresh"
        elif days_since_posted <= 7:
            return "Recent"
        elif days_since_posted <= 14:
            return "Moderate"
        else:
            return "Old"
    
    def _get_company_tier(self, company: str) -> Optional[str]:
        """Get company tier (FAANG, unicorn, well_funded) from metadata."""
        if not company:
            return None
        
        # Try exact match first
        if company in self.companies_metadata:
            return self.companies_metadata[company].get('tier')
        
        # Try case-insensitive match
        company_lower = company.lower()
        for comp_name, metadata in self.companies_metadata.items():
            if comp_name.lower() == company_lower:
                return metadata.get('tier')
        
        # Try partial match (e.g., "Amazon Dev Center" -> "Amazon")
        for comp_name, metadata in self.companies_metadata.items():
            if comp_name.lower() in company_lower or company_lower in comp_name.lower():
                return metadata.get('tier')
        
        return None
    
    def _calculate_skills_match(self, job_title: str, job_description: str) -> float:
        """
        Calculate skills match percentage (0-100%).
        
        Args:
            job_title: Job title
            job_description: Job description
            
        Returns:
            Match percentage (0-100)
        """
        if not self.user_skills:
            return 0.0
        
        text = f"{job_title} {job_description}".lower()
        
        # Extract skills mentioned in job description
        mentioned_skills = []
        for skill in self.user_skills:
            # Check if skill is mentioned (word boundary to avoid partial matches)
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                mentioned_skills.append(skill)
        
        # Also check for common tech stack keywords
        tech_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'nodejs', 'typescript', 'ts'],
            'react': ['react', 'reactjs', 'redux'],
            'aws': ['aws', 'amazon web services', 's3', 'ec2', 'lambda'],
            'docker': ['docker', 'container', 'kubernetes', 'k8s'],
            'java': ['java', 'spring', 'spring boot'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'sql': ['sql', 'postgresql', 'mysql', 'mongodb', 'database'],
        }
        
        # Count matches
        total_skills = len(self.user_skills)
        if total_skills == 0:
            return 0.0
        
        matched_count = len(mentioned_skills)
        
        # Calculate percentage
        match_pct = (matched_count / total_skills) * 100
        return min(100.0, match_pct)
    
    def calculate_score(self, job: Dict) -> Dict:
        """
        Calculate priority score for a job (0-100).
        
        Scoring breakdown:
        - Recency (0-40 points): Jobs posted within 24h = 40pts, 3 days = 30pts, 7 days = 20pts, 14 days = 10pts
        - Company Quality (0-30 points): FAANG = 30pts, Unicorns = 25pts, Well-funded = 15pts
        - Salary Info (0-20 points): Jobs with salary mentioned = 20pts
        - Skills Match (0-10 points): Based on skills match percentage
        
        Args:
            job: Job dictionary with keys: title, company, location, description, posted_date, etc.
            
        Returns:
            Dictionary with score breakdown:
            {
                'score': 0-100,
                'days_since_posted': int or None,
                'salary': str or None,
                'skills_match_pct': 0-100,
                'company_tier': str or None
            }
        """
        job_title = str(job.get('title', '') or '')
        job_description = str(job.get('description', '') or '')
        company = str(job.get('company', '') or '')
        posted_date = str(job.get('posted_date', '') or '')
        
        score = 0
        breakdown = {}
        
        # 1. Recency (0-40 points)
        days_since_posted = self._calculate_days_since_posted(posted_date)
        if days_since_posted is not None:
            if days_since_posted <= 1:
                recency_score = 40
            elif days_since_posted <= 3:
                recency_score = 30
            elif days_since_posted <= 7:
                recency_score = 20
            elif days_since_posted <= 14:
                recency_score = 10
            else:
                recency_score = 0
            score += recency_score
            breakdown['recency'] = recency_score
        else:
            breakdown['recency'] = 0
        
        # 2. Company Quality (0-30 points)
        company_tier = self._get_company_tier(company)
        if company_tier == 'FAANG':
            company_score = 30
        elif company_tier == 'unicorn':
            company_score = 25
        elif company_tier == 'well_funded':
            company_score = 15
        else:
            company_score = 0
        score += company_score
        breakdown['company'] = company_score
        
        # 3. Salary Info (0-20 points)
        salary = self.salary_extractor.extract(f"{job_title} {job_description}")
        if salary:
            salary_score = 20
            score += salary_score
            breakdown['salary'] = salary_score
        else:
            salary = None
            breakdown['salary'] = 0
        
        # 4. Skills Match (0-10 points)
        skills_match_pct = self._calculate_skills_match(job_title, job_description)
        # Convert percentage to 0-10 points (linear scaling)
        skills_score = int(skills_match_pct / 10)
        score += skills_score
        breakdown['skills'] = skills_score
        
        # Extract deadline
        deadline = self.deadline_extractor.extract(f"{job_title} {job_description}")
        days_until_deadline = None
        if deadline:
            days_until_deadline = self.deadline_extractor.get_days_until_deadline(deadline)
        
        # Get freshness indicator
        freshness = self._get_freshness_indicator(days_since_posted)
        
        return {
            'score': min(100, score),  # Cap at 100
            'days_since_posted': days_since_posted,
            'freshness': freshness,
            'salary': salary,
            'deadline': deadline,
            'days_until_deadline': days_until_deadline,
            'skills_match_pct': round(skills_match_pct, 1),
            'company_tier': company_tier,
            'breakdown': breakdown
        }
