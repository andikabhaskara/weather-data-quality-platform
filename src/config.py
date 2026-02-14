"""Configuration settings for weather data ingestion"""
from dataclasses import dataclass
import os

#Api Configuration
API_URL = "https://archive-api.open-meteo.com/v1/archive"
TIMEOUT_IN_SECONDS = 10
MAX_RETRIES = 3
DELAY_BETWEEN_CITIES = 1

#Data Configuration
HISTORY_DAYS = 30
HOURLY_METRICS = [
    'temperature_2m',
    'relative_humidity_2m',
    'weather_code',
    'wind_speed_10m',
    'precipitation'
]

#City Configuration
@dataclass
class City:
  name: str
  latitude: float
  longitude: float
  country: str

CITIES = [
    City("New York", 40.7128, -74.0060, "USA"),
    City("Singapore", 1.3048, 103.8312, "Singapore"),
    City("Tokyo", 35.6815, 139.7671, "Japan")
]

# Storage Configuration
IS_LAMBDA = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None

if IS_LAMBDA:
  #Lambda environment
  RAW_DATA_PATH = "/tmp/data/raw"
  LOG_PATH = ".tmp/logs"
else:
  #Local environment
  RAW_DATA_PATH = "data/raw"
  LOG_PATH = "logs"