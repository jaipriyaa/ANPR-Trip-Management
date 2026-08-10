# Edge ANPR & Vehicle Trip Management Platform — Setup & Execution Guide

This document contains all updated execution commands for running, testing, benchmarking, and deploying the **ANPR Vehicle & Trip Management Platform**.

---

## 1. Quick Start (Services Execution)

### Start Backend API Server (FastAPI / Uvicorn)
```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API**: `http://localhost:8000`
- **Interactive OpenAPI / Swagger Docs**: `http://localhost:8000/docs`

### Start Frontend Dashboard (React / Vite)
```bash
cd frontend
npm install
npm run dev
```
- **Frontend Dashboard UI**: `http://localhost:3000`

---

## 2. Complete Test Suite Execution (149/149 Passing Tests)

To run the entire repository regression test suite across all 9 target modules:

```bash
cd c:\Users\Manoj Kumar\Desktop\ANPR-Trip-Management
backend\venv\Scripts\python.exe -m pytest
```

### Run Specific Target Test Files:

```bash
# Target 1: Vehicle Detection & Model Basics
backend\venv\Scripts\python.exe -m pytest tests/test_vehicle_detector.py

# Target 1: Vehicle Tracking, Multi-Frame OCR Fusion & Deduplication
backend\venv\Scripts\python.exe -m pytest tests/test_tracking_fusion_dedup.py

# Target 2: Entry/Exit Matching, Trip State Engine & Dwell Time
backend\venv\Scripts\python.exe -m pytest tests/test_trip_state_machine.py

# Target 3: Daily Aggregation & Operational Reporting
backend\venv\Scripts\python.exe -m pytest tests/test_daily_reporting.py

# Target 4: Alert Engine & Multi-Channel Delivery
backend\venv\Scripts\python.exe -m pytest tests/test_alert_engine.py

# Target 5: Plate Correction Feedback & Data Retention / Archival
backend\venv\Scripts\python.exe -m pytest tests/test_retention_feedback.py

# Target 6: NVIDIA Jetson Edge Deployment & Backend Selection
backend\venv\Scripts\python.exe -m pytest tests/test_jetson_deployment.py

# Full Regression Across All 9 Test Files
backend\venv\Scripts\python.exe -m pytest tests/test_vehicle_detector.py tests/test_data_engineering_pipeline.py tests/test_recognition_regression.py tests/test_tracking_fusion_dedup.py tests/test_trip_state_machine.py tests/test_daily_reporting.py tests/test_alert_engine.py tests/test_retention_feedback.py tests/test_jetson_deployment.py
```

---

## 3. Data Retention & Archival Jobs

### Trigger Data Retention Cleanup (Dry-Run Mode — No Records Deleted)
```bash
# Via Python Service
backend\venv\Scripts\python.exe -c "
from app.database.connection import SessionLocal
from app.services.retention_service import retention_service
db = SessionLocal()
res = retention_service.run_retention_job(db, dry_run=True)
print(res)
db.close()
"
```

### Trigger Active Data Retention Cleanup (Archive Before Delete)
```bash
# Via Python Service
backend\venv\Scripts\python.exe -c "
from app.database.connection import SessionLocal
from app.services.retention_service import retention_service
db = SessionLocal()
res = retention_service.run_retention_job(db, dry_run=False)
print(res)
db.close()
"
```

### Check Retention Status via REST API:
- `GET http://localhost:8000/api/v1/admin/retention/status`
- `POST http://localhost:8000/api/v1/admin/retention/run?dry_run=true`

---

## 4. Manual Plate Correction & Retraining Dataset Export

### Submit Operator Plate Correction (API)
```bash
curl -X POST "http://localhost:8000/api/v1/manual-review/correct" \
  -H "Content-Type: application/json" \
  -d '{
    "original_plate": "OR02BU3389",
    "corrected_plate": "OR02BU3388",
    "reason": "OCR character misread 9 for 8",
    "reviewer": "Security Officer"
  }'
```
- Appends retraining metadata to `datasets/plate_correction_feedback/metadata.jsonl`.

---

## 5. NVIDIA Jetson Edge Deployment & Benchmarking (Target 6)

### Run Jetson Hardware & Model Verification
```bash
backend\venv\Scripts\python.exe deployment/jetson/verify_jetson.py
```

### Run Performance Latency & Throughput Benchmark
```bash
backend\venv\Scripts\python.exe deployment/jetson/benchmark_jetson.py
```

### Generate All Debug Validation Artifacts
```bash
backend\venv\Scripts\python.exe scratch/dump_target6_debug_artifacts.py
```

### Convert Models to TensorRT FP16 Engines (On NVIDIA Jetson Device)
```bash
cd deployment/jetson
chmod +x setup_jetson.sh build_tensorrt.sh
./setup_jetson.sh
./build_tensorrt.sh
```

---

## 6. Configurable Environment Variables (`.env`)

```env
# Backend & Database
API_V1_STR=/api/v1
DATABASE_URL=postgresql://postgres:1234@localhost:5432/anpr_db

# AI Inference Backend Selection: TENSORRT | ONNX | PYTORCH | AUTO
MODEL_BACKEND=AUTO
GPU_ENABLED=false
GPU_DEVICE=0
FP16_ENABLED=true
FRAME_SKIP=1
MAX_FPS=30.0

# Detection Thresholds
VEHICLE_DETECTION_CONFIDENCE=0.35
VEHICLE_DETECTION_IOU=0.45
VEHICLE_DETECTION_IMAGE_SIZE=640

# Data Retention Defaults (Days)
DETECTION_RETENTION_DAYS=90
ALERT_RETENTION_DAYS=60
AUDIT_LOG_RETENTION_DAYS=180
CAMERA_HEALTH_RETENTION_DAYS=30
RETENTION_DRY_RUN=false
```

---

## 7. Operational Documentation & Artifact Reports

- **Target 1 Report**: [`docs/TRIP_STATE_ENTRY_EXIT_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/TRIP_STATE_ENTRY_EXIT_REPORT.md)
- **Target 3 Report**: [`docs/DAILY_AGGREGATION_REPORTING_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/DAILY_AGGREGATION_REPORTING_REPORT.md)
- **Target 4 Report**: [`docs/ALERT_ENGINE_DELIVERY_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/ALERT_ENGINE_DELIVERY_REPORT.md)
- **Target 5 Report**: [`docs/PLATE_FEEDBACK_RETENTION_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/PLATE_FEEDBACK_RETENTION_REPORT.md)
- **Target 6 Report**: [`docs/JETSON_TENSORRT_DEPLOYMENT_REPORT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/JETSON_TENSORRT_DEPLOYMENT_REPORT.md)
