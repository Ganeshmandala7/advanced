"""Integration tests."""

import pytest


@pytest.mark.integration
def test_full_pipeline_import():
    """Test that full pipeline can be imported."""
    import fexsics
    from fexsics.layers import (
        photon_physics,
        signal_processing,
        geometry_perspective,
        compression_physics,
        deep_learning,
        metadata_chain,
        bayesian_fusion
    )
    
    assert photon_physics is not None
