import numpy as np
from scipy.optimize import minimize
import pandas as pd

def calculate_fuel_consumption(speed, vessel_data):
    """
    Calculate fuel consumption based on the cubic relationship with speed
    
    Args:
        speed: Speed in knots
        vessel_data: Dictionary containing vessel specifications
    
    Returns:
        float: Fuel consumption in tons per day
    """
    # Using the cubic relationship between speed and fuel consumption
    # Fuel consumption ∝ speed^3
    design_speed = vessel_data.get('design_speed', 20)
    design_consumption = vessel_data.get('design_consumption', 180)
    
    # Calculate fuel consumption based on the cubic relationship
    fuel_consumption = design_consumption * (speed / design_speed) ** 3
    
    return fuel_consumption

def calculate_emissions(fuel_consumption, emission_factors=None):
    """
    Calculate emissions based on fuel consumption
    
    Args:
        fuel_consumption: Fuel consumption in tons
        emission_factors: Dictionary with emission factors (g/ton of fuel)
    
    Returns:
        dict: Emissions of different types in tons
    """
    if emission_factors is None:
        # Default emission factors in g/ton of fuel (based on IMO guidelines)
        emission_factors = {
            'CO2': 3114000,  # g/ton
            'SOx': 54000,    # g/ton for 0.5% sulfur fuel
            'NOx': 57000     # g/ton for Tier II engines
        }
    
    emissions = {}
    for emission_type, factor in emission_factors.items():
        # Convert from g to tons
        emissions[emission_type] = (fuel_consumption * factor) / 1000000
    
    return emissions

def calculate_cost(fuel_consumption, fuel_price, transit_time, vessel_day_cost):
    """
    Calculate voyage cost based on fuel consumption and transit time
    
    Args:
        fuel_consumption: Total fuel consumption in tons
        fuel_price: Fuel price in USD per ton
        transit_time: Transit time in days
        vessel_day_cost: Vessel operating cost in USD per day
    
    Returns:
        float: Total voyage cost in USD
    """
    fuel_cost = fuel_consumption * fuel_price
    time_cost = transit_time * vessel_day_cost
    
    return fuel_cost + time_cost

def optimize_speed(vessel_data, route_distance, fuel_price, vessel_day_cost, min_speed=8, max_speed=24):
    """
    Optimize vessel speed based on fuel consumption and time costs
    
    Args:
        vessel_data: Dictionary containing vessel specifications
        route_distance: Route distance in nautical miles
        fuel_price: Fuel price in USD per ton
        vessel_day_cost: Vessel operating cost in USD per day
        min_speed: Minimum allowable speed in knots
        max_speed: Maximum allowable speed in knots
    
    Returns:
        dict: Optimization results including optimal speed and costs
    """
    def objective_function(speed):
        """
        Cost objective function to minimize
        """
        speed_value = speed[0]  # Extract the speed value from the array
        transit_time = route_distance / (speed_value * 24)  # in days
        daily_fuel = calculate_fuel_consumption(speed_value, vessel_data)
        total_fuel = daily_fuel * transit_time
        
        fuel_cost = total_fuel * fuel_price
        time_cost = transit_time * vessel_day_cost
        
        return fuel_cost + time_cost
    
    # Initial guess for speed optimization
    initial_speed = vessel_data.get('design_speed', 20) * 0.8  # Starting with 80% of design speed
    
    # Bounds for optimization
    bounds = [(min_speed, max_speed)]
    
    # Run optimization
    result = minimize(objective_function, [initial_speed], bounds=bounds, method='L-BFGS-B')
    
    optimal_speed = result.x[0]
    transit_time = route_distance / (optimal_speed * 24)
    daily_fuel = calculate_fuel_consumption(optimal_speed, vessel_data)
    total_fuel = daily_fuel * transit_time
    
    emissions = calculate_emissions(total_fuel)
    
    # Calculate costs
    fuel_cost = total_fuel * fuel_price
    time_cost = transit_time * vessel_day_cost
    total_cost = fuel_cost + time_cost
    
    # Generate comparison with design speed
    design_speed = vessel_data.get('design_speed', 20)
    design_transit_time = route_distance / (design_speed * 24)
    design_daily_fuel = calculate_fuel_consumption(design_speed, vessel_data)
    design_total_fuel = design_daily_fuel * design_transit_time
    design_emissions = calculate_emissions(design_total_fuel)
    
    design_fuel_cost = design_total_fuel * fuel_price
    design_time_cost = design_transit_time * vessel_day_cost
    design_total_cost = design_fuel_cost + design_time_cost
    
    # Calculate savings
    fuel_savings = design_total_fuel - total_fuel
    cost_savings = design_total_cost - total_cost
    co2_reduction = design_emissions['CO2'] - emissions['CO2']
    
    # Prepare the result dictionary
    optimization_result = {
        'optimal_speed': optimal_speed,
        'transit_time': transit_time,
        'daily_fuel_consumption': daily_fuel,
        'total_fuel_consumption': total_fuel,
        'fuel_cost': fuel_cost,
        'time_cost': time_cost,
        'total_cost': total_cost,
        'emissions': emissions,
        'fuel_savings': fuel_savings,
        'cost_savings': cost_savings,
        'co2_reduction': co2_reduction,
        'comparison': {
            'design_speed': design_speed,
            'design_transit_time': design_transit_time,
            'design_fuel_consumption': design_total_fuel,
            'design_cost': design_total_cost,
            'design_emissions': design_emissions
        }
    }
    
    return optimization_result

def generate_speed_profile(vessel_data, route_distance, fuel_price, vessel_day_cost, speed_range=(8, 24), step=0.5):
    """
    Generate a speed profile with costs and consumption for different speeds
    
    Args:
        vessel_data: Dictionary containing vessel specifications
        route_distance: Route distance in nautical miles
        fuel_price: Fuel price in USD per ton
        vessel_day_cost: Vessel operating cost in USD per day
        speed_range: Tuple of (min_speed, max_speed) in knots
        step: Step size for speed increments
    
    Returns:
        pandas.DataFrame: Speed profile with costs and consumption
    """
    min_speed, max_speed = speed_range
    speeds = np.arange(min_speed, max_speed + step, step)
    
    data = []
    for speed in speeds:
        transit_time = route_distance / (speed * 24)
        daily_fuel = calculate_fuel_consumption(speed, vessel_data)
        total_fuel = daily_fuel * transit_time
        
        emissions = calculate_emissions(total_fuel)
        
        fuel_cost = total_fuel * fuel_price
        time_cost = transit_time * vessel_day_cost
        total_cost = fuel_cost + time_cost
        
        data.append({
            'speed': speed,
            'transit_time': transit_time,
            'daily_fuel': daily_fuel,
            'total_fuel': total_fuel,
            'fuel_cost': fuel_cost,
            'time_cost': time_cost,
            'total_cost': total_cost,
            'co2_emissions': emissions['CO2'],
            'sox_emissions': emissions['SOx'],
            'nox_emissions': emissions['NOx']
        })
    
    return pd.DataFrame(data)
