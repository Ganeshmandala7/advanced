# FEXsics Backend - Forensic Image Analysis System

## Overview

**FEXsics** (Forensic Expert System for Image Credibility & Authenticity) is a production-ready forensic image analysis backend that uses physics-grounded multimodal analysis to detect image manipulation, deepfakes, and AI-generated content.

The system combines 7 specialized physics-based forensic engines with Bayesian inference to produce courtroom-grade authenticity verdicts suitable for litigation and expert testimony.

## Architecture

### 7 Forensic Engines

1. **ELA Engine** - JPEG Compression Forensics
   - Re-compression analysis at known quality levels
   - Double JPEG compression detection via DCT histogram
   - JPEG block boundary misalignment detection

2. **Metadata Engine** - Camera & Chain of Custody
   - EXIF metadata extraction and analysis
   - Timestamp consistency validation
   - GPS coordinate verification
   - Software fingerprint detection
   - Metadata completeness analysis

3. **Noise Engine** - Sensor Physics
   - Noise variance uniformity analysis
   - PRNU (Photo Response Non-Uniformity) sensor fingerprint
   - Frequency domain (1/f spectrum) analysis

4. **Illumination Engine** - Light Source Physics
   - Light source position estimation
   - Shadow consistency analysis
   - Chromatic aberration detection

5. **Geometry Engine** - 3D Perspective Physics
   - Vanishing point detection
   - Perspective consistency analysis
   - Geometric constraint validation

6. **Deepfake Engine** - GAN Synthesis Detection
   - Face detection and analysis
   - Eye artifact detection
   - Facial geometry consistency
   - Frequency domain anomalies

7. **AI-Gen Engine** - AI Generation Detection
   - Noise distribution analysis
   - Patch redundancy detection
   - Texture uniformity analysis
   - Frequency spectrum deviation

8. **Fusion Engine** - Bayesian Inference
   - Combines all 7 engines using Bayes' theorem
   - Computes posterior probability P(Manipulated | Evidence)
   - Generates legally defensible conclusions

## Quick Start

### Installation

```bash
# Navigate to backend directory
cd backend/

# Install dependencies
pip install -r requirements.txt

# Create evidence directory
mkdir -p /tmp/fexsics/evidence
```

### Running the API Server

```bash
# Start FastAPI server
python app.py

# Server runs on http://localhost:8000
# API documentation: http://localhost:8000/api/docs
```

### Running Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test class
pytest tests/test_engines.py::TestELAEngine -v

