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
git clone https://github.com/andikabhaskara/weather-data-quality-platform.git
cd weather-data-quality-platform

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

**[LinkedIn](https://id.linkedin.com/in/mohamad-andika-bhaskara) | [Medium](https://medium.com/@AndikaBhas/about)**


========================================



# weather-data-quality-platform

Goal: Monitor weather data quality for 10 ASEAN cities

Architecture diagram (simple boxes/arrows)
┌─────────────────┐
│  Open-Meteo API │ (External data source)
└────────┬────────┘
         │ 2. Write raw JSON to S3
         ▼
┌─────────────────┐
│  S3 (raw-data/) │ (Partitioned: s3://bucket/raw/year=2026/month=01/day=30/)
└────────┬────────┘
         │ 3. Lambda triggers dbt (via ECS Fargate free tier)
         ▼
┌─────────────────┐
│  dbt transforms │ (Reads S3 via Athena, writes to S3 staging/)
└────────┬────────┘
         │ 4. Creates clean Parquet files
         ▼
┌─────────────────┐
│ S3 (staging/)   │ (Partitioned, Parquet format)
└────────┬────────┘
         │ 5. Lambda runs Great Expectations checks
         ▼
┌─────────────────┐
│ S3 (dq-results/)│ (JSON reports + metrics)
└────────┬────────┘
         │ 6. Athena queries all layers (dashboard reads this)
         ▼
┌─────────────────┐
│  Streamlit on   │ (Deployed on AWS EC2 free tier or Streamlit Cloud)
│  EC2 / Cloud    │
└─────────────────┘

Infrastructure: Terraform (provisions all AWS resources)
CI/CD: GitHub Actions (tests dbt, deploys Lambda)
Monitoring: CloudWatch Alarms + SNS alerts