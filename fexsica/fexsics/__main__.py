#!/usr/bin/env python
"""FeXsics command-line interface."""

import sys
import argparse
from pathlib import Path
from fexsics.core import ImageProcessor, Config
from fexsics.reports import ForensicReport


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FeXsics: Physics-Grounded Forensic Analysis Platform"
    )
    
    parser.add_argument(
        "image",
        type=str,
        help="Path to image file for analysis"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="report.html",
        help="Output report file path"
    )
    
    parser.add_argument(
        "--format",
        choices=["html", "json", "pdf"],
        default="html",
        help="Report format"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = Config()
    
    # Create processor
    processor = ImageProcessor(config)
    
    # Load and analyze image
    try:
        processor.load_image(args.image)
        results = processor.run_full_analysis()
        
        # Generate report
        report = ForensicReport(
            title=f"Forensic Analysis: {Path(args.image).name}"
        )
        
        report.add_section("Analysis Results", results)
        
        # Save report
        if args.format == "html":
            with open(args.output, "w") as f:
                f.write(report.generate_html_report())
        elif args.format == "json":
            with open(args.output, "w") as f:
                f.write(report.generate_json_report())
        
        print(f"Report saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
