# Weather Data Quality Platform 🌤️

A production data engineering pipeline that ingests, transforms, and monitors weather data quality using modern cloud-native tools.

## 🎯 Project Goals

- Build end-to-end data pipeline from ingestion to visualization
- Implement comprehensive data quality framework
- Demonstrate infrastructure-as-code best practices
- Showcase skills relevant to Big Tech and Middle East tech companies

## 🏗️ Architecture

```
Open-Meteo API → AWS Lambda → S3 (raw) → dbt → S3 (staging/mart) 
→ Great Expectations → Athena → Streamlit Dashboard
```

**Orchestration:** Apache Airflow  
**Infrastructure:** Terraform  
**CI/CD:** GitHub Actions

## 📊 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Cloud | AWS | Free tier, MENA region presence |
| Storage | S3 + Athena | Serverless data lake |
| Compute | Lambda | Event-driven ingestion |
| Transformation | dbt | SQL-based analytics engineering |
| Data Quality | Great Expectations | Automated validation & profiling |
| Orchestration | Airflow | Workflow management |
| IaC | Terraform | Infrastructure provisioning |
| CI/CD | GitHub Actions | Automated testing & deployment |

## 🚀 Quick Start

### Local Development

```bash
# Clone repo
git clone https://github.com/andikabhaskara/weather-dq-platform.git
cd weather-dq-platform

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run ingestion
python src/ingestion.py
```

## 📂 Project Structure

```
├── src/               # Source code
├── terraform/         # Infrastructure as code
├── dbt/              # Data transformation models
├── tests/            # Unit & integration tests
└── docs/             # Documentation & architecture diagrams
```

## ✅ Current Status

**Phase 1A: Local Ingestion** ✅ Complete
- Multi-city weather data ingestion (New York, Singapore, Tokyo)
- Pydantic-based schema validation
- Retry logic with exponential backoff
- Structured logging

**Phase 1B: AWS Deployment** 🚧 In Progress

## 📈 Data Contract

- **Sources:** Open-Meteo Historical Weather API
- **Locations:** 3 cities (NY, Singapore, Tokyo)
- **Frequency:** Daily backfill (30-day rolling window)
- **Volume:** ~2,160 records/day
- **SLA:** Data ingested within 24 hours

See [DATA_CONTRACT.md](DATA_CONTRACT.md) for full schema & validation rules.

## 🎓 Learning Outcomes

- ✅ API integration with error handling
- ✅ Data validation using Pydantic
- ✅ Logging best practices
- 🚧 AWS Lambda deployment
- 🚧 dbt transformation patterns
- 🚧 Data quality monitoring

## 📧 Contact

Built by Andika Bhaskara as part of portfolio for Data Platform Engineer roles.

[LinkedIn](#) | [Blog Post](#)


========================================



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

