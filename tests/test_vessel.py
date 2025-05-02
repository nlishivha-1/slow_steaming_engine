"""
Tests for the Vessel model class
"""

import pytest
from models.vessel import Vessel
import math


def test_vessel_initialization(sample_vessel_data):
    """Test the vessel initialization with valid data"""
    vessel = Vessel(sample_vessel_data)

    # Test basic properties are set correctly
    assert vessel.name == "Test Vessel"
    assert vessel.type == "Container Ship"
    assert vessel.length == 300
    assert vessel.beam == 40
    assert vessel.draft == 14.5
    assert vessel.deadweight == 100000
    assert vessel.engine_type == "MAN B&W 12K98ME-C"
    assert vessel.max_speed == 25
    assert vessel.max_power == 68000
    assert vessel.design_speed == 20
    assert vessel.design_consumption == 180
    assert vessel.year_built == 2010


def test_vessel_default_values():
    """Test vessel initialization with empty data uses default values"""
    vessel = Vessel({})

    # Check that default values are applied
    assert vessel.name == "Unknown Vessel"
    assert vessel.type == "Container Ship"
    assert vessel.length == 300
    assert vessel.beam == 40
    assert vessel.draft == 14.5
    assert vessel.deadweight == 100000
    assert vessel.engine_type == "Unknown"
    assert vessel.max_speed == 25
    assert vessel.design_speed == 20
    assert vessel.design_consumption == 180
    assert vessel.year_built == 2010


def test_derived_parameters(sample_vessel):
    """Test the calculated derived parameters are correct"""
    # Specific fuel consumption based on year_built
    assert sample_vessel.specific_fuel_consumption == 185  # 2010 vessel

    # Optimal load range
    assert sample_vessel.optimal_load_min == 70
    assert sample_vessel.optimal_load_max == 85

    # Optimal speed range calculated from load range
    expected_min_speed = sample_vessel.design_speed * (
        sample_vessel.optimal_load_min / 100
    ) ** (1 / 3)
    expected_max_speed = sample_vessel.design_speed * (
        sample_vessel.optimal_load_max / 100
    ) ** (1 / 3)

    assert math.isclose(sample_vessel.optimal_speed_min, expected_min_speed)
    assert math.isclose(sample_vessel.optimal_speed_max, expected_max_speed)


def test_specific_fuel_consumption_by_year():
    """Test specific fuel consumption calculation based on build year"""
    # Modern vessel (2015+)
    modern_vessel = Vessel({"year_built": 2020})
    assert modern_vessel.specific_fuel_consumption == 175

    # Mid-age vessel (2000-2014)
    mid_vessel = Vessel({"year_built": 2010})
    assert mid_vessel.specific_fuel_consumption == 185

    # Older vessel (pre-2000)
    old_vessel = Vessel({"year_built": 1995})
    assert old_vessel.specific_fuel_consumption == 195


def test_fuel_consumption_calculation(sample_vessel):
    """Test the fuel consumption calculation at different speeds"""
    # At design speed, consumption should be design_consumption
    consumption_at_design = sample_vessel.get_fuel_consumption(
        sample_vessel.design_speed
    )
    assert math.isclose(consumption_at_design, sample_vessel.design_consumption)

    # At half of design speed, consumption should be 1/8 of design_consumption (cubic relationship)
    half_speed = sample_vessel.design_speed / 2
    expected_consumption = sample_vessel.design_consumption * (0.5**3)
    consumption_at_half = sample_vessel.get_fuel_consumption(half_speed)
    assert math.isclose(consumption_at_half, expected_consumption)

    # At 1.2x design speed, consumption should be 1.728x design_consumption (1.2^3 = 1.728)
    higher_speed = sample_vessel.design_speed * 1.2
    expected_consumption = sample_vessel.design_consumption * (1.2**3)
    consumption_at_higher = sample_vessel.get_fuel_consumption(higher_speed)
    assert math.isclose(consumption_at_higher, expected_consumption)


def test_engine_load_calculation(sample_vessel):
    """Test the engine load calculation at different speeds"""
    # At max speed, load should be 100%
    load_at_max = sample_vessel.get_engine_load(sample_vessel.max_speed)
    assert math.isclose(load_at_max, 100.0)

    # At half of max speed, load should be 12.5% (0.5^3 = 0.125)
    half_speed = sample_vessel.max_speed / 2
    expected_load = 100 * (0.5**3)
    load_at_half = sample_vessel.get_engine_load(half_speed)
    assert math.isclose(load_at_half, expected_load)


def test_optimal_speed_range_check(sample_vessel):
    """Test the speed range validation"""
    # Get speeds for optimal load range boundaries
    min_optimal_speed = sample_vessel.optimal_speed_min
    max_optimal_speed = sample_vessel.optimal_speed_max

    # Speed in the middle of the optimal range
    mid_optimal_speed = (min_optimal_speed + max_optimal_speed) / 2
    assert sample_vessel.is_speed_in_optimal_range(mid_optimal_speed)

    # Speed slightly below optimal range
    below_optimal = min_optimal_speed * 0.9
    assert not sample_vessel.is_speed_in_optimal_range(below_optimal)

    # Speed slightly above optimal range
    above_optimal = max_optimal_speed * 1.1
    assert not sample_vessel.is_speed_in_optimal_range(above_optimal)


def test_to_dict_method(sample_vessel):
    """Test the to_dict serialization method"""
    vessel_dict = sample_vessel.to_dict()

    # Check all original fields are present
    assert vessel_dict["name"] == sample_vessel.name
    assert vessel_dict["type"] == sample_vessel.type
    assert vessel_dict["length"] == sample_vessel.length
    assert vessel_dict["beam"] == sample_vessel.beam
    assert vessel_dict["draft"] == sample_vessel.draft
    assert vessel_dict["deadweight"] == sample_vessel.deadweight
    assert vessel_dict["engine_type"] == sample_vessel.engine_type
    assert vessel_dict["max_speed"] == sample_vessel.max_speed
    assert vessel_dict["max_power"] == sample_vessel.max_power
    assert vessel_dict["design_speed"] == sample_vessel.design_speed
    assert vessel_dict["design_consumption"] == sample_vessel.design_consumption
    assert vessel_dict["year_built"] == sample_vessel.year_built

    # Check derived fields are also included
    assert (
        vessel_dict["specific_fuel_consumption"]
        == sample_vessel.specific_fuel_consumption
    )
    assert vessel_dict["optimal_load_min"] == sample_vessel.optimal_load_min
    assert vessel_dict["optimal_load_max"] == sample_vessel.optimal_load_max
    assert vessel_dict["optimal_speed_min"] == sample_vessel.optimal_speed_min
    assert vessel_dict["optimal_speed_max"] == sample_vessel.optimal_speed_max
