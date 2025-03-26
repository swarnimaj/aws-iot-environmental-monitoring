# AWS IoT Environmental Monitoring System

This project implements a cloud-based IoT system that collects environmental data from virtual sensors using MQTT and AWS IoT Core.

## Features

- Virtual environmental stations generating random sensor data:
  - Temperature (-50 to 50 Celsius)
  - Humidity (0 to 100%)
  - CO2 (300ppm to 2000ppm)
- Secure MQTT communication with AWS IoT Core
- Automatic data storage in DynamoDB
- Web dashboard for data visualization:
  - Latest sensor readings for any station
  - Historical data (last 5 hours) for any sensor type

## Prerequisites

- Python 3.8 or higher
- AWS account with access to IoT Core and DynamoDB
- AWS CLI configured with appropriate credentials

## Installation

1. Clone this repository:
git clone http://github.com/swarnimaj/aws-iot-environmental-monitoring
cd aws-iot-environmental-monitoring

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate                         # On Windows: venv\Scripts\activate

3. Install required packages:
pip3 install -r requirements.txt

4. Set up AWS IoT Core:
- Create an IoT "thing" in the AWS IoT Core console
- Create and download certificates
- Create a policy with the following permissions:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "iot:Connect",
        "Resource": "arn:aws:iot:*:*:client/*"
      },
      {
        "Effect": "Allow",
        "Action": "iot:Publish",
        "Resource": "arn:aws:iot:*:*:topic/sensors/*"
      },
      {
        "Effect": "Allow",
        "Action": "iot:Subscribe",
        "Resource": "arn:aws:iot:*:*:topicfilter/sensors/*"
      },
      {
        "Effect": "Allow",
        "Action": "iot:Receive",
        "Resource": "arn:aws:iot:*:*:topic/sensors/*"
      }
    ]
  }
  ```
- Attach the policy to certificates

5. Create a DynamoDB table:
- Table name: `EnvironmentalData`
- Partition key: `station_id` (String)
- Sort key: `timestamp` (String)

6. Create an AWS IoT rule to store data in DynamoDB:
- Rule query statement: `SELECT * FROM 'sensors/#'`
- Action: Store message in DynamoDB table
- Configure with your table name and role with appropriate permissions

7. Place the certificates in a `certificates` directory:
- `certificates/AmazonRootCA1.pem`
- `certificates/certificate.pem.crt`
- `certificates/private.pem.key`

8. Create a `config.py` file with AWS IoT endpoint and region:
```python
# AWS IoT Core configuration
IOT_ENDPOINT = "your-iot-endpoint.iot.region.amazonaws.com"
ROOT_CA_PATH = "certificates/AmazonRootCA1.pem"
PRIVATE_KEY_PATH = "certificates/private.pem.key"
CERTIFICATE_PATH = "certificates/certificate.pem.crt"

# MQTT Topic configuration
TOPIC_BASE = "sensors"

# DynamoDB configuration
DYNAMODB_TABLE = "EnvironmentalData"
AWS_REGION = "your-aws-region"

# Sensor configuration
SENSOR_INTERVAL = 30

## Usage ------------------------------------------------------------------------------------------------

1. Start the virtual environmental station: python3 mqtt_publisher.py --station-id YourStationName (EnvironmentalStation1 in my case)

2. In a separate terminal, start the web dashboard: python3 app.py

3. Open a web browser and navigate to http://localhost:5000

Use the dashboard to:
- View latest sensor data by selecting a station and clicking "Get Latest Data"
- View historical data by selecting a sensor type and clicking "Get History"

To run multiple stations, open additional terminals and run the publisher with different station IDs.
