import os, sys, time
import pandas as pd
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from ingestion.producers.base_producer import create_producer

TOPIC = "ipdr.raw"
BATCH = 500
DELAY = 0.05

def stream_ipdrs(parquet_path: str = "data/raw/ipdr_data_usage.parquet"):
    logger.info(f"Loading IPDR data...")
    df = pd.read_parquet(parquet_path)
    total = len(df)
    logger.info(f"Loaded {total:,} IPDR records. Streaming to topic: {TOPIC}")

    producer = create_producer()
    sent = 0
    start = time.time()

    for i in range(0, total, BATCH):
        batch = df.iloc[i: i + BATCH]
        for _, row in batch.iterrows():
            record = row.to_dict()
            producer.send(topic=TOPIC, key=record["subscriber_id"], value=record)
            sent += 1
        producer.flush()
        time.sleep(DELAY)

    producer.flush()
    producer.close()
    logger.success(f"Done: {sent:,} IPDR records streamed in {round(time.time()-start,1)}s")

if __name__ == "__main__":
    stream_ipdrs()
