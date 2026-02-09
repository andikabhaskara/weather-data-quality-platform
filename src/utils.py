"""Helper functions for data ingestion"""
import logging
import time
import requests as rq
from datetime import datetime, timedelta
from typing import Tuple
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

def get_date_range(days: int = 30) -> Tuple[str, str]:
  """
  Calculate date range in historical data
  Args:
    days: Numbers of days from yesterday
  Returns:
    (start_date, end_date) in YYYY-MM-DD format
  """
  end_date = datetime.now().date() - timedelta(days=1)
  start_date = end_date - timedelta(days=days)
  return start_date.isoformat(), end_date.isoformat()

def fetch_api_with_retry(url:str , params: dict, max_retries: int = 3, timeout: int = 5) -> dict | None:
  """
  Fetch data weather api with retries

  Returns:
    dict: API response when sucessful
    None: if all retries fail
  """
  for attempt in range(1, max_retries + 1):
    try:
      response = rq.get(url, params=params, timeout=timeout)
      response.raise_for_status()
      return response.json()
    except RequestException as e:
      logger.info(f"Retries {attempt/max_retries} failed: " + {e})

      if attempt < max_retries:
        wait_time = 2 ** attempt
        logger.info(f"   Retrying in {wait_time} seconds...")
        time.sleep(wait_time)
      else:

        logger.critical(f"❌ All retries failed for {params.get('latitude', 'unknown')}")
        return None
  return None