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