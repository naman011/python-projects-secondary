"""Failure reporter for scrapers.

Writes a CSV so you can see exactly which companies were skipped and why.
"""

import csv
import os
from typing import Dict, List, Optional


class FailureReporter:
    def __init__(self, output_file: str = "data/failures.csv"):
        self.output_file = output_file
        self.fieldnames = [
            "Company",
            "Career URL",
            "Scraper Type",
            "Stage",
            "Error",
        ]

    def write(self, failures: List[Dict]) -> None:
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for item in failures:
                if not isinstance(item, dict):
                    continue
                writer.writerow(
                    {
                        "Company": item.get("company", ""),
                        "Career URL": item.get("career_url", ""),
                        "Scraper Type": item.get("scraper_type", ""),
                        "Stage": item.get("stage", ""),
                        "Error": item.get("error", ""),
                    }
                )