# Run with markers
pytest tests/ -m unit -v
pytest tests/ -m integration -v
```

## API Endpoints

### Main Analysis Endpoint

**POST** `/api/v1/analyze`

Upload image and case information for forensic analysis.

**Request (Multipart Form):**
- `file`: Image file (JPEG, PNG, TIFF, WEBP, BMP)
- `case_number`: Case identifier
- `case_name`: Case name
- `investigator`: Investigator name (optional)
- `include_report`: Generate PDF report (default: true)

**Response:**
```json
{
  "status": "success",
  "case_number": "2024-001234",
  "analysis_id": "FX-2024-0001",
  "image_hash": "abc123def456...",
  "verdict": "manipulated",
  "confidence": 0.82,
  "engine_results": [
    {
      "engine": "ELA",
      "verdict": "manipulated",
      "confidence": 0.85,
      "findings": ["..."],
      "physics_law_violated": "Deterministic JPEG compression",
      "raw_scores": {}
    }
  ],
  "bayesian_data": {
    "posterior_manipulated": 0.82,
    "posterior_authentic": 0.18,
    "engine_contributions": {}
  },
  "report_path": "/tmp/fexsics/evidence/report_FX-2024-0001.pdf",
  "report_hash": "xyz789...",
  "summary": "Forensic analysis indicates 82% probability of manipulation..."
}
```

### Other Endpoints

- **GET** `/api/v1/health` - Service health check
- **GET** `/api/v1/report/{analysis_id}` - Download PDF report
- **GET** `/api/v1/evidence/{evidence_id}` - Download evidence heatmap
- **POST** `/api/v1/validate-image` - Pre-validate image before analysis
- **GET** `/api/v1/status/{analysis_id}` - Check analysis status

## Configuration

Edit `config.py` to customize:

- `EVIDENCE_DIR` - Directory for evidence maps and reports
- `MAX_UPLOAD_SIZE` - Maximum image file size (default: 50MB)
- `JPEG_QUALITY_LEVELS` - Quality levels for ELA analysis
- `DEFAULT_ELA_QUALITY` - Default JPEG quality for re-compression
- `ELA_ANOMALY_THRESHOLD` - Threshold for ELA anomaly detection (in σ)
- `NOISE_STD_MULTIPLIER` - Noise anomaly detection multiplier
- `SHADOW_ANGLE_TOLERANCE` - Shadow angle tolerance (degrees)
- `PERSPECTIVE_DEVIATION_THRESHOLD` - Perspective deviation threshold
- `PRIOR_MANIPULATED` - Prior probability of manipulation (base rate)
- `ENGINE_WEIGHTS` - Contribution weights for each engine in fusion

## Physics Principles

Each engine enforces fundamental physical laws:

| Engine | Physics Principle | Violation Indicates |
|--------|-------------------|---------------------|
| ELA | Deterministic JPEG compression | Different compression histories (editing) |
| Metadata | Physical cause-and-effect | Temporal/spatial/equipment inconsistencies |
| Noise | Unique sensor fingerprint (PRNU) | Multiple sources or re-compression |
| Illumination | Lambertian + Phong reflectance | Mismatched light sources or splicing |
| Geometry | Perspective projection consistency | Misaligned vanishing points or warping |
| Deepfake | 3D geometry + optical reflection | GAN-synthesized content |
| AI-Gen | Natural sensor noise statistics | Neural network synthesis artifacts |

## Chain of Custody

All images are protected via SHA-256 hashing:

1. **Original image hash** computed immediately upon upload
2. **Evidence maps** saved with UUID filenames in `/tmp/fexsics/evidence/`
3. **Report hash** ensures report integrity
4. All hashes included in PDF report for auditability

This ensures forensic defensibility for legal proceedings.

## Output Report

The generated PDF report contains 9 pages:

1. **Cover** - Case information and metadata
2. **Executive Summary** - Main verdict and confidence
3. **Findings Table** - All engine verdicts and key findings
4. **Visual Evidence** - Heatmaps from engines
5. **Bayesian Analysis** - Posterior probabilities
6. **Metadata Summary** - EXIF and equipment info
7. **Methodology** - Forensic principles explanation
8. **Expert Declaration** - Legal certification with hash chain
9. **Footer** - Audit trail and hashes

## Bayesian Fusion

The fusion engine applies Bayes' theorem:

```
P(Manipulated|Evidence) = P(Evidence|Manipulated) × P(Manipulated) / P(Evidence)
```

Where:
- **Prior** P(Manipulated) = 0.15 (base rate from literature)
- **Likelihoods** computed from each engine's verdict and confidence
- **Posterior** provides legally defensible probability

## Error Handling

All endpoints return standardized error responses:

```json
{
  "status": "error",
  "error_code": "INVALID_IMAGE_FORMAT",
  "message": "Image must be JPEG, PNG, TIFF, WEBP, or BMP format",
  "details": {
    "provided_format": "GIF",
    "allowed_formats": ["JPEG", "PNG", "TIFF", "WEBP", "BMP"]
  }
}
```

## Performance

Typical analysis time (per image):
- **ELA Analysis** - 2-5 seconds
- **Metadata Extraction** - 0.5-1 second
- **Noise Analysis** - 1-3 seconds
- **Illumination Analysis** - 1-2 seconds
- **Geometry Analysis** - 1-3 seconds
- **Deepfake Analysis** - 1-2 seconds
- **AI-Gen Analysis** - 1-2 seconds
- **Bayesian Fusion** - <0.1 seconds
- **Report Generation** - 1-2 seconds

**Total: ~10-20 seconds per image**

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tif, .tiff)
- WebP (.webp)
- BMP (.bmp)

Requirements:
- Minimum dimension: 32x32 pixels
- Maximum dimension: 65536x65536 pixels
- Maximum aspect ratio: 10:1
- Maximum file size: 50MB

## Requirements

- Python 3.10+
- FastAPI 0.110.0+
- OpenCV 4.9.0.80
- NumPy 1.26.4
- SciPy 1.13.0
- PIL/Pillow 10.3.0
- PyTorch (optional, for advanced models)
- ReportLab 4.1.0
- Pydantic 2.7.0
- exifread, piexif, geopy, astral

See `requirements.txt` for exact versions.

## Development

### Project Structure

```
backend/
├── app.py                 # Main FastAPI application
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── api/
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic models
├── engines/
│   ├── __init__.py
│   ├── ela_engine.py      # JPEG forensics
│   ├── metadata_engine.py # Metadata analysis
│   ├── noise_engine.py    # Sensor physics
│   ├── illumination_engine.py  # Light physics
│   ├── geometry_engine.py # Perspective physics
│   ├── deepfake_engine.py # Deepfake detection
│   ├── ai_gen_engine.py   # AI detection
│   └── fusion_engine.py   # Bayesian fusion
├── report/
│   ├── __init__.py
│   ├── generator.py       # PDF report generation
│   └── templates/         # Report templates
├── utils/
│   ├── __init__.py
│   ├── image_utils.py     # Image I/O and processing
│   ├── hash_utils.py      # SHA-256 chain of custody
│   └── validators.py      # Input validation
└── tests/
    ├── conftest.py
    └── test_engines.py    # Unit tests
```

### Adding a New Engine

1. Create `new_engine.py` in `engines/`
2. Implement functions following standardized format
3. Return dict with: `engine`, `verdict`, `confidence`, `findings`, etc.
4. Update `engines/__init__.py` exports
5. Add to `api/routes.py` analysis pipeline
6. Add test class to `tests/test_engines.py`

### Code Standards

- **Type hints** required on all functions
- **Docstrings** for all public methods
- **Logging** at INFO, DEBUG, ERROR levels
- **Exception handling** returns error dicts (never crashes)
- **Confidence scores** strictly 0.0-1.0 (never 1.0)
- **Black formatter** with 100-char line length
- **Pytest** with unit/integration markers

## Legal & Ethical Use

This system is designed for:
- ✅ Legitimate forensic analysis
- ✅ Evidence preservation in legal proceedings
- ✅ Research and academic use
- ✅ Expert testimony support

Not intended for:
- ❌ Unauthorized surveillance
- ❌ Privacy violation
- ❌ Fabricating false evidence
- ❌ Any illegal purpose

Users must comply with all applicable laws and regulations.

## References

- NIST Digital Forensics Guidelines
- ISO/IEC 27037 Guidelines for IT Evidence Preservation
- ACM Workshop on Multimedia Forensics
- IEEE Transactions on Image Processing

## Support

For issues, feature requests, or questions:
- Check existing documentation
- Review test cases for examples
- Examine engine source code comments

## License

This project is part of the FeXsics academic research initiative.
