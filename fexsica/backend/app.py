"""
MAIN FASTAPI APPLICATION

Entry point for FEXsics forensic analysis backend.
Combines all forensic engines with Bayesian fusion and courtroom-grade reporting.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from api import router
from config import EVIDENCE_DIR
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FEXsics Forensic Analysis Backend",
    description=(
        "Physics-grounded multimodal forensic image authentication system. "
        "Applies 7 independent forensic engines with Bayesian fusion for "
        "courtroom-grade authenticity analysis."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("FEXsics Backend Starting")
    
    # Ensure evidence directory exists
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Evidence directory: {EVIDENCE_DIR}")
    
    # Verify all engines are importable
    try:
        from engines import (
            ela_engine, metadata_engine, noise_engine,
            illumination_engine, geometry_engine, deepfake_engine,
            ai_gen_engine, fusion_engine
        )
        logger.info("✓ All forensic engines loaded successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to load engines: {e}")
        raise
    
    # Verify utilities
    try:
        from utils import hash_utils, image_utils, validators
        logger.info("✓ Utilities loaded successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to load utilities: {e}")
        raise
    
    logger.info("✓ FEXsics Backend ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("FEXsics Backend Shutting Down")


@app.get("/")
async def root():
    """Root endpoint - service information."""
    return {
        "service": "FEXsics Forensic Analysis Backend",
        "version": "1.0.0",
        "description": "Physics-grounded multimodal image authentication",
        "docs": "/api/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze": "POST /api/v1/analyze",
            "report": "GET /api/v1/report/{analysis_id}",
            "evidence": "GET /api/v1/evidence/{evidence_id}",
            "validate": "POST /api/v1/validate-image"
        }
    }


def custom_openapi():
    """Customize OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FEXsics API",
        version="1.0.0",
        description="Forensic image analysis with physics-based engines",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fexsics.example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
