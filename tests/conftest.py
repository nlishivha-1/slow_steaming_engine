"""
Pytest configurations and fixtures for the Maritime Efficiency application.
"""

import pytest
import pandas as pd
import os
import json
from models.vessel import Vessel
from models.route import Route
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def sample_vessel_data():
    """
    Fixture providing sample vessel data for testing
    """
    return {
        "name": "Test Vessel",
        "type": "Container Ship",
        "length": 300,
        "beam": 40,
        "draft": 14.5,
        "deadweight": 100000,
        "engine_type": "MAN B&W 12K98ME-C",
        "max_speed": 25,
        "max_power": 68000,
        "design_speed": 20,
        "design_consumption": 180,
        "year_built": 2010,
    }


@pytest.fixture
def sample_vessel(sample_vessel_data):
    """
    Fixture providing a sample Vessel instance for testing
    """
    return Vessel(sample_vessel_data)


@pytest.fixture
def sample_route_data():
    """
    Fixture providing sample route data for testing
    """
    return {
        "name": "Test Route",
        "departure_port": "Rotterdam",
        "arrival_port": "Singapore",
        "distance": 8200,  # nautical miles
        "waypoints": [
            {"lat": 51.95, "lon": 4.12, "name": "Rotterdam"},
            {"lat": 35.95, "lon": -5.54, "name": "Gibraltar Strait"},
            {"lat": 31.25, "lon": 32.35, "name": "Suez Canal"},
            {"lat": 12.65, "lon": 43.35, "name": "Bab el-Mandeb"},
            {"lat": 1.25, "lon": 103.83, "name": "Singapore"},
        ],
    }


@pytest.fixture
def mock_streamlit():
    """
    Fixture for mocking Streamlit for page testing
    """
    import sys
    from unittest.mock import MagicMock

    mock_st = MagicMock()
    sys.modules["streamlit"] = mock_st
    yield mock_st
    del sys.modules["streamlit"]
