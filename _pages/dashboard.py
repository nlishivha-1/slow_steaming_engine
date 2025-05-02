import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.visualization import create_dashboard_metrics, create_route_map, create_cii_gauge

def app():
    """
    Performance Dashboard page for visualizing key metrics and analysis results
    """
    st.title("Performance Dashboard")
    
    st.markdown("""
    This dashboard provides a comprehensive overview of vessel performance metrics, 
    optimization results, and environmental impact analysis.
    """)
    
    # Check if necessary data is available
    if 'vessel_data' not in st.session_state or st.session_state.vessel_data is None:
        st.warning("Please enter vessel specifications first in the Vessel Input page.")
        return
    
    if 'route_data' not in st.session_state or st.session_state.route_data is None:
        st.warning("Please enter route information first in the Route Optimization page.")
        return
    
    if 'optimization_results' not in st.session_state or st.session_state.optimization_results is None:
        st.warning("Please run speed optimization first in the Speed Optimization page.")
        return
    
    # Get data from session state
    vessel_data = st.session_state.vessel_data
    route_data = st.session_state.route_data
    optimization_results = st.session_state.optimization_results
    
    # Dashboard header with current date
    current_date = datetime.now().strftime("%B %d, %Y")
    st.markdown(f"### Performance Report - {current_date}")
    
    # Create dashboard sections
    tab1, tab2, tab3 = st.tabs([
        "Summary Metrics",
        "Optimization Analysis",
        "Environmental Impact"
    ])
    
    with tab1:
        st.subheader("Performance Summary")
        
        # Display vessel and route information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Vessel Information")
            st.markdown(f"""
            **Name:** {vessel_data.get('name', 'N/A')}  
            **Type:** {vessel_data.get('type', 'N/A')}  
            **Deadweight:** {vessel_data.get('deadweight', 'N/A')} tons  
            **Engine:** {vessel_data.get('engine_type', 'N/A')}  
            **Design Speed:** {vessel_data.get('design_speed', 'N/A')} knots  
            **Optimal Speed Range:** {vessel_data.get('optimal_speed_min', 'N/A'):.2f} - {vessel_data.get('optimal_speed_max', 'N/A'):.2f} knots
            """)
        
        with col2:
            st.markdown("### Route Information")
            st.markdown(f"""
            **Route:** {route_data.get('name', 'N/A')}  
            **Distance:** {route_data.get('distance', 'N/A')} nautical miles  
            **Waypoints:** {route_data.get('number_of_waypoints', 'N/A')}  
            **Origin:** {route_data.get('waypoints', [{}])[0].get('name', 'N/A')}  
            **Destination:** {route_data.get('waypoints', [{}])[-1].get('name', 'N/A')}
            """)
        
        # Display optimization metrics
        st.markdown("### Optimization Results")
        create_dashboard_metrics(optimization_results)
        
        # Display route map
        st.markdown("### Route Visualization")
        create_route_map(route_data, vessel_data, optimization_results)
    
    with tab2:
        st.subheader("Detailed Optimization Analysis")
        
        # Create speed vs cost analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Speed vs fuel consumption
            if 'speed_profile' in st.session_state:
                speed_profile = st.session_state.speed_profile
                
                fig = px.line(
                    speed_profile, 
                    x='speed', 
                    y='daily_fuel',
                    title='Speed vs. Daily Fuel Consumption',
                    labels={'speed': 'Speed (knots)', 'daily_fuel': 'Fuel Consumption (tons/day)'}
                )
                
                # Add vertical line for optimal speed
                fig.add_vline(
                    x=optimization_results['optimal_speed'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Optimal: {optimization_results['optimal_speed']:.2f} knots",
                    annotation_position="top right"
                )
                
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Speed profile data not available. Run optimization to generate data.")
        
        with col2:
            # Speed vs transit time
            if 'speed_profile' in st.session_state:
                speed_profile = st.session_state.speed_profile
                
                fig = px.line(
                    speed_profile, 
                    x='speed', 
                    y='transit_time',
                    title='Speed vs. Transit Time',
                    labels={'speed': 'Speed (knots)', 'transit_time': 'Transit Time (days)'}
                )
                
                # Add vertical line for optimal speed
                fig.add_vline(
                    x=optimization_results['optimal_speed'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Optimal: {optimization_results['optimal_speed']:.2f} knots",
                    annotation_position="top right"
                )
                
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Speed profile data not available. Run optimization to generate data.")
        
        # Display cost breakdown
        if 'speed_profile' in st.session_state:
            speed_profile = st.session_state.speed_profile
            
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
                height=400
            )
            
            # Add vertical line for optimal speed
            fig.add_vline(
                x=optimization_results['optimal_speed'],
                line_dash="dash",
                line_color="black",
                annotation_text=f"Optimal: {optimization_results['optimal_speed']:.2f} knots",
                annotation_position="top right"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Optimal speed comparison table
            st.subheader("Speed Comparison Analysis")
            
            comparison_data = {
                "Metric": [
                    "Speed (knots)",
                    "Transit Time (days)",
                    "Fuel Consumption (tons)",
                    "Fuel Cost (USD)",
                    "Time Cost (USD)",
                    "Total Cost (USD)",
                    "CO₂ Emissions (tons)"
                ],
                "Design Speed": [
                    optimization_results['comparison']['design_speed'],
                    optimization_results['comparison']['design_transit_time'],
                    optimization_results['comparison']['design_fuel_consumption'],
                    optimization_results['comparison']['design_cost'] - optimization_results['comparison']['design_transit_time'] * optimization_results['time_cost'] / optimization_results['transit_time'],
                    optimization_results['comparison']['design_transit_time'] * optimization_results['time_cost'] / optimization_results['transit_time'],
                    optimization_results['comparison']['design_cost'],
                    optimization_results['comparison']['design_emissions']['CO2']
                ],
                "Optimal Speed": [
                    optimization_results['optimal_speed'],
                    optimization_results['transit_time'],
                    optimization_results['total_fuel_consumption'],
                    optimization_results['fuel_cost'],
                    optimization_results['time_cost'],
                    optimization_results['total_cost'],
                    optimization_results['emissions']['CO2']
                ]
            }
            
            # Calculate savings and percentages
            comparison_data["Savings"] = [
                comparison_data["Design Speed"][0] - comparison_data["Optimal Speed"][0],
                comparison_data["Design Speed"][1] - comparison_data["Optimal Speed"][1],
                comparison_data["Design Speed"][2] - comparison_data["Optimal Speed"][2],
                comparison_data["Design Speed"][3] - comparison_data["Optimal Speed"][3],
                comparison_data["Design Speed"][4] - comparison_data["Optimal Speed"][4],
                comparison_data["Design Speed"][5] - comparison_data["Optimal Speed"][5],
                comparison_data["Design Speed"][6] - comparison_data["Optimal Speed"][6]
            ]
            
            comparison_data["Savings %"] = [
                (comparison_data["Savings"][0] / comparison_data["Design Speed"][0]) * 100,
                (comparison_data["Savings"][1] / comparison_data["Design Speed"][1]) * 100,
                (comparison_data["Savings"][2] / comparison_data["Design Speed"][2]) * 100,
                (comparison_data["Savings"][3] / comparison_data["Design Speed"][3]) * 100,
                (comparison_data["Savings"][4] / comparison_data["Design Speed"][4]) * 100,
                (comparison_data["Savings"][5] / comparison_data["Design Speed"][5]) * 100,
                (comparison_data["Savings"][6] / comparison_data["Design Speed"][6]) * 100
            ]
            
            # Create and format dataframe
            df = pd.DataFrame(comparison_data)
            
            # Format numeric columns
            format_dict = {
                "Design Speed": lambda x: f"{x:.2f}",
                "Optimal Speed": lambda x: f"{x:.2f}",
                "Savings": lambda x: f"{x:.2f}",
                "Savings %": lambda x: f"{x:.2f}%"
            }
            
            for col, formatter in format_dict.items():
                df[col] = df[col].apply(formatter)
            
            st.dataframe(df, use_container_width=True)
        
        else:
            st.info("Run speed optimization to view detailed analysis.")
    
    with tab3:
        st.subheader("Environmental Impact Assessment")
        
        # Create emissions visualization
        if 'speed_profile' in st.session_state:
            speed_profile = st.session_state.speed_profile
            
            # Create emissions vs speed chart
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
                height=400
            )
            
            # Add vertical line for optimal speed
            fig.add_vline(
                x=optimization_results['optimal_speed'],
                line_dash="dash",
                line_color="black",
                annotation_text=f"Optimal: {optimization_results['optimal_speed']:.2f} knots",
                annotation_position="top right"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Display CII rating if available
        if 'cii_data' in st.session_state and st.session_state.cii_data is not None:
            st.subheader("Carbon Intensity Indicator (CII)")
            
            # Display CII gauge
            create_cii_gauge(st.session_state.cii_data)
            
            # Add explanatory text
            st.markdown(f"""
            **CII Rating:** {st.session_state.cii_data['rating']}
            
            The Carbon Intensity Indicator (CII) is an operational efficiency measure that applies to vessels 5,000 GT and above.
            It determines the annual reduction factor needed to ensure continuous improvement of the ship's operational carbon intensity
            within a specific rating level.
            
            The CII rating scale ranges from A to E, where A is the best performance level:
            - A: Major Superior Performance
            - B: Minor Superior Performance
            - C: Moderate Performance (minimum acceptable level)
            - D: Minor Inferior Performance
            - E: Inferior Performance
            
            Ships rated D for three consecutive years or E for one year must submit a corrective action plan to show how the required
            index (C or above) will be achieved.
            """)
        else:
            st.info("Calculate your vessel's CII rating in the Emissions Calculator page to view it here.")
        
        # Display emissions forecast if available
        if 'compliance_forecast' in st.session_state and st.session_state.compliance_forecast is not None:
            st.subheader("Emissions Compliance Forecast")
            
            forecast = st.session_state.compliance_forecast
            
            # Create a bar chart comparing current vs proposed scenarios
            current_rating = forecast['current_scenario']['cii_rating']
            proposed_rating = forecast['proposed_scenario']['cii_rating']
            
            # Create labels for ratings with corresponding colors
            rating_colors = {'A': '#00FF00', 'B': '#88FF00', 'C': '#FFFF00', 'D': '#FFA500', 'E': '#FF0000'}
            
            # Create comparison dataframe for annual fuel and emissions
            comparison_df = pd.DataFrame({
                'Scenario': ['Current Operations', 'Proposed Slow Steaming'],
                'Annual Fuel (tons)': [
                    forecast['current_scenario']['annual_fuel'],
                    forecast['proposed_scenario']['annual_fuel']
                ],
                'CO₂ Emissions (tons)': [
                    forecast['current_scenario']['annual_fuel'] * 3.114,
                    forecast['proposed_scenario']['annual_fuel'] * 3.114
                ],
                'CII Rating': [
                    f"{current_rating} ({forecast['current_scenario']['cii_ratio']:.2f})",
                    f"{proposed_rating} ({forecast['proposed_scenario']['cii_ratio']:.2f})"
                ],
                'Rating Color': [
                    rating_colors.get(current_rating, '#CCCCCC'),
                    rating_colors.get(proposed_rating, '#CCCCCC')
                ]
            })
            
            # Create fuel comparison chart
            fig = px.bar(
                comparison_df,
                x='Scenario',
                y='Annual Fuel (tons)',
                title='Annual Fuel Consumption Comparison',
                color='Scenario',
                text='Annual Fuel (tons)',
                color_discrete_map={
                    'Current Operations': '#1565C0',
                    'Proposed Slow Steaming': '#4CAF50'
                }
            )
            
            fig.update_layout(height=350)
            fig.update_traces(texttemplate='%{y:.1f}', textposition='outside')
            
            # Show percent reduction
            reduction_pct = forecast['savings']['percentage_reduction']
            fig.add_annotation(
                x=1, y=comparison_df['Annual Fuel (tons)'][1] / 2,
                text=f"{reduction_pct:.1f}% Reduction",
                showarrow=False,
                font=dict(size=14, color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create CII rating comparison chart with custom colors
            fig = go.Figure()
            
            for i, row in comparison_df.iterrows():
                fig.add_trace(go.Bar(
                    x=[row['Scenario']],
                    y=[row['CO₂ Emissions (tons)']],
                    name=row['Scenario'],
                    text=row['CII Rating'],
                    marker_color=row['Rating Color'],
                    textposition='inside',
                    textfont=dict(size=14, color='black')
                ))
            
            fig.update_layout(
                title='CO₂ Emissions and CII Rating Comparison',
                yaxis_title='CO₂ Emissions (tons)',
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display savings information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Fuel Reduction",
                    value=f"{forecast['savings']['fuel_savings']:.2f} tons",
                    delta=f"{forecast['savings']['percentage_reduction']:.1f}%"
                )
            
            with col2:
                emission_savings = forecast['savings']['emission_savings']
                st.metric(
                    label="CO₂ Reduction",
                    value=f"{emission_savings:.2f} tons",
                    delta=f"{forecast['savings']['percentage_reduction']:.1f}%"
                )
            
            with col3:
                # Calculate equivalent passenger cars
                cars_equivalent = emission_savings / 4.6  # Average passenger car emissions ~4.6 tons CO2/year
                st.metric(
                    label="Equivalent to removing",
                    value=f"{int(cars_equivalent)} cars"
                )
        else:
            st.info("Generate a compliance forecast in the Emissions Calculator page to view it here.")
    
    # Add download options for report
    st.markdown("### Download Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'optimization_results' in st.session_state and st.session_state.optimization_results is not None:
            # Prepare optimization results for download
            optimization_data = {
                "Vessel": vessel_data.get('name', 'Unknown'),
                "Route": route_data.get('name', 'Unknown'),
                "Distance": route_data.get('distance', 0),
                "Design Speed": optimization_results['comparison']['design_speed'],
                "Optimal Speed": optimization_results['optimal_speed'],
                "Transit Time": optimization_results['transit_time'],
                "Fuel Consumption": optimization_results['total_fuel_consumption'],
                "Fuel Cost": optimization_results['fuel_cost'],
                "Time Cost": optimization_results['time_cost'],
                "Total Cost": optimization_results['total_cost'],
                "CO2 Emissions": optimization_results['emissions']['CO2'],
                "SOx Emissions": optimization_results['emissions']['SOx'],
                "NOx Emissions": optimization_results['emissions']['NOx'],
                "Fuel Savings": optimization_results['fuel_savings'],
                "Cost Savings": optimization_results['cost_savings'],
                "CO2 Reduction": optimization_results['co2_reduction'],
                "Report Date": current_date
            }
            
            # Convert to CSV string
            csv_data = ",".join(optimization_data.keys()) + "\n" + ",".join([str(v) for v in optimization_data.values()])
            
            st.download_button(
                label="Download Optimization Results",
                data=csv_data,
                file_name=f"optimization_results_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("Download Optimization Results", disabled=True, use_container_width=True)
    
    with col2:
        if 'emissions_data' in st.session_state and st.session_state.emissions_data is not None:
            # Prepare emissions data for download
            emissions_data = {
                "Vessel": vessel_data.get('name', 'Unknown'),
                "Route": route_data.get('name', 'Unknown'),
                "Speed": st.session_state.emissions_data['voyage_speed'],
                "Fuel Type": st.session_state.emissions_data['fuel_type'],
                "Fuel Consumption": st.session_state.emissions_data['total_fuel'],
                "CO2 Emissions": st.session_state.emissions_data['emissions']['CO2'],
                "SOx Emissions": st.session_state.emissions_data['emissions']['SOx'],
                "NOx Emissions": st.session_state.emissions_data['emissions']['NOx'],
                "PM Emissions": st.session_state.emissions_data['emissions']['PM'],
                "Fuel Cost": st.session_state.emissions_data['fuel_cost'],
                "Carbon Cost": st.session_state.emissions_data['carbon_cost'],
                "Report Date": current_date
            }
            
            # Convert to CSV string
            csv_data = ",".join(emissions_data.keys()) + "\n" + ",".join([str(v) for v in emissions_data.values()])
            
            st.download_button(
                label="Download Emissions Data",
                data=csv_data,
                file_name=f"emissions_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("Download Emissions Data", disabled=True, use_container_width=True)
    
    with col3:
        if 'compliance_forecast' in st.session_state and st.session_state.compliance_forecast is not None:
            # Prepare compliance forecast data for download
            forecast = st.session_state.compliance_forecast
            forecast_data = {
                "Vessel": vessel_data.get('name', 'Unknown'),
                "Current Speed": forecast['current_scenario']['speed'],
                "Proposed Speed": forecast['proposed_scenario']['speed'],
                "Current Annual Fuel": forecast['current_scenario']['annual_fuel'],
                "Proposed Annual Fuel": forecast['proposed_scenario']['annual_fuel'],
                "Current CII Rating": forecast['current_scenario']['cii_rating'],
                "Proposed CII Rating": forecast['proposed_scenario']['cii_rating'],
                "Current CII Ratio": forecast['current_scenario']['cii_ratio'],
                "Proposed CII Ratio": forecast['proposed_scenario']['cii_ratio'],
                "Fuel Savings": forecast['savings']['fuel_savings'],
                "Emission Savings": forecast['savings']['emission_savings'],
                "Percentage Reduction": forecast['savings']['percentage_reduction'],
                "Report Date": current_date
            }
            
            # Convert to CSV string
            csv_data = ",".join(forecast_data.keys()) + "\n" + ",".join([str(v) for v in forecast_data.values()])
            
            st.download_button(
                label="Download Compliance Forecast",
                data=csv_data,
                file_name=f"compliance_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.button("Download Compliance Forecast", disabled=True, use_container_width=True)
