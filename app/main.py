from fastapi import FastAPI
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
