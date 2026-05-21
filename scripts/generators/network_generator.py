import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
from loguru import logger
from .config import (
    CIRCLES, WEAK_CIRCLES, NETWORK_TYPES, NETWORK_WEIGHTS,
    NUM_TOWERS, SIMULATION_DAYS, DATA_RAW_PATH
)

fake = Faker("en_IN")
random.seed(42)
np.random.seed(42)


def generate_towers(n: int = NUM_TOWERS) -> pd.DataFrame:
    """Generate static tower/BTS master data."""
    logger.info(f"Generating {n} tower records...")
    records = []
    circle_list = CIRCLES * (n // len(CIRCLES) + 1)

    for i in range(n):
        circle       = circle_list[i]
        is_weak      = circle in WEAK_CIRCLES
        network_type = random.choices(NETWORK_TYPES, weights=NETWORK_WEIGHTS)[0]

        # Weak circles have fewer 5G towers
        if is_weak and network_type == "5G":
            network_type = "4G"

        records.append({
            "tower_id":      f"TW{str(i + 1).zfill(5)}",
            "circle":        circle,
            "network_type":  network_type,
            "latitude":      round(random.uniform(8.0, 35.0), 6),
            "longitude":     round(random.uniform(68.0, 97.0), 6),
            "is_weak_circle": is_weak,
            "commissioned_year": random.randint(2010, 2023),
        })

    return pd.DataFrame(records)


def generate_network_kpis(towers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate hourly KPI snapshots for each tower over SIMULATION_DAYS."""
    logger.info(f"Generating network KPIs for {len(towers_df)} towers "
                f"over {SIMULATION_DAYS} days...")

    records = []
    base_date = datetime.now() - timedelta(days=SIMULATION_DAYS)
    tower_ids = towers_df["tower_id"].tolist()
    tower_meta = towers_df.set_index("tower_id")[["is_weak_circle", "network_type"]].to_dict("index")

    # Sample 1 KPI snapshot per tower per day (not hourly — keeps row count manageable)
    for day_offset in range(SIMULATION_DAYS):
        snapshot_dt = base_date + timedelta(days=day_offset)
        hour = random.randint(0, 23)
        ts = snapshot_dt.replace(hour=hour, minute=random.randint(0, 59))

        for tower_id in tower_ids:
            meta    = tower_meta[tower_id]
            is_weak = meta["is_weak_circle"]

            # Weak towers have worse KPIs
            signal_strength_dbm = round(random.gauss(-85 if is_weak else -70, 8), 2)
            packet_loss_pct     = round(abs(random.gauss(3.5 if is_weak else 0.8, 1.2)), 2)
            latency_ms          = round(abs(random.gauss(55 if is_weak else 22, 10)), 2)
            throughput_mbps     = round(abs(random.gauss(18 if is_weak else 45, 12)), 2)
            call_drop_rate_pct  = round(abs(random.gauss(4.5 if is_weak else 1.2, 1.0)), 2)
            active_users        = random.randint(20, 300)

            # Network quality score (0–100), higher = better
            quality_score = round(
                max(0, min(100,
                    (100 + signal_strength_dbm / 1.5)
                    - packet_loss_pct * 5
                    - latency_ms / 3
                    + throughput_mbps / 2
                    - call_drop_rate_pct * 4
                )), 2
            )

            records.append({
                "tower_id":           tower_id,
                "circle":             towers_df.loc[towers_df.tower_id == tower_id, "circle"].values[0],
                "network_type":       meta["network_type"],
                "snapshot_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "snapshot_date":      ts.strftime("%Y-%m-%d"),
                "signal_strength_dbm":  signal_strength_dbm,
                "packet_loss_pct":      packet_loss_pct,
                "latency_ms":           latency_ms,
                "throughput_mbps":      throughput_mbps,
                "call_drop_rate_pct":   call_drop_rate_pct,
                "active_users":         active_users,
                "quality_score":        quality_score,
            })

    df = pd.DataFrame(records)
    logger.info(f"Network KPIs: {len(df)} records | avg quality score: {df.quality_score.mean():.1f}")
    return df


def save_network_data(towers_df: pd.DataFrame, kpi_df: pd.DataFrame):
    towers_df.to_csv(f"{DATA_RAW_PATH}/network_towers.csv", index=False)
    towers_df.to_parquet(f"{DATA_RAW_PATH}/network_towers.parquet", index=False)
    kpi_df.to_csv(f"{DATA_RAW_PATH}/network_kpis.csv", index=False)
    kpi_df.to_parquet(f"{DATA_RAW_PATH}/network_kpis.parquet", index=False)
    logger.success(f"Saved: network_towers ({len(towers_df)} rows), network_kpis ({len(kpi_df)} rows)")
