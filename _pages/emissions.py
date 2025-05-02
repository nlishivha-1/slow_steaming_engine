import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.emissions import calculate_detailed_emissions, calculate_cii_rating, calculate_compliance_forecast
from utils.visualization import create_cii_gauge, create_emissions_comparison_chart

def app():
    """
    Emissions Calculator page for analyzing vessel emissions and regulatory compliance
    """
    st.title("Emissions Calculator")
    
    st.markdown("""
    Calculate and analyze vessel emissions based on operational parameters.
    Track compliance with IMO regulations and forecast future emissions scenarios.
    """)
    
    # Check if vessel and route data are available
    if 'vessel_data' not in st.session_state or st.session_state.vessel_data is None:
        st.warning("Please enter vessel specifications first in the Vessel Input page.")
        return
    
    if 'route_data' not in st.session_state or st.session_state.route_data is None:
        st.warning("Please enter route information first in the Route Optimization page.")
        return
    
    # Get vessel and route data
    vessel_data = st.session_state.vessel_data
    route_data = st.session_state.route_data
    route_distance = route_data.get('distance', 5000)
    
    # Create tabs for different emission analysis sections
    tab1, tab2, tab3 = st.tabs([
        "Voyage Emissions",
        "CII Rating Calculator",
        "Compliance Forecast"
    ])
    
    with tab1:
        st.header("Voyage Emissions Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            voyage_speed = st.number_input(
                "Voyage Speed (knots)",
                min_value=5.0,
                max_value=float(vessel_data.get('max_speed', 25)),
                value=float(vessel_data.get('design_speed', 20)) * 0.8,
                step=0.5,
                help="Operational speed for the voyage"
            )
            
            fuel_type = st.selectbox(
                "Fuel Type",
                ["VLSFO", "MGO", "LSFO", "HFO"],
                index=0,
                help="Type of fuel used for the voyage"
            )
        
        with col2:
            fuel_price = st.number_input(
                "Fuel Price (USD/ton)",
                min_value=200,
                max_value=1500,
                value=600,
                step=10,
                help="Current market price of fuel per ton"
            )
            
            carbon_price = st.number_input(
                "Carbon Price (USD/ton CO₂)",
                min_value=0,
                max_value=200,
                value=25,
                step=5,
                help="Price of carbon emissions per ton of CO₂"
            )
        
        if st.button("Calculate Voyage Emissions", use_container_width=True):
            with st.spinner("Calculating emissions..."):
                # Calculate transit time
                transit_time = route_distance / (voyage_speed * 24)  # days
                
                # Calculate fuel consumption (using cubic relationship)
                design_speed = vessel_data.get('design_speed', 20)
                design_consumption = vessel_data.get('design_consumption', 180)
                daily_fuel = design_consumption * (voyage_speed / design_speed) ** 3
                total_fuel = daily_fuel * transit_time
                
                # Calculate emissions
                emissions = calculate_detailed_emissions(total_fuel, fuel_type)
                
                # Calculate costs
                fuel_cost = total_fuel * fuel_price
                carbon_cost = emissions['CO2'] * carbon_price
                
                # Store results in session state
                st.session_state.emissions_data = {
                    'voyage_speed': voyage_speed,
                    'fuel_type': fuel_type,
                    'transit_time': transit_time,
                    'daily_fuel': daily_fuel,
                    'total_fuel': total_fuel,
                    'emissions': emissions,
                    'fuel_cost': fuel_cost,
                    'carbon_cost': carbon_cost
                }
                
                st.success("Emissions calculation completed!")
        
        # Display emissions results if available
        if 'emissions_data' in st.session_state and st.session_state.emissions_data is not None:
            st.subheader("Voyage Emissions Results")
            
            data = st.session_state.emissions_data
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="CO₂ Emissions",
                    value=f"{data['emissions']['CO2']:.2f} tons"
                )
            
            with col2:
                st.metric(
                    label="SOₓ Emissions",
                    value=f"{data['emissions']['SOx']:.2f} tons"
                )
            
            with col3:
                st.metric(
                    label="NOₓ Emissions",
                    value=f"{data['emissions']['NOx']:.2f} tons"
                )
            
            with col4:
                st.metric(
                    label="PM Emissions",
                    value=f"{data['emissions']['PM']:.2f} tons"
                )
            
            # Display cost information
            st.subheader("Emissions-Related Costs")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Fuel Cost",
                    value=f"${data['fuel_cost']:,.2f}"
                )
            
            with col2:
                st.metric(
                    label="Carbon Cost",
                    value=f"${data['carbon_cost']:,.2f}"
                )
            
            with col3:
                st.metric(
                    label="Total Environmental Cost",
                    value=f"${data['fuel_cost'] + data['carbon_cost']:,.2f}"
                )
            
            # Create emissions visualization
            st.subheader("Emissions Breakdown")
            
            emissions_df = pd.DataFrame({
                'Type': list(data['emissions'].keys()),
                'Amount (tons)': list(data['emissions'].values())
            })
            
            fig = px.bar(
                emissions_df,
                x='Type',
                y='Amount (tons)',
                title=f"Emissions for Voyage at {data['voyage_speed']:.1f} knots",
                color='Type',
                color_discrete_map={
                    'CO2': '#FF6B6B',
                    'SOx': '#4ECDC4',
                    'NOx': '#FFD166',
                    'PM': '#8338EC'
                }
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Add comparison with different speeds
            with st.expander("Compare with different speeds"):
                st.markdown("### Emissions at Different Speeds")
                
                # Generate speed range for comparison
                # Define design speed and consumption from vessel data
                design_speed = vessel_data.get('design_speed', 14)
                design_consumption = vessel_data.get('design_consumption', 30)
                
                speeds = np.linspace(
                    max(5, data['voyage_speed'] * 0.7),
                    min(vessel_data.get('max_speed', 25), data['voyage_speed'] * 1.3),
                    5
                )
                
                comparison_data = []
                
                for speed in speeds:
                    # Calculate transit time and fuel consumption
                    transit = route_distance / (speed * 24)
                    fuel = design_consumption * (speed / design_speed) ** 3
                    total_f = fuel * transit
                    
                    # Calculate emissions
                    emis = calculate_detailed_emissions(total_f, data['fuel_type'])
                    
                    # Add to comparison data
                    comparison_data.append({
                        'Speed': f"{speed:.1f} knots",
                        'Transit Time': f"{transit:.2f} days",
                        'Fuel': f"{total_f:.2f} tons",
                        'CO₂': emis['CO2'],
                        'SOₓ': emis['SOx'],
                        'NOₓ': emis['NOx'],
                        'PM': emis['PM'],
                        'Fuel Cost': fuel_price * total_f,
                        'Carbon Cost': carbon_price * emis['CO2']
                    })
                
                # Create comparison table
                comparison_df = pd.DataFrame(comparison_data)
                
                # Format monetary columns
                for col in ['Fuel Cost', 'Carbon Cost']:
                    comparison_df[col] = comparison_df[col].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(comparison_df, use_container_width=True)
    
    with tab2:
        st.header("Carbon Intensity Indicator (CII) Calculator")
        
        st.markdown("""
        Calculate the CII rating for your vessel based on annual operational data.
        The CII rating is a measure of carbon efficiency required by IMO regulations.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            annual_distance = st.number_input(
                "Annual Distance (nautical miles)",
                min_value=5000,
                max_value=200000,
                value=100000,
                step=5000,
                help="Total distance sailed in one year"
            )
            
            annual_fuel = st.number_input(
                "Annual Fuel Consumption (tons)",
                min_value=100,
                max_value=50000,
                value=10000,
                step=100,
                help="Total fuel consumed in one year"
            )
        
        with col2:
            cargo_capacity_utilization = st.slider(
                "Average Cargo Capacity Utilization (%)",
                min_value=10,
                max_value=100,
                value=70,
                step=5,
                help="Average percentage of cargo capacity utilized"
            ) / 100
            
            st.markdown(f"""
            **Vessel Deadweight:** {vessel_data.get('deadweight', 'N/A')} tons  
            **Vessel Type:** {vessel_data.get('type', 'N/A')}  
            **Year Built:** {vessel_data.get('year_built', 'N/A')}
            """)
        
        if st.button("Calculate CII Rating", use_container_width=True):
            with st.spinner("Calculating CII rating..."):
                # Calculate CII rating
                cii_results = calculate_cii_rating(
                    vessel_data,
                    annual_distance,
                    annual_fuel,
                    cargo_capacity_utilization
                )
                
                # Store results in session state
                st.session_state.cii_data = cii_results
                
                st.success("CII rating calculation completed!")
        
        # Display CII results if available
        if 'cii_data' in st.session_state and st.session_state.cii_data is not None:
            st.subheader("CII Rating Results")
            
            data = st.session_state.cii_data
            
            # Display gauge chart
            create_cii_gauge(data)
            
            # Display detailed metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="CO₂ Emissions",
                    value=f"{data['co2_emissions']:.2f} tons"
                )
            
            with col2:
                st.metric(
                    label="Transport Work",
                    value=f"{(data['transport_work']/1000000):.2f} M ton-miles"
                )
            
            with col3:
                st.metric(
                    label="Annual Efficiency Ratio",
                    value=f"{data['aer']:.2f} g CO₂/ton-mile",
                    delta=f"{((data['aer'] - data['reference_aer']) / data['reference_aer']) * 100:.1f}% vs Reference",
                    delta_color="inverse"
                )
            
            # Display explanation
            rating_explanations = {
                'A': "Superior performance - significantly better than required",
                'B': "Good performance - exceeds requirements",
                'C': "Moderate performance - meets minimum requirements",
                'D': "Below average performance - improvement needed soon",
                'E': "Poor performance - major improvement required immediately"
            }
            
            st.info(f"""
            **CII Rating: {data['rating']}** - {rating_explanations.get(data['rating'], '')}
            
            Your vessel's CII ratio is {data['cii_ratio']:.3f}, which is calculated by dividing your actual
            Annual Efficiency Ratio ({data['aer']:.2f}) by the reference value ({data['reference_aer']:.2f}).
            
            CII ratings are assigned as follows:
            - A: ratio < 0.86
            - B: 0.86 ≤ ratio < 0.93
            - C: 0.93 ≤ ratio < 1.03
            - D: 1.03 ≤ ratio < 1.10
            - E: ratio ≥ 1.10
            
            Vessels with D rating for 3 consecutive years or E rating for 1 year must develop and implement
            a corrective action plan to achieve a C rating or better.
            """)
    
    with tab3:
        st.header("Emissions Compliance Forecast")
        
        st.markdown("""
        Forecast the impact of speed reductions on your vessel's CII rating and emissions compliance.
        This tool helps you plan the necessary operational changes to meet future regulatory requirements.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_speed = st.number_input(
                "Current Average Speed (knots)",
                min_value=5.0,
                max_value=float(vessel_data.get('max_speed', 25)),
                value=float(vessel_data.get('design_speed', 20)),
                step=0.5,
                help="Current average operational speed"
            )
            
            annual_distance_forecast = st.number_input(
                "Annual Distance (nautical miles)",
                min_value=5000,
                max_value=200000,
                value=100000,
                step=5000,
                help="Expected annual distance sailed"
            )
        
        with col2:
            proposed_speed = st.number_input(
                "Proposed Average Speed (knots)",
                min_value=5.0,
                max_value=float(vessel_data.get('max_speed', 25)),
                value=float(vessel_data.get('design_speed', 20)) * 0.8,
                step=0.5,
                help="Proposed reduced speed for compliance"
            )
            
            # Calculate and display the % reduction
            speed_reduction_pct = ((current_speed - proposed_speed) / current_speed) * 100
            st.markdown(f"**Speed Reduction:** {speed_reduction_pct:.1f}% from current speed")
        
        if st.button("Generate Compliance Forecast", use_container_width=True):
            with st.spinner("Generating compliance forecast..."):
                # Calculate compliance forecast
                forecast_results = calculate_compliance_forecast(
                    vessel_data,
                    current_speed,
                    proposed_speed,
                    annual_distance_forecast
                )
                
                # Store results in session state
                st.session_state.compliance_forecast = forecast_results
                
                st.success("Compliance forecast generated!")
        
        # Display forecast results if available
        if 'compliance_forecast' in st.session_state and st.session_state.compliance_forecast is not None:
            st.subheader("Compliance Forecast Results")
            
            forecast = st.session_state.compliance_forecast
            
            # Display comparison metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Scenario")
                st.metric(
                    label="Speed",
                    value=f"{forecast['current_scenario']['speed']:.2f} knots"
                )
                st.metric(
                    label="Annual Fuel Consumption",
                    value=f"{forecast['current_scenario']['annual_fuel']:.2f} tons"
                )
                st.metric(
                    label="CII Rating",
                    value=forecast['current_scenario']['cii_rating']
                )
                st.metric(
                    label="CII Ratio",
                    value=f"{forecast['current_scenario']['cii_ratio']:.3f}"
                )
            
            with col2:
                st.subheader("Proposed Scenario")
                st.metric(
                    label="Speed",
                    value=f"{forecast['proposed_scenario']['speed']:.2f} knots",
                    delta=f"{((forecast['proposed_scenario']['speed'] - forecast['current_scenario']['speed']) / forecast['current_scenario']['speed']) * 100:.1f}%"
                )
                st.metric(
                    label="Annual Fuel Consumption",
                    value=f"{forecast['proposed_scenario']['annual_fuel']:.2f} tons",
                    delta=f"{((forecast['proposed_scenario']['annual_fuel'] - forecast['current_scenario']['annual_fuel']) / forecast['current_scenario']['annual_fuel']) * 100:.1f}%",
                    delta_color="inverse"
                )
                st.metric(
                    label="CII Rating",
                    value=forecast['proposed_scenario']['cii_rating']
                )
                st.metric(
                    label="CII Ratio",
                    value=f"{forecast['proposed_scenario']['cii_ratio']:.3f}",
                    delta=f"{((forecast['proposed_scenario']['cii_ratio'] - forecast['current_scenario']['cii_ratio']) / forecast['current_scenario']['cii_ratio']) * 100:.1f}%",
                    delta_color="inverse"
                )
            
            # Display savings information
            st.subheader("Environmental and Economic Benefits")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Fuel Savings",
                    value=f"{forecast['savings']['fuel_savings']:.2f} tons",
                    delta=f"{forecast['savings']['percentage_reduction']:.1f}%"
                )
            
            with col2:
                st.metric(
                    label="CO₂ Emission Reduction",
                    value=f"{forecast['savings']['emission_savings']:.2f} tons",
                    delta=f"{forecast['savings']['percentage_reduction']:.1f}%"
                )
            
            with col3:
                # Calculate cost savings (assuming the previously entered fuel price)
                fuel_price_to_use = 600  # Default if not set
                if 'emissions_data' in st.session_state and st.session_state.emissions_data is not None:
                    if 'fuel_cost' in st.session_state.emissions_data and 'total_fuel' in st.session_state.emissions_data:
                        fuel_price_to_use = st.session_state.emissions_data['fuel_cost'] / st.session_state.emissions_data['total_fuel']
                
                cost_savings = forecast['savings']['fuel_savings'] * fuel_price_to_use
                
                st.metric(
                    label="Cost Savings",
                    value=f"${cost_savings:,.2f}",
                    delta=f"{forecast['savings']['percentage_reduction']:.1f}%"
                )
            
            # Create a visualization comparing emissions
            st.subheader("Emissions Comparison")
            
            # Calculate emissions for both scenarios
            current_co2 = forecast['current_scenario']['annual_fuel'] * 3.114  # tons CO2
            proposed_co2 = forecast['proposed_scenario']['annual_fuel'] * 3.114  # tons CO2
            
            # Create emissions data for comparison
            current_emissions = {
                'CO2': current_co2,
                'SOx': current_co2 * 0.00173,  # Approximate ratio for VLSFO
                'NOx': current_co2 * 0.0183,   # Approximate ratio for VLSFO
                'PM': current_co2 * 0.00045    # Approximate ratio for VLSFO
            }
            
            proposed_emissions = {
                'CO2': proposed_co2,
                'SOx': proposed_co2 * 0.00173,
                'NOx': proposed_co2 * 0.0183,
                'PM': proposed_co2 * 0.00045
            }
            
            # Create emissions comparison chart
            create_emissions_comparison_chart(current_emissions, proposed_emissions)
            
            # Add explanation and recommendations
            rating_improvements = {
                'E': {'to_d': 'Reduce speed by 5-10%', 'to_c': 'Reduce speed by 10-15%', 'to_b': 'Reduce speed by 15-20% and optimize route'},
                'D': {'to_c': 'Reduce speed by 5-10%', 'to_b': 'Reduce speed by 10-15%', 'to_a': 'Reduce speed by 15% and optimize route'},
                'C': {'to_b': 'Reduce speed by 5-10%', 'to_a': 'Reduce speed by 10-15% and optimize route'},
                'B': {'to_a': 'Reduce speed by 5-10% and optimize route'}
            }
            
            current_rating = forecast['current_scenario']['cii_rating']
            proposed_rating = forecast['proposed_scenario']['cii_rating']
            
            st.subheader("Compliance Recommendations")
            
            if current_rating == proposed_rating:
                if current_rating in ['D', 'E']:
                    st.warning(f"""
                    Your proposed speed reduction is not sufficient to improve your CII rating from {current_rating}.
                    Consider more significant speed reductions or additional measures to improve efficiency.
                    
                    Recommendations:
                    - {rating_improvements.get(current_rating, {}).get('to_c', 'Further reduce operational speed')}
                    - Optimize hull and propeller maintenance
                    - Consider route optimization to reduce distance traveled
                    - Evaluate technical upgrades to improve energy efficiency
                    """)
                else:
                    st.success(f"""
                    Your proposed speed reduction maintains your current CII rating of {current_rating}.
                    This still provides significant fuel savings and emissions reductions.
                    
                    Additional recommendations:
                    - Continue monitoring operational efficiency
                    - Consider weather routing to further reduce fuel consumption
                    - Implement just-in-time arrival coordination with ports
                    """)
            elif ord(proposed_rating) < ord(current_rating):  # Improvement in rating (e.g., from C to B)
                st.success(f"""
                Congratulations! Your proposed speed reduction improves your CII rating from {current_rating} to {proposed_rating}.
                This represents a significant improvement in environmental performance and regulatory compliance.
                
                Benefits:
                - Improved regulatory compliance status
                - Reduced fuel costs and emissions
                - Better positioning for future regulatory requirements
                - Potential marketing advantage for environmentally conscious customers
                """)
            else:  # Deterioration in rating
                st.error(f"""
                Warning: Your proposed changes would worsen your CII rating from {current_rating} to {proposed_rating}.
                This would negatively impact your regulatory compliance status.
                
                Please reconsider your operational strategy to maintain or improve your current rating.
                """)
