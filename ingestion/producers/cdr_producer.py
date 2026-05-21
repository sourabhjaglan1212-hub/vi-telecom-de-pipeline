import os, sys, time
import pandas as pd
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from ingestion.producers.base_producer import create_producer

TOPIC = "cdr.raw"
BATCH = 500
DELAY = 0.05

def stream_cdrs(parquet_path: str = "data/raw/cdr_events.parquet"):
    logger.info(f"Loading CDR data...")
    df = pd.read_parquet(parquet_path)
    total = len(df)
    logger.info(f"Loaded {total:,} CDR records. Streaming to topic: {TOPIC}")

    producer = create_producer()
    sent = 0
    start = time.time()

    for i in range(0, total, BATCH):
        batch = df.iloc[i: i + BATCH]
        for _, row in batch.iterrows():
            record = row.to_dict()
            producer.send(topic=TOPIC, key=record["caller_id"], value=record)
            sent += 1
        producer.flush()
        if sent % 10000 == 0:
            elapsed = round(time.time() - start, 1)
            logger.info(f"  Sent {sent:,}/{total:,} | {round(sent/elapsed):,} msg/sec")
        time.sleep(DELAY)

    producer.flush()
    producer.close()
    logger.success(f"Done: {sent:,} CDR records streamed in {round(time.time()-start,1)}s")

if __name__ == "__main__":
    stream_cdrs()
