import streamlit as st
import pandas as pd
import json
from models.vessel import Vessel
from utils.data_processing import load_sample_vessel_data, prepare_vessel_data

def app():
    """
    Vessel Input page for entering vessel specifications
    """
    st.title("Vessel Specifications Input")
    
    st.markdown("""
    Enter the vessel specifications to be used for slow steaming optimization. 
    You can either enter the details manually, upload a data file, or use sample data.
    """)
    
    # Initialize session state
    if 'vessel_data' not in st.session_state:
        st.session_state.vessel_data = None
    
    # Data input options
    input_method = st.radio(
        "Choose input method:",
        ["Manual Entry", "Upload File", "Use Sample Data"]
    )
    
    if input_method == "Manual Entry":
        col1, col2 = st.columns(2)
        
        with col1:
            vessel_name = st.text_input("Vessel Name", "Example Vessel")
            vessel_type = st.selectbox(
                "Vessel Type",
                ["Container Ship", "Bulk Carrier", "Oil Tanker", "Gas Carrier", "General Cargo"]
            )
            length = st.number_input("Length (m)", min_value=50, max_value=500, value=300)
            beam = st.number_input("Beam (m)", min_value=10, max_value=100, value=40)
            draft = st.number_input("Draft (m)", min_value=5.0, max_value=30.0, value=14.5)
        
        with col2:
            deadweight = st.number_input("Deadweight (tons)", min_value=1000, max_value=500000, value=100000)
            engine_type = st.text_input("Engine Type", "MAN B&W 12K98ME-C")
            max_speed = st.number_input("Maximum Speed (knots)", min_value=10, max_value=35, value=25)
            design_speed = st.number_input("Design Speed (knots)", min_value=10, max_value=30, value=20)
            design_consumption = st.number_input("Design Fuel Consumption (tons/day)", min_value=10, max_value=500, value=180)
            year_built = st.number_input("Year Built", min_value=1970, max_value=2023, value=2010)
        
        if st.button("Save Vessel Data", use_container_width=True):
            vessel_data = {
                "name": vessel_name,
                "type": vessel_type,
                "length": length,
                "beam": beam,
                "draft": draft,
                "deadweight": deadweight,
                "engine_type": engine_type,
                "max_speed": max_speed,
                "design_speed": design_speed,
                "design_consumption": design_consumption,
                "year_built": year_built
            }
            
            vessel_obj = Vessel(vessel_data)
            st.session_state.vessel_data = vessel_obj.to_dict()
            st.success("Vessel data saved successfully!")
    
    elif input_method == "Upload File":
        st.markdown("""
        Upload a file containing vessel specifications. The file should be in one of the following formats:
        - CSV: with column headers matching the vessel parameters
        - Excel: with column headers matching the vessel parameters
        - JSON: structured with vessel parameters
        """)
        
        uploaded_file = st.file_uploader("Upload vessel data file", type=["csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            try:
                vessel_data_dict = prepare_vessel_data(uploaded_file)
                if vessel_data_dict and 'vessels' in vessel_data_dict and len(vessel_data_dict['vessels']) > 0:
                    st.write("Available vessels in the file:")
                    vessels = vessel_data_dict['vessels']
                    vessel_names = [v.get('name', f"Vessel {i+1}") for i, v in enumerate(vessels)]
                    selected_vessel = st.selectbox("Select a vessel", vessel_names)
                    
                    # Find the selected vessel in the data
                    selected_vessel_data = next((v for v in vessels if v.get('name') == selected_vessel), vessels[0])
                    
                    # Create Vessel object and save to session state
                    vessel_obj = Vessel(selected_vessel_data)
                    st.session_state.vessel_data = vessel_obj.to_dict()
                    
                    st.success("Vessel data loaded successfully!")
                    
                    # Display the loaded data
                    with st.expander("View loaded vessel data"):
                        st.json(selected_vessel_data)
                else:
                    st.error("No vessel data found in the uploaded file.")
            
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    elif input_method == "Use Sample Data":
        sample_data = load_sample_vessel_data()
        
        if sample_data and 'vessels' in sample_data:
            st.write("Available sample vessels:")
            vessel_names = [v.get('name', f"Vessel {i+1}") for i, v in enumerate(sample_data['vessels'])]
            selected_vessel = st.selectbox("Select a vessel", vessel_names)
            
            # Find the selected vessel in the data
            selected_vessel_data = next((v for v in sample_data['vessels'] if v.get('name') == selected_vessel), sample_data['vessels'][0])
            
            if st.button("Use Selected Sample Data", use_container_width=True):
                # Create Vessel object and save to session state
                vessel_obj = Vessel(selected_vessel_data)
                st.session_state.vessel_data = vessel_obj.to_dict()
                st.success("Sample vessel data loaded successfully!")
                
                # Display the loaded data
                with st.expander("View loaded vessel data"):
                    st.json(selected_vessel_data)
    
    # Display current vessel data if available
    if st.session_state.vessel_data is not None:
        st.header("Current Vessel Specifications")
        
        # Create two columns for display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            st.write(f"**Name:** {st.session_state.vessel_data.get('name', 'N/A')}")
            st.write(f"**Type:** {st.session_state.vessel_data.get('type', 'N/A')}")
            st.write(f"**Dimensions:** {st.session_state.vessel_data.get('length', 'N/A')}m × {st.session_state.vessel_data.get('beam', 'N/A')}m × {st.session_state.vessel_data.get('draft', 'N/A')}m")
            st.write(f"**Deadweight:** {st.session_state.vessel_data.get('deadweight', 'N/A')} tons")
            st.write(f"**Year Built:** {st.session_state.vessel_data.get('year_built', 'N/A')}")
        
        with col2:
            st.subheader("Performance Parameters")
            st.write(f"**Engine Type:** {st.session_state.vessel_data.get('engine_type', 'N/A')}")
            st.write(f"**Max Speed:** {st.session_state.vessel_data.get('max_speed', 'N/A')} knots")
            st.write(f"**Design Speed:** {st.session_state.vessel_data.get('design_speed', 'N/A')} knots")
            st.write(f"**Design Consumption:** {st.session_state.vessel_data.get('design_consumption', 'N/A')} tons/day")
            
            # Display derived parameters
            st.write(f"**Optimal Speed Range:** {st.session_state.vessel_data.get('optimal_speed_min', 'N/A'):.2f} - {st.session_state.vessel_data.get('optimal_speed_max', 'N/A'):.2f} knots")
            st.write(f"**Optimal Engine Load:** {st.session_state.vessel_data.get('optimal_load_min', 'N/A')}% - {st.session_state.vessel_data.get('optimal_load_max', 'N/A')}%")
        
        # Allow clearing the data
        if st.button("Clear Vessel Data", use_container_width=True):
            st.session_state.vessel_data = None
            st.success("Vessel data cleared!")
            st.rerun()
    else:
        st.info("No vessel data available. Please enter or load vessel specifications.")
