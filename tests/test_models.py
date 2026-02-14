from pydantic import ValidationError
from src.models import HourlyData, WeatherAPIResponse, HourlyUnitData
import pytest

# -- FIXTURES --
@pytest.fixture
def valid_hourly_data_payload():
    """Provides a valid payload for HourlyData model"""
    return {
        "time": ["2024-01-01T00:00", "2024-01-01T01:00"],
        "temperature_2m": [20.5, 18.2],
        "relative_humidity_2m": [50.0, 55.0],
        "weather_code": [1, 2],
        "wind_speed_10m": [10.5, 12.0],
        "precipitation": [0.0, 0.1]
    }

@pytest.fixture
def valid_hourly_unit_data_payload():
    """Valid HourlyUnitData dependency."""
    return {
        "time": "iso8601",
        "temperature_2m": "°C",
        "relative_humidity_2m": "%",
        "weather_code": "wmo code",
        "wind_speed_10m": "km/h",
        "precipitation": "mm"
    }

@pytest.fixture
def full_weather_payload(valid_hourly_unit_data_payload, valid_hourly_data_payload):
    """The complete 'Happy Path' response."""
    return {
        "latitude": 52.52,
        "longitude": 13.41,
        "generationtime_ms": 0.1,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "timezone_abbreviation": "GMT",
        "elevation": 38.0,
        "hourly_units": valid_hourly_unit_data_payload,
        "hourly": valid_hourly_data_payload
    }

# -- HAPPY PATH TESTS --
def test_weather_api_response_success(full_weather_payload):
    """Verify that a perfect API response parses correctly."""
    model = WeatherAPIResponse(**full_weather_payload)
    assert model.latitude == 52.52
    assert model.hourly_units.temperature_2m == "°C"

def test_hourly_unit_data_model_success(valid_hourly_unit_data_payload):
    """Test that valid data is accepted by HourlyUnitData model"""
    data = HourlyUnitData(**valid_hourly_unit_data_payload)
    assert data.time == "iso8601"
    assert data.temperature_2m == "°C"
    assert data.relative_humidity_2m == "%"
    assert data.weather_code == "wmo code"
    assert data.wind_speed_10m == "km/h"
    assert data.precipitation == "mm"   

def test_hourly_data_model_accepts_valid_data(valid_hourly_data_payload):
    """Test that valid data is accepted by HourlyData model"""
    data = HourlyData(**valid_hourly_data_payload)
    assert data.temperature_2m == [20.5, 18.2]
    assert data.relative_humidity_2m == [50.0, 55.0]
    assert data.weather_code == [1, 2]
    assert data.wind_speed_10m == [10.5, 12.0]
    assert data.precipitation == [0.0, 0.1]
    assert data.check_all_length_is_match() == data

# -- PARAMETRIZED TESTS FOR RANGE VALIDATORS --
@pytest.mark.parametrize("field, invalid_value, error_msg", [
    ("temperature_2m", [100.0], "out of valid range (-60 to 60)"),
    ("relative_humidity_2m", [110.0], "out of valid range (0 to 100)"),
    ("weather_code", [105], "out of valid range (0 to 99)"),
    ("wind_speed_10m", [-5.0], "out of valid range (0 to 400)"),
    ("precipitation", [600.0], "out of valid range (0 to 500)"),
    ])

def test_range_validators(valid_hourly_data_payload, field, invalid_value, error_msg):
    """Test all range validators using parametrization."""
    valid_hourly_data_payload[field] = invalid_value
    
    with pytest.raises(ValidationError) as exc:
        HourlyData(**valid_hourly_data_payload)
    assert error_msg in str(exc.value)

def test_empty_lists(valid_hourly_data_payload):
    """Test if empty lists are allowed (Pydantic allows this unless specified)."""
    empty_data = {k: [] for k in valid_hourly_data_payload.keys()}
    model = HourlyData(**empty_data)
    assert model.time == []

@pytest.mark.parametrize("field, value", [
    ("latitude", 91.0),    # Above +90
    ("latitude", -91.0),   # Below -90
    ("longitude", 181.0),  # Above +180
    ("longitude", -181.0), # Below -180
])
def test_coordinates_out_of_bounds(full_weather_payload, field, value):
    """Test Annotated Field constraints for lat/long."""
    full_weather_payload[field] = value
    with pytest.raises(ValidationError) as exc:
        WeatherAPIResponse(**full_weather_payload)
    assert "greater than or equal to" in str(exc.value) or "less than or equal to" in str(exc.value)

@pytest.mark.parametrize("field, bad_tz", [
    ("timezone", "PST"),
    ("timezone_abbreviation", "EST"),
])
def test_timezone_must_be_gmt(full_weather_payload, field, bad_tz):
    """Verify the custom GMT validator."""
    full_weather_payload[field] = bad_tz
    with pytest.raises(ValidationError) as exc:
        WeatherAPIResponse(**full_weather_payload)
    assert f"Expected GMT, but got {bad_tz}" in str(exc.value)

def test_nested_validation_failure(full_weather_payload):
    """
    Ensure that if HourlyData is invalid, the parent WeatherAPIResponse fails.
    This tests 'bubbling' validation.
    """
    # Break the nested hourly data (mismatched range from previous model)
    full_weather_payload["hourly"]["temperature_2m"] = [150.0] 
    
    with pytest.raises(ValidationError) as exc:
        WeatherAPIResponse(**full_weather_payload)
    
    # Notice how we can check the path to the error
    assert "temperature_2m" in str(exc.value)

