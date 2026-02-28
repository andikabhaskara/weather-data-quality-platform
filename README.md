# Weather Data Quality Platform 🌤️

A production data engineering pipeline that ingests, transforms, and monitors weather data quality using modern cloud-native tools.

## 🎯 Project Goals

- Build end-to-end data pipeline from ingestion to visualization
- Implement comprehensive data quality framework
- Demonstrate infrastructure-as-code best practices
- Showcase skills relevant to Big Tech companies

## 🏗️ Architecture

![Architecture](docs/architecture.png)

**Orchestration:** Apache Airflow  
**Infrastructure:** Terraform  
**CI/CD:** GitHub Actions

## 📊 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Cloud | AWS | Free tier |
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
- ✅ AWS Lambda deployment
- ✅ dbt transformation patterns
- ✅ Data quality monitoring

## 📧 Contact

Built by Andika Bhaskara as part of portfolio for Data Platform Engineer roles.

**[LinkedIn](https://id.linkedin.com/in/mohamad-andika-bhaskara) | [Medium](https://medium.com/@AndikaBhas/about)**