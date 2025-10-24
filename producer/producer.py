import time
from db import get_connection
from kafka import KafkaProducer
import json
import logging

KAFKA_BOOTSTRAP = "kafka:29092"
TOPIC = "kvs_updates"
BATCH_SIZE = 32
POLL_INTERVAL = "2"


# setup logging
logging.basicConfig(
    level=logging.INFO, # Set the default logging level (e.g., DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def producer_loop():
    
    time.sleep(16)

    # get the producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=5
    )

    logger.info("[producer] producer configured")

    # producer logic
    while True:
        try:
            with get_connection() as conn, conn.cursor() as cur:
                
                # get some rows
                cur.execute(f"""
                    SELECT id, key, value
                    FROM kvs_outbox
                    WHERE status = 'pending'
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED
                    LIMIT {BATCH_SIZE}
                """)
                rows = cur.fetchall()

                if len(rows) == 0:
                    logger.info("[producer] no rows sleeping for 4 sec")
                    time.sleep(4)
                    continue
                # iterate over rows
                logger.info(f"[producer] processing {len(rows)} messages")
                for row in rows:
                    request_id = row["id"]
                    key = row["key"]
                    value = row["value"]
                    payload = {
                        "request_id": str(request_id),
                        "key":key,
                        "value": value
                    }
                    
                    # send the data to the topic
                    future = producer.send(TOPIC, payload)
                    try:
                        record_metadata = future.get(timeout=10)
                    except Exception as e:
                        logger.error(f"[producer] failed to send request_id: {request_id}, will try later:",e)
                        continue 

                    cur.execute("""
                        UPDATE kvs_outbox
                        SET status = 'published'
                        WHERE id = %s
                    """, (request_id))
                    logger.debug(f"[producer] marked record_id {request_id} as 'published'.")
                conn.commit()
        except Exception as e:
            print("[producer] error:", e)
            time.sleep(5)

if __name__ == "__main__":
    producer_loop()