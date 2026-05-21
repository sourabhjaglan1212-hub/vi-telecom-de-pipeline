import os
from dotenv import load_dotenv

load_dotenv()

# Vi operates in 22 telecom circles in India
CIRCLES = [
    "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Andhra Pradesh",
    "Gujarat", "Rajasthan", "Uttar Pradesh East", "Uttar Pradesh West",
    "West Bengal", "Kerala", "Punjab", "Haryana", "Madhya Pradesh",
    "Odisha", "Bihar", "Jharkhand", "Himachal Pradesh", "Mumbai",
    "Kolkata", "Chennai", "Assam"
]

# Vi's weak circles (higher churn, poor network) — reflects real market
WEAK_CIRCLES = [
    "Uttar Pradesh East", "Uttar Pradesh West", "Bihar",
    "Jharkhand", "Assam", "Odisha"
]

# Plan types with realistic distribution weights
PLAN_TYPES = ["prepaid", "postpaid"]
PLAN_WEIGHTS = [0.72, 0.28]  # 72% prepaid in Indian telecom

PREPAID_PLANS = [
    {"name": "Vi Basic 28", "data_gb": 1.0, "validity_days": 28, "price": 155},
    {"name": "Vi Value 56", "data_gb": 6.0, "validity_days": 56, "price": 299},
    {"name": "Vi Smart 28", "data_gb": 1.5, "validity_days": 28, "price": 199},
    {"name": "Vi Hero Unlimited", "data_gb": 1.5, "validity_days": 28, "price": 249},
    {"name": "Vi Work From Home", "data_gb": 3.0, "validity_days": 28, "price": 299},
    {"name": "Vi Annual 365", "data_gb": 1.5, "validity_days": 365, "price": 1799},
]

POSTPAID_PLANS = [
    {"name": "Vi Red 499", "data_gb": 75.0, "validity_days": 30, "price": 499},
    {"name": "Vi Red 699", "data_gb": 100.0, "validity_days": 30, "price": 699},
    {"name": "Vi Red 999", "data_gb": 150.0, "validity_days": 30, "price": 999},
    {"name": "Vi Business 1199", "data_gb": 200.0, "validity_days": 30, "price": 1199},
]

CALL_TYPES = ["voice", "sms", "video_call"]
CALL_WEIGHTS = [0.65, 0.25, 0.10]

NETWORK_TYPES = ["4G", "5G", "3G"]
NETWORK_WEIGHTS = [0.70, 0.18, 0.12]

APP_CATEGORIES = [
    "video_streaming", "social_media", "gaming", "messaging",
    "browsing", "music_streaming", "voip", "ecommerce"
]
APP_WEIGHTS = [0.30, 0.25, 0.15, 0.12, 0.08, 0.05, 0.03, 0.02]

NUM_SUBSCRIBERS = int(os.getenv("NUM_SUBSCRIBERS", 50000))
NUM_TOWERS      = int(os.getenv("NUM_TOWERS", 500))
SIMULATION_DAYS = int(os.getenv("SIMULATION_DAYS", 90))

DATA_RAW_PATH = "data/raw"
