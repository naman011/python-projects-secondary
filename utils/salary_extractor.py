"""Salary extraction from job descriptions."""

import re
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class SalaryExtractor:
    """Extract salary information from job descriptions."""
    
    def __init__(self):
        """Initialize salary extractor with regex patterns."""
        # Salary patterns for different currencies and formats
        self.patterns = [
            # USD formats: $80k-120k, $80,000-120,000, $80K-$120K
            (r'\$(\d+[kK]?)\s*[-–—]\s*\$?(\d+[kK]?)', 'USD'),
            (r'\$(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*\$?(\d{1,3}(?:,\d{3})*)', 'USD'),
            # INR formats: ₹15-25 LPA, ₹15 LPA, 15-25 LPA, 15 LPA
            (r'[₹]?(\d+)\s*[-–—]\s*(\d+)\s*LPA', 'INR'),
            (r'[₹]?(\d+)\s*LPA', 'INR'),
            # EUR formats: €50,000-70,000, €50k-70k
            (r'€(\d+[kK]?)\s*[-–—]\s*€?(\d+[kK]?)', 'EUR'),
            (r'€(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*€?(\d{1,3}(?:,\d{3})*)', 'EUR'),
            # GBP formats: £40k-60k, £40,000-60,000
            (r'£(\d+[kK]?)\s*[-–—]\s*£?(\d+[kK]?)', 'GBP'),
            (r'£(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*£?(\d{1,3}(?:,\d{3})*)', 'GBP'),
            # Generic: 80k-120k, 80,000-120,000 (assume USD if no currency)
            (r'(?<![$€£₹])(\d+[kK])\s*[-–—]\s*(\d+[kK])', 'USD'),
            (r'(?<![$€£₹])(\d{1,3}(?:,\d{3})*)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*)', 'USD'),
        ]
    
    def _normalize_amount(self, amount_str: str, currency: str) -> Optional[float]:
        """Normalize amount string to number (handles 'k' suffix)."""
        try:
            amount_str = amount_str.replace(',', '').upper()
            if amount_str.endswith('K'):
                return float(amount_str[:-1]) * 1000
            return float(amount_str)
        except (ValueError, AttributeError):
            return None
    
    def extract(self, text: str) -> Optional[str]:
        """
        Extract salary range from text.
        
        Args:
            text: Job description or title text
            
        Returns:
            Salary string in format "currency min-max" or None
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Skip if text doesn't contain salary-related keywords
        salary_keywords = ['salary', 'compensation', 'pay', 'lpa', 'package', 'remuneration']
        if not any(keyword in text_lower for keyword in salary_keywords):
            # Still try to extract if pattern matches (might be in title)
            pass
        
        for pattern, currency in self.patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) == 2:
                        # Range format: min-max
                        min_amount = self._normalize_amount(groups[0], currency)
                        max_amount = self._normalize_amount(groups[1], currency)
                        if min_amount and max_amount:
                            # Format output
                            if currency == 'INR' and min_amount >= 1000:
                                # For INR, show in LPA if > 1000
                                min_lpa = min_amount / 100000
                                max_lpa = max_amount / 100000
                                return f"₹{min_lpa:.1f}-{max_lpa:.1f} LPA"
                            elif min_amount >= 1000:
                                # Show in thousands
                                min_k = min_amount / 1000
                                max_k = max_amount / 1000
                                symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(currency, '')
                                return f"{symbol}{min_k:.0f}k-{max_k:.0f}k"
                            else:
                                symbol = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}.get(currency, '')
                                return f"{symbol}{min_amount:.0f}-{max_amount:.0f}"
                    elif len(groups) == 1:
                        # Single amount format
                        amount = self._normalize_amount(groups[0], currency)
                        if amount:
                            if currency == 'INR' and amount >= 1000:
                                lpa = amount / 100000
                                return f"₹{lpa:.1f} LPA"
                            elif amount >= 1000:
                                amount_k = amount / 1000
                                symbol = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(currency, '')
                                return f"{symbol}{amount_k:.0f}k"
                            else:
                                symbol = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}.get(currency, '')
                                return f"{symbol}{amount:.0f}"
                except Exception as e:
                    logger.debug(f"Error extracting salary from match {match.group()}: {e}")
                    continue
        
        return None
