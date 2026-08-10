# Docker Containerization & Deployment Runbook

This document details the multi-container production deployment architecture for the Industrial Vehicle Trip Management System using Docker, Docker Compose, PostgreSQL 16, Nginx, and FastAPI.

---

## 1. Multi-Container Architecture

```
                                  [ User / Browser ]
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │    Frontend Container   │
                             │  (Nginx + React @ 3000) │
                             └────────────┬────────────┘
                                          │  Reverse Proxy (/api/*)
                                          ▼
                             ┌─────────────────────────┐
                             │    Backend Container    │
                             │  (FastAPI + AI @ 8000)  │
                             └──────┬───────────┬──────┘
                                    │           │
                     ┌──────────────┘           └──────────────┐
                     ▼                                         ▼
        ┌─────────────────────────┐               ┌─────────────────────────┐
        │   PostgreSQL Container  │               │     Redis Container     │
        │  (Postgres 16 @ 5432)   │               │   (Redis Cache @ 6379)  │
        └─────────────────────────┘               └─────────────────────────┘
```

---

## 2. Prerequisites

1. **Docker Desktop** installed (Windows, macOS, or Linux).
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Verify Docker & Compose installation:
   ```bash
   docker --version
   docker compose version
   ```

---

## 3. Quickstart - Single Command Launch

To build, initialize the database, execute migrations, and start all services:

```bash
# 1. Clone repository
git clone https://github.com/your-org/ANPR-Trip-Management.git
cd ANPR-Trip-Management

# 2. Setup environment configuration
cp .env.example .env

# 3. Launch full stack with Docker Compose
docker compose up --build
```

Access Applications:
- **React Web UI**: `http://localhost:3000`
- **FastAPI API Docs**: `http://localhost:8000/docs`
- **System Health Endpoint**: `http://localhost:8000/api/system/health`

---

## 4. Useful Docker Commands

### Run Containers in Background (Detached Mode)
```bash
docker compose up -d
```

### Check Container Status & Health
```bash
docker compose ps
```

### View Application Logs
```bash
# All service logs
docker compose logs -f

# Backend logs only
docker compose logs -f backend

# Frontend logs only
docker compose logs -f frontend
```

### Stop All Containers
```bash
docker compose down
```

### Stop & Delete Persistent Volumes (Full Reset)
```bash
docker compose down -v
```

### Force Rebuild Containers Without Cache
```bash
docker compose build --no-cache
docker compose up -d
```

---

## 5. Production Deployment Configuration

For production environments with log rotation, restart policies, and resource limits:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 6. Docker Persistent Volumes

The following Docker volumes ensure zero data loss across container rebuilds:

| Volume Name | Target Path inside Container | Description |
| :--- | :--- | :--- |
| `anpr_postgres_data` | `/var/lib/postgresql/data` | PostgreSQL database files |
| `anpr_redis_data` | `/data` | Redis persistent cache |
| `anpr_uploads_data` | `/app/backend/uploads` | Uploaded images & video crops |
| `anpr_models_data` | `/app/models` | Exported ONNX / TensorRT AI models |
| `anpr_logs_data` | `/app/logs` | Application & system diagnostic logs |

---

## 7. Troubleshooting

### Issue 1: `Port 5432 or 8000 is already in use`
- **Cause**: A local instance of PostgreSQL or Uvicorn is already running on the host system.
- **Solution**: Stop local services:
  - Windows: Stop `postgresql-x64-16` in Services.
  - Linux/macOS: `sudo systemctl stop postgresql`.

### Issue 2: `Backend fails with database connection refused`
- **Cause**: Backend container started before PostgreSQL finished initialization.
- **Solution**: The `entrypoint.sh` script automatically retries connection for 60 seconds. Ensure `postgres` service status is `healthy`.

### Issue 3: `Nvidia GPU acceleration in Docker`
- **Requirement**: Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
- Set `GPU_ENABLED=true` in `.env`.
