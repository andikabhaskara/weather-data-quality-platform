{{
    config(
        materialized='view',
        schema='weather_analytics'
    )
}}

WITH source_data AS (
    SELECT 
        city,
        country,
        ingested_at,
        raw_response
     FROM {{ source('raw_layer', 'raw_weather')}}
)

SELECT
    city,
    country,
    ingested_at,
    -- Zip all arrays together in one UNNEST command
    t.forecast_time as timestamp,
    t.temp as temperature_c,
    t.rh as humidity_pct,
    t.w_code as weather_code,
    t.w_speed as wind_speed_kmh,
    t.precip as precipitation_mm
FROM source_data
CROSS JOIN UNNEST(
    raw_response.hourly.time,
    raw_response.hourly.temperature_2m,
    raw_response.hourly.relative_humidity_2m,
    raw_response.hourly.weather_code,
    raw_response.hourly.wind_speed_10m,
    raw_response.hourly.precipitation
) AS t(forecast_time, temp, rh, w_code, w_speed, precip)