# weather-data-quality-platform

Goal: Monitor weather data quality for 10 ASEAN cities

Architecture diagram (simple boxes/arrows)
┌─────────────────┐
│  Open-Meteo API │ (External data source)
└────────┬────────┘
         │ 1. Python script fetches weather data every hour
         ▼
┌─────────────────┐
│   GCP Pub/Sub   │ (Message queue - buffers data)
└────────┬────────┘
         │ 2. Pub/Sub triggers function to load data
         ▼
┌─────────────────┐
│  BigQuery (raw) │ (Data warehouse - stores raw JSON)
└────────┬────────┘
         │ 3. dbt transforms raw → clean tables
         ▼
┌─────────────────┐
│ BigQuery (mart) │ (Clean, modeled data)
└────────┬────────┘
         │ 4. Python runs data quality checks
         ▼
┌─────────────────┐
│  DQ Results     │ (Pass/Fail metrics stored in BigQuery)
└────────┬────────┘
         │ 5. Airflow orchestrates steps 1-4 daily
         ▼
┌─────────────────┐
│    Dashboard    │ (Streamlit - visualizes DQ metrics)
└─────────────────┘

Infrastructure: Terraform provisions all GCP resources
CI/CD: GitHub Actions deploys code changes

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

