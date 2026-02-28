{{
    config(
        materialized='table',
        format='parquet'
    )
}}

SELECT 
    city,
    country,
    DATE(date_parse(timestamp, '%Y-%m-%dT%H:%i')) AS forecast_date,
    COUNT(*) AS hourly_records,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    ROUND(MIN(temperature_c), 2) AS min_temperature_c,
    ROUND(MAX(temperature_c), 2) AS max_temperature_c,
    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
    ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm,
    ROUND(AVG(wind_speed_kmh), 2) AS avg_wind_speed_kmh
FROM {{ ref('stg_weather_hourly') }}
-- Group by city, country, and forecast date to get daily summaries
GROUP BY 1, 2, 3
ORDER BY forecast_date DESC, city
