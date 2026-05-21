import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta
from loguru import logger
from .config import (
    CALL_TYPES, CALL_WEIGHTS, SIMULATION_DAYS, DATA_RAW_PATH
)

random.seed(42)
np.random.seed(42)


def generate_cdrs(subscribers_df: pd.DataFrame, towers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate Call Detail Records.
    Each subscriber makes on average 3-8 calls/events per day.
    Total = ~NUM_SUBSCRIBERS * avg_daily_events * fraction_active_per_day
    """
    logger.info("Generating CDR events...")

    sub_ids    = subscribers_df["subscriber_id"].tolist()
    sub_meta   = subscribers_df.set_index("subscriber_id")[
        ["circle", "plan_type", "is_churned", "is_weak_circle"]
    ].to_dict("index")
    tower_ids  = towers_df["tower_id"].tolist()
    base_date  = datetime.now() - timedelta(days=SIMULATION_DAYS)

    records = []

    for day_offset in range(SIMULATION_DAYS):
        event_date = base_date + timedelta(days=day_offset)

        # ~40% of subscribers are active on any given day (realistic)
        active_subs = random.sample(sub_ids, k=int(len(sub_ids) * 0.40))

        for sub_id in active_subs:
            meta       = sub_meta[sub_id]
            is_churned = meta["is_churned"]
            is_weak    = meta["is_weak_circle"]

            # Churned subscribers make fewer calls
            num_events = random.randint(1, 3) if is_churned else random.randint(3, 9)

            for _ in range(num_events):
                call_type = random.choices(CALL_TYPES, weights=CALL_WEIGHTS)[0]
                hour      = random.choices(
                    range(24),
                    weights=[1,1,1,1,1,1,2,4,5,5,5,5,5,5,5,5,5,4,4,3,3,2,2,1]
                )[0]
                ts = event_date.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )

                if call_type == "voice":
                    duration_sec = random.randint(5, 1800)
                elif call_type == "video_call":
                    duration_sec = random.randint(30, 3600)
                else:  # sms
                    duration_sec = 0

                # Calls in weak circles drop more
                call_dropped = random.random() < (0.06 if is_weak else 0.015)

                records.append({
                    "cdr_id":          str(uuid.uuid4()),
                    "caller_id":       sub_id,
                    "receiver_id":     random.choice(sub_ids),
                    "caller_circle":   meta["circle"],
                    "tower_id":        random.choice(tower_ids),
                    "call_type":       call_type,
                    "call_timestamp":  ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "call_date":       ts.strftime("%Y-%m-%d"),
                    "call_hour":       hour,
                    "duration_sec":    duration_sec if not call_dropped else random.randint(0, 10),
                    "call_dropped":    int(call_dropped),
                    "is_roaming":      int(random.random() < 0.03),
                    "is_international":int(random.random() < 0.01),
                })

    df = pd.DataFrame(records)
    logger.info(f"CDR: {len(df)} records | "
                f"dropped={df.call_dropped.sum()} | "
                f"voice={len(df[df.call_type=='voice'])}")
    return df


def save_cdrs(df: pd.DataFrame):
    df.to_csv(f"{DATA_RAW_PATH}/cdr_events.csv", index=False)
    df.to_parquet(f"{DATA_RAW_PATH}/cdr_events.parquet", index=False)
    logger.success(f"Saved: cdr_events ({len(df)} rows)")
