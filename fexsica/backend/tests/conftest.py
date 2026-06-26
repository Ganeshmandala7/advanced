"""
PYTEST CONFIGURATION

Shared fixtures and configuration for all tests.
"""

import pytest
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as a performance test"
    )


# You can add global fixtures here that are used across test files
