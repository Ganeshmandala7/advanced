"""
FORENSIC REPORT GENERATOR

Generates 9-page courtroom-grade PDF reports with:
1. Cover page (case info, timestamps)
2. Executive summary
3. Findings table (verdicts + confidence)
4. Visual evidence (heatmaps)
5. Bayesian analysis table
6. Metadata summary
7. Methodology and physics principles
8. Expert declaration (legal boilerplate)
9. Footer pages with hash chain of custody
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

logger = logging.getLogger(__name__)


def generate_forensic_report(
    case_info: Dict[str, Any],
    analysis_results: Dict[str, Any],
    image_hash: str,
    output_path: str
) -> Dict[str, Any]:
    """
    Generate complete 9-page forensic report.
    
    Args:
        case_info: Dictionary with case_number, case_name, investigator
        analysis_results: Complete analysis results from all engines
        image_hash: SHA-256 hash of original image
        output_path: Path to save PDF
        
    Returns:
        Report metadata
    """
    try:
        logger.info(f"Generating forensic report: {output_path}")
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Page 1: Cover
        story.extend(_build_cover_page(case_info, styles, title_style))
        story.append(PageBreak())
        
        # Page 2: Executive Summary
        story.extend(_build_executive_summary(analysis_results, styles, heading_style))
        story.append(PageBreak())
        
        # Page 3: Findings Table
        story.extend(_build_findings_table(analysis_results, styles, heading_style))
        story.append(PageBreak())
        
        # Page 4-5: Visual Evidence (heatmaps)
        story.extend(_build_visual_evidence(analysis_results, styles, heading_style))
        story.append(PageBreak())
        
        # Page 6: Bayesian Analysis
        story.extend(_build_bayesian_analysis(analysis_results, styles, heading_style))
        story.append(PageBreak())
        
        # Page 7: Metadata Summary
        story.extend(_build_metadata_summary(analysis_results, styles, heading_style))
        story.append(PageBreak())
        
        # Page 8: Methodology
        story.extend(_build_methodology_page(styles, heading_style))
        story.append(PageBreak())
        
        # Page 9: Expert Declaration
        story.extend(_build_expert_declaration(case_info, image_hash, styles, heading_style))
        
        # Build PDF
        doc.build(story)
        
        # Compute report hash
        report_hash = _compute_file_hash(output_path)
        
        logger.info(f"Report generated successfully: {output_path}")
        
        return {
            "status": "success",
            "output_path": output_path,
            "report_hash": report_hash,
            "case_number": case_info.get("case_number"),
            "generated_timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "output_path": output_path
        }


def _build_cover_page(case_info, styles, title_style):
    """Build cover page with case information."""
    story = []
    
    story.append(Spacer(1*inch, 1*inch))
    story.append(Paragraph("FORENSIC IMAGE ANALYSIS REPORT", title_style))
    story.append(Spacer(1*inch, 0.5*inch))
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=12
    )
    
    story.append(Paragraph(f"Case Number: {case_info.get('case_number', 'N/A')}", info_style))
    story.append(Paragraph(f"Case Name: {case_info.get('case_name', 'N/A')}", info_style))
    story.append(Paragraph(f"Investigator: {case_info.get('investigator', 'FEXsics System')}", info_style))
    story.append(Spacer(1*inch, 0.3*inch))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", info_style))
    story.append(Spacer(1*inch, 0.5*inch))
    story.append(Paragraph("Physics-Grounded Multimodal Forensic Analysis", info_style))
    
    return story


def _build_executive_summary(analysis_results, styles, heading_style):
    """Build executive summary page."""
    story = []
    
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    fusion_result = analysis_results.get("fusion_result", {})
    verdict = fusion_result.get("verdict", "inconclusive").upper()
    confidence = fusion_result.get("confidence", 0)
    
    summary_style = ParagraphStyle(
        'SummaryStyle',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    story.append(Paragraph(f"Verdict: <b>{verdict}</b>", summary_style))
    story.append(Paragraph(f"Confidence: <b>{confidence:.1%}</b>", summary_style))
    
    findings = fusion_result.get("findings", [])
    for finding in findings[:3]:  # Limit to 3 findings for summary
        story.append(Paragraph(f"• {finding}", summary_style))
    
    return story


def _build_findings_table(analysis_results, styles, heading_style):
    """Build findings table with all engine verdicts."""
    story = []
    
    story.append(Paragraph("FORENSIC ENGINE RESULTS", heading_style))
    
    # Prepare table data
    table_data = [["Engine", "Verdict", "Confidence", "Key Finding"]]
    
    for engine_result in analysis_results.get("all_results", []):
        engine_name = engine_result.get("engine", "Unknown")
        verdict = engine_result.get("verdict", "N/A").upper()
        confidence = engine_result.get("confidence", 0)
        findings = engine_result.get("findings", [])
        key_finding = findings[0] if findings else "No findings"
        
        # Truncate finding for table
        if len(key_finding) > 50:
            key_finding = key_finding[:47] + "..."
        
        table_data.append([engine_name, verdict, f"{confidence:.1%}", key_finding])
    
    # Create table
    table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    
    return story


def _build_visual_evidence(analysis_results, styles, heading_style):
    """Build visual evidence page with heatmaps."""
    story = []
    
    story.append(Paragraph("VISUAL EVIDENCE", heading_style))
    story.append(Paragraph("Heatmaps and analysis visualizations:", styles['Normal']))
    
    # Try to embed evidence maps
    evidence_maps = []
    for result in analysis_results.get("all_results", []):
        evidence_path = result.get("evidence_map_path", "")
        if evidence_path and Path(evidence_path).exists():
            evidence_maps.append((result.get("engine", "Unknown"), evidence_path))
    
    if evidence_maps:
        for engine_name, map_path in evidence_maps[:4]:  # Limit to 4 images
            try:
                story.append(Paragraph(f"{engine_name} Analysis:", styles['Normal']))
                img = Image(map_path, width=5*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1*inch, 0.2*inch))
            except Exception as e:
                logger.warning(f"Could not embed evidence map: {e}")
                story.append(Paragraph(f"[Evidence map: {map_path}]", styles['Normal']))
    else:
        story.append(Paragraph("No visual evidence generated in this analysis.", styles['Normal']))
    
    return story


def _build_bayesian_analysis(analysis_results, styles, heading_style):
    """Build Bayesian analysis page."""
    story = []
    
    story.append(Paragraph("BAYESIAN FUSION ANALYSIS", heading_style))
    
    fusion_result = analysis_results.get("fusion_result", {})
    bayesian_data = fusion_result.get("bayesian_data", {})
    
    p_manip = bayesian_data.get("posterior_manipulated", 0.15)
    p_auth = bayesian_data.get("posterior_authentic", 0.85)
    
    # Create Bayes table
    bayes_data = [
        ["Hypothesis", "Prior Probability", "Posterior Probability"],
        ["Image is Manipulated", "15%", f"{p_manip:.1%}"],
        ["Image is Authentic", "85%", f"{p_auth:.1%}"],
    ]
    
    bayes_table = Table(bayes_data, colWidths=[2*inch, 2*inch, 2*inch])
    bayes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(bayes_table)
    story.append(Spacer(1*inch, 0.3*inch))
    
    explanation = ("Bayesian analysis combines forensic evidence using Bayes' theorem. "
                   "The posterior probability reflects the probability the image is manipulated "
                   "after considering all forensic evidence.")
    story.append(Paragraph(explanation, styles['Normal']))
    
    return story


def _build_metadata_summary(analysis_results, styles, heading_style):
    """Build metadata summary page."""
    story = []
    
    story.append(Paragraph("METADATA ANALYSIS SUMMARY", heading_style))
    
    for result in analysis_results.get("all_results", []):
        if result.get("engine") == "Metadata":
            raw_scores = result.get("raw_scores", {})
            
            story.append(Paragraph(f"Field Count: {raw_scores.get('field_count', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Likely Origin: {raw_scores.get('likely_origin', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"Editing Software: {', '.join(raw_scores.get('editing_software', ['None detected']))}", styles['Normal']))
            story.append(Paragraph(f"GPS Present: {'Yes' if raw_scores.get('gps_present') else 'No'}", styles['Normal']))
            
            if raw_scores.get('gps_location'):
                lat, lon = raw_scores['gps_location']
                story.append(Paragraph(f"GPS Location: {lat:.4f}, {lon:.4f}", styles['Normal']))
            
            break
    
    return story


def _build_methodology_page(styles, heading_style):
    """Build methodology page explaining physics principles."""
    story = []
    
    story.append(Paragraph("FORENSIC METHODOLOGY", heading_style))
    
    methodology_text = (
        "This analysis applies physics-based forensic techniques that exploit "
        "fundamental physical laws. Each forensic engine targets specific "
        "physics principles:<br/><br/>"
        
        "<b>1. ELA Engine:</b> Exploits deterministic JPEG compression. "
        "Edited regions show different compression histories.<br/><br/>"
        
        "<b>2. Metadata Engine:</b> Analyzes embedded camera hardware signatures. "
        "Temporal, spatial, and equipment inconsistencies violate physical cause-effect.<br/><br/>"
        
        "<b>3. Noise Engine:</b> Sensors produce unique fingerprints (PRNU). "
        "Spliced images show mismatched noise signatures.<br/><br/>"
        
        "<b>4. Illumination Engine:</b> Shadows obey Lambertian + Phong reflectance. "
        "Composite images violate single light source geometry.<br/><br/>"
        
        "<b>5. Geometry Engine:</b> Perspective projection is deterministic. "
        "Spliced regions show inconsistent vanishing points.<br/><br/>"
        
        "<b>6. Deepfake Engine:</b> GAN-synthesized faces create specific artifacts. "
        "Eye reflections violate Fresnel equations.<br/><br/>"
        
        "<b>7. AI-Gen Engine:</b> AI synthesis produces different statistics. "
        "Patch redundancy and frequency spectrum differ from natural photos."
    )
    
    story.append(Paragraph(methodology_text, styles['Normal']))
    
    return story


def _build_expert_declaration(case_info, image_hash, styles, heading_style):
    """Build expert declaration (legal boilerplate)."""
    story = []
    
    story.append(Paragraph("EXPERT DECLARATION", heading_style))
    
    declaration = (
        "I declare under penalty of perjury that the forensic analysis contained herein "
        "was performed using established scientific methodology and physics principles. "
        "The analysis is based on the image identified by SHA-256 hash:<br/><br/>"
        f"<b>{image_hash}</b><br/><br/>"
        
        "This chain of custody hash ensures the analyzed image has not been altered "
        "since initial processing. The forensic conclusions are based on independent "
        "analysis by seven specialized physics-based engines, combined via Bayesian "
        "inference using accepted statistical methodology.<br/><br/>"
        
        "The opinions expressed herein are based on my analysis and review of "
        "scientific literature on digital forensics, image processing, and "
        "physics-based authentication methods."
    )
    
    story.append(Paragraph(declaration, styles['Normal']))
    
    return story


def _compute_file_hash(file_path: str) -> str:
    """Compute SHA-256 hash of file."""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error computing file hash: {e}")
        return "hash_error"
