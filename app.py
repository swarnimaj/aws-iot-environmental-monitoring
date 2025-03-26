# app.py
from flask import Flask, render_template, jsonify, request
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json
from datetime import datetime, timedelta
import config

# Initialize Flask application
app = Flask(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=config.AWS_REGION)
table = dynamodb.Table(config.DYNAMODB_TABLE)

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle Decimal values from DynamoDB.
    DynamoDB returns numbers as Decimal objects, which are not JSON serializable.
    This encoder converts them to floats.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/stations')
def get_stations():
    """
    Get a list of all station IDs from the database.
    Returns:
        JSON: List of unique station IDs
    """
    # Scan the DynamoDB table to get all station IDs
    response = table.scan(ProjectionExpression="station_id")
    
    # Extract unique station IDs from the response
    stations = {item['station_id'] for item in response['Items']}
    
    # Handle pagination for large datasets
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression="station_id",
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        stations.update({item['station_id'] for item in response['Items']})
    
    return jsonify(list(stations))

@app.route('/api/latest/<station_id>')
def get_latest_data(station_id):
    """
    Get the latest data for a specific station.
    Args:
        station_id (str): ID of the station to get data for
    Returns:
        JSON: Latest sensor readings for the specified station
    """
    # Query the DynamoDB table for the latest record for this station
    response = table.query(
        KeyConditionExpression=Key('station_id').eq(station_id),
        ScanIndexForward=False,  # Sort in descending order (newest first)
        Limit=1  # Only get the most recent record
    )
    
    # Check if any data was found
    if not response['Items']:
        return jsonify({"error": "No data found for this station"})
    
    # Return the latest data, handling Decimal values
    return json.dumps(response['Items'][0], cls=DecimalEncoder)

@app.route('/api/history/<sensor_type>')
def get_sensor_history(sensor_type):
    """
    Get historical data for a specific sensor type from all stations.
    Args:
        sensor_type (str): Type of sensor (temperature, humidity, or co2)
    Returns:
        JSON: Sensor readings from the last 5 hours for all stations
    """
    # Calculate the timestamp from 5 hours ago
    five_hours_ago = (datetime.now() - timedelta(hours=5)).isoformat()
    
    # Get list of all stations
    stations_response = table.scan(ProjectionExpression="station_id")
    stations = {item['station_id'] for item in stations_response['Items']}
    
    # Handle pagination for large datasets
    while 'LastEvaluatedKey' in stations_response:
        stations_response = table.scan(
            ProjectionExpression="station_id",
            ExclusiveStartKey=stations_response['LastEvaluatedKey']
        )
        stations.update({item['station_id'] for item in stations_response['Items']})
    
    result = {}
    
    # Query data for each station
    for station_id in stations:
        # Query DynamoDB for records from this station in the last 5 hours
        response = table.query(
            KeyConditionExpression=
                Key('station_id').eq(station_id) & 
                Key('timestamp').gt(five_hours_ago)
        )
        
        station_data = []
        # Extract the relevant sensor data from each record
        for item in response['Items']:
            if 'readings' in item and sensor_type in item['readings']:
                station_data.append({
                    'timestamp': item['timestamp'],
                    'value': item['readings'][sensor_type]['value'],
                    'unit': item['readings'][sensor_type]['unit']
                })
        
        # Only include stations that have data for this sensor
        if station_data:
            result[station_id] = station_data
    
    # Return the historical data, handling Decimal values
    return json.dumps(result, cls=DecimalEncoder)

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)