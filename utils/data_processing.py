import pandas as pd
import numpy as np
import json
import os

def load_sample_vessel_data():
    """
    Load sample vessel data from the assets folder
    """
    try:
        with open("assets/sample_vessel_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default vessel data if file not found
        return {
            "vessels": [
                {
                    "name": "Example Vessel",
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
                    "year_built": 2010
                }
            ]
        }

def load_sample_route_data():
    """
    Load sample route data from the assets folder
    """
    try:
        with open("assets/sample_route_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default route data if file not found
        return {
            "routes": [
                {
                    "name": "Singapore to Rotterdam",
                    "distance": 8352,
                    "waypoints": [
                        {"name": "Singapore", "lat": 1.264, "lon": 103.825},
                        {"name": "Suez Canal", "lat": 30.028, "lon": 32.552},
                        {"name": "Gibraltar", "lat": 36.144, "lon": -5.353},
                        {"name": "Rotterdam", "lat": 51.949, "lon": 4.138}
                    ]
                }
            ]
        }

def prepare_vessel_data(uploaded_file):
    """
    Process uploaded vessel data file
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        dict: Processed vessel data
    """
    if uploaded_file is None:
        return None
    
    try:
        # Determine file type and process accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            vessel_data = df.to_dict('records')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            vessel_data = df.to_dict('records')
        elif uploaded_file.name.endswith('.json'):
            vessel_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
        else:
            raise ValueError(f"Unsupported file format: {uploaded_file.name}")
        
        return {"vessels": vessel_data}
    
    except Exception as e:
        raise Exception(f"Error processing vessel data: {str(e)}")

def prepare_route_data(uploaded_file):
    """
    Process uploaded route data file
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        dict: Processed route data
    """
    if uploaded_file is None:
        return None
    
    try:
        # Determine file type and process accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            route_data = df.to_dict('records')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            route_data = df.to_dict('records')
        elif uploaded_file.name.endswith('.json'):
            route_data = json.loads(uploaded_file.getvalue().decode('utf-8'))
        else:
            raise ValueError(f"Unsupported file format: {uploaded_file.name}")
        
        return {"routes": route_data}
    
    except Exception as e:
        raise Exception(f"Error processing route data: {str(e)}")

def calculate_transit_time(distance, speed):
    """
    Calculate transit time based on distance and speed
    
    Args:
        distance: Distance in nautical miles
        speed: Speed in knots
    
    Returns:
        float: Transit time in days
    """
    if speed <= 0:
        return float('inf')
    return distance / (speed * 24)
