# Industrial Vehicle Trip Management System - Complete Installation Guide

This document provides a comprehensive, step-by-step installation guide for setting up the environment on Windows, Linux, and NVIDIA Jetson platforms.

---

## 1. System Requirements & Prerequisites

### Hardware Requirements
- **Development Host**: x86_64 CPU (Intel Core i5/i7 or AMD Ryzen 5/7), 8 GB RAM (16 GB recommended), 10 GB free SSD disk space.
- **Edge Deployment Host**: NVIDIA Jetson AGX Orin, Orin NX, Orin Nano, or Xavier NX.

### Software Prerequisites
- **Python**: 3.11.x (64-bit)
- **Node.js**: 18.x or 20.x LTS
- **PostgreSQL**: 16.x (running locally or via Docker on port 5432)
- **Docker & Docker Compose**: Docker Engine 24.0+ and Compose v2.20+
- **Git**: 2.30+

---

## 2. Step-by-Step Manual Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/ANPR-Trip-Management.git
cd ANPR-Trip-Management
```

### Step 2: Backend Setup (Python Virtual Environment)
```bash
cd backend

# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Upgrade Pip & Install Dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 3: Frontend Setup (Node.js & npm)
```bash
cd ../frontend
npm install
```

### Step 4: Environment Variables Configuration
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```
Ensure `.env` contains valid PostgreSQL credentials:
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/anpr_db
MODEL_BACKEND=AUTO
GPU_ENABLED=false
GPU_DEVICE=0
SECRET_KEY=your_secret_key_here
API_V1_STR=/api/v1
```

### Step 5: Database Creation & Alembic Migrations
Ensure PostgreSQL service is running and `anpr_db` exists:
```bash
# Navigate to backend directory with venv active
cd backend

# Create Database Tables via SQLAlchemy ORM
python create_tables.py

# Run Alembic Database Migrations
alembic upgrade head
```

---

## 3. Running the System

### Running Backend (FastAPI Development Server)
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **FastAPI Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc API Documentation**: `http://localhost:8000/redoc`
- **Health Check API**: `http://localhost:8000/api/system/health`

### Running Frontend (React Development Server)
```bash
cd frontend
npm run dev
```
- **React Application Web UI**: `http://localhost:3000`

### Running via Docker Compose (Single Command)
```bash
# In project root:
docker compose up --build
```

---

## 4. Common Installation Errors & Troubleshooting

| Error Symptom | Root Cause | Resolution |
| :--- | :--- | :--- |
| `psycopg2.OperationalError: connection refused` | PostgreSQL not running on port 5432 or `anpr_db` not created | Start PostgreSQL service (`sudo systemctl start postgresql` or Windows Services) and create database `anpr_db`. |
| `FileNotFoundError: yolo11n.pt` | Model weights missing from `backend/` | Ensure `yolo11n.pt` exists in `backend/` or update `VEHICLE_MODEL_PATH` in `.env`. |
| `Port 3000 or 8000 already in use` | Local process occupying port | Terminate existing Uvicorn/Node processes or modify port bindings in `docker-compose.yml`. |
| `TensorRT bindings not found` | Attempting TensorRT generation on Windows x86 | TensorRT engines must be generated natively on NVIDIA Jetson Linux hardware. Use `MODEL_BACKEND=ONNX` on Windows. |

---

## 5. System Verification Steps

Run system diagnostics and the automated test suite to verify installation:

```bash
# 1. Run Hardware Diagnostic Check
python deployment/system_check.py

# 2. Run Full Pytest Automated Test Suite (44 Tests)
pytest tests/
```
All 44 automated tests should pass with `0 errors`.
