"""
API REQUEST/RESPONSE SCHEMAS

Pydantic v2 models for request/response validation and OpenAPI documentation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class CaseInfo(BaseModel):
    """Case information for forensic analysis."""
    case_number: str = Field(..., min_length=1, max_length=100, description="Unique case identifier")
    case_name: str = Field(..., min_length=1, max_length=200, description="Case name/title")
    investigator: Optional[str] = Field(None, max_length=100, description="Investigating officer name")
    jurisdiction: Optional[str] = Field(None, max_length=100, description="Jurisdiction")
    
    @field_validator('case_number')
    def validate_case_number(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Case number must be alphanumeric")
        return v


class AnalysisRequest(BaseModel):
    """Request to analyze an image."""
    case_info: CaseInfo = Field(..., description="Case information")
    include_report: bool = Field(True, description="Generate PDF report")
    include_evidence_maps: bool = Field(True, description="Include heatmaps in report")
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_info": {
                    "case_number": "2024-001234",
                    "case_name": "State v. Defendant",
                    "investigator": "Detective Smith",
                    "jurisdiction": "District 5"
                },
                "include_report": True,
                "include_evidence_maps": True
            }
        }


class EngineResult(BaseModel):
    """Result from a single forensic engine."""
    engine: str = Field(..., description="Engine name")
    verdict: str = Field(..., description="Verdict: authentic/manipulated/inconclusive/error")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    findings: List[str] = Field(default_factory=list, description="Detailed findings")
    physics_law_violated: str = Field(..., description="Physics principle violated (if manipulated)")
    evidence_map_path: Optional[str] = Field(None, description="Path to evidence visualization")
    raw_scores: Dict[str, Any] = Field(default_factory=dict, description="Raw numerical data")


class BayesianData(BaseModel):
    """Bayesian fusion analysis data."""
    posterior_manipulated: float = Field(..., ge=0.0, le=1.0, description="P(Manipulated|Evidence)")
    posterior_authentic: float = Field(..., ge=0.0, le=1.0, description="P(Authentic|Evidence)")
    engine_contributions: Dict[str, float] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Complete analysis response."""
    status: str = Field(..., description="Status: success/error")
    case_number: str = Field(..., description="Case identifier")
    analysis_id: str = Field(..., description="Unique analysis ID")
    image_hash: str = Field(..., description="SHA-256 hash of original image")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    # Main results
    verdict: str = Field(..., description="Final verdict: authentic/manipulated/inconclusive")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Final confidence score")
    
    # Engine results
    engine_results: List[EngineResult] = Field(default_factory=list, description="All engine results")
    
    # Bayesian data
    bayesian_data: BayesianData = Field(..., description="Bayesian fusion analysis")
    
    # Report
    report_path: Optional[str] = Field(None, description="Path to generated PDF report")
    report_hash: Optional[str] = Field(None, description="SHA-256 of report for auditability")
    
    # Summary
    summary: str = Field(..., description="Plain English summary for non-technical readers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "case_number": "2024-001234",
                "analysis_id": "FX-2024-0001",
                "image_hash": "abc123def456...",
                "verdict": "manipulated",
                "confidence": 0.82,
                "engine_results": [],
                "bayesian_data": {
                    "posterior_manipulated": 0.82,
                    "posterior_authentic": 0.18,
                    "engine_contributions": {}
                },
                "summary": "Bayesian analysis indicates 82% probability of manipulation."
            }
        }


class ErrorResponse(BaseModel):
    """Error response format."""
    status: str = Field("error", description="Always 'error'")
    error_code: str = Field(..., description="Error code for categorization")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error_code": "INVALID_IMAGE_FORMAT",
                "message": "Image must be JPEG, PNG, TIFF, WEBP, or BMP format",
                "details": {
                    "provided_format": "GIF",
                    "allowed_formats": ["JPEG", "PNG", "TIFF", "WEBP", "BMP"]
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field("healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReportRequest(BaseModel):
    """Request to generate report from analysis results."""
    analysis_id: str = Field(..., description="Analysis ID to generate report for")
    format: str = Field("pdf", description="Report format (pdf, html, json)")


class ChainOfCustodyRecord(BaseModel):
    """Chain of custody entry for auditability."""
    timestamp: datetime
    image_hash: str
    case_number: str
    action: str  # "uploaded", "analyzed", "reported"
    operator: Optional[str] = None
    system_hash: Optional[str] = None  # Hash of system state
