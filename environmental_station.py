import random
import uuid
from datetime import datetime

class EnvironmentalStation:
    """
    A virtual environmental station that generates random sensor data.
    This class simulates an IoT device that collects environmental data
    from multiple sensors (temperature, humidity, CO2).
    """
    
    def __init__(self, station_id=None):
        """
        Initialize a new environmental station.
        station_id (str, optional): Unique identifier for this station. If not provided, a random UUID will be generated.
        """
        # If no station ID is provided, generate a random one
        self.station_id = station_id if station_id else f"station-{uuid.uuid4().hex[:8]}"
        
        # Define the sensors with their range limits and units
        self.sensors = {
            "temperature": {"min": -50, "max": 50, "unit": "Celsius"},
            "humidity": {"min": 0, "max": 100, "unit": "%"},
            "co2": {"min": 300, "max": 2000, "unit": "ppm"}
        }
    
    def generate_sensor_data(self):
        """
        Generate random sensor readings for all sensors.
        Returns:
            dict: A dictionary containing the station ID, timestamp,
                  and readings from all sensors.
        """
        # Create the base data structure with station ID and current timestamp
        data = {
            "station_id": self.station_id,
            "timestamp": datetime.now().isoformat(),  # ISO format timestamp
            "readings": {}
        }
        
        # Generate a random value for each sensor within its defined range
        for sensor_name, sensor_info in self.sensors.items():
            # Generate a random value between min and max
            value = random.uniform(sensor_info["min"], sensor_info["max"])
            
            # Add the sensor reading to the data structure
            data["readings"][sensor_name] = {
                "value": round(value, 2),  # Round to 2 decimal places
                "unit": sensor_info["unit"]  # Include the unit of measurement
            }
        
        return data