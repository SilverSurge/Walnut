import psycopg
from psycopg.rows import dict_row

DB_DSN = "postgresql://uadmin:padmin@pgbouncer:6432/walnut"

def get_connection():
    return psycopg.connect(DB_DSN, row_factory=dict_row)
