"""
join_datasets.py
-----------------
Merges cleaned HubSpot contacts with Mailchimp campaign data on the shared
'email' column, then saves the result as a single unified CSV.

Usage (from project root):
    pip install pandas
    python processing/join_datasets.py

Inputs  (expected in storage/processed_data/):
    hubspot_processed_data.csv
    mailchimp_campaigns_data.csv

Output:
    storage/processed_data/joined_contacts_campaigns.csv
"""

import os
import pandas as pd

# ── Resolve paths relative to this file ──────────────────────────────────────
HERE          = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT  = os.path.dirname(HERE)
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "storage", "processed_data")

HUBSPOT_CSV   = os.path.join(PROCESSED_DIR, "hubspot_processed_data.csv")
MAILCHIMP_CSV = os.path.join(PROCESSED_DIR, "mailchimp_campaigns_data.csv")
OUTPUT_CSV    = os.path.join(PROCESSED_DIR, "joined_contacts_campaigns.csv")

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading HubSpot data...")
hubspot_df = pd.read_csv(HUBSPOT_CSV)

print("Loading Mailchimp data...")
mailchimp_df = pd.read_csv(MAILCHIMP_CSV)

# ── Merge ─────────────────────────────────────────────────────────────────────
# Keep name/phone columns from HubSpot; drop the duplicate versions in Mailchimp
common_cols   = ["first_name", "last_name", "phone"]
mailchimp_sel = mailchimp_df.drop(columns=common_cols, errors="ignore")

joined_df = pd.merge(hubspot_df, mailchimp_sel, on="email", how="inner")
print(f"Matched records (inner join on email): {len(joined_df)}")

# ── Column order ──────────────────────────────────────────────────────────────
hubspot_extra   = [c for c in hubspot_df.columns   if c not in ["email"] + common_cols]
mailchimp_extra = [c for c in mailchimp_sel.columns if c != "email"]
final_cols      = common_cols + ["email"] + hubspot_extra + mailchimp_extra
joined_df       = joined_df[final_cols]

# ── Save ──────────────────────────────────────────────────────────────────────
os.makedirs(PROCESSED_DIR, exist_ok=True)
joined_df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved → {OUTPUT_CSV}")
