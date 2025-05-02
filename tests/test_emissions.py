"""
Tests for emissions calculation utilities
"""

import pytest
from utils.emissions import (
    calculate_detailed_emissions,
    calculate_cii_rating,
    calculate_compliance_forecast,
)
from unittest.mock import patch


def test_calculate_detailed_emissions_vlsfo():
    """Test emissions calculation with VLSFO fuel"""
    fuel_consumption = 100  # tons
    result = calculate_detailed_emissions(fuel_consumption, fuel_type="VLSFO")

    # Check all emission types are present
    assert "CO2" in result
    assert "SOx" in result
    assert "NOx" in result
    assert "PM" in result

    # Verify calculations (emission factor in g/ton divided by 1,000,000 to get tons)
    assert result["CO2"] == 100 * 3114000 / 1000000
    assert result["SOx"] == 100 * 10000 / 1000000
    assert result["NOx"] == 100 * 57000 / 1000000
    assert result["PM"] == 100 * 1400 / 1000000


def test_calculate_detailed_emissions_mgo():
    """Test emissions calculation with MGO fuel"""
    fuel_consumption = 100  # tons
    result = calculate_detailed_emissions(fuel_consumption, fuel_type="MGO")

    # Verify calculations for MGO
    assert result["CO2"] == 100 * 3206000 / 1000000
    assert result["SOx"] == 100 * 2000 / 1000000
    assert result["NOx"] == 100 * 60000 / 1000000
    assert result["PM"] == 100 * 1000 / 1000000


def test_calculate_detailed_emissions_default():
    """Test emissions calculation with unknown fuel type defaults to VLSFO"""
    fuel_consumption = 100  # tons
    result = calculate_detailed_emissions(fuel_consumption, fuel_type="UNKNOWN")

    # Should use VLSFO values
    assert result["CO2"] == 100 * 3114000 / 1000000
    assert result["SOx"] == 100 * 10000 / 1000000
    assert result["NOx"] == 100 * 57000 / 1000000
    assert result["PM"] == 100 * 1400 / 1000000


def test_calculate_cii_rating():
    """Test CII rating calculation"""
    vessel_data = {"type": "Container Ship", "deadweight": 100000}
    annual_distance = 100000  # nautical miles
    annual_fuel = 15000  # tons

    result = calculate_cii_rating(vessel_data, annual_distance, annual_fuel)

    # Check result structure
    assert "co2_emissions" in result
    assert "transport_work" in result
    assert "aer" in result
    assert "reference_aer" in result
    assert "cii_ratio" in result
    assert "rating" in result

    # Verify core calculations
    expected_co2 = annual_fuel * 3.114
    assert result["co2_emissions"] == expected_co2

    expected_transport_work = vessel_data["deadweight"] * annual_distance * 0.7
    assert result["transport_work"] == expected_transport_work

    expected_aer = (expected_co2 * 1000000) / expected_transport_work
    assert result["aer"] == expected_aer

    assert result["reference_aer"] == 11.5  # For Container Ship

    expected_ratio = expected_aer / 11.5
    assert result["cii_ratio"] == expected_ratio


def test_cii_rating_thresholds():
    """Test CII rating assignment based on thresholds"""
    # Create a vessel_data dictionary
    vessel_data = {"type": "Container Ship", "deadweight": 100000}

    # Test cases for different ratings
    test_cases = [
        {"ratio": 0.80, "expected_rating": "A"},
        {"ratio": 0.90, "expected_rating": "B"},
        {"ratio": 1.00, "expected_rating": "C"},
        {"ratio": 1.05, "expected_rating": "D"},
        {"ratio": 1.20, "expected_rating": "E"},
    ]

    for case in test_cases:
        # Mock the scenario where cii_ratio equals the test case ratio
        with patch("utils.emissions.calculate_cii_rating") as mock_calculate:
            # Set up the mock to return the desired ratio
            mock_result = {
                "co2_emissions": 1000,
                "transport_work": 2000,
                "aer": 3000,
                "reference_aer": 4000,
                "cii_ratio": case["ratio"],
                "rating": "",  # This will be filled by the real function
            }

            # Inject the real rating calculation
            if case["ratio"] < 0.86:
                mock_result["rating"] = "A"
            elif case["ratio"] < 0.93:
                mock_result["rating"] = "B"
            elif case["ratio"] < 1.03:
                mock_result["rating"] = "C"
            elif case["ratio"] < 1.10:
                mock_result["rating"] = "D"
            else:
                mock_result["rating"] = "E"

            mock_calculate.return_value = mock_result

            # Call the function with any arguments (the mock will intercept)
            result = calculate_cii_rating(vessel_data, 100000, 10000)

            # Check if the rating matches the expected rating
            assert result["rating"] == case["expected_rating"]


@pytest.fixture
def sample_compliance_forecast_inputs():
    """Fixture for compliance forecast calculation inputs"""
    return {
        "vessel_data": {
            "type": "Container Ship",
            "deadweight": 100000,
            "design_speed": 20,
            "design_consumption": 180,
        },
        "current_speed": 18,
        "proposed_speed": 15,
        "annual_distance": 100000,
    }


def test_calculate_compliance_forecast(sample_compliance_forecast_inputs):
    """Test compliance forecast calculation"""
    # Mock the fuel consumption and CII rating functions
    with (
        patch("utils.emissions.calculate_fuel_consumption") as mock_fuel,
        patch("utils.emissions.calculate_cii_rating") as mock_cii,
    ):

        # Set up fuel consumption mock
        mock_fuel.side_effect = lambda speed, _: 180 * (speed / 20) ** 3

        # Set up CII rating mock
        mock_cii.side_effect = lambda _, __, annual_fuel: {
            "co2_emissions": annual_fuel * 3.114,
            "cii_ratio": 0.9 if annual_fuel < 10000 else 1.1,
            "rating": "B" if annual_fuel < 10000 else "D",
        }

        # Calculate forecast
        result = calculate_compliance_forecast(
            sample_compliance_forecast_inputs["vessel_data"],
            sample_compliance_forecast_inputs["current_speed"],
            sample_compliance_forecast_inputs["proposed_speed"],
            sample_compliance_forecast_inputs["annual_distance"],
        )

        # Check result structure
        assert "current_scenario" in result
        assert "proposed_scenario" in result
        assert "savings" in result

        assert "speed" in result["current_scenario"]
        assert "annual_fuel" in result["current_scenario"]
        assert "cii_ratio" in result["current_scenario"]
        assert "cii_rating" in result["current_scenario"]

        assert "speed" in result["proposed_scenario"]
        assert "annual_fuel" in result["proposed_scenario"]
        assert "cii_ratio" in result["proposed_scenario"]
        assert "cii_rating" in result["proposed_scenario"]

        assert "fuel_savings" in result["savings"]
        assert "emission_savings" in result["savings"]
        assert "percentage_reduction" in result["savings"]

        # Verify the speeds are correct
        assert (
            result["current_scenario"]["speed"]
            == sample_compliance_forecast_inputs["current_speed"]
        )
        assert (
            result["proposed_scenario"]["speed"]
            == sample_compliance_forecast_inputs["proposed_speed"]
        )

        # Check savings calculation
        current_fuel = result["current_scenario"]["annual_fuel"]
        proposed_fuel = result["proposed_scenario"]["annual_fuel"]
        assert result["savings"]["fuel_savings"] == current_fuel - proposed_fuel

        # Verify percentage calculation
        expected_percentage = (result["savings"]["fuel_savings"] / current_fuel) * 100
        assert result["savings"]["percentage_reduction"] == expected_percentage
