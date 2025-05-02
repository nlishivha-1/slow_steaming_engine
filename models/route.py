class Route:
    """
    Class to represent a shipping route with waypoints and characteristics
    """
    
    def __init__(self, data):
        """
        Initialize a route with data
        
        Args:
            data: Dictionary containing route information
        """
        self.name = data.get('name', 'Unknown Route')
        self.distance = data.get('distance', 0)  # nautical miles
        self.waypoints = data.get('waypoints', [])
        
        # Calculate additional derived parameters
        self.calculate_derived_parameters()
    
    def calculate_derived_parameters(self):
        """
        Calculate derived parameters based on route information
        """
        # Count number of waypoints
        self.number_of_waypoints = len(self.waypoints)
        
        # Calculate average leg distance if there are waypoints
        if self.number_of_waypoints > 1:
            self.avg_leg_distance = self.distance / (self.number_of_waypoints - 1)
        else:
            self.avg_leg_distance = 0
    
    def get_transit_time(self, speed):
        """
        Calculate transit time for a given speed
        
        Args:
            speed: Speed in knots
        
        Returns:
            float: Transit time in days
        """
        if speed <= 0:
            return float('inf')
        return self.distance / (speed * 24)
    
    def get_waypoint_coordinates(self):
        """
        Get list of waypoint coordinates for mapping
        
        Returns:
            list: List of [lat, lon] coordinates
        """
        return [[wp['lat'], wp['lon']] for wp in self.waypoints]
    
    def get_origin_destination(self):
        """
        Get origin and destination waypoints
        
        Returns:
            tuple: (origin, destination) dictionaries
        """
        if len(self.waypoints) < 2:
            return None, None
        
        return self.waypoints[0], self.waypoints[-1]
    
    def to_dict(self):
        """
        Convert route object to dictionary for serialization
        
        Returns:
            dict: Route data as dictionary
        """
        return {
            'name': self.name,
            'distance': self.distance,
            'waypoints': self.waypoints,
            'number_of_waypoints': self.number_of_waypoints,
            'avg_leg_distance': self.avg_leg_distance
        }
