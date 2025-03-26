# mqtt_publisher.py
import json
import time
import logging
import ssl
import paho.mqtt.client as mqtt
from environmental_station import EnvironmentalStation
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTPublisher:
    """
    Publishes sensor data to AWS IoT Core using MQTT protocol.
    
    This class handles the secure connection to AWS IoT Core and
    publishes messages to MQTT topics.
    """
    
    def __init__(self, client_id, endpoint, root_ca_path, private_key_path, certificate_path):
        """
        Initialize the MQTT publisher.
        
        Args:
            client_id (str): Unique identifier for this MQTT client
            endpoint (str): AWS IoT endpoint
            root_ca_path (str): Path to Amazon Root CA certificate
            private_key_path (str): Path to private key file
            certificate_path (str): Path to certificate file
        """
        # Create an MQTT client
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        
        # Configure TLS/SSL
        self.client.tls_set(
            ca_certs=root_ca_path,
            certfile=certificate_path,
            keyfile=private_key_path,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        
        # Set the endpoint and port
        self.endpoint = endpoint
        self.port = 8883  # Standard MQTT TLS port
        
        # Store connection status
        self.connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client connects to the broker."""
        if rc == 0:
            self.connected = True
            logger.info("Connected to AWS IoT Core")
        else:
            logger.error(f"Failed to connect to AWS IoT Core with result code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from AWS IoT Core with result code {rc}")
        else:
            logger.info("Disconnected from AWS IoT Core")
    
    def connect(self):
        """
        Connect to AWS IoT Core.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            # Connect to the MQTT broker
            self.client.connect(self.endpoint, self.port, 60)
            
            # Start the MQTT loop in a background thread
            self.client.loop_start()
            
            # Wait for connection to be established
            timeout = 5  # seconds
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
                
            return self.connected
        except Exception as e:
            # Log any connection errors
            logger.error(f"Failed to connect to AWS IoT Core: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from AWS IoT Core."""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish(self, topic, message):
        """
        Publish a message to an MQTT topic.
        
        Args:
            topic (str): The MQTT topic to publish to
            message (dict): The message to publish (will be converted to JSON)
            
        Returns:
            bool: True if publish was successful, False otherwise
        """
        try:
            # Convert the message to JSON
            json_message = json.dumps(message)
            
            # Publish the message with QoS 1
            result = self.client.publish(topic, json_message, qos=1)
            
            # Wait for the message to be published
            result.wait_for_publish()
            
            # Check if the publish was successful
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
            else:
                logger.error(f"Failed to publish message: result code {result.rc}")
                return False
        except Exception as e:
            # Log any publishing errors
            logger.error(f"Failed to publish message: {e}")
            return False

def run_station(station_id=None, interval=config.SENSOR_INTERVAL):
    """
    Run a virtual environmental station and publish its data to AWS IoT Core.
    
    Args:
        station_id (str, optional): ID for the station. If None, a random ID will be generated.
        interval (int, optional): Time between sensor readings in seconds.
    """
    # Create a virtual environmental station
    station = EnvironmentalStation(station_id)
    logger.info(f"Starting environmental station with ID: {station.station_id}")
    
    # Create an MQTT publisher with the station ID as the client ID
    publisher = MQTTPublisher(
        client_id=station.station_id,
        endpoint=config.IOT_ENDPOINT,
        root_ca_path=config.ROOT_CA_PATH,
        private_key_path=config.PRIVATE_KEY_PATH,
        certificate_path=config.CERTIFICATE_PATH
    )
    
    # Connect to AWS IoT Core
    if publisher.connect():
        logger.info("Connected to AWS IoT Core")
    else:
        logger.error("Failed to connect to AWS IoT Core. Exiting.")
        return
    
    try:
        # Continuously generate and publish sensor data
        while True:
            # Generate random sensor data
            sensor_data = station.generate_sensor_data()
            
            # Create the full MQTT topic
            topic = f"{config.TOPIC_BASE}/{station.station_id}"
            
            # Log the data being published
            logger.info(f"Publishing to {topic}: {json.dumps(sensor_data)}")
            
            # Publish the data
            if publisher.publish(topic, sensor_data):
                logger.info("Published successfully")
            else:
                logger.warning("Failed to publish message")
            
            # Wait for the specified interval before next reading
            time.sleep(interval)
            
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        logger.info("Stopping data publication")
        publisher.disconnect()
    except Exception as e:
        # Handle any other exceptions
        logger.error(f"Error in run_station: {e}")
        publisher.disconnect()

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run a virtual environmental station')
    parser.add_argument('--station-id', help='Station ID (default: auto-generated)')
    parser.add_argument('--interval', type=int, default=config.SENSOR_INTERVAL,
                        help=f'Time between readings in seconds (default: {config.SENSOR_INTERVAL})')
    
    args = parser.parse_args()
    
    # Run the station with the provided arguments
    run_station(args.station_id, args.interval)