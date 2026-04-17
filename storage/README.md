# Storage

This folder holds all data artefacts produced during the pipeline run.
All data files are excluded from Git via `.gitignore` — run the pipeline locally to regenerate them.

```
storage/
├── raw_data/                          # Raw CSV pulled from HubSpot via Airbyte
│   └── Hubspot_raw.csv                # (gitignored — large, sensitive)
│
├── processed_data/                    # Cleaned and joined CSVs
│   ├── hubspot_processed_data.csv     # After PostgreSQL cleanup (gitignored)
│   ├── mailchimp_campaigns_data.csv   # Mailchimp export (gitignored)
│   └── joined_contacts_campaigns.csv # Output of join_datasets.py (gitignored)
│
└── delta_lake/                        # Unified Delta Lake table (gitignored)
    ├── part-*.snappy.parquet
    └── _delta_log/
        └── 00000000000000000000.json
```

## Regenerating Data

Run the pipeline steps in order (see main README.md):

1. Airbyte sync → populates `raw_data/`
2. PostgreSQL cleanup → produces `processed_data/hubspot_processed_data.csv`
3. `python processing/join_datasets.py` → produces `joined_contacts_campaigns.csv`
4. PySpark notebooks → produces `delta_lake/`
