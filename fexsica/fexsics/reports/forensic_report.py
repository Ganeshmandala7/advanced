"""Report generation for forensic analysis results."""

from typing import Dict, Any
from datetime import datetime
import json


class ForensicReport:
    """Generates formatted forensic analysis reports."""
    
    def __init__(self, title: str = "FeXsics Forensic Analysis Report"):
        """
        Initialize forensic report.
        
        Args:
            title: Report title.
        """
        self.title = title
        self.timestamp = datetime.now()
        self.sections = {}
    
    def add_section(self, section_name: str, content: Dict[str, Any]) -> None:
        """
        Add a section to the report.
        
        Args:
            section_name: Section identifier.
            content: Section content.
        """
        self.sections[section_name] = content
    
    def generate_html_report(self) -> str:
        """
        Generate HTML formatted report.
        
        Returns:
            HTML report as string.
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #666; margin-top: 20px; }}
        .section {{ margin: 20px 0; }}
        .verdict {{ font-size: 18px; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{self.title}</h1>
    <p>Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
        
        for section_name, content in self.sections.items():
            html += f"<div class='section'><h2>{section_name}</h2>"
            html += f"<pre>{json.dumps(content, indent=2)}</pre></div>"
        
        html += "</body></html>"
        return html
    
    def generate_json_report(self) -> str:
        """
        Generate JSON formatted report.
        
        Returns:
            JSON report as string.
        """
        report_data = {
            "title": self.title,
            "timestamp": self.timestamp.isoformat(),
            "sections": self.sections
        }
        return json.dumps(report_data, indent=2)
