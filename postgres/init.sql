-- key value store
CREATE TABLE IF NOT EXISTS kvs (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    request_id UUID UNIQUE NOT NULL
);

-- key value store outbox
CREATE TABLE IF NOT EXISTS kvs_outbox (
    id UUID PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
