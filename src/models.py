"""Pydantic data models for weather API validation"""
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Annotated

class HourlyData(BaseModel):
  time: list[str]
  temperature_2m: list[float]
  relative_humidity_2m: list[float]
  weather_code: list[int]
  wind_speed_10m: list[float]
  precipitation: list[float]

  @model_validator(mode='after')
  def check_all_length_is_match(self) -> 'HourlyData':
    data_dict = self.model_dump()
    lengths = {len(v) for v in data_dict.values() if isinstance(v, list)}

    if len(lengths) > 1:
      raise ValueError(f"Mismatched array lengths: {lengths}")
    return self

  #because Annotated only works best for single value, while this is list, better use field validator
  @field_validator('temperature_2m', mode='after')
  @classmethod
  def check_temperature_range(cls, temps:list[float]) -> list[float]:
    for temp in temps:
      if not -60 <= temp <= 60:
        raise ValueError(f"Temperature {temp}°C out of valid range (-60 to 60)")
    return temps

  @field_validator('relative_humidity_2m', mode='after')
  @classmethod
  def check_humidity_range(cls, values: list[float]) -> list[float]:
    for value in values:
      if not 0 <= value <= 100:
        raise ValueError(f"Humidity {value}% out of valid range (0 to 100)")
    return values

  @field_validator('weather_code', mode='after')
  @classmethod
  def check_weather_code_range(cls, values: list[int]) -> list[int]:
    for value in values:
      if not 0 <= value <= 99:
        raise ValueError(f"Weather code {value} out of valid range (0 to 99)")
    return values

  @field_validator('wind_speed_10m', mode='after')
  @classmethod
  def check_wind_speed_range(cls, values: list[float]) -> list[float]:
    for value in values:
      if not 0 <= value <= 400:
        raise ValueError(f"Wind speed {value}km/h out of valid range (0 to 400)")
    return values

  @field_validator('precipitation', mode='after')
  @classmethod
  def check_precipitation_range(cls, values: list[float]) -> list[float]:
    for value in values:
      if not 0 <= value <= 500:
        raise ValueError(f"Precipitation {value}mm out of valid range (0 to 500)")
    return values

class HourlyUnitData(BaseModel):
  time: str
  temperature_2m: str
  relative_humidity_2m: str
  weather_code: str
  wind_speed_10m: str
  precipitation: str

class WeatherAPIResponse(BaseModel):
  """Represent full api response"""
  latitude: Annotated[float, Field(ge=-90, le=90)]
  longitude: Annotated[float, Field(ge=-180, le=180)]
  generationtime_ms: float
  utc_offset_seconds: float
  timezone: str
  timezone_abbreviation: str
  elevation: float
  hourly_units: HourlyUnitData
  hourly: HourlyData

  @field_validator('timezone', 'timezone_abbreviation', mode='after')
  @classmethod
  def is_gmt_timezone(cls, value: str) -> str:
    if value != 'GMT':
      raise ValueError(f"Expected GMT, but got {value}")
    return value