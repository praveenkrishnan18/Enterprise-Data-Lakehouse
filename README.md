# Enterprise Data Lakehouse for Unified Marketing Analytics


## Problem Statement

HubSpot and Mailchimp are widely used marketing tools, but they store data in silos.
This makes it impossible to answer cross-platform questions like:

- Which CRM contacts actually engaged with email campaigns?
- What is the true conversion rate of a campaign tied to real contacts?
- How does campaign performance influence long-term revenue and CLV?

This project solves that by building an **automated, containerised Data Lakehouse** that ingests,
cleans, joins, and visualises both datasets in a single unified pipeline.

---

## Architecture (High Level)

```
HubSpot API ──┐
              ├──► Airbyte ──► PostgreSQL ──► PySpark + Delta Lake ──► Power BI
Mailchimp ────┘   (Docker)    (Staging)      (Lakehouse Storage)      (Dashboards)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full layer-by-layer breakdown.

---

## Project Structure

```
enterprise-data-lakehouse/
│
├── ingestion/
│   └── airbyte_setup.md              # Airbyte + abctl deployment guide
│
├── processing/
│   ├── join_datasets.py              # Merges HubSpot + Mailchimp CSVs on 'email'
│   └── hubspot_cleanup.sql           # PostgreSQL queries to clean HubSpot raw data
│
├── spark_docker/
│   ├── Dockerfile                    # Jupyter image with Spark 3.4.1 + Delta Lake
│   ├── docker-compose.yml            # Spark master, worker, Jupyter services
│   └── notebooks/
│       ├── hubspot_delta_table.ipynb    # HubSpot CSV → Delta table
│       ├── mailchimp_delta_table.ipynb  # Mailchimp CSV → Delta table
│       └── delta_lake.ipynb             # Joined CSV → unified Delta table
│
├── storage/
│   ├── raw_data/          # Raw HubSpot CSV from Airbyte  (gitignored)
│   ├── processed_data/    # Cleaned & joined CSVs         (gitignored)
│   └── delta_lake/        # Parquet + _delta_log          (gitignored)
│
├── analytics/
│   └── POWER_BI_SETUP.md             # Guide to loading Delta parquet into Power BI
│
└── docs/
    └── ARCHITECTURE.md               # Detailed architecture with ASCII diagram
```

---

## Tech Stack

| Layer | Tool | Version |
|---|---|---|
| Ingestion | Airbyte (abctl) | Open Source |
| Staging DB | PostgreSQL + pgAdmin | Docker container |
| Data Processing | Python / Pandas | 3.x |
| Big Data Engine | Apache Spark / PySpark | 3.4.1 |
| Lakehouse Storage | Delta Lake | 2.4.0 |
| Containerisation | Docker + Docker Compose | Latest |
| Visualisation | Power BI Desktop | Latest |

---

## Quick Start

### Prerequisites
- Windows 10/11 with WSL2 + Docker Desktop running
- Python 3.x with pip
- Power BI Desktop

---

### Step 1 — Start the Spark + Jupyter Stack

```bash
cd spark_docker
docker-compose up --build
```

| Service | URL |
|---|---|
| Jupyter Notebook | http://localhost:8888 |
| Spark Master UI | http://localhost:8080 |
| Spark Worker UI | http://localhost:8081 |

---

### Step 2 — Ingest Data with Airbyte

Follow [`ingestion/airbyte_setup.md`](ingestion/airbyte_setup.md) to:
1. Deploy Airbyte locally via `abctl`
2. Configure HubSpot (API) and Mailchimp (Google Sheets) as sources
3. Set PostgreSQL as the destination
4. Run a sync — data lands in the `airbyte` database

---

### Step 3 — Clean Data in PostgreSQL

Connect to pgAdmin at `http://localhost` and run the SQL in
[`processing/hubspot_cleanup.sql`](processing/hubspot_cleanup.sql).

This will remove unwanted columns, rename fields, drop NULLs, format phone numbers,
and export the cleaned table as `hubspot_processed_data.csv`.

---

### Step 4 — Join the Datasets

```bash
pip install pandas
python processing/join_datasets.py
```

Output → `storage/processed_data/joined_contacts_campaigns.csv`

---

### Step 5 — Build Delta Lake Tables (Jupyter)

Open Jupyter at http://localhost:8888 and run notebooks **in order**:

1. `hubspot_delta_table.ipynb` — HubSpot contacts → `delta_hubspot/`
2. `mailchimp_delta_table.ipynb` — Mailchimp campaigns → `delta_mailchimp/`
3. `delta_lake.ipynb` — Joined dataset → `delta_lake/`

---

### Step 6 — View Dashboards in Power BI

Follow [`analytics/POWER_BI_SETUP.md`](analytics/POWER_BI_SETUP.md) to connect Power BI
to the Delta parquet files and explore the marketing dashboards.

---

## Key Concepts Demonstrated

- **Lakehouse Architecture** — Combines data lake flexibility with warehouse reliability (ACID, schema enforcement)
- **ELT Pipeline** — Extract via Airbyte, Load to PostgreSQL, Transform with PySpark
- **Delta Lake** — Version-controlled Parquet storage with transaction logs and time travel
- **Containerised Stack** — Full pipeline runs in Docker for reproducibility on any machine
- **Marketing Analytics** — CLV, ROI, conversion rate, and campaign performance dashboards

---

## Results

- Unified HubSpot and Mailchimp data with zero manual CSV exports
- ACID-compliant Delta Lake with schema enforcement and version history
- Power BI dashboards for CLV, ROI, campaign performance, and sales forecasting
- Fully reproducible via Docker — no environment setup beyond Docker Desktop

---

*All data used in this project is sample/synthetic data generated for academic demonstration purposes.*
