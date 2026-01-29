# weather-data-quality-platform

Goal: Monitor weather data quality for 10 ASEAN cities

Architecture diagram (simple boxes/arrows)
Open-Meteo API → Python script → Pub/Sub → BigQuery (raw)
                                                ↓
                                          dbt (clean/transform)
                                                ↓
                                    Python checks (is data accurate?)
                                                ↓
                                          Airflow (orchestrate daily)
                                                ↓
                                    Dashboard (show pass/fail metrics)

Input: Fetch weather for 10 cities (Jakarta, Singapore, Tokyo, etc.) every hour
Storage: Save raw JSON to BigQuery
Transform (dbt): Create clean tables (staging → mart)
Quality checks:
Are temperatures within valid range (-50°C to 60°C)?
Is any data missing?
Does Singapore temp match expected pattern?
Orchestrate: Airflow runs this daily
Visualize: Streamlit dashboard shows "95% data passed quality checks"

Tech stack: Python, GCP Pub/Sub, BigQuery, dbt, Airflow, Terraform

