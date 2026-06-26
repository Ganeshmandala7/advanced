"""
FASTAPI ROUTES - MAIN API ENDPOINTS

Async routes for image upload, analysis orchestration, and report generation.
"""

import logging
import uuid
from fastapi import APIRouter, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
from pathlib import Path

from api.schemas import (
    AnalysisRequest, AnalysisResponse, ErrorResponse, HealthResponse,
    EngineResult, BayesianData, CaseInfo
)
from utils.validators import validate_all_image_checks, validate_case_info
from utils.hash_utils import compute_sha256, generate_report_id, format_hash_for_display
from engines import ela_engine, metadata_engine, noise_engine, illumination_engine
from engines import geometry_engine, deepfake_engine, ai_gen_engine, fusion_engine
from report.generator import generate_forensic_report
from config import EVIDENCE_DIR, MAX_UPLOAD_SIZE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["forensics"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile,
    case_number: str = Form(...),
    case_name: str = Form(...),
    investigator: str = Form(None),
    include_report: bool = Form(True),
    background_tasks: BackgroundTasks = None
):
    """
    Analyze image for forensic authenticity.
    
    Accepts image file and case information, runs complete forensic pipeline,
    returns verdict with Bayesian confidence and detailed findings.
    """
    try:
        logger.info(f"Received analysis request: case {case_number}")
        
        # Validate case info
        case_info = {
            "case_number": case_number,
            "case_name": case_name,
            "investigator": investigator or "FEXsics System"
        }
        
        is_valid, msg = validate_case_info(case_info)
        if not is_valid:
            raise HTTPException(status_code=400, detail=msg)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
            tmp_path = tmp_file.name
            await file.seek(0)
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Validate image
            is_valid, msg = validate_all_image_checks(tmp_path)
            if not is_valid:
                raise HTTPException(status_code=400, detail=msg)
            
            # Compute chain of custody hash
            image_hash = compute_sha256(tmp_path)
            logger.info(f"Image hash: {format_hash_for_display(image_hash)}")
            
            # Generate analysis ID
            analysis_id = generate_report_id()
            
            # Run all forensic engines
            logger.info(f"Running forensic analysis: {analysis_id}")
            
            results = []
            results.append(ela_engine.run_ela(tmp_path))
            results.append(metadata_engine.run_metadata_analysis(tmp_path))
            results.append(noise_engine.run_noise_analysis(tmp_path))
            results.append(illumination_engine.run_illumination_analysis(tmp_path))
            results.append(geometry_engine.run_geometry_analysis(tmp_path))
            results.append(deepfake_engine.run_deepfake_analysis(tmp_path))
            results.append(ai_gen_engine.detect_ai_generation(tmp_path))
            
            # Fuse results with Bayesian inference
            logger.info("Performing Bayesian fusion")
            fusion_result = fusion_engine.fuse_engine_results(results)
            
            # Convert to response models
            engine_results = [EngineResult(**result) for result in results if result.get("engine") != "Bayesian Fusion"]
            
            bayesian_data = BayesianData(
                posterior_manipulated=fusion_result.get("raw_scores", {}).get("posterior_manipulated", 0.5),
                posterior_authentic=fusion_result.get("raw_scores", {}).get("posterior_authentic", 0.5),
                engine_contributions=fusion_result.get("bayesian_data", {}).get("engine_contributions", {})
            )
            
            # Generate plain English summary
            summary = _generate_summary(fusion_result, case_number)
            
            # Optionally generate PDF report
            report_path = None
            report_hash = None
            
            if include_report:
                report_path = str(EVIDENCE_DIR / f"report_{analysis_id}.pdf")
                report_result = generate_forensic_report(
                    case_info=case_info,
                    analysis_results={
                        "all_results": results,
                        "fusion_result": fusion_result
                    },
                    image_hash=image_hash,
                    output_path=report_path
                )
                
                if report_result.get("status") == "success":
                    report_hash = report_result.get("report_hash")
                    logger.info(f"Report generated: {report_path}")
                else:
                    logger.warning(f"Report generation failed: {report_result.get('error')}")
                    report_path = None
            
            logger.info(f"Analysis complete: {fusion_result.get('verdict')} ({fusion_result.get('confidence'):.2%})")
            
            return AnalysisResponse(
                status="success",
                case_number=case_number,
                analysis_id=analysis_id,
                image_hash=image_hash,
                verdict=fusion_result.get("verdict", "inconclusive"),
                confidence=fusion_result.get("confidence", 0.5),
                engine_results=engine_results,
                bayesian_data=bayesian_data,
                report_path=report_path,
                report_hash=report_hash,
                summary=summary
            )
            
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ANALYSIS_FAILED",
                "message": str(e)
            }
        )


@router.get("/report/{analysis_id}")
async def get_report(analysis_id: str):
    """
    Download forensic report by analysis ID.
    """
    try:
        report_path = EVIDENCE_DIR / f"report_{analysis_id}.pdf"
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report not found: {analysis_id}"
            )
        
        return FileResponse(
            path=report_path,
            media_type="application/pdf",
            filename=f"forensic_report_{analysis_id}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/validate-image")
async def validate_image(file: UploadFile):
    """
    Pre-validate image before submission for analysis.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            is_valid, msg = validate_all_image_checks(tmp_path)
            
            if is_valid:
                return {
                    "status": "valid",
                    "message": "Image is valid for analysis"
                }
            else:
                return {
                    "status": "invalid",
                    "message": msg
                }
                
        finally:
            Path(tmp_path).unlink()
            
    except Exception as e:
        logger.error(f"Error validating image: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """
    Get evidence map (heatmap visualization) by ID.
    """
    try:
        # Search for evidence file
        evidence_files = list(EVIDENCE_DIR.glob(f"*_{evidence_id}.png"))
        
        if not evidence_files:
            raise HTTPException(
                status_code=404,
                detail=f"Evidence not found: {evidence_id}"
            )
        
        return FileResponse(
            path=evidence_files[0],
            media_type="image/png"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving evidence: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/status/{analysis_id}")
async def check_status(analysis_id: str):
    """
    Check status of ongoing analysis.
    """
    # In production, this would query a database
    return {
        "analysis_id": analysis_id,
        "status": "complete",
        "timestamp": None
    }


def _generate_summary(fusion_result, case_number):
    """Generate plain English summary for non-technical readers."""
    verdict = fusion_result.get("verdict", "inconclusive").upper()
    confidence = fusion_result.get("confidence", 0.5)
    
    if verdict == "MANIPULATED":
        summary = (
            f"CASE {case_number}: Forensic analysis indicates the submitted image "
            f"is likely MANIPULATED with {confidence:.0%} confidence. "
            f"Multiple independent forensic engines detected inconsistencies "
            f"with physical and optical principles expected in authentic images. "
            f"See detailed findings below."
        )
    elif verdict == "AUTHENTIC":
        summary = (
            f"CASE {case_number}: Forensic analysis indicates the submitted image "
            f"is likely AUTHENTIC with {(1-confidence):.0%} confidence. "
            f"The image exhibits characteristics consistent with unmodified "
            f"camera capture, with no significant manipulation indicators detected."
        )
    else:
        summary = (
            f"CASE {case_number}: Forensic analysis is INCONCLUSIVE. "
            f"Evidence is mixed across multiple forensic engines. "
            f"Additional investigation or expert analysis is recommended. "
            f"See detailed findings for engine-specific results."
        )
    
    return summary
