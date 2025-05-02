class Vessel:
    """
    Class to represent a vessel with its specifications and performance characteristics
    """
    
    def __init__(self, data):
        """
        Initialize a vessel with specification data
        
        Args:
            data: Dictionary containing vessel specifications
        """
        self.name = data.get('name', 'Unknown Vessel')
        self.type = data.get('type', 'Container Ship')
        self.length = data.get('length', 300)  # meters
        self.beam = data.get('beam', 40)  # meters
        self.draft = data.get('draft', 14.5)  # meters
        self.deadweight = data.get('deadweight', 100000)  # tons
        self.engine_type = data.get('engine_type', 'Unknown')
        self.max_speed = data.get('max_speed', 25)  # knots
        self.max_power = data.get('max_power', 68000)  # kW
        self.design_speed = data.get('design_speed', 20)  # knots
        self.design_consumption = data.get('design_consumption', 180)  # tons/day
        self.year_built = data.get('year_built', 2010)
        
        # Calculate additional derived parameters
        self.calculate_derived_parameters()
    
    def calculate_derived_parameters(self):
        """
        Calculate derived parameters based on vessel specifications
        """
        # Calculate specific fuel consumption (g/kWh)
        # Simplified formula, would typically be based on engine type and year
        if self.year_built >= 2015:
            self.specific_fuel_consumption = 175  # g/kWh for newer engines
        elif self.year_built >= 2000:
            self.specific_fuel_consumption = 185  # g/kWh for modern engines
        else:
            self.specific_fuel_consumption = 195  # g/kWh for older engines
        
        # Calculate optimal engine load range (% of MCR)
        self.optimal_load_min = 70
        self.optimal_load_max = 85
        
        # Calculate speed at optimal load range
        self.optimal_speed_min = self.design_speed * (self.optimal_load_min/100)**(1/3)
        self.optimal_speed_max = self.design_speed * (self.optimal_load_max/100)**(1/3)
    
    def get_fuel_consumption(self, speed):
        """
        Calculate fuel consumption for a given speed
        
        Args:
            speed: Speed in knots
        
        Returns:
            float: Fuel consumption in tons per day
        """
        # Using the cubic relationship between speed and fuel consumption
        return self.design_consumption * (speed / self.design_speed) ** 3
    
    def get_engine_load(self, speed):
        """
        Calculate engine load for a given speed
        
        Args:
            speed: Speed in knots
        
        Returns:
            float: Engine load as percentage of maximum continuous rating (MCR)
        """
        # Simplified relationship between speed and engine load
        return 100 * (speed / self.max_speed) ** 3
    
    def is_speed_in_optimal_range(self, speed):
        """
        Check if a given speed is within the optimal engine load range
        
        Args:
            speed: Speed in knots
        
        Returns:
            bool: True if speed is within optimal range, False otherwise
        """
        load = self.get_engine_load(speed)
        return self.optimal_load_min <= load <= self.optimal_load_max
    
    def to_dict(self):
        """
        Convert vessel object to dictionary for serialization
        
        Returns:
            dict: Vessel data as dictionary
        """
        return {
            'name': self.name,
            'type': self.type,
            'length': self.length,
            'beam': self.beam,
            'draft': self.draft,
            'deadweight': self.deadweight,
            'engine_type': self.engine_type,
            'max_speed': self.max_speed,
            'max_power': self.max_power,
            'design_speed': self.design_speed,
            'design_consumption': self.design_consumption,
            'year_built': self.year_built,
            'specific_fuel_consumption': self.specific_fuel_consumption,
            'optimal_load_min': self.optimal_load_min,
            'optimal_load_max': self.optimal_load_max,
            'optimal_speed_min': self.optimal_speed_min,
            'optimal_speed_max': self.optimal_speed_max
        }
