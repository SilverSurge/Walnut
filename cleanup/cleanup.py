import time
from db import get_connection

# How often to run cleanup (seconds)
CLEANUP_INTERVAL = 60 * 60  # every 1 min for testing

# How long to keep processed rows
RETENTION_DAYS = 7

# Batch size for deletes
BATCH_SIZE = 1024

def cleanup_outbox():
    while True:
        try:
            with get_connection() as conn, conn.cursor() as cur:
                total_deleted = 0

                while True:
                    # Delete a batch of processed rows older than RETENTION_DAYS
                    cur.execute("""
                        DELETE FROM kvs_outbox
                        WHERE id IN (
                            SELECT id
                            FROM kvs_outbox
                            WHERE status = 'processed'
                            AND created_at < NOW() - INTERVAL '%s days'
                            ORDER BY created_at
                            FOR UPDATE SKIP LOCKED
                            LIMIT %s
                        )
                    """, (RETENTION_DAYS, BATCH_SIZE))

                    deleted = cur.rowcount
                    total_deleted += deleted
                    conn.commit()

                    if deleted < BATCH_SIZE:
                        # Less than a full batch means we're done
                        break

                if total_deleted:
                    print(f"[Cleanup] Deleted {total_deleted} old outbox rows in batches")

        except Exception as e:
            print("[Cleanup] Error:", e)

        time.sleep(CLEANUP_INTERVAL)

if __name__ == "__main__":
    print("[Cleanup] Worker started...")
    cleanup_outbox()
