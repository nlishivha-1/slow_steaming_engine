import streamlit as st
import pandas as pd
import numpy as np
import json
from models.route import Route
from models.weather import WeatherData
from utils.data_processing import load_sample_route_data, prepare_route_data
from utils.visualization import create_route_map

def app():
    """
    Route Optimization page for entering route information and analysis
    """
    st.title("Route Optimization")
    
    st.markdown("""
    Enter route information for optimization. You can add waypoints, 
    specify route distances, and visualize the route on a map.
    """)
    
    # Check if vessel data is available
    if 'vessel_data' not in st.session_state or st.session_state.vessel_data is None:
        st.warning("Please enter vessel specifications first in the Vessel Input page.")
        return
    
    # Initialize session state variables
    if 'route_data' not in st.session_state:
        st.session_state.route_data = None
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None
    
    # Tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Manual Entry", "Upload File", "Use Sample Data"])
    
    with tab1:
        st.subheader("Manual Route Entry")
        
        route_name = st.text_input("Route Name", "Custom Route")
        route_distance = st.number_input("Total Distance (nautical miles)", min_value=100, max_value=20000, value=5000)
        
        st.subheader("Waypoints")
        st.markdown("Add waypoints for your route (minimum 2 points required)")
        
        # Initialize waypoints in session state if not exists
        if 'waypoints' not in st.session_state:
            st.session_state.waypoints = [
                {"name": "Origin", "lat": 1.264, "lon": 103.825},
                {"name": "Destination", "lat": 51.949, "lon": 4.138}
            ]
        
        # Display existing waypoints with option to edit
        for i, wp in enumerate(st.session_state.waypoints):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.session_state.waypoints[i]["name"] = st.text_input(
                    f"Name {i+1}", 
                    value=wp["name"], 
                    key=f"wp_name_{i}"
                )
            
            with col2:
                st.session_state.waypoints[i]["lat"] = st.number_input(
                    f"Latitude {i+1}", 
                    value=float(wp["lat"]),
                    min_value=-90.0,
                    max_value=90.0,
                    format="%.6f",
                    key=f"wp_lat_{i}"
                )
            
            with col3:
                st.session_state.waypoints[i]["lon"] = st.number_input(
                    f"Longitude {i+1}",
                    value=float(wp["lon"]),
                    min_value=-180.0,
                    max_value=180.0,
                    format="%.6f",
                    key=f"wp_lon_{i}"
                )
            
            with col4:
                if i > 1 or len(st.session_state.waypoints) > 2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.waypoints.pop(i)
                        st.rerun()
        
        # Button to add a new waypoint
        if st.button("Add Waypoint"):
            # Add a new waypoint with default values
            st.session_state.waypoints.append({
                "name": f"Waypoint {len(st.session_state.waypoints) + 1}",
                "lat": 0.0,
                "lon": 0.0
            })
            st.rerun()
        
        # Button to save route data
        if st.button("Save Route Data", use_container_width=True):
            if len(st.session_state.waypoints) < 2:
                st.error("At least 2 waypoints are required for a route.")
            else:
                route_data = {
                    "name": route_name,
                    "distance": route_distance,
                    "waypoints": st.session_state.waypoints
                }
                
                route_obj = Route(route_data)
                st.session_state.route_data = route_obj.to_dict()
                
                # Generate synthetic weather data
                weather_obj = WeatherData()
                weather_obj.generate_synthetic_data(route_data)
                st.session_state.weather_data = weather_obj.to_dict()
                
                st.success("Route data saved successfully!")
                st.rerun()
    
    with tab2:
        st.subheader("Upload Route Data")
        
        st.markdown("""
        Upload a file containing route information. The file should be in one of the following formats:
        - CSV: with column headers for waypoint information
        - Excel: with column headers for waypoint information
        - JSON: structured with route details and waypoints
        """)
        
        uploaded_file = st.file_uploader("Upload route data file", type=["csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            try:
                route_data_dict = prepare_route_data(uploaded_file)
                if route_data_dict and 'routes' in route_data_dict and len(route_data_dict['routes']) > 0:
                    st.write("Available routes in the file:")
                    routes = route_data_dict['routes']
                    route_names = [r.get('name', f"Route {i+1}") for i, r in enumerate(routes)]
                    selected_route = st.selectbox("Select a route", route_names)
                    
                    # Find the selected route in the data
                    selected_route_data = next((r for r in routes if r.get('name') == selected_route), routes[0])
                    
                    # Create Route object and save to session state
                    if st.button("Use Selected Route", use_container_width=True):
                        route_obj = Route(selected_route_data)
                        st.session_state.route_data = route_obj.to_dict()
                        
                        # Generate synthetic weather data
                        weather_obj = WeatherData()
                        weather_obj.generate_synthetic_data(selected_route_data)
                        st.session_state.weather_data = weather_obj.to_dict()
                        
                        st.success("Route data loaded successfully!")
                        
                        # Display the loaded data
                        with st.expander("View loaded route data"):
                            st.json(selected_route_data)
                else:
                    st.error("No route data found in the uploaded file.")
            
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab3:
        st.subheader("Use Sample Route Data")
        
        sample_data = load_sample_route_data()
        
        if sample_data and 'routes' in sample_data:
            st.write("Available sample routes:")
            route_names = [r.get('name', f"Route {i+1}") for i, r in enumerate(sample_data['routes'])]
            selected_route = st.selectbox("Select a route", route_names)
            
            # Find the selected route in the data
            selected_route_data = next((r for r in sample_data['routes'] if r.get('name') == selected_route), sample_data['routes'][0])
            
            if st.button("Use Selected Sample Route", use_container_width=True):
                # Create Route object and save to session state
                route_obj = Route(selected_route_data)
                st.session_state.route_data = route_obj.to_dict()
                
                # Generate synthetic weather data
                weather_obj = WeatherData()
                weather_obj.generate_synthetic_data(selected_route_data)
                st.session_state.weather_data = weather_obj.to_dict()
                
                st.success("Sample route data loaded successfully!")
                
                # Display the loaded data
                with st.expander("View loaded route data"):
                    st.json(selected_route_data)
    
    # Display current route data if available
    if st.session_state.route_data is not None:
        st.header("Current Route Information")
        
        # Create two columns for display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Route Details")
            st.write(f"**Name:** {st.session_state.route_data.get('name', 'N/A')}")
            st.write(f"**Distance:** {st.session_state.route_data.get('distance', 'N/A')} nautical miles")
            st.write(f"**Number of Waypoints:** {st.session_state.route_data.get('number_of_waypoints', 'N/A')}")
            
            # Display waypoints in a table
            if 'waypoints' in st.session_state.route_data:
                waypoints_df = pd.DataFrame(st.session_state.route_data['waypoints'])
                st.dataframe(waypoints_df, use_container_width=True)
        
        with col2:
            st.subheader("Route Visualization")
            create_route_map(st.session_state.route_data, st.session_state.vessel_data)
        
        # Display weather information if available
        if st.session_state.weather_data is not None and st.session_state.weather_data.get('has_data', False):
            st.subheader("Weather and Ocean Conditions")
            
            # Display average conditions
            avg_conditions = st.session_state.weather_data.get('average_conditions', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                wind_speed = avg_conditions.get('avg_wind_speed')
                if wind_speed is not None:
                    st.metric("Average Wind Speed", f"{wind_speed:.1f} knots")
                else:
                    st.metric("Average Wind Speed", "N/A")
            
            with col2:
                current_speed = avg_conditions.get('avg_current_speed')
                if current_speed is not None:
                    st.metric("Average Current Speed", f"{current_speed:.1f} knots")
                else:
                    st.metric("Average Current Speed", "N/A")
            
            with col3:
                wave_height = avg_conditions.get('avg_wave_height')
                if wave_height is not None:
                    st.metric("Average Wave Height", f"{wave_height:.1f} meters")
                else:
                    st.metric("Average Wave Height", "N/A")
            
            # Create a weather object to calculate impact
            weather_obj = WeatherData(st.session_state.weather_data.get('data', {}))
            weather_impact = weather_obj.get_weather_impact(st.session_state.route_data)
            
            # Display weather impact
            st.markdown("### Weather Impact on Voyage")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Estimated Speed Reduction", f"{weather_impact['speed_reduction']:.1f}%")
            
            with col2:
                st.metric("Estimated Fuel Increase", f"{weather_impact['fuel_increase']:.1f}%")
            
            # Display high risk areas if any
            if weather_impact['high_risk_areas']:
                st.markdown("### High Risk Areas")
                high_risk_df = pd.DataFrame(weather_impact['high_risk_areas'])
                st.dataframe(high_risk_df, use_container_width=True)
        
        # Allow clearing the data
        if st.button("Clear Route Data", use_container_width=True):
            st.session_state.route_data = None
            st.session_state.weather_data = None
            if 'waypoints' in st.session_state:
                del st.session_state.waypoints
            st.success("Route data cleared!")
            st.rerun()
    else:
        st.info("No route data available. Please enter or load route information.")
