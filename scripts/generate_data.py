"""
Master data generation script for Vi Telecom DE Pipeline.
Run: python scripts/generate_data.py
"""
import os
import sys
import time
from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generators.crm_generator     import generate_subscribers, save_subscribers
from scripts.generators.network_generator import generate_towers, generate_network_kpis, save_network_data
from scripts.generators.cdr_generator     import generate_cdrs, save_cdrs
from scripts.generators.ipdr_generator    import generate_ipdrs, save_ipdrs

os.makedirs("data/raw", exist_ok=True)

def main():
    logger.info("=" * 60)
    logger.info("Vi Telecom — Synthetic Data Generation Starting")
    logger.info("=" * 60)
    start = time.time()

    # 1. CRM (must be first — others depend on subscriber_ids)
    logger.info("\n[1/4] Generating CRM / Subscriber data...")
    subscribers_df = generate_subscribers()
    save_subscribers(subscribers_df)

    # 2. Network towers + KPIs
    logger.info("\n[2/4] Generating Network tower + KPI data...")
    towers_df = generate_towers()
    kpi_df    = generate_network_kpis(towers_df)
    save_network_data(towers_df, kpi_df)

    # 3. CDR events (largest dataset)
    logger.info("\n[3/4] Generating CDR events...")
    cdr_df = generate_cdrs(subscribers_df, towers_df)
    save_cdrs(cdr_df)

    # 4. IPDR data usage
    logger.info("\n[4/4] Generating IPDR data usage records...")
    ipdr_df = generate_ipdrs(subscribers_df, towers_df)
    save_ipdrs(ipdr_df)

    # Summary
    elapsed = round(time.time() - start, 1)
    total_rows = len(subscribers_df) + len(towers_df) + len(kpi_df) + len(cdr_df) + len(ipdr_df)

    logger.info("\n" + "=" * 60)
    logger.success(f"Data generation complete in {elapsed}s")
    logger.info(f"  CRM subscribers : {len(subscribers_df):>10,}")
    logger.info(f"  Network towers  : {len(towers_df):>10,}")
    logger.info(f"  Network KPIs    : {len(kpi_df):>10,}")
    logger.info(f"  CDR events      : {len(cdr_df):>10,}")
    logger.info(f"  IPDR sessions   : {len(ipdr_df):>10,}")
    logger.info(f"  TOTAL ROWS      : {total_rows:>10,}")
    logger.info("=" * 60)
    logger.info(f"\nFiles saved to: data/raw/")
    logger.info("  crm_subscribers.csv + .parquet")
    logger.info("  network_towers.csv + .parquet")
    logger.info("  network_kpis.csv + .parquet")
    logger.info("  cdr_events.csv + .parquet")
    logger.info("  ipdr_data_usage.csv + .parquet")

if __name__ == "__main__":
    main()
