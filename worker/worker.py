import time
from db import get_connection

POLL_INTERVAL = 2  # seconds
BATCH_SIZE = 10    # configurable batch size

def process_outbox():
    while True:
        try:
            with get_connection() as conn, conn.cursor() as cur:
                cur.execute(f"""
                    SELECT id, key, value FROM kvs_outbox
                    WHERE status = 'pending'
                    ORDER BY created_at
                    FOR UPDATE SKIP LOCKED
                    LIMIT {BATCH_SIZE}
                """)
                rows = cur.fetchall()

                if not rows:
                    time.sleep(POLL_INTERVAL)
                    continue

                for row in rows:
                    request_id, key, value = row["id"], row["key"], row["value"]

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
            print("Worker error:", e)
            time.sleep(5)  # backoff on failure

if __name__ == "__main__":
    print("Worker started...")
    process_outbox()
