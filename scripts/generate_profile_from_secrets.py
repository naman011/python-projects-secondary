#!/usr/bin/env python3
"""Generate user_profile.json from GitHub Secrets."""

import os
import json
import sys
from pathlib import Path

def main():
    """Generate user_profile.json from environment variable."""
    # Get user profile JSON from environment (set by GitHub Secrets)
    user_profile_json = os.environ.get('USER_PROFILE_JSON')
    
    if not user_profile_json:
        print("ERROR: USER_PROFILE_JSON environment variable not set")
        print("Please set USER_PROFILE_JSON secret in GitHub repository settings")
        sys.exit(1)
    
    try:
        # Parse JSON to validate it
        profile_data = json.loads(user_profile_json)
        
        # Ensure data directory exists
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Write user_profile.json
        profile_file = data_dir / "user_profile.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully generated {profile_file}")
        print(f"Profile contains {len(profile_data.get('work_experience', []))} work experiences")
        print(f"Profile contains {len(profile_data.get('education', []))} education entries")
        
        # Validate required fields
        required_fields = ['personal_info', 'education', 'work_experience']
        missing_fields = [field for field in required_fields if field not in profile_data]
        
        if missing_fields:
            print(f"WARNING: Missing required fields: {missing_fields}")
            sys.exit(1)
        
        # Check personal info
        personal_info = profile_data.get('personal_info', {})
        required_personal = ['full_name', 'email', 'phone']
        missing_personal = [field for field in required_personal if not personal_info.get(field)]
        
        if missing_personal:
            print(f"WARNING: Missing required personal info: {missing_personal}")
        
        # Check resume path
        resume_info = profile_data.get('resume', {})
        resume_path = resume_info.get('file_path', '')
        if resume_path:
            if not os.path.exists(resume_path):
                print(f"WARNING: Resume file not found at: {resume_path}")
        else:
            print("WARNING: No resume file path specified")
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in USER_PROFILE_JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to generate user profile: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
