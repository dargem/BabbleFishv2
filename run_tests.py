"""Test runner script for BabbleFishv2 tests."""

"""
# Run all unit tests (fast using mocked api replies)
python run_tests.py

# Run integration tests with actual API calls
python run_tests.py --integration

# Run specific tests
pytest tests/test_translator.py -v

# Remove old test files
./cleanup_old_tests.sh
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test configuration
from tests.conftest import setup_test_environment, teardown_test_environment


def run_unit_tests():
    """Run only unit tests (fast, with mocked dependencies)."""
    print("Running unit tests...")
    setup_test_environment()

    try:
        # Discover and run unit tests
        loader = unittest.TestLoader()
        start_dir = Path(__file__).parent
        suite = loader.discover(str(start_dir), pattern="test_*.py")

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()
    finally:
        teardown_test_environment()


def run_integration_tests():
    """Run integration tests (slower, with real LLM calls)."""
    print("Running integration tests using actual API keys...")
    print("This uses API calls rather than simulated responses")

    setup_test_environment()

    try:
        # Import pytest to run integration tests without skip
        import pytest
        import os
        
        # Set environment variable to enable integration tests
        os.environ["RUN_INTEGRATION_TESTS"] = "true"
        
        # Run pytest with integration marker
        exit_code = pytest.main([
            "tests/", 
            "-v", 
            "-m", "integration or not integration",  # Run all tests including integration
            "--tb=short"
        ])
        
        return exit_code == 0
    finally:
        teardown_test_environment()


def run_specific_test(test_module, test_class=None, test_method=None):
    """Run a specific test module, class, or method."""
    setup_test_environment()

    try:
        loader = unittest.TestLoader()

        if test_method and test_class:
            suite = loader.loadTestsFromName(
                f"{test_module}.{test_class}.{test_method}"
            )
        elif test_class:
            suite = loader.loadTestsFromName(f"{test_module}.{test_class}")
        else:
            suite = loader.loadTestsFromName(test_module)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()
    finally:
        teardown_test_environment()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BabbleFishv2 tests")
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests (makes real API calls)",
    )
    parser.add_argument(
        "--module", type=str, help="Run specific test module (e.g., test_translator)"
    )
    parser.add_argument(
        "--class", type=str, dest="test_class", help="Run specific test class"
    )
    parser.add_argument("--method", type=str, help="Run specific test method")

    args = parser.parse_args()

    if args.module:
        success = run_specific_test(
            f"tests.{args.module}", args.test_class, args.method
        )
    elif args.integration:
        success = run_integration_tests()
    else:
        success = run_unit_tests()

    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)
