# Weather Data Quality Platform - Data Contract v1.0

## 1. Data Source
- **Provider**: Open-Meteo Historical Weather API
- **Endpoint**: `https://archive-api.open-meteo.com/v1/archive`
- **Update Frequency**: Daily backfill (fetches previous day's data)
- **SLA**: Data must be ingested within 24 hours of event time

## 2. Scope
- **Locations**:
  - New York (40.7128, -74.0060)
  - London (51.5074, -0.1278)
  - Tokyo (35.6762, 139.6503)
- **Time Range**: Rolling 30-day window
- **Granularity**: Hourly

## 3. Schema Definition

### 3.1 Raw Table (`weather_raw`)
Stores API responses as-is for audit trail.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | STRING | UUID for each ingestion | PRIMARY KEY, NOT NULL |
| `ingested_at` | TIMESTAMP | When data was fetched | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| `location_name` | STRING | City name | NOT NULL |
| `latitude` | FLOAT64 | Location latitude | NOT NULL |
| `longitude` | FLOAT64 | Location longitude | NOT NULL |
| `raw_json` | JSON | Full API response | NOT NULL |
| `partition_date` | DATE | For BigQuery partitioning | NOT NULL |

### 3.2 Staging Table (`stg_weather`)
Cleaned, flattened data.

| Column | Type | Description | Valid Range |
|--------|------|-------------|-------------|
| `event_id` | STRING | UUID | PRIMARY KEY |
| `location_name` | STRING | City name | NOT NULL |
| `latitude` | FLOAT64 | Location | -90 to 90 |
| `longitude` | FLOAT64 | Location | -180 to 180 |
| `event_timestamp` | TIMESTAMP | Weather observation time (UTC) | NOT NULL |
| `temperature_c` | FLOAT64 | Temperature (Celsius) | -60 to 60 |
| `humidity_pct` | FLOAT64 | Relative humidity | 0 to 100 |
| `precipitation_mm` | FLOAT64 | Hourly precipitation | 0 to 500 |
| `wind_speed_kmh` | FLOAT64 | Wind speed | 0 to 400 |
| `weather_code` | INT64 | WMO weather code | 0 to 99 |
| `ingested_at` | TIMESTAMP | Processing timestamp | NOT NULL |

### 3.3 Mart Table (`fct_weather_hourly`)
Analytics-ready with quality flags.

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | STRING | Links to staging |
| `location_name` | STRING | City |
| `event_timestamp` | TIMESTAMP | Observation time |
| `temperature_c` | FLOAT64 | Temperature |
| `humidity_pct` | FLOAT64 | Humidity |
| `precipitation_mm` | FLOAT64 | Rainfall |
| `wind_speed_kmh` | FLOAT64 | Wind speed |
| `weather_code` | INT64 | Weather code |
| `is_anomaly_temp` | BOOLEAN | Temp outside 3 std dev |
| `is_anomaly_wind` | BOOLEAN | Wind outside 3 std dev |
| `data_quality_score` | FLOAT64 | 0-100 score |
| `dq_flags` | ARRAY<STRING> | List of issues (e.g., ["null_temp", "extreme_wind"]) |

## 4. Data Quality Rules

### Critical (Pipeline Fails)
1. **No nulls** in `event_timestamp`, `location_name`, `latitude`, `longitude`
2. **Schema match**: All expected fields present
3. **Freshness**: Data < 48 hours old

### Warning (Log but Continue)
4. **Range checks**: Values within valid ranges (see table above)
5. **Anomaly detection**: Temperature/wind > 3 standard deviations from 30-day mean
6. **Completeness**: < 5% missing values per location per day

### Info (Track Metrics)
7. **Record count**: Expect 24 records/day per location (72 total)
8. **API response time**: < 2 seconds
9. **Duplicate check**: No duplicate (location, timestamp) pairs

## 5. Failure Handling
- **API down**: Retry 3x with exponential backoff, alert after 1 hour
- **Schema change**: Fail pipeline, send Slack alert
- **Partial data**: Load available data, flag missing locations

## 6. Cost Controls
- **BigQuery partitioning**: By `partition_date` (prune queries)
- **Clustering**: By `location_name`, `event_timestamp`
- **Retention**: Keep raw data 90 days, marts 1 year

## 7. Change Log
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-30 | Initial contract |