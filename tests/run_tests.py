#!/usr/bin/env python
"""
Run tests for the Maritime Efficiency project
"""
import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    """Run the test suite"""
    # Define test categories
    model_tests = [
        "test_vessel.py",
    ]

    utility_tests = [
        "test_data_processing.py",
        "test_emissions.py",
    ]

    page_tests = [
        "test_vessel_input_page.py",
    ]

    all_tests = model_tests + utility_tests + page_tests

    # Run the tests
    if len(sys.argv) > 1:
        # If a specific test suite is specified
        suite = sys.argv[1].lower()
        if suite == "models":
            exit_code = pytest.main(model_tests + ["-v"])
        elif suite == "utils":
            exit_code = pytest.main(utility_tests + ["-v"])
        elif suite == "pages":
            exit_code = pytest.main(page_tests + ["-v"])
        else:
            print(f"Unknown test suite: {suite}")
            print("Available suites: models, utils, pages")
            exit_code = 1
    else:
        # Run all tests
        exit_code = pytest.main(all_tests + ["-v"])

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
