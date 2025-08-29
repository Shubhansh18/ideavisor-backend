import json
import os
from pathlib import Path

# Create reports directory if it doesn't exist
REPORTS_DIR = Path(__file__).parent / 'data'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def save_report(report_id: str, report_data: dict) -> None:
    """Save report data to a JSON file"""
    try:
        # Ensure data directory exists
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"{report_id}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, default=str)
    except Exception as e:
        print(f"Error saving report {report_id}: {str(e)}")
        raise

def get_report(report_id: str) -> dict:
    """Retrieve report data from JSON file"""
    try:
        report_path = REPORTS_DIR / f"{report_id}.json"
        if not report_path.exists():
            return None
            
        with open(report_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading report {report_id}: {str(e)}")
        return None