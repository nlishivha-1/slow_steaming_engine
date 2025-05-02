import streamlit as st
import pandas as pd
import numpy as np
from utils.optimization import optimize_speed, generate_speed_profile
from utils.visualization import plot_fuel_speed_curve, plot_cost_speed_curve, create_route_map

def app():
    """
    Speed Optimization page for analyzing optimal vessel speeds
    """
    st.title("Speed Optimization")
    
    st.markdown("""
    Optimize vessel speed to balance fuel consumption, transit time, and operational costs.
    The application uses a cubic relationship between speed and fuel consumption to find the optimal speed.
    """)
    
    # Check if vessel and route data are available
    if 'vessel_data' not in st.session_state or st.session_state.vessel_data is None:
        st.warning("Please enter vessel specifications first in the Vessel Input page.")
        return
    
    if 'route_data' not in st.session_state or st.session_state.route_data is None:
        st.warning("Please enter route information first in the Route Optimization page.")
        return
    
    # Cost parameters
    st.header("Cost Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fuel_price = st.number_input(
            "Fuel Price (USD/ton)",
            min_value=200,
            max_value=1500,
            value=600,
            step=10,
            help="Current market price of fuel per ton"
        )
    
    with col2:
        vessel_day_cost = st.number_input(
            "Vessel Operating Cost (USD/day)",
            min_value=5000,
            max_value=100000,
            value=25000,
            step=1000,
            help="Daily operating cost including crew, maintenance, insurance, etc."
        )
    
    # Speed range constraints
    st.header("Speed Range Constraints")
    
    col1, col2 = st.columns(2)
    
    vessel_max_speed = st.session_state.vessel_data.get('max_speed', 25)
    
    with col1:
        min_speed = st.number_input(
            "Minimum Speed (knots)",
            min_value=5.0,
            max_value=float(vessel_max_speed) - 1,
            value=12.0,
            step=0.5,
            help="Minimum allowable speed for optimization"
        )
    
    with col2:
        max_speed = st.number_input(
            "Maximum Speed (knots)",
            min_value=float(min_speed) + 1,
            max_value=float(vessel_max_speed),
            value=float(vessel_max_speed),
            step=0.5,
            help="Maximum allowable speed for optimization"
        )
    
    # Additional constraints
    show_advanced = st.checkbox("Show Advanced Options")
    
    if show_advanced:
        col1, col2 = st.columns(2)
        
        with col1:
            weather_factor = st.slider(
                "Weather Impact Factor (%)",
                min_value=0,
                max_value=30,
                value=0,
                step=1,
                help="Estimated impact of weather on fuel consumption"
            )
        
        with col2:
            engine_efficiency = st.slider(
                "Engine Efficiency (%)",
                min_value=80,
                max_value=100,
                value=100,
                step=1,
                help="Engine efficiency factor"
            )
    else:
        weather_factor = 0
        engine_efficiency = 100
    
    # Run optimization
    if st.button("Run Speed Optimization", use_container_width=True):
        with st.spinner("Optimizing speed..."):
            # Apply weather and efficiency factors to vessel data
            vessel_data = st.session_state.vessel_data.copy()
            if weather_factor > 0:
                # Increase design consumption based on weather factor
                vessel_data['design_consumption'] *= (1 + weather_factor/100)
            
            if engine_efficiency < 100:
                # Adjust consumption based on engine efficiency
                vessel_data['design_consumption'] *= (100/engine_efficiency)
            
            # Get route distance
            route_distance = st.session_state.route_data.get('distance', 5000)
            
            # Run optimization
            optimization_results = optimize_speed(
                vessel_data,
                route_distance,
                fuel_price,
                vessel_day_cost,
                min_speed,
                max_speed
            )
            
            # Generate speed profile for charts
            speed_profile = generate_speed_profile(
                vessel_data,
                route_distance,
                fuel_price,
                vessel_day_cost,
                (min_speed, max_speed),
                0.5
            )
            
            # Store results in session state
            st.session_state.optimization_results = optimization_results
            st.session_state.speed_profile = speed_profile
            
            st.success("Optimization completed successfully!")
    
    # Display optimization results if available
    if 'optimization_results' in st.session_state and st.session_state.optimization_results is not None:
        st.header("Optimization Results")
        
        results = st.session_state.optimization_results
        design_speed = results['comparison']['design_speed']
        optimal_speed = results['optimal_speed']
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Optimal Speed",
                value=f"{optimal_speed:.2f} knots",
                delta=f"{((optimal_speed - design_speed) / design_speed) * 100:.1f}% vs Design"
            )
        
        with col2:
            design_transit = results['comparison']['design_transit_time']
            optimal_transit = results['transit_time']
            
            st.metric(
                label="Transit Time",
                value=f"{optimal_transit:.2f} days",
                delta=f"{((optimal_transit - design_transit) / design_transit) * 100:.1f}%",
                delta_color="inverse"
            )
        
        with col3:
            design_fuel = results['comparison']['design_fuel_consumption']
            optimal_fuel = results['total_fuel_consumption']
            
            st.metric(
                label="Fuel Consumption",
                value=f"{optimal_fuel:.2f} tons",
                delta=f"{-((design_fuel - optimal_fuel) / design_fuel) * 100:.1f}%",
                delta_color="inverse"
            )
        
        # Create tabs for different visualization options
        tab1, tab2, tab3, tab4 = st.tabs([
            "Fuel Consumption", 
            "Cost Analysis", 
            "Detailed Results",
            "Route Map"
        ])
        
        with tab1:
            st.subheader("Speed vs. Fuel Consumption")
            
            if 'speed_profile' in st.session_state:
                plot_fuel_speed_curve(st.session_state.speed_profile)
                
                # Add vertical lines for optimal and design speeds
                st.markdown(f"""
                * **Optimal Speed:** {optimal_speed:.2f} knots (blue line)
                * **Design Speed:** {design_speed:.2f} knots (red line)
                """)
            else:
                st.info("Run optimization to generate fuel consumption curve.")
        
        with tab2:
            st.subheader("Cost Analysis")
            
            if 'speed_profile' in st.session_state:
                plot_cost_speed_curve(st.session_state.speed_profile)
                
                # Show cost breakdown
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Fuel Cost",
                        value=f"${results['fuel_cost']:,.2f}",
                        delta=f"${results['comparison']['design_cost'] - results['total_cost']:,.2f} saved"
                    )
                
                with col2:
                    st.metric(
                        label="Time Cost",
                        value=f"${results['time_cost']:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="Total Cost",
                        value=f"${results['total_cost']:,.2f}",
                        delta=f"{((results['comparison']['design_cost'] - results['total_cost']) / results['comparison']['design_cost']) * 100:.1f}%"
                    )
            else:
                st.info("Run optimization to generate cost analysis.")
        
        with tab3:
            st.subheader("Detailed Optimization Results")
            
            # Create comparison table
            comparison_data = {
                "Parameter": [
                    "Speed (knots)",
                    "Transit Time (days)",
                    "Daily Fuel Consumption (tons/day)",
                    "Total Fuel Consumption (tons)",
                    "Fuel Cost (USD)",
                    "Time Cost (USD)",
                    "Total Cost (USD)",
                    "CO₂ Emissions (tons)",
                    "SOₓ Emissions (tons)",
                    "NOₓ Emissions (tons)"
                ],
                "Design Speed": [
                    f"{design_speed:.2f}",
                    f"{results['comparison']['design_transit_time']:.2f}",
                    f"{results['comparison']['design_fuel_consumption'] / results['comparison']['design_transit_time']:.2f}",
                    f"{results['comparison']['design_fuel_consumption']:.2f}",
                    f"${results['comparison']['design_cost'] - results['comparison']['design_transit_time'] * vessel_day_cost:,.2f}",
                    f"${results['comparison']['design_transit_time'] * vessel_day_cost:,.2f}",
                    f"${results['comparison']['design_cost']:,.2f}",
                    f"{results['comparison']['design_emissions']['CO2']:.2f}",
                    f"{results['comparison']['design_emissions']['SOx']:.2f}",
                    f"{results['comparison']['design_emissions']['NOx']:.2f}"
                ],
                "Optimal Speed": [
                    f"{optimal_speed:.2f}",
                    f"{results['transit_time']:.2f}",
                    f"{results['daily_fuel_consumption']:.2f}",
                    f"{results['total_fuel_consumption']:.2f}",
                    f"${results['fuel_cost']:,.2f}",
                    f"${results['time_cost']:,.2f}",
                    f"${results['total_cost']:,.2f}",
                    f"{results['emissions']['CO2']:.2f}",
                    f"{results['emissions']['SOx']:.2f}",
                    f"{results['emissions']['NOx']:.2f}"
                ],
                "Difference": [
                    f"{optimal_speed - design_speed:.2f}",
                    f"{results['transit_time'] - results['comparison']['design_transit_time']:.2f}",
                    f"{results['daily_fuel_consumption'] - (results['comparison']['design_fuel_consumption'] / results['comparison']['design_transit_time']):.2f}",
                    f"{results['total_fuel_consumption'] - results['comparison']['design_fuel_consumption']:.2f}",
                    f"${results['fuel_cost'] - (results['comparison']['design_cost'] - results['comparison']['design_transit_time'] * vessel_day_cost):,.2f}",
                    f"${results['time_cost'] - (results['comparison']['design_transit_time'] * vessel_day_cost):,.2f}",
                    f"${results['total_cost'] - results['comparison']['design_cost']:,.2f}",
                    f"{results['emissions']['CO2'] - results['comparison']['design_emissions']['CO2']:.2f}",
                    f"{results['emissions']['SOx'] - results['comparison']['design_emissions']['SOx']:.2f}",
                    f"{results['emissions']['NOx'] - results['comparison']['design_emissions']['NOx']:.2f}"
                ],
                "% Change": [
                    f"{((optimal_speed - design_speed) / design_speed) * 100:.1f}%",
                    f"{((results['transit_time'] - results['comparison']['design_transit_time']) / results['comparison']['design_transit_time']) * 100:.1f}%",
                    f"{((results['daily_fuel_consumption'] - (results['comparison']['design_fuel_consumption'] / results['comparison']['design_transit_time'])) / (results['comparison']['design_fuel_consumption'] / results['comparison']['design_transit_time'])) * 100:.1f}%",
                    f"{((results['total_fuel_consumption'] - results['comparison']['design_fuel_consumption']) / results['comparison']['design_fuel_consumption']) * 100:.1f}%",
                    f"{((results['fuel_cost'] - (results['comparison']['design_cost'] - results['comparison']['design_transit_time'] * vessel_day_cost)) / (results['comparison']['design_cost'] - results['comparison']['design_transit_time'] * vessel_day_cost)) * 100:.1f}%",
                    f"{((results['time_cost'] - (results['comparison']['design_transit_time'] * vessel_day_cost)) / (results['comparison']['design_transit_time'] * vessel_day_cost)) * 100:.1f}%",
                    f"{((results['total_cost'] - results['comparison']['design_cost']) / results['comparison']['design_cost']) * 100:.1f}%",
                    f"{((results['emissions']['CO2'] - results['comparison']['design_emissions']['CO2']) / results['comparison']['design_emissions']['CO2']) * 100:.1f}%",
                    f"{((results['emissions']['SOx'] - results['comparison']['design_emissions']['SOx']) / results['comparison']['design_emissions']['SOx']) * 100:.1f}%",
                    f"{((results['emissions']['NOx'] - results['comparison']['design_emissions']['NOx']) / results['comparison']['design_emissions']['NOx']) * 100:.1f}%"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Download button for results
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="speed_optimization_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with tab4:
            st.subheader("Route Map with Optimization Results")
            create_route_map(
                st.session_state.route_data,
                st.session_state.vessel_data,
                st.session_state.optimization_results
            )
    
    else:
        st.info("Run the optimization to see results.")
