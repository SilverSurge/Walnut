from fastapi import FastAPI, HTTPException
import uuid
from db import get_connection
from pydantic import BaseModel

app = FastAPI()

class KVItem(BaseModel):
    key: str
    value: str

@app.post("/kv")
def create_kv(item:KVItem):
    request_id = str(uuid.uuid4())
    print(item)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO kvs_outbox (id, key, value) VALUES (%s, %s, %s)",
            (request_id, item.key, item.value)
        )

    return {
        "status": "accepted",
        "request_id": request_id
    }

@app.get("/status/{request_id}")
def get_status(request_id: str):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT status
            FROM kvs_outbox
            WHERE id = %s
        """, (request_id,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Request ID not found")

    return {
        "request_id": request_id,
        "status": row["status"]
    }


@app.get("/kv/{key}")
def get_kv(key: str):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT value
            FROM kvs
            WHERE key = %s
        """, (key,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Key not found")

    return {
        "key": key,
        "value": row["value"]
    }