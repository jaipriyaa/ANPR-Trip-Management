# Industrial Vehicle Trip Management System - TFrenzy Submission

An enterprise-grade, edge-native industrial platform for real-time Vehicle Detection, License Plate Recognition (ANPR), SORT Vehicle Tracking, Gate Automation, Trip Lifecycle Scheduling, Dwell-Time Analytics, Access Control, and Multi-Backend Acceleration (TensorRT / ONNX / PyTorch).

---

  ## Executive Overview & Key Features

-  **YOLOv11 Vehicle Detection & Sub-Type Classification**: Detects and categorizes Cars, SUVs, Pickup Trucks, Heavy Trucks, Mini Trucks, Buses, Vans, Motorcycles, and Auto Rickshaws.
-  **YOLOv11 License Plate Detection & Cropping**: High-precision localization of Indian standard, commercial, tilted, damaged, and dirty plates.
-  **Multi-Pass OCR Engine & Indian Regex Correction**: Multi-stage OCR ensemble with confusion matrix correction (`0`<->`O`, `1`<->`I`, `8`<->`B`, `5`<->`S`).
-  **Multi-Backend Inference Acceleration**: Automatic selection & fallback order: **NVIDIA TensorRT (FP16)** → **ONNX Runtime (CUDA/CPU)** → **PyTorch YOLO**.
-  **Gate Automation & Live Control Room**: Real-time camera feeds, RTSP stream ingestion, automated boom barrier triggers, and access decision logging.
-  **Trip Lifecycle Engine**: Tracks trips from `PLANNED` → `REGISTERED` → `IN_PLANT` → `COMPLETED` / `CANCELLED` with dwell-time alerts.
-  **Authorization Engine**: Whitelist, Watchlist, and Automated Gate Decision Engine.
-  **Manual Review Queue**: Human-in-the-loop UI for low-confidence OCR scans with automated feedback dataset collection.
-  **Performance Benchmarking & Telemetry**: Built-in latency, FPS, CPU, RAM, and GPU profiling dashboard.
-  **Single-Command Production Docker Launch**: Complete multi-container stack (`React`, `FastAPI`, `PostgreSQL 16`, `Redis`) started via `docker compose up --build`.

---

##  Technology Stack

- **Backend**: FastAPI, Python 3.11+, SQLAlchemy 2.0 ORM, Alembic, Pydantic V2, PostgreSQL 16, Redis 7
- **Frontend**: React 18, Vite, TailwindCSS, TanStack Query, Axios, Lucide Icons, React Router v6
- **AI Engine**: PyTorch, Ultralytics YOLOv11, SORT Tracker, OpenCV, EasyOCR, ONNX Runtime, NVIDIA TensorRT
- **Containerization**: Docker, Docker Compose, Nginx

---

##  Quickstart - Running the System

### Option A: Single-Command Docker Deployment (Recommended)
```bash
# 1. Clone repository
git clone https://github.com/your-org/ANPR-Trip-Management.git
cd ANPR-Trip-Management

# 2. Copy environment configuration
cp .env.example .env

# 3. Launch full stack
docker compose up --build
```
- **React Frontend**: `http://localhost:3000`
- **FastAPI API Documentation**: `http://localhost:8000/docs`
- **System Health Check**: `http://localhost:8000/api/system/health`

---

### Option B: Local Manual Start

#### 1. Backend Server
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1 | Linux: source venv/bin/activate
pip install -r requirements.txt
python create_tables.py
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```

---

### Option C: NVIDIA Jetson Edge Deployment
```bash
# On target NVIDIA Jetson hardware:
python deployment/system_check.py
python deployment/export_onnx.py
bash deployment/generate_engine.sh
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

##  Project Structure Overview

```
ANPR-Trip-Management/
├── backend/            # FastAPI Python Application & AI Pipeline
├── frontend/           # ReactJS Frontend Web Application
├── deployment/         # ONNX Exporter, TensorRT scripts, System Check, Runbooks
├── models/             # Exported ONNX & TensorRT Engine Models
├── tests/              # Pytest Unit & Integration Test Suites (44 Passing Tests)
├── docs/               # Enterprise Documentation Package (15 Technical Manuals)
├── docker-compose.yml  # Docker Multi-Container Orchestration
├── DEMO_SCRIPT.md      # 8-10 Minute Live Presentation & Demo Guide
└── SUBMISSION_CHECKLIST.md # Final Submission Audit Checklist
```

---

##  Complete Documentation Package

Explore detailed technical manuals inside [`docs/`](docs/README.md):
-  [**System Architecture & Diagrams**](docs/ARCHITECTURE.md)
-  [**Installation Guide**](docs/INSTALL.md)
-  [**Docker Deployment Guide**](docs/DOCKER_DEPLOYMENT.md)
-  [**Jetson & TensorRT Deployment**](docs/JETSON_DEPLOYMENT.md)
-  [**Performance Benchmark Report**](docs/BENCHMARK_REPORT.md)
-  [**Test Suite Report**](docs/TEST_REPORT.md)
-  [**REST API Documentation**](docs/API_DOCUMENTATION.md)
-  [**User Manual**](docs/USER_MANUAL.md)

---

##  Verification & Automated Tests

Run system hardware check and the automated pytest suite:
```bash
python deployment/system_check.py
pytest tests/
```
Result: **44 passed in 4.24s (100% Pass Rate)**.
