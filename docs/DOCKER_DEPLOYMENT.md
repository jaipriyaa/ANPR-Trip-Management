# Multi-Container Docker Production Deployment Guide

This document details the multi-container Docker architecture, network configuration, storage volumes, container lifecycles, and Compose workflows.

---

## 1. Docker Architecture & Container Communication Diagrams

### 1.1 Docker Multi-Container Architecture

```mermaid
graph TD
    subgraph Host Network Interface
        Port3000[Host Port 3000]
        Port8000[Host Port 8000]
        Port5432[Host Port 5432]
    end

    subgraph Docker Bridge Network: anpr-bridge-network
        Frontend[Frontend Container: Nginx + React]
        Backend[Backend Container: FastAPI + AI Engine]
        Postgres[PostgreSQL Container: Postgres 16]
        Redis[Redis Container: Cache & Queue]
    end

    Port3000 --> Frontend
    Port8000 --> Backend
    Port5432 --> Postgres

    Frontend -->|Proxy /api/*| Backend
    Backend -->|SQLAlchemy ORM| Postgres
    Backend -->|Redis-py| Redis
```

### 1.2 Container Communication Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Client as Browser Client
    participant Nginx as Frontend Container (Port 3000)
    participant FastAPI as Backend Container (Port 8000)
    participant DB as Postgres Container (Port 5432)

    Client->>Nginx: HTTP Request (GET /api/v1/vehicles)
    Nginx->>FastAPI: Forward Request to http://backend:8000/api/v1/vehicles
    FastAPI->>DB: Execute Query over anpr-bridge-network
    DB-->>FastAPI: Return Data Records
    FastAPI-->>Nginx: Return JSON Response Payload
    Nginx-->>Client: Serve Response to User Browser
```

---

## 2. Container Overview Matrix

| Service Name | Base Image | Port Mapping | Health Check | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`frontend`** | `nginx:alpine` (Multi-stage Node 20) | `3000:3000` | HTTP GET `/` | Production Nginx server serving built React SPA & reverse proxying `/api/`. |
| **`backend`** | `python:3.11-slim` | `8000:8000` | HTTP GET `/health` | FastAPI REST API, AI inference engine, and database repositories. |
| **`postgres`** | `postgres:16-alpine` | `5432:5432` | `pg_isready -U postgres` | Relational database persisting trip records, vehicles, and audit trails. |
| **`redis`** | `redis:7-alpine` | `6379:6379` | `redis-cli ping` | In-memory cache and background message queue. |

---

## 3. Persistent Docker Volumes

| Volume Name | Container Target Path | Purpose |
| :--- | :--- | :--- |
| `anpr_postgres_data` | `/var/lib/postgresql/data` | Database tables & records |
| `anpr_redis_data` | `/data` | Redis cache persistence |
| `anpr_uploads_data` | `/app/backend/uploads` | Uploaded images & video crops |
| `anpr_models_data` | `/app/models` | Exported ONNX / TensorRT models |
| `anpr_logs_data` | `/app/logs` | Diagnostic & application logs |

---

## 4. Single-Command Launch & Workflows

### Standard Launch
```bash
docker compose up --build
```

### Production Launch (Background Daemon with Restart Policies)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Inspect Container Status & Health
```bash
docker compose ps
```

### View Live Container Logs
```bash
docker compose logs -f backend
```

### Stopping Containers
```bash
docker compose down
```
To remove volumes as well: `docker compose down -v`.
