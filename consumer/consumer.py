import time
from db import get_connection
from kafka import KafkaConsumer
import json
import logging

KAFKA_BOOTSTRAP = "kafka:29092"
TOPIC = "kvs_updates"
BATCH_SIZE = 32
POLL_INTERVAL = "2"
GROUP_ID = "kvs-consumer-group"

# setup logging
logging.basicConfig(
    level=logging.INFO, # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def consumer_loop():
    time.sleep(16)
    # get the consumer
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=1000
    )
    logger.info("[consumer] consumer configured")
    # consumer logic logic
    while True:
        try:

            # iterate over messages
            for msg in consumer:
                
                payload = msg.value
                request_id = payload.get("request_id")
                key = payload.get("key")
                value = payload.get("value")

                with get_connection() as conn, conn.cursor() as cur:
                    try:
                        cur.execute("""
                            INSERT INTO kvs (key, value, updated_at, request_id)
                            VALUES (%s, %s, NOW(), %s)
                            ON CONFLICT (key) DO UPDATE
                            SET value = EXCLUDED.value,
                                updated_at = NOW(),
                                request_id = EXCLUDED.request_id
                        """, (key, value, request_id))

                        cur.execute("""
                            UPDATE kvs_outbox
                            SET status = 'processed'
                            WHERE id = %s
                        """, (request_id,))

                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        print("[consumer] failed to process message", e)
       
        except Exception as e:
            print("[consumer] error:", e)
            time.sleep(5)

if __name__ == "__main__":
    consumer_loop()