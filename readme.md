# Walnut 🌰

> A nod to the Postgres Write-Ahead Log (WAL) and a solid, reliable seed.

A **Key-Value Store** system built using **FastAPI**, **PostgreSQL**, **PgBouncer**, **Kafka**, and Python-based microservices. This project demonstrates an **outbox pattern** with **event-driven processing**, enabling reliable propagation of KV updates to a Kafka topic and eventual persistence.

---

## Table of Contents

* [Architecture](#architecture)
* [Components](#components)
* [Setup & Run](#setup--run)
* [API Endpoints](#api-endpoints)
* [Configuration](#configuration)
* [Cleanup](#cleanup)

---

## Architecture

```
Client → FastAPI App → PostgreSQL (via PgBouncer)
                   ↘ Outbox Table → Producer → Kafka → Consumer/Worker → KV Table
```

Key features:

* **Outbox Pattern**: Ensures reliable event delivery from DB changes to Kafka.
* **Workers**: Process pending KV changes and update main KV table.
* **Cleanup Service**: Removes processed outbox entries older than a retention period.
* **PgBouncer**: Connection pooling for Postgres.
* **Kafka**: Event streaming for distributed updates.

---

## Components

### 1. **FastAPI App (`app/`)**

* Provides endpoints to create KV entries and check their status.
* Inserts entries into `kvs_outbox` for asynchronous processing.

### 2. **Producer (`producer/`)**

* Reads `pending` entries from `kvs_outbox` and publishes them to Kafka.
* Marks entries as `published`.

### 3. **Consumer (`consumer/`)**

* Consumes Kafka messages and updates the main `kvs` table.
* Marks outbox entries as `processed`.

### 4. **Worker (`worker/`)**

* Alternative background processor that directly processes `pending` outbox entries into `kvs`.

### 5. **Cleanup (`cleanup/`)**

* Periodically deletes `processed` outbox entries older than a configurable retention period.

### 6. **Database & PgBouncer**

* **Postgres**: Stores `kvs` and `kvs_outbox` tables.
* **PgBouncer**: Connection pooling for better performance with concurrent microservices.

### 7. **Kafka**

* Acts as the messaging backbone between producer and consumer for reliable KV updates.

---

## Setup & Run

### Requirements

* Docker & Docker Compose

### Steps

1. Clone the repo:

```bash
git clone <repo-url>
cd <repo-directory>
```

2. Build and start services:

```bash
docker-compose up --build
```

3. Access services:

* FastAPI: `http://localhost:8000`
* Adminer (DB GUI): `http://localhost:8080`
* Kafka exposed at `localhost:9092` (PLAINTEXT)

---

## API Endpoints

### Create KV Entry

```http
POST /kv
Content-Type: application/json

{
  "key": "my_key",
  "value": "my_value"
}
```

**Response:**

```json
{
  "status": "accepted",
  "request_id": "uuid"
}
```

### Check Request Status

```http
GET /status/{request_id}
```

**Response:**

```json
{
  "request_id": "uuid",
  "status": "pending | published | processed"
}
```

### Get KV Value

```http
GET /kv/{key}
```

**Response:**

```json
{
  "key": "my_key",
  "value": "my_value"
}
```

---

## Configuration

* **Database DSN:** `postgresql://uadmin:padmin@pgbouncer:6432/walnut`
* **Kafka Bootstrap:** `kafka:29092`
* **Cleanup Interval:** `CLEANUP_INTERVAL` (default 1 hour)
* **Outbox Retention:** `RETENTION_DAYS` (default 7 days)

All configs are currently hardcoded in service `db.py` files but can be externalized using `python-dotenv`.

---

## Cleanup

The **cleanup service** periodically deletes processed outbox rows older than the retention period to prevent table growth:

```bash
python cleanup.py
```

---

## Notes

* `FOR UPDATE SKIP LOCKED` is used in worker/producer queries to avoid race conditions.
* The system supports **concurrent writes** and **asynchronous event processing**.
* Designed for **learning and demonstration** of the outbox pattern, Kafka integration, and microservice orchestration.

---
