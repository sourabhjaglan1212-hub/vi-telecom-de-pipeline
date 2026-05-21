import json
import time
from kafka import KafkaProducer
from loguru import logger


def create_producer(bootstrap_servers: str = "localhost:9092") -> KafkaProducer:
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all",
        retries=3,
        batch_size=16384,
        linger_ms=10,
        compression_type="gzip",
    )
    logger.info(f"Kafka producer connected to {bootstrap_servers}")
    return producer
