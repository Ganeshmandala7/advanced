"""Unit tests for core components."""

import pytest
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    return np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)


def test_config_import():
    """Test configuration module import."""
    from fexsics.core.config import Config
    config = Config()
    assert config.project_name == "FeXsics"
    assert config.version == "0.1.0"


def test_image_processor_import():
    """Test image processor import."""
    from fexsics.core.image_processor import ImageProcessor
    processor = ImageProcessor()
    assert processor.image is None
    assert processor.analysis_results == {}


def test_image_utils():
    """Test image utilities."""
    from fexsics.utils.image_utils import ImageUtils
    
    image = np.ones((10, 10, 3), dtype=np.uint8) * 255
    normalized = ImageUtils.normalize(image)
    
    assert normalized.min() == pytest.approx(1.0)
    assert normalized.max() == pytest.approx(1.0)


@pytest.mark.unit
def test_bayesian_fusion():
    """Test Bayesian fusion engine."""
    from fexsics.layers.bayesian_fusion import BayesianFusionEngine
    
    engine = BayesianFusionEngine(prior_authentic=0.5)
    engine.add_evidence("layer1", 2.0)  # Evidence supporting forgery
    
    verdict = engine.get_verdict()
    assert "verdict" in verdict
    assert "confidence" in verdict
    assert "posterior_probability" in verdict
