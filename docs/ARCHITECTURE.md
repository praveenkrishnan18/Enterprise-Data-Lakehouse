# Architecture — Enterprise Data Lakehouse for Unified Marketing Analytics

---

## Full Pipeline Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                                    │
│                                                                          │
│   ┌──────────────────┐              ┌──────────────────────────────┐     │
│   │    HubSpot CRM   │              │   Mailchimp (Email Campaigns)│     │
│   │  (Contacts API)  │              │   (Exported to Google Sheets)│     │
│   └────────┬─────────┘              └──────────────┬───────────────┘     │
└────────────┼──────────────────────────────────────┼────────────────────-┘
             │                                      │
             ▼                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        INGESTION LAYER                                   │
│                                                                          │
│                    Airbyte  (deployed via abctl)                         │
│          ┌──────────────────────────────────────────────┐               │
│          │  • Pulls HubSpot contacts via Private App API │               │
│          │  • Pulls Mailchimp data via Google Sheets     │               │
│          │  • Loads both into PostgreSQL (staging DB)    │               │
│          └──────────────────────────────────────────────┘               │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      STAGING & CLEANING LAYER                            │
│                                                                          │
│              PostgreSQL  (Docker container)  +  pgAdmin                  │
│                                                                          │
│   SQL operations (hubspot_cleanup.sql):                                  │
│     1. Backup raw table  →  airbyte_backup                               │
│     2. Drop 100+ unnecessary Airbyte metadata columns                    │
│     3. Rename remaining columns to clean schema (e.g. properties_email   │
│        → email, properties_firstname → first_name)                       │
│     4. DELETE rows where phone IS NULL                                   │
│     5. REGEXP_REPLACE to strip non-numeric chars from phone numbers      │
│     6. ROUND deal_value and clv to 2 decimal places                      │
│     7. Export as hubspot_processed_data.csv                              │
│                                                                          │
│   Mailchimp data exported as mailchimp_campaigns_data.csv                │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        PROCESSING LAYER                                  │
│                                                                          │
│                   Python / Pandas  (join_datasets.py)                    │
│                                                                          │
│     • Inner join hubspot_processed_data.csv + mailchimp_campaigns_data   │
│       on the shared 'email' column                                       │
│     • Deduplicates common columns (first_name, last_name, phone)         │
│     • Reorders columns: identity fields → HubSpot fields → campaign data │
│     • Output: joined_contacts_campaigns.csv                              │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  TRANSFORMATION & STORAGE LAYER                          │
│                                                                          │
│         PySpark 3.4.1  +  Delta Lake 2.4.0  (Jupyter in Docker)         │
│                                                                          │
│   Notebooks run in this order:                                           │
│                                                                          │
│   1. hubspot_delta_table.ipynb                                           │
│      CSV  →  delta_hubspot/  (Parquet + _delta_log)                     │
│                                                                          │
│   2. mailchimp_delta_table.ipynb                                         │
│      CSV  →  delta_mailchimp/  (Parquet + _delta_log)                   │
│                                                                          │
│   3. delta_lake.ipynb                                                    │
│      Joined CSV  →  delta_lake/  (Parquet + _delta_log)                 │
│                                                                          │
│   Delta Lake capabilities used:                                          │
│     • ACID transactions                                                  │
│     • Schema enforcement                                                 │
│     • Version history (time travel)                                      │
│     • Efficient columnar storage (Snappy-compressed Parquet)             │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      ANALYTICS & VISUALISATION                           │
│                                                                          │
│                         Power BI Desktop                                 │
│                                                                          │
│   Connects directly to Delta parquet files (no separate DB needed)       │
│                                                                          │
│   Dashboards:                                                            │
│     • Customer Lifetime Value (CLV) by segment                          │
│     • Return on Investment (ROI) per campaign                           │
│     • Revenue vs Marketing Spend                                         │
│     • Conversion Rate Trends                                             │
│     • Sales Forecasting                                                  │
│     • Contact & Campaign Segmentation                                    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Container Architecture

```
docker-compose.yml  (spark_docker/)
│
├── spark-master    image: bitnami/spark:3.4.1
│   ├── port 8080   Spark Master Web UI
│   └── port 7077   Spark cluster endpoint
│
├── spark-worker    image: bitnami/spark:3.4.1
│   └── port 8081   Spark Worker Web UI
│
└── jupyter         image: custom (Dockerfile)
    ├── port 8888   Jupyter Notebook UI
    ├── Base: jupyter/base-notebook
    ├── Java 11 (OpenJDK)
    ├── Spark 3.4.1
    ├── PySpark 3.4.1
    └── delta-spark 2.4.0
```

---

## Data Schema

### HubSpot Contacts (after cleaning)

| Column | Type | Description |
|---|---|---|
| first_name | text | Contact first name |
| last_name | text | Contact last name |
| email | text | Primary key for join |
| phone | text | Phone (digits only after cleaning) |
| company | text | Company name |
| lead_source | text | Where the lead came from |
| lifecycle_stage | text | CRM stage (lead, MQL, customer, etc.) |
| deal_value | numeric(20,2) | Associated deal value |
| clv | numeric(20,2) | Customer lifetime value |
| created_date | date | Contact creation date |

### Mailchimp Campaigns (key fields)

| Column | Description |
|---|---|
| email | Contact email (join key) |
| campaign_id | Unique campaign identifier |
| campaign_name | Campaign title |
| send_time | When the campaign was sent |
| opens | Number of email opens |
| clicks | Number of link clicks |
| unsubscribed | Unsubscribe flag |

---

## Technology Choices

| Decision | Rationale |
|---|---|
| Airbyte over custom scripts | Pre-built connectors; no API pagination code needed |
| PostgreSQL as staging | SQL-based cleaning is intuitive; pgAdmin provides visual validation |
| PySpark over plain Pandas | Demonstrates distributed processing; scales to larger datasets |
| Delta Lake over plain Parquet | ACID compliance + version history = production-grade reliability |
| Docker Compose | Single command spins up the entire stack; reproducible on any machine |
| Power BI | Reads Parquet natively; widely used in industry analytics teams |
