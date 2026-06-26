"""
UNIT TESTS FOR FEXSICS BACKEND

Tests for all engines, utilities, and API endpoints.
Run with: pytest tests/test_engines.py -v
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
import cv2
from PIL import Image

from config import EVIDENCE_DIR, PRIOR_MANIPULATED
from utils.hash_utils import compute_sha256, generate_report_id
from utils.validators import validate_image_file, validate_case_info
from utils.image_utils import load_image_cv2, convert_bgr_to_gray

# Test fixtures

@pytest.fixture
def sample_image():
    """Create a sample test image."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        # Create a simple test image
        img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
        cv2.imwrite(tmp.name, img)
        yield tmp.name
        Path(tmp.name).unlink()


@pytest.fixture
def case_info():
    """Sample case information."""
    return {
        "case_number": "TEST-2024-001",
        "case_name": "Test Case v. Defendant",
        "investigator": "Test Investigator"
    }


# Tests for utilities

class TestHashUtils:
    """Test hash computation and report ID generation."""
    
    def test_compute_sha256(self, sample_image):
        """Test SHA-256 computation."""
        hash_val = compute_sha256(sample_image)
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64  # SHA-256 hex string
        assert all(c in '0123456789abcdef' for c in hash_val)
    
    def test_generate_report_id(self):
        """Test report ID generation."""
        report_id = generate_report_id()
        assert isinstance(report_id, str)
        assert report_id.startswith("FX-")
        assert len(report_id) == 11  # FX-YYYY-NNNN


class TestValidators:
    """Test validation functions."""
    
    def test_validate_case_info_valid(self, case_info):
        """Test validation of valid case info."""
        is_valid, msg = validate_case_info(case_info)
        assert is_valid
    
    def test_validate_case_info_invalid(self):
        """Test validation of invalid case info."""
        invalid_case = {
            "case_number": "",  # Empty
            "case_name": "Test"
        }
        is_valid, msg = validate_case_info(invalid_case)
        assert not is_valid
    
    def test_validate_image_file(self, sample_image):
        """Test image file validation."""
        is_valid, msg = validate_image_file(sample_image)
        assert is_valid


class TestImageUtils:
    """Test image utility functions."""
    
    def test_load_image_cv2(self, sample_image):
        """Test loading image with OpenCV."""
        img = load_image_cv2(sample_image)
        assert img is not None
        assert img.shape[2] == 3  # BGR channels
    
    def test_convert_bgr_to_gray(self, sample_image):
        """Test BGR to grayscale conversion."""
        img = load_image_cv2(sample_image)
        gray = convert_bgr_to_gray(img)
        assert gray is not None
        assert len(gray.shape) == 2


# Tests for forensic engines

class TestELAEngine:
    """Test ELA forensic engine."""
    
    @pytest.mark.unit
    def test_run_ela(self, sample_image):
        """Test ELA analysis."""
        from engines.ela_engine import run_ela
        
        result = run_ela(sample_image)
        
        assert result["engine"] == "ELA"
        assert result["verdict"] in ["authentic", "manipulated", "inconclusive", "error"]
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["findings"], list)
    
    @pytest.mark.unit
    def test_run_dct_analysis(self, sample_image):
        """Test DCT analysis."""
        from engines.ela_engine import run_dct_analysis
        
        result = run_dct_analysis(sample_image)
        
        assert result["engine"] == "DCT"
        assert result["verdict"] in ["authentic", "manipulated", "inconclusive", "error"]
        assert "raw_scores" in result


class TestMetadataEngine:
    """Test metadata forensic engine."""
    
    @pytest.mark.unit
    def test_extract_metadata(self, sample_image):
        """Test metadata extraction."""
        from engines.metadata_engine import extract_all_metadata
        
        result = extract_all_metadata(sample_image)
        
        assert "all_fields" in result
        assert "field_count" in result
        assert isinstance(result["field_count"], int)


class TestNoiseEngine:
    """Test noise physics engine."""
    
    @pytest.mark.unit
    def test_analyze_noise_field(self, sample_image):
        """Test noise field analysis."""
        from engines.noise_engine import analyze_noise_field
        
        result = analyze_noise_field(sample_image)
        
        assert "verdict" in result
        assert "confidence" in result
        assert "findings" in result


class TestFusionEngine:
    """Test Bayesian fusion engine."""
    
    @pytest.mark.unit
    def test_fuse_engine_results(self):
        """Test Bayesian fusion of results."""
        from engines.fusion_engine import fuse_engine_results
        
        # Create mock engine results
        mock_results = [
            {
                "engine": "ELA",
                "verdict": "manipulated",
                "confidence": 0.8,
                "findings": ["Test finding"],
                "physics_law_violated": "Test physics",
                "evidence_map_path": "",
                "raw_scores": {}
            },
            {
                "engine": "Metadata",
                "verdict": "authentic",
                "confidence": 0.7,
                "findings": ["Test finding"],
                "physics_law_violated": "Test physics",
                "evidence_map_path": "",
                "raw_scores": {}
            }
        ]
        
        result = fuse_engine_results(mock_results)
        
        assert result["engine"] == "Bayesian Fusion"
        assert result["verdict"] in ["authentic", "manipulated", "inconclusive"]
        assert 0 <= result["confidence"] <= 1
        assert "bayesian_data" in result


# Tests for API

class TestAPIEndpoints:
    """Test FastAPI endpoints."""
    
    @pytest.mark.integration
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        from fastapi.testclient import TestClient
        from app import app
        
        client = TestClient(app)
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.integration
    def test_root_endpoint(self):
        """Test root endpoint."""
        from fastapi.testclient import TestClient
        from app import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "FEXsics Forensic Analysis Backend"


# Integration tests

@pytest.mark.integration
class TestFullPipeline:
    """Test complete analysis pipeline."""
    
    def test_full_analysis(self, sample_image, case_info):
        """Test complete forensic analysis pipeline."""
        from engines import ela_engine, metadata_engine, fusion_engine
        
        # Run individual engines
        ela_result = ela_engine.run_ela(sample_image)
        metadata_result = metadata_engine.run_metadata_analysis(sample_image)
        
        # Fuse results
        fusion_result = fusion_engine.fuse_engine_results([ela_result, metadata_result])
        
        # Verify results
        assert fusion_result["engine"] == "Bayesian Fusion"
        assert fusion_result["verdict"] in ["authentic", "manipulated", "inconclusive"]
        assert 0 <= fusion_result["confidence"] <= 1


# Performance tests

@pytest.mark.performance
def test_image_loading_performance(sample_image):
    """Test image loading performance."""
    import time
    
    start = time.time()
    for _ in range(100):
        load_image_cv2(sample_image)
    elapsed = time.time() - start
    
    # Should complete 100 loads in < 5 seconds
    assert elapsed < 5, f"Image loading too slow: {elapsed:.2f}s for 100 loads"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
