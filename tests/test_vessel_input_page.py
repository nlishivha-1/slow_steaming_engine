"""
Tests for the vessel_input page
"""

import pytest
from unittest.mock import patch, MagicMock
import _pages.vessel_input as vessel_input
from models.vessel import Vessel


def test_vessel_input_initialization(mock_streamlit):
    """Test the vessel input page initialization"""
    # Create a mock session state
    mock_streamlit.session_state = {}

    # Call the app function
    vessel_input.app()

    # Check that the title was set
    mock_streamlit.title.assert_called_once_with("Vessel Specifications Input")

    # Check that markdown was called
    mock_streamlit.markdown.assert_called()

    # Check that session state was initialized
    assert "vessel_data" in mock_streamlit.session_state


def test_vessel_input_displays_current_data(mock_streamlit):
    """Test that current vessel data is displayed when available"""
    # Create a test vessel
    test_vessel = Vessel(
        {
            "name": "Test Vessel",
            "type": "Container Ship",
            "length": 300,
            "beam": 40,
            "draft": 14.5,
            "deadweight": 100000,
            "engine_type": "MAN B&W 12K98ME-C",
            "max_speed": 25,
            "design_speed": 20,
            "design_consumption": 180,
            "year_built": 2010,
        }
    )

    # Set up mock session state with vessel data
    mock_streamlit.session_state = {"vessel_data": test_vessel.to_dict()}

    # Create mock columns
    col1_mock = MagicMock()
    col2_mock = MagicMock()
    mock_streamlit.columns.return_value = [col1_mock, col2_mock]

    # Call the app function
    vessel_input.app()

    # Check that the header was displayed
    mock_streamlit.header.assert_called_with("Current Vessel Specifications")

    # Check that columns were created for display
    mock_streamlit.columns.assert_called_with(2)

    # Verify subheaders
    col1_mock.subheader.assert_called_with("Basic Information")
    col2_mock.subheader.assert_called_with("Performance Parameters")

    # Check that vessel data was written
    # Note: In a real test, you would check specific write calls, but this depends on
    # the exact implementation of the vessel_input.app() function


@patch("_pages.vessel_input.load_sample_vessel_data")
def test_vessel_input_sample_data(mock_load_sample, mock_streamlit):
    """Test loading sample data in the vessel input page"""
    # Setup mock for radio button
    mock_streamlit.radio.return_value = "Use Sample Data"

    # Setup mock sample data
    mock_sample_data = {
        "vessels": [
            {"name": "Sample Vessel 1", "type": "Container Ship"},
            {"name": "Sample Vessel 2", "type": "Bulk Carrier"},
        ]
    }
    mock_load_sample.return_value = mock_sample_data

    # Setup mock for selectbox - select the first vessel
    vessel_names = [v.get("name") for v in mock_sample_data["vessels"]]
    mock_streamlit.selectbox.return_value = vessel_names[0]

    # Setup mock for button - simulate button press
    mock_streamlit.button.return_value = True

    # Setup session state
    mock_streamlit.session_state = {}

    # Call the app function
    vessel_input.app()

    # Verify that load_sample_vessel_data was called
    mock_load_sample.assert_called_once()

    # Verify that selectbox for vessels was displayed
    mock_streamlit.selectbox.assert_called_with("Select a vessel", vessel_names)

    # Verify that button was created
    mock_streamlit.button.assert_called_with(
        "Use Selected Sample Data", use_container_width=True
    )

    # Check that vessel data was saved to session state
    assert "vessel_data" in mock_streamlit.session_state


@patch("_pages.vessel_input.prepare_vessel_data")
def test_vessel_input_file_upload(mock_prepare_data, mock_streamlit):
    """Test file upload in the vessel input page"""
    # Setup mock for radio button
    mock_streamlit.radio.return_value = "Upload File"

    # Create a mock uploaded file
    mock_file = MagicMock()
    mock_streamlit.file_uploader.return_value = mock_file

    # Setup mock prepared data
    mock_vessel_data = {"vessels": [{"name": "Uploaded Vessel", "type": "Oil Tanker"}]}
    mock_prepare_data.return_value = mock_vessel_data

    # Setup mock for selectbox - select the vessel
    vessel_names = [v.get("name") for v in mock_vessel_data["vessels"]]
    mock_streamlit.selectbox.return_value = vessel_names[0]

    # Setup session state
    mock_streamlit.session_state = {}

    # Call the app function
    vessel_input.app()

    # Verify that file uploader was displayed
    mock_streamlit.file_uploader.assert_called_with(
        "Upload vessel data file", type=["csv", "xlsx", "json"]
    )

    # Verify that prepare_vessel_data was called with the uploaded file
    mock_prepare_data.assert_called_once_with(mock_file)

    # Verify that selectbox for vessels was displayed
    mock_streamlit.selectbox.assert_called_with("Select a vessel", vessel_names)

    # Check that vessel data was saved to session state
    assert "vessel_data" in mock_streamlit.session_state
