import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta
from loguru import logger
from .config import (
    APP_CATEGORIES, APP_WEIGHTS, SIMULATION_DAYS, DATA_RAW_PATH
)

random.seed(42)
np.random.seed(42)


def generate_ipdrs(subscribers_df: pd.DataFrame, towers_df: pd.DataFrame) -> pd.DataFrame:
    """Generate internet/data usage (IPDR) records."""
    logger.info("Generating IPDR data usage records...")

    sub_ids   = subscribers_df["subscriber_id"].tolist()
    sub_meta  = subscribers_df.set_index("subscriber_id")[
        ["plan_data_gb", "plan_type", "is_churned", "circle"]
    ].to_dict("index")
    tower_ids = towers_df["tower_id"].tolist()
    base_date = datetime.now() - timedelta(days=SIMULATION_DAYS)

    records = []

    for day_offset in range(SIMULATION_DAYS):
        event_date = base_date + timedelta(days=day_offset)

        # ~55% of subscribers generate data sessions each day
        active_subs = random.sample(sub_ids, k=int(len(sub_ids) * 0.55))

        for sub_id in active_subs:
            meta       = sub_meta[sub_id]
            is_churned = meta["is_churned"]
            daily_cap  = meta["plan_data_gb"] * 1024  # convert to MB

            # Churned users use very little data
            sessions = random.randint(1, 2) if is_churned else random.randint(2, 7)

            daily_used = 0
            for _ in range(sessions):
                if daily_used >= daily_cap:
                    break

                app_cat  = random.choices(APP_CATEGORIES, weights=APP_WEIGHTS)[0]
                hour     = random.randint(0, 23)
                duration = random.randint(60, 7200)  # seconds

                # Data consumption by app category
                base_rates = {
                    "video_streaming": 500, "gaming": 200,
                    "social_media": 80,     "music_streaming": 50,
                    "voip": 30,             "browsing": 20,
                    "messaging": 5,         "ecommerce": 15
                }
                data_mb = round(
                    min(base_rates[app_cat] * (duration / 3600) * random.uniform(0.7, 1.3),
                        daily_cap - daily_used),
                    2
                )
                daily_used += data_mb

                session_start = event_date.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                session_end = session_start + timedelta(seconds=duration)

                records.append({
                    "session_id":      str(uuid.uuid4()),
                    "subscriber_id":   sub_id,
                    "circle":          meta["circle"],
                    "tower_id":        random.choice(tower_ids),
                    "app_category":    app_cat,
                    "session_start":   session_start.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_end":     session_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "session_date":    event_date.strftime("%Y-%m-%d"),
                    "duration_sec":    duration,
                    "data_consumed_mb": data_mb,
                    "is_throttled":    int(daily_used >= daily_cap * 0.95),
                })

    df = pd.DataFrame(records)
    logger.info(f"IPDR: {len(df)} records | "
                f"total data: {df.data_consumed_mb.sum()/1024:.1f} GB")
    return df


def save_ipdrs(df: pd.DataFrame):
    df.to_csv(f"{DATA_RAW_PATH}/ipdr_data_usage.csv", index=False)
    df.to_parquet(f"{DATA_RAW_PATH}/ipdr_data_usage.parquet", index=False)
    logger.success(f"Saved: ipdr_data_usage ({len(df)} rows)")
