"""Tests for the ingestion pipeline core functions."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import City
from src.ingestion import save_raw_data, validate_data


class TestValidateData:
    """Test Pydantic validation of API responses."""

    def test_valid_response(self):
        """Valid API response should return a WeatherAPIResponse model."""
        valid_payload = {
            "latitude": 40.71,
            "longitude": -74.01,
            "generationtime_ms": 0.5,
            "utc_offset_seconds": 0,
            "timezone": "GMT",
            "timezone_abbreviation": "GMT",
            "elevation": 10.0,
            "hourly_units": {
                "time": "iso8601",
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "weather_code": "wmo code",
                "wind_speed_10m": "km/h",
                "precipitation": "mm",
            },
            "hourly": {
                "time": ["2026-02-01T00:00", "2026-02-01T01:00"],
                "temperature_2m": [5.0, 4.5],
                "relative_humidity_2m": [80, 82],
                "weather_code": [3, 3],
                "wind_speed_10m": [10.0, 12.0],
                "precipitation": [0.0, 0.1],
            },
        }
        city = City("New York", 40.7128, -74.006, "USA")
        result = validate_data(valid_payload, city)
        assert result is not None
        assert len(result.hourly.time) == 2

    def test_invalid_response_returns_none(self):
        """Missing required fields should return None (not crash)."""
        invalid_payload = {"latitude": 40.71}  # Missing almost everything
        city = City("New York", 40.7128, -74.006, "USA")
        result = validate_data(invalid_payload, city)
        assert result is None


class TestSaveRawData:
    """Test local file saving."""

    def test_saves_json_file(self, tmp_path):
        """Should save a properly structured JSON file to disk."""
        with patch("ingestion.RAW_DATA_PATH", str(tmp_path / "raw")):
            city = City("Tokyo", 35.68, 139.77, "Japan")
            data = {"hourly": {"time": ["2026-02-01T00:00"], "temperature_2m": [10.0]}}
            timestamp = datetime(2026, 3, 1, 12, 0, 0)

            result = save_raw_data(city, data, timestamp)

            assert "tokyo" in result.lower()
            # Verify the file exists and is valid JSON
            saved_file = Path(result)
            assert saved_file.exists()
            with open(saved_file) as f:
                content = json.load(f)
            assert content["city"] == "Tokyo"
            assert content["raw_response"] == data
