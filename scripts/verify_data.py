import pandas as pd
import os

datasets = {
    "CRM":         "data/raw/crm_subscribers.parquet",
    "Towers":      "data/raw/network_towers.parquet",
    "Network KPI": "data/raw/network_kpis.parquet",
    "CDR":         "data/raw/cdr_events.parquet",
    "IPDR":        "data/raw/ipdr_data_usage.parquet",
}

for name, path in datasets.items():
    df = pd.read_parquet(path)
    print(f"\n{'='*50}")
    print(f"{name}: {len(df):,} rows | {len(df.columns)} columns")
    print(f"Columns: {', '.join(df.columns.tolist())}")
    print(f"Nulls: {df.isnull().sum().sum()}")
    print(df.head(2).to_string())
