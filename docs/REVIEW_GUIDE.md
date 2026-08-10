# Evaluator & Code Reviewer Guide

Welcome to the review guide for the **Industrial Vehicle Trip Management System**. This document helps technical reviewers, evaluators, and judges quickly inspect, run, deploy, and verify the codebase.

---

## 1. Quick Navigation & File Map for Evaluators

| What are you looking for? | File Path |
| :--- | :--- |
| **Master Project README** | [`README.md`](../README.md) |
| **Documentation Hub & Index** | [`docs/README.md`](README.md) |
| **Single-Command Docker Config** | [`docker-compose.yml`](../docker-compose.yml) |
| **Backend Source Code** | [`backend/app/`](../backend/app/) |
| **AI Inference Subsystem** | [`backend/app/ai/`](../backend/app/ai/) |
| **Exported ONNX Models** | [`models/vehicle_detector.onnx`](../models/vehicle_detector.onnx) (10.2 MB) |
| **Automated Test Suite (44 Tests)**| [`tests/`](../tests/) |
| **Hardware Diagnostic Script** | [`deployment/system_check.py`](../deployment/system_check.py) |
| **ONNX Exporter & Verifier** | [`deployment/export_onnx.py`](../deployment/export_onnx.py) |
| **Jetson TensorRT Build Script** | [`deployment/generate_engine.sh`](../deployment/generate_engine.sh) |
| **Generated Benchmark Reports** | [`debug/benchmark_reports/`](../debug/benchmark_reports/) |
| **Interactive API Documentation**| `http://localhost:8000/docs` (when running) |

---

## 2. How to Run & Evaluate the System

### Method A: Single-Command Docker Deployment (Recommended)
```bash
docker compose up --build
```
- Open browser to `http://localhost:3000` to interact with the React Web UI.
- Open browser to `http://localhost:8000/docs` to inspect interactive Swagger APIs.

### Method B: Local Environment Execution
```bash
# 1. Start Backend Server
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start Frontend Server (New Terminal)
cd frontend
npm run dev
```

---

## 3. How to Run Verification & Tests

### Step 1: Execute Hardware Diagnostic Check
```bash
python deployment/system_check.py
```
- **Expected Output**: `OVERALL STATUS: PASS - Core AI Pipeline & Inference Infrastructure Healthy!`

### Step 2: Run Full Pytest Automated Test Suite
```bash
pytest tests/ -v
```
- **Expected Output**: `44 passed in 4.47s (100% Pass Rate)`

---

## 4. Key Verification Touchpoints for Reviewers

1. **System Health API**: Visit `http://localhost:8000/api/system/health` to verify active inference backend resolution (`ONNX` / `TENSORRT`).
2. **AI Recognition View**: Visit `http://localhost:3000/vehicle-recognition` and upload an image to inspect YOLOv11 vehicle detection bounding box, plate cropping, perspective homography rectification, and EasyOCR character extraction.
3. **Performance Dashboard**: Visit `http://localhost:3000/performance-dashboard` to view live FPS, latency breakdown, hardware resource gauges, and the PyTorch vs ONNX vs TensorRT comparison matrix.
