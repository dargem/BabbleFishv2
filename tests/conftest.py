"""Configuration and utilities for running tests."""

import os
import sys
from pathlib import Path

# Add src to Python path for tests
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test configuration
TEST_CONFIG = {
    "skip_integration_tests": True,
    "mock_llm_by_default": True,
    "test_data_dir": Path(__file__).parent / "data",
}


# Environment setup for tests
def setup_test_environment():
    """Set up test environment variables."""
    # Set dummy API keys for testing if not present
    if not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = "test-api-key-for-testing"


def teardown_test_environment():
    """Clean up test environment."""
    # Remove test API key if it was set by tests
    test_key = "test-api-key-for-testing"
    if os.getenv("GOOGLE_API_KEY") == test_key:
        del os.environ["GOOGLE_API_KEY"]
