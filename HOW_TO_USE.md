# User Guide & Operations Manual

This document details how to start, operate, and interact with the **Industrial Vehicle Trip Management System** via the Web Interface, REST API, and command-line execution tools.

---

## 1. Quick Start / Starting Services

### Option A: Launcher Script (Recommended)
Run the root startup script:
```bash
bash start.sh
```

### Option B: Docker Compose
```bash
docker compose up --build -d
```

### Option C: Manual CLI Execution
- **Backend**:
  ```bash
  cd backend
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```

Access Points:
- **Web UI**: `http://localhost:5173`
- **FastAPI API & Swagger UI**: `http://localhost:8000/docs`
- **ReDoc UI**: `http://localhost:8000/redoc`

---

## 2. Web Interface Walkthrough

The web dashboard is organized into four core modules:

### 1. Vehicle Recognition (ANPR Live Pipeline)
- **Live Video & Image Recognition**: Upload video files (`.mp4`, `.avi`, `.mov`) or static vehicle images (`.jpg`, `.png`).
- **Detection Pipeline Viz**: Displays step-by-step visual pipeline execution:
  1. Input Frame / Ingestion
  2. Vehicle Detection Box (`car`, `motorcycle`, `bus`, `truck`)
  3. Bounding Box License Plate Cropping
  4. Perspective Homography Correction & Contrast Enhancement
  5. OCR Engine Recognition Output & Confidence Score
- **Multi-Frame Deduplication & Track Smoothing**: Prevents duplicate entry logs for the same vehicle as it passes through the gate camera field of view.

### 2. Industrial Reports & Trip Logs
- **Trip Records**: Filter records by gate location (Entry / Exit), date range, vehicle type, and license plate number.
- **Video Preview**: Review stored video clips and vehicle snapshot crops associated with each detection event.
- **Exporting Data**: Export aggregated daily trip summary reports as CSV or Excel spreadsheets.

### 3. Manual Review Queue
- **Low Confidence Safeguard**: When plate text confidence falls below configured thresholds (e.g., `< 85%`) or when plates are obstructed, events are flagged as `REQUIRES MANUAL REVIEW`.
- **Human Verification UI**: Gate operators can review cropped plate images side-by-side with original frames and manually override or verify license plate strings.

### 4. Alert Engine & System Health
- **System Monitoring**: View CPU/GPU utilization, RAM memory profile, active backend execution provider (`PyTorch`, `ONNX`, or `TensorRT FP16`), and system status.
- **Alert Rules**: Configure real-time alerts for unauthorized vehicles, expired trip durations, or unexpected gate entries.

---

## 3. REST API Usage & Core Endpoints

The system exposes RESTful APIs for camera stream ingestion, manual recognition requests, report extraction, and health checks.

### Key API Endpoints

| HTTP Method | Endpoint Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/system/health` | Backend status, GPU check, active AI backend |
| `POST` | `/api/recognition/process-image` | Upload image for single-frame ANPR recognition |
| `POST` | `/api/recognition/process-video` | Upload video file for batch/frame-by-frame processing |
| `GET` | `/api/trips` | Query recorded vehicle trips with pagination |
| `GET` | `/api/reports/daily` | Get aggregated daily trip entry/exit report data |
| `POST` | `/api/manual-review/verify` | Submit operator verification for flagged plate |
| `GET` | `/api/benchmark/metrics` | Retrieve live latency & accuracy metrics |

### Example API Request (Python)

```python
import requests

url = "http://localhost:8000/api/recognition/process-image"
files = {"file": open("inputs/moving vehicle.mp4", "rb")}
response = requests.post(url, files=files)

print(response.json())
```

---

## 4. Input Recommendations & Supported Media

- **Supported Image Formats**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`
- **Supported Video Formats**: `.mp4`, `.avi`, `.mkv`, `.mov`
- **RTSP Streams**: Supported via OpenCV / GStreamer RTSP input URI string (`rtsp://user:pass@camera_ip:554/stream`).
- **Optimal Camera Angle**: Position gate cameras 15° - 30° relative to incoming traffic for highest OCR accuracy.
