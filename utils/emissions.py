import pandas as pd
import numpy as np
from utils.optimization import calculate_fuel_consumption

def calculate_detailed_emissions(fuel_consumption, fuel_type='VLSFO'):
    """
    Calculate detailed emissions based on fuel consumption and fuel type
    
    Args:
        fuel_consumption: Fuel consumption in tons
        fuel_type: Type of fuel (VLSFO, MGO, LSFO, HFO)
    
    Returns:
        dict: Emissions of different types in tons
    """
    # Emission factors by fuel type in g/ton of fuel
    emission_factors = {
        'VLSFO': {  # Very Low Sulfur Fuel Oil (0.5% sulfur)
            'CO2': 3114000,
            'SOx': 10000,
            'NOx': 57000,
            'PM': 1400
        },
        'MGO': {  # Marine Gas Oil (0.1% sulfur)
            'CO2': 3206000,
            'SOx': 2000,
            'NOx': 60000,
            'PM': 1000
        },
        'LSFO': {  # Low Sulfur Fuel Oil (1.0% sulfur)
            'CO2': 3114000,
            'SOx': 20000,
            'NOx': 57000,
            'PM': 1800
        },
        'HFO': {  # Heavy Fuel Oil (3.5% sulfur)
            'CO2': 3114000,
            'SOx': 70000,
            'NOx': 57000,
            'PM': 2400
        }
    }
    
    # Use VLSFO as default if fuel type not found
    factors = emission_factors.get(fuel_type, emission_factors['VLSFO'])
    
    emissions = {}
    for emission_type, factor in factors.items():
        # Convert from g to tons
        emissions[emission_type] = (fuel_consumption * factor) / 1000000
    
    return emissions

def calculate_cii_rating(vessel_data, annual_distance, annual_fuel, cargo_capacity_utilization=0.7):
    """
    Calculate Carbon Intensity Indicator (CII) rating for a vessel
    
    Args:
        vessel_data: Dictionary containing vessel specifications
        annual_distance: Annual distance sailed in nautical miles
        annual_fuel: Annual fuel consumption in tons
        cargo_capacity_utilization: Average cargo capacity utilization ratio (0-1)
    
    Returns:
        dict: CII calculation results including rating
    """
    # Calculate CO2 emissions
    co2_emissions = (annual_fuel * 3.114)  # tons of CO2 (using 3.114 as factor for converting fuel to CO2)
    
    # Calculate transport work (capacity x distance x utilization)
    deadweight = vessel_data.get('deadweight', 100000)  # in tons
    transport_work = deadweight * annual_distance * cargo_capacity_utilization  # in ton-miles
    
    # Calculate AER (Annual Efficiency Ratio)
    aer = (co2_emissions * 1000000) / transport_work  # g CO2 per ton-mile
    
    # CII reference values depend on ship type (using container ship as example)
    # These are simplified and should be replaced with actual IMO reference lines
    ship_type = vessel_data.get('type', 'Container Ship')
    
    # Simplified reference values for demonstration
    reference_values = {
        'Container Ship': 11.5,
        'Bulk Carrier': 7.0,
        'Oil Tanker': 5.1,
        'Gas Carrier': 8.9,
        'General Cargo': 15.3
    }
    
    reference_aer = reference_values.get(ship_type, 10.0)
    
    # Calculate CII rating
    cii_ratio = aer / reference_aer
    
    # Determine rating
    if cii_ratio < 0.86:
        rating = 'A'
    elif cii_ratio < 0.93:
        rating = 'B'
    elif cii_ratio < 1.03:
        rating = 'C'
    elif cii_ratio < 1.10:
        rating = 'D'
    else:
        rating = 'E'
    
    return {
        'co2_emissions': co2_emissions,
        'transport_work': transport_work,
        'aer': aer,
        'reference_aer': reference_aer,
        'cii_ratio': cii_ratio,
        'rating': rating
    }

def calculate_compliance_forecast(vessel_data, current_speed, proposed_speed, annual_distance):
    """
    Forecast future emissions compliance based on speed changes
    
    Args:
        vessel_data: Dictionary containing vessel specifications
        current_speed: Current operational speed in knots
        proposed_speed: Proposed new speed in knots
        annual_distance: Annual distance sailed in nautical miles
    
    Returns:
        dict: Compliance forecast showing improvement in ratings
    """
    # Calculate fuel consumption for current and proposed speeds
    current_daily_consumption = calculate_fuel_consumption(current_speed, vessel_data)
    proposed_daily_consumption = calculate_fuel_consumption(proposed_speed, vessel_data)
    
    # Calculate annual sailing time (days) for current and proposed speeds
    current_annual_time = annual_distance / (current_speed * 24)
    proposed_annual_time = annual_distance / (proposed_speed * 24)
    
    # Calculate annual fuel consumption
    current_annual_fuel = current_daily_consumption * current_annual_time
    proposed_annual_fuel = proposed_daily_consumption * proposed_annual_time
    
    # Calculate CII ratings for current and proposed scenarios
    current_cii = calculate_cii_rating(vessel_data, annual_distance, current_annual_fuel)
    proposed_cii = calculate_cii_rating(vessel_data, annual_distance, proposed_annual_fuel)
    
    # Calculate fuel and emission savings
    fuel_savings = current_annual_fuel - proposed_annual_fuel
    emission_savings = (current_cii['co2_emissions'] - proposed_cii['co2_emissions'])
    
    return {
        'current_scenario': {
            'speed': current_speed,
            'annual_fuel': current_annual_fuel,
            'cii_ratio': current_cii['cii_ratio'],
            'cii_rating': current_cii['rating']
        },
        'proposed_scenario': {
            'speed': proposed_speed,
            'annual_fuel': proposed_annual_fuel,
            'cii_ratio': proposed_cii['cii_ratio'],
            'cii_rating': proposed_cii['rating']
        },
        'savings': {
            'fuel_savings': fuel_savings,
            'emission_savings': emission_savings,
            'percentage_reduction': (fuel_savings / current_annual_fuel) * 100
        }
    }
