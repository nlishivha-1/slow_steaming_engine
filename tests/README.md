# Maritime Efficiency Tests

This directory contains unit tests for the Maritime Efficiency application.

## Test Structure

The tests are organized into three categories:

1. **Model Tests**: Tests for the data model classes in `models/`
2. **Utility Tests**: Tests for utility functions in `utils/`
3. **Page Tests**: Tests for Streamlit page functionality in `_pages/`

## Running the Tests

You can run the tests using the `run_tests.py` script:

```bash
# Run all tests
./run_tests.py

# Run specific test suites
./run_tests.py models
./run_tests.py utils
./run_tests.py pages
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_vessel.py

# Run a specific test function
pytest tests/test_vessel.py::test_vessel_initialization
```

## Test Coverage

To run tests with coverage reports:

```bash
# Install coverage dependencies
pip install pytest-cov

# Run tests with coverage
pytest --cov=models --cov=utils --cov=_pages

# Generate HTML coverage report
pytest --cov=models --cov=utils --cov=_pages --cov-report=html
```

## Adding New Tests

When adding new tests:

1. Create a new file named `test_<module>.py` in the `tests/` directory
2. Import the module to be tested
3. Create test functions prefixed with `test_`
4. Use fixtures from `conftest.py` as needed
5. Add the new test file to the appropriate category in `run_tests.py` 