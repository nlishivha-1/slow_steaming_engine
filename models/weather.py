import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class WeatherData:
    """
    Class to represent weather and ocean conditions for route optimization
    """
    
    def __init__(self, data=None):
        """
        Initialize weather data for a route
        
        Args:
            data: Dictionary containing weather data or None to create empty data
        """
        if data is None:
            self.has_data = False
            self.data = {}
            self.winds = pd.DataFrame()
            self.currents = pd.DataFrame()
            self.waves = pd.DataFrame()
        else:
            self.has_data = True
            self.data = data
            self.process_data()
    
    def process_data(self):
        """
        Process raw weather data into structured formats
        """
        # Process wind data if available
        if 'winds' in self.data:
            self.winds = pd.DataFrame(self.data['winds'])
        else:
            self.winds = pd.DataFrame()
        
        # Process current data if available
        if 'currents' in self.data:
            self.currents = pd.DataFrame(self.data['currents'])
        else:
            self.currents = pd.DataFrame()
        
        # Process wave data if available
        if 'waves' in self.data:
            self.waves = pd.DataFrame(self.data['waves'])
        else:
            self.waves = pd.DataFrame()
    
    def generate_synthetic_data(self, route_data, start_date=None, days=7):
        """
        Generate synthetic weather data for demonstration purposes
        
        Args:
            route_data: Dictionary containing route information
            start_date: Start date for weather data or None for current date
            days: Number of days to generate data for
        """
        if start_date is None:
            start_date = datetime.now()
        
        waypoints = route_data.get('waypoints', [])
        if not waypoints:
            self.has_data = False
            return
        
        # Generate hourly timestamps
        timestamps = []
        for i in range(days * 24):
            timestamps.append((start_date + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'))
        
        # Generate synthetic wind data
        winds = []
        for wp in waypoints:
            for ts in timestamps:
                # Random wind speed between 5-25 knots
                speed = np.random.uniform(5, 25)
                # Random wind direction
                direction = np.random.uniform(0, 360)
                winds.append({
                    'timestamp': ts,
                    'lat': wp['lat'],
                    'lon': wp['lon'],
                    'speed': speed,
                    'direction': direction
                })
        
        # Generate synthetic current data
        currents = []
        for wp in waypoints:
            for ts in timestamps:
                # Random current speed between 0-3 knots
                speed = np.random.uniform(0, 3)
                # Random current direction
                direction = np.random.uniform(0, 360)
                currents.append({
                    'timestamp': ts,
                    'lat': wp['lat'],
                    'lon': wp['lon'],
                    'speed': speed,
                    'direction': direction
                })
        
        # Generate synthetic wave data
        waves = []
        for wp in waypoints:
            for ts in timestamps:
                # Random wave height between 0-5 meters
                height = np.random.uniform(0, 5)
                # Random wave period between 5-15 seconds
                period = np.random.uniform(5, 15)
                # Random wave direction
                direction = np.random.uniform(0, 360)
                waves.append({
                    'timestamp': ts,
                    'lat': wp['lat'],
                    'lon': wp['lon'],
                    'height': height,
                    'period': period,
                    'direction': direction
                })
        
        # Store the data
        self.data = {
            'winds': winds,
            'currents': currents,
            'waves': waves
        }
        
        # Process the data into dataframes
        self.process_data()
        self.has_data = True
    
    def get_average_conditions(self):
        """
        Calculate average weather conditions across the dataset
        
        Returns:
            dict: Dictionary of average conditions
        """
        if not self.has_data:
            return {
                'avg_wind_speed': None,
                'avg_current_speed': None,
                'avg_wave_height': None
            }
        
        avg_wind_speed = self.winds['speed'].mean() if not self.winds.empty else None
        avg_current_speed = self.currents['speed'].mean() if not self.currents.empty else None
        avg_wave_height = self.waves['height'].mean() if not self.waves.empty else None
        
        return {
            'avg_wind_speed': avg_wind_speed,
            'avg_current_speed': avg_current_speed,
            'avg_wave_height': avg_wave_height
        }
    
    def get_weather_impact(self, route_data):
        """
        Estimate the impact of weather conditions on voyage
        
        Args:
            route_data: Dictionary containing route information
        
        Returns:
            dict: Dictionary with weather impact factors
        """
        if not self.has_data:
            return {
                'speed_reduction': 0,
                'fuel_increase': 0,
                'high_risk_areas': []
            }
        
        # Calculate average conditions
        avg_conditions = self.get_average_conditions()
        
        # Simplified model for speed reduction due to weather
        # Based on Beaufort scale and general maritime practices
        avg_wind = avg_conditions['avg_wind_speed'] or 0
        avg_wave = avg_conditions['avg_wave_height'] or 0
        
        # Speed reduction based on wind and waves
        # Each knot of wind above 15 reduces speed by 0.5%
        # Each meter of wave height above 2m reduces speed by 3%
        wind_reduction = max(0, (avg_wind - 15) * 0.5) if avg_wind else 0
        wave_reduction = max(0, (avg_wave - 2) * 3) if avg_wave else 0
        
        speed_reduction = min(30, wind_reduction + wave_reduction)  # Cap at 30%
        
        # Fuel increase is typically higher than speed reduction
        fuel_increase = speed_reduction * 1.5
        
        # Identify high risk areas (simplified)
        high_risk_areas = []
        if not self.waves.empty:
            # Areas with wave height > 4m are considered high risk
            high_waves = self.waves[self.waves['height'] > 4]
            if not high_waves.empty:
                for _, row in high_waves.head(5).iterrows():
                    high_risk_areas.append({
                        'lat': row['lat'],
                        'lon': row['lon'],
                        'wave_height': row['height'],
                        'timestamp': row['timestamp']
                    })
        
        return {
            'speed_reduction': speed_reduction,
            'fuel_increase': fuel_increase,
            'high_risk_areas': high_risk_areas
        }
    
    def to_dict(self):
        """
        Convert weather data object to dictionary for serialization
        
        Returns:
            dict: Weather data as dictionary
        """
        return {
            'has_data': self.has_data,
            'data': self.data,
            'average_conditions': self.get_average_conditions()
        }
