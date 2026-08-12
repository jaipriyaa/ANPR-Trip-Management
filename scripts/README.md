# Enterprise ANPR & Vehicle Trip Management Platform - Scripts & Automation Directory

This directory contains cross-platform operational scripts (`.sh` for Linux/macOS/Git Bash and `.bat` for Windows CMD) for environment setup, service execution, production builds, hardware benchmarking, regression testing, data retention, Docker orchestration, and workspace cleanup.

---

## 📁 Available Scripts Overview

| Script Name | Operating System | Purpose & Function |
| :--- | :--- | :--- |
| [`setup.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/setup.sh) / [`setup.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/setup.bat) | Linux / Windows | Sets up Python venv (`backend/venv`), installs pip & npm dependencies, creates `.env`, and initializes DB schema. |
| [`start.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/start.sh) / [`start.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/start.bat) | Linux / Windows | Launches FastAPI backend server (Port 8000) and React frontend dev server (Port 3000). Supports `--backend`, `--frontend`, or `--docker`. |
| [`build.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/build.sh) / [`build.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/build.bat) | Linux / Windows | Compiles React production bundle (`frontend/dist`), exports ONNX AI models, and builds Docker container images. |
| [`benchmark.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/benchmark.sh) / [`benchmark.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/benchmark.bat) | Linux / Windows | Runs hardware diagnostic check, Jetson/TensorRT/ONNX latency & FPS benchmarking, and end-to-end pipeline validation. |
| [`test.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/test.sh) / [`test.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/test.bat) | Linux / Windows | Executes full pytest regression test suite across all target modules, or custom pytest target arguments. |
| [`retention.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/retention.sh) / [`retention.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/retention.bat) | Linux / Windows | Executes automated data retention and archival jobs in `--dry-run` or `--active` deletion mode. |
| [`docker_run.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/docker_run.sh) / [`docker_run.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/docker_run.bat) | Linux / Windows | Manages Docker multi-container stack (`up`, `daemon`, `down`, `build`, `logs`, `status`, `restart`). |
| [`cleanup.sh`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/cleanup.sh) / [`cleanup.bat`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/scripts/cleanup.bat) | Linux / Windows | Cleans `__pycache__`, `.pytest_cache`, `.coverage`, logs (`*.log`), `frontend/dist`, and temporary files. |

---

## 🚀 Quickstart Usage Guide

### 1. Environment Setup
**Linux / macOS / Git Bash:**
```bash
bash scripts/setup.sh
```
**Windows CMD:**
```cmd
scripts\setup.bat
```

### 2. Launch Local Development Stack
**Linux / macOS / Git Bash:**
```bash
# Start both Backend + Frontend
bash scripts/start.sh

# Start backend only
bash scripts/start.sh backend

# Start frontend only
bash scripts/start.sh frontend
```
**Windows CMD:**
```cmd
# Start both Backend (in new CMD window) + Frontend
scripts\start.bat

# Start backend only
scripts\start.bat backend
```

### 3. Run Automated Pytest Suite
```bash
# Linux / macOS
bash scripts/test.sh

# Windows CMD
scripts\test.bat
```

### 4. Run Benchmarks & System Diagnostics
```bash
# Linux / macOS
bash scripts/benchmark.sh

# Windows CMD
scripts\benchmark.bat
```

### 5. Docker Orchestration
```bash
# Linux / macOS
bash scripts/docker_run.sh up
bash scripts/docker_run.sh daemon
bash scripts/docker_run.sh down

# Windows CMD
scripts\docker_run.bat up
scripts\docker_run.bat daemon
scripts\docker_run.bat down
```

### 6. Workspace Cleanup
```bash
# Linux / macOS
bash scripts/cleanup.sh

# Windows CMD
scripts\cleanup.bat
```
