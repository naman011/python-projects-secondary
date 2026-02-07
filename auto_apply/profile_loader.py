"""Load and validate user profile data for job applications."""

import json
import os
import logging
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ProfileLoader:
    """Load and validate user profile data from JSON file."""
    
    def __init__(self, profile_file: str = "data/user_profile.json"):
        """
        Initialize profile loader.
        
        Args:
            profile_file: Path to user profile JSON file
        """
        self.profile_file = profile_file
        self.profile_data: Optional[Dict] = None
        self.template_file = "data/user_profile.json.template"
    
    def load(self) -> Dict:
        """
        Load user profile from JSON file.
        
        Returns:
            Dictionary containing user profile data
            
        Raises:
            FileNotFoundError: If profile file doesn't exist
            ValueError: If profile data is invalid
        """
        if not os.path.exists(self.profile_file):
            template_path = self.template_file
            if os.path.exists(template_path):
                raise FileNotFoundError(
                    f"Profile file not found: {self.profile_file}\n"
                    f"Please copy {template_path} to {self.profile_file} and fill in your details."
                )
            else:
                raise FileNotFoundError(
                    f"Profile file not found: {self.profile_file}\n"
                    "Please create a user_profile.json file with your application data."
                )
        
        try:
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                self.profile_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in profile file: {e}")
        except Exception as e:
            raise ValueError(f"Error reading profile file: {e}")
        
        # Validate required fields
        self._validate_profile()
        
        return self.profile_data
    
    def _validate_profile(self):
        """Validate that profile contains required fields."""
        if not self.profile_data:
            raise ValueError("Profile data is empty")
        
        required_sections = ['personal_info', 'education', 'work_experience']
        for section in required_sections:
            if section not in self.profile_data:
                raise ValueError(f"Missing required section: {section}")
        
        # Validate personal info
        personal_info = self.profile_data.get('personal_info', {})
        required_personal = ['full_name', 'email', 'phone']
        for field in required_personal:
            if not personal_info.get(field):
                raise ValueError(f"Missing required personal info field: {field}")
        
        # Validate education
        education = self.profile_data.get('education', [])
        if not education or len(education) == 0:
            raise ValueError("At least one education entry is required")
        
        # Validate resume path
        resume_info = self.profile_data.get('resume', {})
        resume_path = resume_info.get('file_path')
        if resume_path and not os.path.exists(resume_path):
            logger.warning(f"Resume file not found at: {resume_path}")
    
    def get_personal_info(self) -> Dict:
        """Get personal information."""
        return self.profile_data.get('personal_info', {}) if self.profile_data else {}
    
    def get_education(self) -> List[Dict]:
        """Get education history."""
        return self.profile_data.get('education', []) if self.profile_data else []
    
    def get_work_experience(self) -> List[Dict]:
        """Get work experience."""
        return self.profile_data.get('work_experience', []) if self.profile_data else []
    
    def get_skills(self) -> Dict:
        """Get skills dictionary."""
        return self.profile_data.get('skills', {}) if self.profile_data else {}
    
    def get_resume_path(self) -> Optional[str]:
        """Get resume file path."""
        if not self.profile_data:
            return None
        resume_info = self.profile_data.get('resume', {})
        return resume_info.get('file_path')
    
    def get_form_data(self) -> Dict:
        """
        Get formatted data ready for form filling.
        
        Returns:
            Dictionary with common form field mappings
        """
        if not self.profile_data:
            return {}
        
        personal = self.get_personal_info()
        education = self.get_education()
        experience = self.get_work_experience()
        skills = self.get_skills()
        
        # Get most recent education
        latest_education = education[0] if education else {}
        
        # Get current/most recent work experience
        current_job = next((exp for exp in experience if exp.get('is_current', False)), None)
        if not current_job and experience:
            current_job = experience[0]
        
        # Format skills as comma-separated string
        all_skills = []
        for skill_list in skills.values():
            if isinstance(skill_list, list):
                all_skills.extend(skill_list)
        skills_string = ", ".join(all_skills)
        
        # Format work experience as text
        experience_text = ""
        if current_job:
            experience_text = f"{current_job.get('position', '')} at {current_job.get('company', '')}"
        
        return {
            'full_name': personal.get('full_name', ''),
            'first_name': personal.get('first_name', personal.get('full_name', '').split()[0] if personal.get('full_name') else ''),
            'last_name': personal.get('last_name', ' '.join(personal.get('full_name', '').split()[1:]) if personal.get('full_name') else ''),
            'email': personal.get('email', ''),
            'phone': personal.get('phone', ''),
            'location': personal.get('location', personal.get('current_location', '')),
            'linkedin_url': personal.get('linkedin_url', ''),
            'github_url': personal.get('github_url', ''),
            'degree': latest_education.get('degree', ''),
            'institution': latest_education.get('institution', ''),
            'graduation_date': latest_education.get('end_date', ''),
            'gpa': latest_education.get('gpa', ''),
            'current_position': current_job.get('position', '') if current_job else '',
            'current_company': current_job.get('company', '') if current_job else '',
            'years_of_experience': self._calculate_years_experience(),
            'skills': skills_string,
            'resume_path': self.get_resume_path(),
        }
    
    def _calculate_years_experience(self) -> float:
        """Calculate total years of work experience."""
        experience = self.get_work_experience()
        if not experience:
            return 0.0
        
        # Simple calculation - could be enhanced
        total_months = 0
        for exp in experience:
            # This is a simplified calculation
            # In a real implementation, you'd parse dates properly
            if exp.get('is_current', False):
                total_months += 12  # Approximate for current role
            else:
                total_months += 12  # Approximate
        
        return round(total_months / 12, 1)
    
    def get_cover_letter_text(self, company: str = "", position: str = "") -> str:
        """
        Get cover letter text, optionally customized for company/position.
        
        Args:
            company: Company name
            position: Job position
            
        Returns:
            Cover letter text
        """
        if not self.profile_data:
            return ""
        
        cover_letter = self.profile_data.get('cover_letter', {})
        template = cover_letter.get('default_template', '')
        
        # Replace placeholders
        template = template.replace('[Company]', company)
        template = template.replace('[Position]', position)
        
        return template
