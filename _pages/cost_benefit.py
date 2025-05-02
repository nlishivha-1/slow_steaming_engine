import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.optimization import generate_speed_profile, optimize_speed
from utils.data_processing import calculate_transit_time

def app():
    """
    Cost-Benefit Analysis page for analyzing the economic impact of slow steaming
    """
    st.title("Cost-Benefit Analysis")
    
    st.markdown("""
    Analyze the economic trade-offs between fuel savings, transit time costs, 
    and other operational factors related to slow steaming practices.
    """)
    
    # Check if vessel and route data are available
    if 'vessel_data' not in st.session_state or st.session_state.vessel_data is None:
        st.warning("Please enter vessel specifications first in the Vessel Input page.")
        return
    
    if 'route_data' not in st.session_state or st.session_state.route_data is None:
        st.warning("Please enter route information first in the Route Optimization page.")
        return
    
    # Economic parameters
    st.header("Economic Parameters")
    
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
        
        vessel_day_cost = st.number_input(
            "Vessel Operating Cost (USD/day)",
            min_value=5000,
            max_value=100000,
            value=25000,
            step=1000,
            help="Daily operating cost including crew, maintenance, insurance, etc."
        )
    
    with col2:
        cargo_value = st.number_input(
            "Cargo Value (USD)",
            min_value=0,
            max_value=100000000,
            value=20000000,
            step=1000000,
            help="Total value of cargo being transported"
        )
        
        inventory_cost_pct = st.number_input(
            "Inventory Cost (%/year)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            help="Annual inventory carrying cost as percentage of cargo value"
        )
    
    # Additional factors
    show_advanced = st.checkbox("Show Advanced Factors")
    
    if show_advanced:
        col1, col2 = st.columns(2)
        
        with col1:
            port_cost = st.number_input(
                "Port Call Cost (USD)",
                min_value=0,
                max_value=100000,
                value=25000,
                step=1000,
                help="Cost per port call"
            )
            
            carbon_price = st.number_input(
                "Carbon Price (USD/ton CO₂)",
                min_value=0,
                max_value=500,
                value=25,
                step=5,
                help="Price of carbon emissions per ton of CO₂"
            )
        
        with col2:
            maintenance_savings_pct = st.slider(
                "Maintenance Savings (%)",
                min_value=0,
                max_value=20,
                value=5,
                step=1,
                help="Estimated maintenance cost reduction due to slow steaming"
            )
            
            market_rate_impact = st.selectbox(
                "Market Rate Impact",
                ["None", "Low", "Medium", "High"],
                help="Impact of slower service on market freight rates"
            )
    else:
        port_cost = 25000
        carbon_price = 25
        maintenance_savings_pct = 5
        market_rate_impact = "None"
    
    # Calculate market rate impact factor
    market_impact_factors = {
        "None": 0.0,
        "Low": -2.0,
        "Medium": -5.0,
        "High": -10.0
    }
    market_rate_factor = market_impact_factors.get(market_rate_impact, 0.0)
    
    # Get vessel and route data
    vessel_data = st.session_state.vessel_data
    route_data = st.session_state.route_data
    route_distance = route_data.get('distance', 5000)
    design_speed = vessel_data.get('design_speed', 20)
    
    # Run analysis
    if st.button("Run Cost-Benefit Analysis", use_container_width=True):
        with st.spinner("Analyzing cost-benefit scenarios..."):
            # Create speed range for analysis
            min_speed = max(6, design_speed * 0.5)
            max_speed = min(design_speed * 1.1, vessel_data.get('max_speed', 25))
            
            # Generate speed profile
            speed_profile = generate_speed_profile(
                vessel_data,
                route_distance,
                fuel_price,
                vessel_day_cost,
                (min_speed, max_speed),
                0.5
            )
            
            # Calculate additional economic factors
            daily_inventory_cost = (cargo_value * (inventory_cost_pct / 100)) / 365
            
            # Add inventory cost and other factors to speed profile
            speed_profile['inventory_cost'] = speed_profile['transit_time'] * daily_inventory_cost
            speed_profile['carbon_cost'] = speed_profile['co2_emissions'] * carbon_price
            speed_profile['maintenance_savings'] = (vessel_day_cost * (maintenance_savings_pct / 100)) * speed_profile['transit_time']
            
            # Calculate market rate impact - simplified model
            baseline_time = route_distance / (design_speed * 24)  # days at design speed
            speed_profile['market_rate_impact'] = 0
            
            if market_rate_factor != 0:
                for idx, row in speed_profile.iterrows():
                    time_increase_pct = ((row['transit_time'] - baseline_time) / baseline_time) * 100
                    if time_increase_pct > 0:
                        # Rate impact is proportional to time increase
                        impact = (cargo_value * market_rate_factor / 100) * (time_increase_pct / 20)
                        speed_profile.at[idx, 'market_rate_impact'] = impact
            
            # Calculate total cost including all factors
            speed_profile['total_economic_cost'] = (
                speed_profile['fuel_cost'] + 
                speed_profile['time_cost'] + 
                speed_profile['inventory_cost'] + 
                speed_profile['carbon_cost'] - 
                speed_profile['maintenance_savings'] +
                speed_profile['market_rate_impact']
            )
            
            # Find the economically optimal speed
            optimal_row = speed_profile.loc[speed_profile['total_economic_cost'].idxmin()]
            optimal_economic_speed = optimal_row['speed']
            
            # Store results in session state
            st.session_state.economic_analysis = {
                'speed_profile': speed_profile,
                'optimal_economic_speed': optimal_economic_speed,
                'optimal_row': optimal_row,
                'parameters': {
                    'fuel_price': fuel_price,
                    'vessel_day_cost': vessel_day_cost,
                    'cargo_value': cargo_value,
                    'inventory_cost_pct': inventory_cost_pct,
                    'port_cost': port_cost,
                    'carbon_price': carbon_price,
                    'maintenance_savings_pct': maintenance_savings_pct,
                    'market_rate_impact': market_rate_impact
                }
            }
            
            st.success("Cost-benefit analysis completed successfully!")
    
    # Display analysis results if available
    if 'economic_analysis' in st.session_state and st.session_state.economic_analysis is not None:
        st.header("Cost-Benefit Analysis Results")
        
        analysis = st.session_state.economic_analysis
        speed_profile = analysis['speed_profile']
        optimal_economic_speed = analysis['optimal_economic_speed']
        optimal_row = analysis['optimal_row']
        
        # Display optimal economic speed
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Economically Optimal Speed",
                value=f"{optimal_economic_speed:.2f} knots",
                delta=f"{((optimal_economic_speed - design_speed) / design_speed) * 100:.1f}% vs Design"
            )
        
        with col2:
            optimal_transit = optimal_row['transit_time']
            design_transit = route_distance / (design_speed * 24)
            
            st.metric(
                label="Transit Time",
                value=f"{optimal_transit:.2f} days",
                delta=f"{((optimal_transit - design_transit) / design_transit) * 100:.1f}%",
                delta_color="inverse"
            )
        
        with col3:
            optimal_cost = optimal_row['total_economic_cost']
            design_row = speed_profile[speed_profile['speed'].round(1) == round(design_speed, 1)]
            
            if not design_row.empty:
                design_cost = design_row.iloc[0]['total_economic_cost']
                st.metric(
                    label="Total Economic Cost",
                    value=f"${optimal_cost:,.2f}",
                    delta=f"{((optimal_cost - design_cost) / design_cost) * 100:.1f}%",
                    delta_color="inverse"
                )
            else:
                st.metric(
                    label="Total Economic Cost",
                    value=f"${optimal_cost:,.2f}"
                )
        
        # Create tabs for different visualization options
        tab1, tab2, tab3 = st.tabs([
            "Total Cost Analysis",
            "Cost Breakdown",
            "Sensitivity Analysis"
        ])
        
        with tab1:
            st.subheader("Speed vs. Total Economic Cost")
            
            # Create total cost curve
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=speed_profile['speed'],
                y=speed_profile['total_economic_cost'],
                mode='lines',
                name='Total Economic Cost',
                line=dict(color='purple', width=3)
            ))
            
            # Add vertical line for optimal economic speed
            fig.add_vline(
                x=optimal_economic_speed,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Optimal: {optimal_economic_speed:.2f} knots",
                annotation_position="top right"
            )
            
            # Add vertical line for design speed
            fig.add_vline(
                x=design_speed,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Design: {design_speed:.2f} knots",
                annotation_position="top left"
            )
            
            fig.update_layout(
                title='Speed vs. Total Economic Cost',
                xaxis_title='Speed (knots)',
                yaxis_title='Total Cost (USD)',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show savings at optimal speed
            design_row = speed_profile[speed_profile['speed'].round(1) == round(design_speed, 1)]
            if not design_row.empty:
                design_cost = design_row.iloc[0]['total_economic_cost']
                savings = design_cost - optimal_cost
                st.success(f"**Total savings at optimal economic speed: ${savings:,.2f}** ({((savings/design_cost) * 100):.1f}% reduction)")
        
        with tab2:
            st.subheader("Cost Component Breakdown")
            
            # Create a stacked area chart for cost components
            cost_components = pd.DataFrame({
                'Speed': speed_profile['speed'],
                'Fuel Cost': speed_profile['fuel_cost'],
                'Time Cost': speed_profile['time_cost'],
                'Inventory Cost': speed_profile['inventory_cost'],
                'Carbon Cost': speed_profile['carbon_cost'],
                'Market Impact': speed_profile['market_rate_impact'],
                'Maintenance Savings': -speed_profile['maintenance_savings']  # Negative as it's a saving
            })
            
            fig = px.area(
                cost_components, 
                x='Speed', 
                y=['Fuel Cost', 'Time Cost', 'Inventory Cost', 'Carbon Cost', 'Market Impact', 'Maintenance Savings'],
                title='Cost Component Breakdown by Speed',
                labels={'value': 'Cost (USD)', 'variable': 'Cost Component'}
            )
            
            # Add vertical line for optimal economic speed
            fig.add_vline(
                x=optimal_economic_speed,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Optimal: {optimal_economic_speed:.2f} knots",
                annotation_position="top right"
            )
            
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a pie chart for the optimal speed cost breakdown
            optimal_cost_breakdown = {
                'Fuel Cost': optimal_row['fuel_cost'],
                'Time Cost': optimal_row['time_cost'],
                'Inventory Cost': optimal_row['inventory_cost'],
                'Carbon Cost': optimal_row['carbon_cost'],
                'Market Impact': optimal_row['market_rate_impact'],
                'Maintenance Savings': -optimal_row['maintenance_savings']  # Negative as it's a saving
            }
            
            # Filter out zero and negative values for the pie chart
            filtered_breakdown = {k: v for k, v in optimal_cost_breakdown.items() if v > 0}
            
            fig = px.pie(
                values=list(filtered_breakdown.values()),
                names=list(filtered_breakdown.keys()),
                title=f'Cost Breakdown at Optimal Speed ({optimal_economic_speed:.2f} knots)'
            )
            
            fig.update_layout(height=500)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display the cost breakdown table
            st.subheader("Cost Breakdown at Optimal Economic Speed")
            
            breakdown_data = {
                "Cost Component": list(optimal_cost_breakdown.keys()),
                "Cost (USD)": list(optimal_cost_breakdown.values()),
                "% of Total": [(v / sum(v for v in optimal_cost_breakdown.values() if v > 0)) * 100 for v in optimal_cost_breakdown.values()]
            }
            
            breakdown_df = pd.DataFrame(breakdown_data)
            breakdown_df["Cost (USD)"] = breakdown_df["Cost (USD)"].map("${:,.2f}".format)
            breakdown_df["% of Total"] = breakdown_df["% of Total"].map("{:.1f}%".format)
            
            st.dataframe(breakdown_df, use_container_width=True)
        
        with tab3:
            st.subheader("Sensitivity Analysis")
            
            # Create sensitivity analysis for different parameters
            sensitivity_factor = st.selectbox(
                "Select parameter for sensitivity analysis:",
                ["Fuel Price", "Vessel Day Cost", "Inventory Cost", "Carbon Price"]
            )
            
            # Define variation range for each factor
            variation_ranges = {
                "Fuel Price": np.linspace(fuel_price * 0.5, fuel_price * 2.0, 6),
                "Vessel Day Cost": np.linspace(vessel_day_cost * 0.5, vessel_day_cost * 2.0, 6),
                "Inventory Cost": np.linspace(max(0.1, inventory_cost_pct * 0.5), inventory_cost_pct * 2.0, 6),
                "Carbon Price": np.linspace(max(1, carbon_price * 0.5), carbon_price * 3.0, 6)
            }
            
            variations = variation_ranges[sensitivity_factor]
            
            # Create a dataframe to store optimal speeds for each variation
            sensitivity_results = []
            
            # Function to run optimization with varied parameters
            def run_varied_optimization(vessel_data, route_distance, varied_fuel_price, varied_vessel_day_cost, 
                                       varied_inventory_cost, varied_carbon_price):
                # Use the same speed range as defined earlier
                speed_min = 8.0
                speed_max = 24.0
                
                # Generate speed profile
                profile = generate_speed_profile(
                    vessel_data,
                    route_distance,
                    varied_fuel_price,
                    varied_vessel_day_cost,
                    (speed_min, speed_max),
                    0.5
                )
                
                # Calculate additional economic factors
                daily_inv_cost = (cargo_value * (varied_inventory_cost / 100)) / 365
                
                # Add factors to profile
                profile['inventory_cost'] = profile['transit_time'] * daily_inv_cost
                profile['carbon_cost'] = profile['co2_emissions'] * varied_carbon_price
                profile['maintenance_savings'] = (varied_vessel_day_cost * (maintenance_savings_pct / 100)) * profile['transit_time']
                
                # Calculate market rate impact
                profile['market_rate_impact'] = 0
                if market_rate_factor != 0:
                    baseline_t = route_distance / (design_speed * 24)
                    for idx, row in profile.iterrows():
                        time_inc_pct = ((row['transit_time'] - baseline_t) / baseline_t) * 100
                        if time_inc_pct > 0:
                            impact = (cargo_value * market_rate_factor / 100) * (time_inc_pct / 20)
                            profile.at[idx, 'market_rate_impact'] = impact
                
                # Calculate total cost
                profile['total_economic_cost'] = (
                    profile['fuel_cost'] + 
                    profile['time_cost'] + 
                    profile['inventory_cost'] + 
                    profile['carbon_cost'] - 
                    profile['maintenance_savings'] +
                    profile['market_rate_impact']
                )
                
                # Find optimal speed
                optimal_r = profile.loc[profile['total_economic_cost'].idxmin()]
                return optimal_r['speed'], optimal_r['total_economic_cost']
            
            # Run sensitivity analysis
            for var in variations:
                varied_fuel_price = var if sensitivity_factor == "Fuel Price" else fuel_price
                varied_vessel_day_cost = var if sensitivity_factor == "Vessel Day Cost" else vessel_day_cost
                varied_inventory_cost = var if sensitivity_factor == "Inventory Cost" else inventory_cost_pct
                varied_carbon_price = var if sensitivity_factor == "Carbon Price" else carbon_price
                
                opt_speed, opt_cost = run_varied_optimization(
                    vessel_data,
                    route_distance,
                    varied_fuel_price,
                    varied_vessel_day_cost,
                    varied_inventory_cost,
                    varied_carbon_price
                )
                
                sensitivity_results.append({
                    'Parameter Value': var,
                    'Optimal Speed': opt_speed,
                    'Total Cost': opt_cost
                })
            
            # Create dataframe for results
            sensitivity_df = pd.DataFrame(sensitivity_results)
            
            # Display the sensitivity results
            col1, col2 = st.columns(2)
            
            with col1:
                # Plot optimal speed vs parameter variation
                parameter_unit = {
                    "Fuel Price": "USD/ton",
                    "Vessel Day Cost": "USD/day",
                    "Inventory Cost": "%/year",
                    "Carbon Price": "USD/ton CO₂"
                }
                
                fig = px.line(
                    sensitivity_df, 
                    x='Parameter Value', 
                    y='Optimal Speed',
                    title=f'Optimal Speed vs {sensitivity_factor}',
                    labels={
                        'Parameter Value': f'{sensitivity_factor} ({parameter_unit[sensitivity_factor]})',
                        'Optimal Speed': 'Optimal Speed (knots)'
                    },
                    markers=True
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Plot total cost vs parameter variation
                fig = px.line(
                    sensitivity_df, 
                    x='Parameter Value', 
                    y='Total Cost',
                    title=f'Total Cost vs {sensitivity_factor}',
                    labels={
                        'Parameter Value': f'{sensitivity_factor} ({parameter_unit[sensitivity_factor]})',
                        'Total Cost': 'Total Cost (USD)'
                    },
                    markers=True
                )
                
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Display sensitivity table
            st.subheader("Sensitivity Analysis Results")
            
            display_df = sensitivity_df.copy()
            display_df['Parameter Value'] = display_df['Parameter Value'].apply(lambda x: f"{x:,.2f} {parameter_unit[sensitivity_factor]}")
            display_df['Optimal Speed'] = display_df['Optimal Speed'].apply(lambda x: f"{x:.2f} knots")
            display_df['Total Cost'] = display_df['Total Cost'].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(display_df, use_container_width=True)
    
    else:
        st.info("Run the cost-benefit analysis to see results.")
        
        # Show sample calculation
        with st.expander("Understanding the Cost-Benefit Calculation"):
            st.markdown("""
            ### Key Components in Cost-Benefit Analysis
            
            1. **Fuel Costs**: Fuel consumption has a cubic relationship with speed. Reducing speed by 10% can reduce fuel consumption by approximately 27%.
            
            2. **Time Costs**: Slower speeds extend voyage duration, increasing crew costs, charter costs, and other time-dependent expenses.
            
            3. **Inventory Costs**: Slower delivery means cargo is in transit longer, increasing inventory carrying costs for cargo owners.
            
            4. **Carbon Costs**: Emissions reductions through slow steaming may have direct financial benefits through carbon pricing mechanisms.
            
            5. **Maintenance Benefits**: Lower engine loads can reduce maintenance costs and extend equipment life.
            
            6. **Market Impact**: Slower service may affect the rates that can be charged in competitive markets.
            
            The economically optimal speed balances all these factors to minimize total cost.
            """)
