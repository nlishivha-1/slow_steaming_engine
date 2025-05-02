"""
Tests for data processing utilities
"""

import pytest
import pandas as pd
import json
import io
from utils.data_processing import (
    load_sample_vessel_data,
    load_sample_route_data,
    prepare_vessel_data,
    prepare_route_data,
    calculate_transit_time,
)
from unittest.mock import patch, mock_open


def test_load_sample_vessel_data():
    """Test loading sample vessel data with mocked file"""
    sample_data = {"vessels": [{"name": "Test Vessel", "type": "Container Ship"}]}

    # Mock file opening and reading
    with patch("builtins.open", mock_open(read_data=json.dumps(sample_data))):
        result = load_sample_vessel_data()
        assert result == sample_data


def test_load_sample_vessel_data_fallback():
    """Test fallback to default data when file is not found"""
    # Mock FileNotFoundError when opening the file
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_sample_vessel_data()

        # Check the structure of the fallback data
        assert "vessels" in result
        assert len(result["vessels"]) > 0
        assert "name" in result["vessels"][0]
        assert "type" in result["vessels"][0]


def test_load_sample_route_data():
    """Test loading sample route data with mocked file"""
    sample_data = {"routes": [{"name": "Test Route", "distance": 1000}]}

    # Mock file opening and reading
    with patch("builtins.open", mock_open(read_data=json.dumps(sample_data))):
        result = load_sample_route_data()
        assert result == sample_data


def test_load_sample_route_data_fallback():
    """Test fallback to default data when file is not found"""
    # Mock FileNotFoundError when opening the file
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_sample_route_data()

        # Check the structure of the fallback data
        assert "routes" in result
        assert len(result["routes"]) > 0
        assert "name" in result["routes"][0]
        assert "distance" in result["routes"][0]
        assert "waypoints" in result["routes"][0]


class MockUploadedFile:
    """Mock class for Streamlit's UploadedFile"""

    def __init__(self, content, filename):
        self.content = content
        self.name = filename

    def getvalue(self):
        return self.content


def test_prepare_vessel_data_csv():
    """Test processing CSV vessel data file"""
    # Create a mock CSV file
    csv_content = "name,type,length\nTest Vessel,Container Ship,300"
    csv_bytes = csv_content.encode("utf-8")
    mock_file = MockUploadedFile(csv_bytes, "vessel_data.csv")

    # Mock pandas read_csv to return a predefined DataFrame
    with patch("pandas.read_csv") as mock_read_csv:
        mock_df = pd.DataFrame(
            {"name": ["Test Vessel"], "type": ["Container Ship"], "length": [300]}
        )
        mock_read_csv.return_value = mock_df

        result = prepare_vessel_data(mock_file)

        # Check the processed data
        assert "vessels" in result
        assert len(result["vessels"]) == 1
        assert result["vessels"][0]["name"] == "Test Vessel"
        assert result["vessels"][0]["type"] == "Container Ship"
        assert result["vessels"][0]["length"] == 300


def test_prepare_vessel_data_excel():
    """Test processing Excel vessel data file"""
    # Create a mock Excel file
    mock_file = MockUploadedFile(b"dummy excel content", "vessel_data.xlsx")

    # Mock pandas read_excel to return a predefined DataFrame
    with patch("pandas.read_excel") as mock_read_excel:
        mock_df = pd.DataFrame(
            {"name": ["Test Vessel"], "type": ["Container Ship"], "length": [300]}
        )
        mock_read_excel.return_value = mock_df

        result = prepare_vessel_data(mock_file)

        # Check the processed data
        assert "vessels" in result
        assert len(result["vessels"]) == 1
        assert result["vessels"][0]["name"] == "Test Vessel"
        assert result["vessels"][0]["type"] == "Container Ship"
        assert result["vessels"][0]["length"] == 300


def test_prepare_vessel_data_json():
    """Test processing JSON vessel data file"""
    # Create a mock JSON file
    vessel_data = [{"name": "Test Vessel", "type": "Container Ship", "length": 300}]
    json_content = json.dumps(vessel_data).encode("utf-8")
    mock_file = MockUploadedFile(json_content, "vessel_data.json")

    result = prepare_vessel_data(mock_file)

    # Check the processed data
    assert "vessels" in result
    assert len(result["vessels"]) == 1
    assert result["vessels"][0]["name"] == "Test Vessel"
    assert result["vessels"][0]["type"] == "Container Ship"
    assert result["vessels"][0]["length"] == 300


def test_prepare_vessel_data_unsupported_format():
    """Test error handling for unsupported file format"""
    # Create a mock file with unsupported extension
    mock_file = MockUploadedFile(b"dummy content", "vessel_data.txt")

    # Check that function raises ValueError for unsupported format
    with pytest.raises(ValueError) as excinfo:
        prepare_vessel_data(mock_file)

    assert "Unsupported file format" in str(excinfo.value)


def test_prepare_route_data_json():
    """Test processing JSON route data file"""
    # Create a mock JSON file
    route_data = [{"name": "Test Route", "distance": 5000}]
    json_content = json.dumps(route_data).encode("utf-8")
    mock_file = MockUploadedFile(json_content, "route_data.json")

    result = prepare_route_data(mock_file)

    # Check the processed data
    assert "routes" in result
    assert len(result["routes"]) == 1
    assert result["routes"][0]["name"] == "Test Route"
    assert result["routes"][0]["distance"] == 5000


def test_calculate_transit_time():
    """Test transit time calculation"""
    # Test with normal values
    distance = 1000  # nautical miles
    speed = 20  # knots
    expected_time = 1000 / (20 * 24)  # days

    assert calculate_transit_time(distance, speed) == expected_time

    # Test with zero speed
    assert calculate_transit_time(distance, 0) == float("inf")

    # Test with negative speed
    assert calculate_transit_time(distance, -5) == float("inf")
