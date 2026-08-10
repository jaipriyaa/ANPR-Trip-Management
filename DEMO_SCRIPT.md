# Industrial Vehicle Trip Management System - 8-10 Minute Presentation & Live Demonstration Plan

This document provides a step-by-step presentation script and live demonstration workflow for the **TFrenzy Final Evaluation Review**.

---

## ⏱️ Presentation Timing Overview (8 - 10 Minutes Total)

| Step # | Topic / Module | Allocated Time | Target View / Screen |
| :--- | :--- | :--- | :--- |
| **1** | **Project Introduction & Architecture** | 0:30 min | Presentation Overview / Architecture Diagram |
| **2** | **System Login & Operational Navigation** | 0:30 min | React Web UI Header & Sidebar Navigation |
| **3** | **Vehicle & Driver Master Management** | 0:45 min | `/transporters`, `/vehicles`, `/drivers` |
| **4** | **AI Single Image Recognition** | 0:45 min | `/vehicle-recognition` (Image Upload) |
| **5** | **AI Video Recognition & Tracking** | 0:45 min | `/vehicle-recognition` (Video Processing) |
| **6** | **Multi-Frame OCR Fusion & Correction** | 0:45 min | `/manual-review`, `/ocr-feedback` |
| **7** | **Trip Creation & Lifecycle Engine** | 0:45 min | `/trips` (PLANNED -> REGISTERED -> COMPLETED) |
| **8** | **Entry & Exit Event Tracking** | 0:45 min | `/entry-exit` |
| **9** | **Authorization Engine & Gate Decisions** | 0:45 min | `/whitelist`, `/watchlist`, `/gate-decisions` |
| **10** | **Live Gate Control Room Monitor** | 0:45 min | `/live-gate` |
| **11** | **Performance Benchmarking Dashboard** | 0:45 min | `/performance-dashboard` |
| **12** | **Industrial Reports & Analytics** | 0:30 min | `/reports`, `/analytics` |
| **13** | **Docker Single-Command Deployment** | 0:30 min | Terminal (`docker compose up --build`) |
| **14** | **NVIDIA Jetson Deployment Overview** | 0:30 min | Jetson Engine Scripts & Benchmarks |

---

## 🎬 Detailed Step-by-Step Demonstration Plan

### Step 1: Project Introduction & Problem Statement (0:00 - 0:30)
- **Script**: "Welcome judges and evaluators. Today we present the Industrial Vehicle Trip Management System—an enterprise edge platform built for high-speed industrial logistics, real-time ANPR plate recognition, trip lifecycle scheduling, and automated gate access control."
- **Key Highlight**: Point out edge-native AI inference execution (< 30ms latency) and multi-backend acceleration.

### Step 2: Login & Navigation Overview (0:30 - 1:00)
- **Screen**: React Web Interface (`http://localhost:3000`).
- **Script**: "The platform features a modern dark-mode responsive dashboard with 5 operational navigation groups: Master Data, Gate Operations, Data Engineering Pipeline, Security Authorization, and Enterprise Analytics."

### Step 3: Vehicle & Driver Master Management (1:00 - 1:45)
- **Screen**: Transporters (`/transporters`), Vehicle Master (`/vehicles`), Drivers (`/drivers`).
- **Demo Action**:
  - Show registered logistics transporter "Apex Logistics Services".
  - Demonstrate vehicle registration "KA01AB1234" assigned to a Heavy Truck category.

### Step 4: AI Image Recognition (1:45 - 2:30)
- **Screen**: AI Recognition (`/vehicle-recognition`).
- **Demo Action**:
  - Drag and drop a vehicle test image.
  - Show instant bounding box visualization: Vehicle Detection (YOLOv11), Plate Detection, Perspective Rectification, and Multi-pass OCR extracted plate text.

### Step 5: AI Video Recognition & Tracking (2:30 - 3:15)
- **Screen**: AI Video Recognition (`/vehicle-recognition`).
- **Demo Action**:
  - Process a video file.
  - Highlight DeepSORT vehicle tracking IDs maintaining tracklets across frames with speed & bounding box stability.

### Step 6: Multi-Frame Recognition & Fusion (3:15 - 4:00)
- **Screen**: Manual Review Queue (`/manual-review`) & OCR Feedback (`/ocr-feedback`).
- **Demo Action**:
  - Show how low-confidence scans trigger human-in-the-loop verification.
  - Edit a character, save correction, and demonstrate feedback dataset collection for future fine-tuning.

### Step 7: Trip Lifecycle Creation & Engine (4:00 - 4:45)
- **Screen**: Trip Engine (`/trips`).
- **Demo Action**:
  - Create a new trip ticket (PLANNED status).
  - Simulate gate entry (REGISTERED -> IN_PLANT status) and show dwell-time calculation.

### Step 8: Entry & Exit Event Tracking (4:45 - 5:30)
- **Screen**: Entry/Exit Logs (`/entry-exit`).
- **Demo Action**: Filter real-time movement logs by gate ID, date range, and movement type (ENTRY/EXIT).

### Step 9: Authorization Engine & Gate Decisions (5:30 - 6:15)
- **Screen**: Whitelist (`/whitelist`), Watchlist (`/watchlist`), Gate Decisions Log (`/gate-decisions`).
- **Demo Action**:
  - Demonstrate instant `ALLOW` decision for a whitelisted vehicle.
  - Demonstrate security alert and `DENY` decision when a watchlisted vehicle scans at a gate.

### Step 10: Live Control Room Monitor (6:15 - 7:00)
- **Screen**: Live Control Room (`/live-gate`).
- **Demo Action**: Show real-time telemetry, simulated RTSP camera stream overlay, recent gate scans, and manual boom-barrier override.

### Step 11: Performance Dashboard (7:00 - 7:45)
- **Screen**: Performance Benchmarks (`/performance-dashboard`).
- **Demo Action**:
  - Show live FPS (32+ FPS), complete pipeline latency (28.5 ms), and hardware usage (CPU %, RAM MB).
  - Show the backend comparison matrix (PyTorch vs ONNX vs TensorRT).
  - Click "Run Benchmark Suite" to trigger an on-demand performance run.

### Step 12: Industrial Reports & Analytics (7:45 - 8:15)
- **Screen**: Reports (`/reports`) & Analytics (`/analytics`).
- **Demo Action**: Show trip volume charts, dwell-time distribution, and generate PDF/Excel export.

### Step 13: Docker Single-Command Deployment (8:15 - 8:45)
- **Screen**: Terminal & Docker Desktop.
- **Demo Action**:
  - Execute `docker compose up --build`.
  - Highlight automatic PostgreSQL container initialization, health check wait, and instant FastAPI + React launch.

### Step 14: NVIDIA Jetson & TensorRT Overview (8:45 - 9:15)
- **Screen**: `deployment/generate_engine.sh` & `docs/JETSON_DEPLOYMENT.md`.
- **Script**: "For edge deployment on NVIDIA Jetson hardware, our deployment script compiles ONNX models into native FP16 TensorRT engines, accelerating pipeline latency down to 4.1ms (243 FPS)."
- **Conclusion**: "This concludes our presentation. Thank you."
