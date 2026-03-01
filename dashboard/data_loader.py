"""
Data loading layer for the Weather Dashboard.

- Separates data access from UI logic (Single Responsibility Principle)
Architecture:
  Local:  data/raw/**/*.json → parse → DataFrame
  AWS:    S3 → Athena query  → DataFrame  (future - v2)
"""

import json
import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# WHY these constants here and not in config.py:
# Dashboard has its own config needs. Coupling it to src/config.py
# creates a circular dependency risk and makes the dashboard non-portable.
LOCAL_DATA_DIR = os.getenv("DATA_DIR", "data/raw")
EXPECTED_CITIES = ["New York", "Singapore", "Tokyo"]


def load_local_data() -> pd.DataFrame:
    """
    Read all ingestion JSON files from local disk and flatten into a DataFrame.

    WHY flatten: Streamlit/Plotly need tabular data. One row per (city, hour).
    This is the same transformation your dbt staging model does — but in Python
    for the local use case.
    """
    data_path = Path(LOCAL_DATA_DIR)

    if not data_path.exists():
        logger.warning(f"Data directory not found: {data_path}")
        return pd.DataFrame()

    all_records = []

    # rglob = recursive glob — finds JSON files in all subdirectories
    # WHY not just glob("*.json"): your ingestion saves to nested
    # year=/month=/day=/ Hive-partitioned directories
    for json_file in sorted(data_path.rglob("*.json")):
        try:
            with open(json_file) as f:
                payload = json.load(f)

            city = payload.get("city", "Unknown")
            ingested_at = payload.get("ingested_at", "")
            hourly = payload.get("raw_response", {}).get("hourly", {})

            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            humidity = hourly.get("relative_humidity_2m", [])
            wind = hourly.get("wind_speed_10m", [])
            precip = hourly.get("precipitation", [])
            weather_code = hourly.get("weather_code", [])

            # Build one row per hourly observation
            for i in range(len(times)):
                all_records.append(
                    {
                        "city": city,
                        "timestamp": times[i],
                        "temperature_c": temps[i] if i < len(temps) else None,
                        "humidity_pct": humidity[i] if i < len(humidity) else None,
                        "wind_speed_kmh": wind[i] if i < len(wind) else None,
                        "precipitation_mm": precip[i] if i < len(precip) else None,
                        "weather_code": weather_code[i] if i < len(weather_code) else None,
                        "ingested_at": ingested_at,
                    }
                )

        except (json.JSONDecodeError, KeyError) as e:
            # WHY catch and continue: one bad file shouldn't crash the dashboard.
            # Log it so you can investigate, but keep serving what we have.
            logger.error(f"Failed to parse {json_file}: {e}")
            continue

    if not all_records:
        logger.warning("No weather records found in data directory")
        return pd.DataFrame()

    df = pd.DataFrame(all_records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    logger.info(f"Loaded {len(df)} records across {df['city'].nunique()} cities")
    return df


def run_quality_checks(df: pd.DataFrame) -> list[dict]:
    """
    Run data quality validations and return results.

    These checks DATA_CONTRACT.md rules:
    - Temperature range (-60 to 60)
    - No null cities
    - Expected city count (3)
    - Record completeness
    - No duplicate (city, timestamp) pairs
    """
    if df.empty:
        return [{"validation": "Data Loaded", "status": "❌ Failed", "detail": "No data found"}]

    checks = []

    # Check 1: Temperature range (matches your Pydantic model + data contract)
    temp_min, temp_max = df["temperature_c"].min(), df["temperature_c"].max()
    temp_pass = temp_min >= -60 and temp_max <= 60
    checks.append(
        {
            "validation": "Temperature Range (-60°C to 60°C)",
            "status": "✅ Passed" if temp_pass else "❌ Failed",
            "detail": f"Range: {temp_min:.1f}°C to {temp_max:.1f}°C",
        }
    )

    # Check 2: No null cities
    null_cities = df["city"].isna().sum()
    checks.append(
        {
            "validation": "Null City Check",
            "status": "✅ Passed" if null_cities == 0 else "❌ Failed",
            "detail": f"{null_cities} null values",
        }
    )

    # Check 3: Expected cities present
    actual_cities = set(df["city"].unique())
    expected = set(EXPECTED_CITIES)
    cities_match = expected.issubset(actual_cities)
    checks.append(
        {
            "validation": f"City Validation ({len(EXPECTED_CITIES)} expected)",
            "status": "✅ Passed" if cities_match else "⚠️ Warning",
            "detail": f"Found: {sorted(actual_cities)}",
        }
    )

    # Check 4: Null percentage per metric
    null_pct = df[["temperature_c", "humidity_pct", "wind_speed_kmh", "precipitation_mm"]].isna().mean() * 100
    max_null_pct = null_pct.max()
    checks.append(
        {
            "validation": "Completeness (< 5% nulls)",
            "status": "✅ Passed" if max_null_pct < 5 else "⚠️ Warning",
            "detail": f"Max null%: {max_null_pct:.2f}%",
        }
    )

    # Check 5: Duplicate check
    dupes = df.duplicated(subset=["city", "timestamp"]).sum()
    checks.append(
        {
            "validation": "Duplicate Detection",
            "status": "✅ Passed" if dupes == 0 else "❌ Failed",
            "detail": f"{dupes} duplicates found",
        }
    )

    return checks


def get_summary_metrics(df: pd.DataFrame) -> dict:
    """Compute top-line metrics for the dashboard header."""
    if df.empty:
        return {"total_records": 0, "cities": 0, "quality_pct": 0.0, "date_range": "N/A"}

    # Quality score: percentage of rows with zero nulls across all metrics
    metric_cols = ["temperature_c", "humidity_pct", "wind_speed_kmh", "precipitation_mm"]
    complete_rows = df[metric_cols].notna().all(axis=1).sum()
    quality_pct = (complete_rows / len(df)) * 100

    return {
        "total_records": len(df),
        "cities": df["city"].nunique(),
        "quality_pct": round(quality_pct, 1),
        "date_range": f"{df['date'].min()} → {df['date'].max()}",
    }
