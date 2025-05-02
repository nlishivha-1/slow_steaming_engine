import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static

def plot_fuel_speed_curve(speed_profile):
    """
    Plot the relationship between speed and fuel consumption
    
    Args:
        speed_profile: DataFrame containing speed profile data
    
    Returns:
        None: Displays the plot in the Streamlit app
    """
    fig = px.line(
        speed_profile, 
        x='speed', 
        y='daily_fuel', 
        title='Speed vs. Daily Fuel Consumption',
        labels={'speed': 'Speed (knots)', 'daily_fuel': 'Fuel Consumption (tons/day)'}
    )
    
    fig.update_layout(
        xaxis_title="Speed (knots)",
        yaxis_title="Fuel Consumption (tons/day)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_cost_speed_curve(speed_profile):
    """
    Plot the relationship between speed and various costs
    
    Args:
        speed_profile: DataFrame containing speed profile data
    
    Returns:
        None: Displays the plot in the Streamlit app
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['fuel_cost'],
        mode='lines',
        name='Fuel Cost',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['time_cost'],
        mode='lines',
        name='Time Cost',
        line=dict(color='green')
    ))
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['total_cost'],
        mode='lines',
        name='Total Cost',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='Speed vs. Voyage Costs',
        xaxis_title='Speed (knots)',
        yaxis_title='Cost (USD)',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_emissions_speed_curve(speed_profile):
    """
    Plot the relationship between speed and emissions
    
    Args:
        speed_profile: DataFrame containing speed profile data
    
    Returns:
        None: Displays the plot in the Streamlit app
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['co2_emissions'],
        mode='lines',
        name='CO₂ Emissions',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['sox_emissions'],
        mode='lines',
        name='SOₓ Emissions',
        line=dict(color='orange')
    ))
    
    fig.add_trace(go.Scatter(
        x=speed_profile['speed'],
        y=speed_profile['nox_emissions'],
        mode='lines',
        name='NOₓ Emissions',
        line=dict(color='purple')
    ))
    
    fig.update_layout(
        title='Speed vs. Emissions',
        xaxis_title='Speed (knots)',
        yaxis_title='Emissions (tons)',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_route_map(route_data, vessel_data=None, optimization_results=None):
    """
    Create an interactive map showing the route with optional vessel and optimization data
    
    Args:
        route_data: Dictionary containing route information
        vessel_data: Optional dictionary containing vessel specifications
        optimization_results: Optional dictionary containing optimization results
    
    Returns:
        None: Displays the map in the Streamlit app
    """
    # Create map centered on the first waypoint
    waypoints = route_data.get('waypoints', [])
    
    if not waypoints:
        st.error("No waypoints available for route visualization")
        return
    
    # Center map on first waypoint
    center_lat = waypoints[0]['lat']
    center_lon = waypoints[0]['lon']
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=3)
    
    # Add base tiles with ocean details
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Ocean Basemap',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add route line connecting waypoints with intermediate points to follow shipping lanes
    route_points = [[wp['lat'], wp['lon']] for wp in waypoints]
    
    # Create shipping lane polylines for each segment
    for i in range(len(route_points) - 1):
        start = route_points[i]
        end = route_points[i+1]
        
        # Use direct line if points are close
        folium.PolyLine(
            [start, end],
            weight=3,
            color='blue',
            opacity=0.7,
            tooltip=f"Route: {route_data.get('name', 'Unknown')}"
        ).add_to(m)
    
    # Add markers for each waypoint
    for i, waypoint in enumerate(waypoints):
        if i == 0:  # Starting point
            icon_color = 'green'
            prefix = 'fa'
            icon = 'play'
        elif i == len(waypoints) - 1:  # Ending point
            icon_color = 'red'
            prefix = 'fa'
            icon = 'stop'
        else:  # Intermediate points
            icon_color = 'blue'
            prefix = 'fa'
            icon = 'flag'
        
        folium.Marker(
            [waypoint['lat'], waypoint['lon']],
            popup=waypoint['name'],
            tooltip=waypoint['name'],
            icon=folium.Icon(color=icon_color, icon=icon, prefix=prefix)
        ).add_to(m)
    
    # Add vessel information if available
    if vessel_data and optimization_results:
        html = f"""
        <div style="width: 300px">
            <h4>{vessel_data.get('name', 'Vessel')}</h4>
            <p><b>Optimal Speed:</b> {optimization_results.get('optimal_speed', 0):.2f} knots</p>
            <p><b>Transit Time:</b> {optimization_results.get('transit_time', 0):.2f} days</p>
            <p><b>Fuel Consumption:</b> {optimization_results.get('total_fuel_consumption', 0):.2f} tons</p>
            <p><b>CO₂ Reduction:</b> {optimization_results.get('co2_reduction', 0):.2f} tons</p>
        </div>
        """
        
        folium.Marker(
            route_points[0],  # Starting point
            popup=folium.Popup(html, max_width=300),
            tooltip=vessel_data.get('name', 'Vessel Info'),
            icon=folium.Icon(color='purple', icon='info-sign')
        ).add_to(m)
    
    # Display the map
    folium_static(m)

