"""Application deadline extraction from job descriptions."""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class DeadlineExtractor:
    """Extract application deadlines from job descriptions."""
    
    def __init__(self):
        """Initialize deadline extractor with regex patterns."""
        # Common deadline patterns
        self.patterns = [
            # "Apply by Jan 15, 2024", "Deadline: Feb 20, 2024"
            (r'(?:apply\s+by|deadline|closes?|closing|due\s+date)[:\s]+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})', '%B %d, %Y'),
            (r'(?:apply\s+by|deadline|closes?|closing|due\s+date)[:\s]+([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})', '%b %d, %Y'),
            # "Deadline: 15/01/2024", "Apply by 01-15-2024"
            (r'(?:apply\s+by|deadline|closes?|closing|due\s+date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})', None),  # Will parse both formats
            # "Apply before Jan 15", "Deadline: Feb 20" (assume current year)
            (r'(?:apply\s+before|deadline|closes?|closing)[:\s]+([A-Za-z]{3,9}\s+\d{1,2})', '%B %d'),
            (r'(?:apply\s+before|deadline|closes?|closing)[:\s]+([A-Za-z]{3,9}\s+\d{1,2})', '%b %d'),
            # "Applications close in 5 days", "Deadline in 2 weeks"
            (r'(?:closes?|deadline|closing)\s+in\s+(\d+)\s+(days?|weeks?|months?)', None),  # Relative
            # "Last date: 15th Jan 2024"
            (r'last\s+date[:\s]+(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9},?\s+\d{4})', None),  # Will clean and parse
        ]
    
    def _parse_date_string(self, date_str: str, format_str: Optional[str] = None) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try provided format first
        if format_str:
            try:
                return datetime.strptime(date_str, format_str)
            except ValueError:
                pass
        
        # Try common date formats
        date_formats = [
            '%B %d, %Y',  # January 15, 2024
            '%b %d, %Y',  # Jan 15, 2024
            '%d %B %Y',   # 15 January 2024
            '%d %b %Y',   # 15 Jan 2024
            '%d/%m/%Y',   # 15/01/2024
            '%m/%d/%Y',   # 01/15/2024
            '%Y-%m-%d',   # 2024-01-15
            '%d-%m-%Y',   # 15-01-2024
            '%m-%d-%Y',   # 01-15-2024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try formats with ordinal suffixes (15th, 1st, etc.)
        date_str_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str_clean, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_relative_deadline(self, amount: str, unit: str) -> Optional[datetime]:
        """Parse relative deadline like '5 days', '2 weeks'."""
        try:
            amount_int = int(amount)
            unit_lower = unit.lower()
            
            if 'day' in unit_lower:
                return datetime.now() + timedelta(days=amount_int)
            elif 'week' in unit_lower:
                return datetime.now() + timedelta(weeks=amount_int)
            elif 'month' in unit_lower:
                return datetime.now() + timedelta(days=amount_int * 30)
        except (ValueError, AttributeError):
            pass
        return None
    
    def extract(self, text: str) -> Optional[str]:
        """
        Extract application deadline from text.
        
        Args:
            text: Job description or title text
            
        Returns:
            Deadline string in format "YYYY-MM-DD" or "MM/DD/YYYY" or None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Skip if text doesn't contain deadline-related keywords
        deadline_keywords = ['deadline', 'closes', 'closing', 'apply by', 'due date', 'last date']
        if not any(keyword in text_lower for keyword in deadline_keywords):
            return None
        
        for pattern, format_str in self.patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) >= 1:
                        date_str = groups[0]
                        
                        # Handle relative deadlines
                        if len(groups) >= 2 and groups[1] in ['days', 'day', 'weeks', 'week', 'months', 'month']:
                            deadline = self._parse_relative_deadline(date_str, groups[1])
                            if deadline:
                                return deadline.strftime('%Y-%m-%d')
                        
                        # Handle absolute dates
                        deadline = self._parse_date_string(date_str, format_str)
                        if deadline:
                            # If no year specified, assume current year
                            if deadline.year == 1900 or deadline.year < 2000:
                                deadline = deadline.replace(year=datetime.now().year)
                            return deadline.strftime('%Y-%m-%d')
                except Exception as e:
                    logger.debug(f"Error extracting deadline from match {match.group()}: {e}")
                    continue
        
        return None
    
    def get_days_until_deadline(self, deadline_str: str) -> Optional[int]:
        """
        Calculate days until deadline.
        
        Args:
            deadline_str: Deadline string in format "YYYY-MM-DD"
            
        Returns:
            Days until deadline (negative if past)
        """
        if not deadline_str:
            return None
        
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            delta = deadline - datetime.now()
            return delta.days
        except ValueError:
            return None
