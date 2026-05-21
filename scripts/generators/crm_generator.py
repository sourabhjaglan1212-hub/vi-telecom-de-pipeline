import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
from loguru import logger
from .config import (
    CIRCLES, WEAK_CIRCLES, PLAN_TYPES, PLAN_WEIGHTS,
    PREPAID_PLANS, POSTPAID_PLANS, NUM_SUBSCRIBERS, DATA_RAW_PATH
)

fake = Faker("en_IN")  # Indian locale
random.seed(42)
np.random.seed(42)


def _pick_plan(plan_type: str) -> dict:
    plans = PREPAID_PLANS if plan_type == "prepaid" else POSTPAID_PLANS
    return random.choice(plans)


def generate_subscribers(n: int = NUM_SUBSCRIBERS) -> pd.DataFrame:
    logger.info(f"Generating {n} subscriber records...")

    records = []
    for i in range(n):
        subscriber_id = f"VI{str(i + 1).zfill(8)}"
        circle        = random.choice(CIRCLES)
        plan_type     = random.choices(PLAN_TYPES, weights=PLAN_WEIGHTS)[0]
        plan          = _pick_plan(plan_type)

        # Subscribers in weak circles churn more and recharge less
        is_weak_circle = circle in WEAK_CIRCLES

        account_age_days = random.randint(30, 2190)  # up to 6 years
        join_date = datetime.now() - timedelta(days=account_age_days)

        # Last recharge: weak circle subscribers wait longer
        if is_weak_circle:
            days_since_recharge = random.randint(5, 60)
        else:
            days_since_recharge = random.randint(0, 35)

        last_recharge = datetime.now() - timedelta(days=days_since_recharge)

        # Churn risk score (0–1), used later by ML
        churn_risk = round(
            (0.4 if is_weak_circle else 0.1)
            + (days_since_recharge / 90) * 0.4
            + (0.2 if account_age_days < 90 else 0.0)
            + random.uniform(-0.05, 0.05),
            4
        )
        churn_risk = min(max(churn_risk, 0.0), 1.0)

        records.append({
            "subscriber_id":       subscriber_id,
            "mobile_number":       fake.phone_number(),
            "full_name":           fake.name(),
            "circle":              circle,
            "state":               circle,
            "plan_type":           plan_type,
            "plan_name":           plan["name"],
            "plan_price_inr":      plan["price"],
            "plan_data_gb":        plan["data_gb"],
            "plan_validity_days":  plan["validity_days"],
            "account_age_days":    account_age_days,
            "join_date":           join_date.strftime("%Y-%m-%d"),
            "last_recharge_date":  last_recharge.strftime("%Y-%m-%d"),
            "days_since_recharge": days_since_recharge,
            "is_weak_circle":      is_weak_circle,
            "churn_risk_score":    churn_risk,
            "is_churned":          int(churn_risk > 0.65),
        })

    df = pd.DataFrame(records)
    logger.info(f"CRM: {len(df)} subscribers | "
                f"prepaid={len(df[df.plan_type=='prepaid'])} | "
                f"churned={(df.is_churned==1).sum()}")
    return df


def save_subscribers(df: pd.DataFrame):
    path_csv     = f"{DATA_RAW_PATH}/crm_subscribers.csv"
    path_parquet = f"{DATA_RAW_PATH}/crm_subscribers.parquet"
    df.to_csv(path_csv, index=False)
    df.to_parquet(path_parquet, index=False)
    logger.success(f"Saved: {path_csv} ({len(df)} rows)")
    return df