def create_dashboard_metrics(optimization_results):
    """
    Create dashboard metrics for optimization results
    
    Args:
        optimization_results: Dictionary containing optimization results
    
    Returns:
        None: Displays the metrics in the Streamlit app
    """
    if not optimization_results:
        st.warning("No optimization results available for dashboard")
        return
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate percentage reductions
    design_fuel = optimization_results['comparison']['design_fuel_consumption']
    optimal_fuel = optimization_results['total_fuel_consumption']
    fuel_reduction_pct = ((design_fuel - optimal_fuel) / design_fuel) * 100
    
    design_cost = optimization_results['comparison']['design_cost']
    optimal_cost = optimization_results['total_cost']
    cost_reduction_pct = ((design_cost - optimal_cost) / design_cost) * 100
    
    design_co2 = optimization_results['comparison']['design_emissions']['CO2']
    optimal_co2 = optimization_results['emissions']['CO2']
    co2_reduction_pct = ((design_co2 - optimal_co2) / design_co2) * 100
    
    with col1:
        st.metric(
            label="Fuel Savings",
            value=f"{optimization_results['fuel_savings']:.2f} tons",
            delta=f"{fuel_reduction_pct:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Cost Savings",
            value=f"${optimization_results['cost_savings']:,.2f}",
            delta=f"{cost_reduction_pct:.1f}%"
        )
    
    with col3:
        st.metric(
            label="CO₂ Reduction",
            value=f"{optimization_results['co2_reduction']:.2f} tons",
            delta=f"{co2_reduction_pct:.1f}%"
        )

def create_cii_gauge(cii_data):
    """
    Create a gauge chart for CII rating visualization
    
    Args:
        cii_data: Dictionary containing CII calculation results
    
    Returns:
        None: Displays the gauge chart in the Streamlit app
    """
    if not cii_data:
        st.warning("No CII data available for visualization")
        return
    
    # Define the ranges for CII ratings
    rating = cii_data['rating']
    ratio = cii_data['cii_ratio']
    
    # Create a gauge chart for the CII ratio
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ratio,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"CII Rating: {rating}", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, 1.5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 0.86], 'color': '#00FF00'},  # A rating - Green
                {'range': [0.86, 0.93], 'color': '#88FF00'},  # B rating - Light Green
                {'range': [0.93, 1.03], 'color': '#FFFF00'},  # C rating - Yellow
                {'range': [1.03, 1.10], 'color': '#FFA500'},  # D rating - Orange
                {'range': [1.10, 1.5], 'color': '#FF0000'}   # E rating - Red
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 1.03  # Compliance threshold
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_emissions_comparison_chart(current_emissions, proposed_emissions):
    """
    Create a bar chart comparing emissions before and after optimization
    
    Args:
        current_emissions: Dictionary containing current emissions data
        proposed_emissions: Dictionary containing proposed emissions data
    
    Returns:
        None: Displays the chart in the Streamlit app
    """
    if not current_emissions or not proposed_emissions:
        st.warning("Insufficient data for emissions comparison")
        return
    
    # Prepare the data for the chart
    emission_types = list(current_emissions.keys())
    current_values = [current_emissions[et] for et in emission_types]
    proposed_values = [proposed_emissions[et] for et in emission_types]
    
    # Create the data frame for plotting
    df = pd.DataFrame({
        'Emission Type': emission_types * 2,
        'Value': current_values + proposed_values,
        'Scenario': ['Current'] * len(emission_types) + ['Optimized'] * len(emission_types)
    })
    
    # Create the bar chart
    fig = px.bar(
        df,
        x='Emission Type',
        y='Value',
        color='Scenario',
        barmode='group',
        title='Emissions Comparison: Current vs. Optimized',
        labels={'Value': 'Emissions (tons)', 'Emission Type': 'Type'},
        color_discrete_map={'Current': '#FF6B6B', 'Optimized': '#4ECDC4'}
    )
    
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)
