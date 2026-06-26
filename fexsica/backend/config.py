"""Fexsics configuration and constants."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = Path("/tmp/fexsics/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
API_TITLE = "Fexsics Forensic Image Analysis API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Physics-grounded multimodal forensic image analysis"
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# Analysis Configuration
JPEG_QUALITY_LEVELS = [70, 75, 80, 85, 90, 95]
DEFAULT_ELA_QUALITY = 90
CONFIDENCE_THRESHOLD = 0.5

# Engine Confidence Weights (sum should be <= 1.0 for proper Bayesian fusion)
ENGINE_WEIGHTS = {
    "ela": 0.18,
    "metadata": 0.15,
    "noise": 0.16,
    "illumination": 0.12,
    "geometry": 0.12,
    "deepfake": 0.14,
    "ai_gen": 0.13,
}

# Prior probability that an image is manipulated (base rate)
PRIOR_MANIPULATED = 0.15

# Supported image formats
SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "tiff", "tif", "webp", "bmp"}

# Report Configuration
REPORT_COMPANY_NAME = "Fexsics Forensic Lab"
REPORT_LOGO_PATH = BASE_DIR / "report" / "templates" / "logo.png"
REPORT_STANDARDS = [
    "ISO/IEC 27037:2012 (Digital forensics)",
    "SWGDE Best Practices",
    "ENFSI Guidelines",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "fexsics.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Physics thresholds
SHADOW_ANGLE_TOLERANCE = 15.0  # degrees
NOISE_STD_MULTIPLIER = 2.0  # standard deviations for anomaly detection
ELA_ANOMALY_THRESHOLD = 1.5  # multiplier of global mean
PERSPECTIVE_DEVIATION_THRESHOLD = 0.15  # 15% deviation in scale
