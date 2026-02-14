"""Main weather data ingestion pipeline"""
import logging
import json
import os
import time
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError

from config import (
    API_URL, TIMEOUT_IN_SECONDS, MAX_RETRIES, DELAY_BETWEEN_CITIES,
    CITIES, HISTORY_DAYS, HOURLY_METRICS, RAW_DATA_PATH, LOG_PATH, City, IS_LAMBDA
)
from models import WeatherAPIResponse
from utils import get_date_range, fetch_api_with_retry

if IS_LAMBDA:
    # Lambda: Log to CloudWatch, no file logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
else:
    # Local: create logs directory and log to file
    Path(LOG_PATH).mkdir(exist_ok=True)
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_PATH}/ingestion_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ])
    
logger = logging.getLogger(__name__)

# Function to validate data contract
def validate_data(raw_json: dict, city: City) -> WeatherAPIResponse | None:
    """
    Validate API response against data contract using Pydantic.

    Args:
        raw_json: Raw API response dictionary
        city: City object for logging context

    Returns:
        WeatherAPIResponse: Validated data model if successful
        None: If validation fails
    """
    try:
        # Pydantic handles the nested 'hourly' dict automatically
        model = WeatherAPIResponse(**raw_json)

        # Accessing data is now type-safe
        logger.info(f"✅ Validated {len(model.hourly.time)} data points for {city.name}")
        return model

    except ValidationError as e:
        logger.error(f"❌ Data contract violation for {city.name}!")
        logger.error(f"   Validation errors: {e.errors()}")

        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error['loc'])
            logger.error(f"   Field '{field}': {error['msg']}")

        return None


# Function to save raw data
def save_raw_data(city: City, data: dict, timestamp: datetime) -> str:
  """
  Save raw API response to S3 (when on Lambda) or local (when testing).
  
  Returns:
    str: File path where data was saved

  File structure: data/raw/year=2026/month=02/day=01/newyork_20260201_120000.json
  """
  # Detect if running on Lambda
  is_lambda = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
  
  # Create directory structure
  date_str = timestamp.strftime("%Y%m%d")
  time_str = timestamp.strftime("%H%M%S")

  if is_lambda:
    #Lambda: save to /tmp first, then upload to S3
    import boto3

    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        raise ValueError("S3_BUCKET_NAME environment variable is not set")
    s3_client = boto3.client('s3')

    #S3 key (path)
    s3_key = f"raw/year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}/{city.name.lower()}_{date_str}_{time_str}.json"

    output = {
        "ingested_at": timestamp.isoformat(),
        "city": city.name,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "country": city.country,
        "raw_response": data
    }

    #Upload to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps(output, indent=2),
        ContentType='application/json'
    )

    logger.info(f"✅ Saved to S3: s3://{bucket_name}/{s3_key}")
    return f"s3://{bucket_name}/{s3_key}"
  
  else:
    #local: save to data/raw/
    output_dir = Path(f"{RAW_DATA_PATH}/year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}")
    output_dir.mkdir(parents=True, exist_ok=True)

    city_name = city.name.lower().replace(" ", "")
    filename = f"{city_name}_{date_str}_{time_str}.json"
    filepath = output_dir / filename

    output = {
        "ingested_at": timestamp.isoformat(),
        "city": city.name,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "country": city.country,
        "raw_response": data
    }

    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"✅ Saved locally to {filepath}")
    return str(filepath)
  

# Main pipeline orchestration
def main():
    """Main pipeline orchestration"""
    logger.info("=" * 50)
    logger.info("Starting weather data ingestion pipeline")
    logger.info("=" * 50)

    start_date, end_date = get_date_range(HISTORY_DAYS)
    logger.info(f"Date range: {start_date} to {end_date}")

    ingestion_timestamp = datetime.now()
    success_count = 0
    failure_count = 0

    for city in CITIES:
        logger.info(f"\n📍 Processing {city.name}, {city.country}")

        # Build API params
        params = {
            'latitude': city.latitude,
            'longitude': city.longitude,
            'start_date': start_date,
            'end_date': end_date,
            'hourly': HOURLY_METRICS,
            'timezone': 'GMT'
        }

        # Fetch data with retry
        raw_data = fetch_api_with_retry(API_URL, params, MAX_RETRIES, TIMEOUT_IN_SECONDS)

        if raw_data is None:
            logger.error(f"Skipping {city.name} - all retries failed")
            failure_count += 1
            continue

        # Validate against data contract
        validated = validate_data(raw_data, city)

        if validated is None:
            logger.error(f"Skipping {city.name} - validation failed")
            failure_count += 1
            continue

        # Save raw data
        save_raw_data(city, raw_data, ingestion_timestamp)
        success_count += 1

        # Rate limiting
        if city != CITIES[-1]:
            time.sleep(DELAY_BETWEEN_CITIES)

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Pipeline Summary")
    logger.info("=" * 50)
    logger.info(f"✅ Successful: {success_count}/{len(CITIES)}")
    print(f"✅ Successful: {success_count}/{len(CITIES)}")
    logger.info(f"❌ Failed: {failure_count}/{len(CITIES)}")
    logger.info(f"📊 Total records: {success_count * 30 * 24} (expected: {len(CITIES) * 30 * 24})")
    print(f"📊 Total records: {success_count * 30 * 24} (expected: {len(CITIES) * 30 * 24})")

    if failure_count > 0:
        logger.warning("Some cities failed - check logs for details")
    
    return {
        'success_count': success_count,
        'failure_count': failure_count,
        'total_records': success_count * 30 * 24,
        'cities_processed': [city.name for city in CITIES]
    }

if __name__ == "__main__":
    main()