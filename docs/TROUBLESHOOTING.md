# Enterprise Troubleshooting & Diagnostic Manual

This manual details diagnostic workflows, error messages, root causes, and resolution steps across all system layers.

---

## 1. Diagnostic Decision Tree & Error Matrix

### 1.1 Database Connection Errors
- **Symptom**: `psycopg2.OperationalError: could not connect to server: Connection refused`
- **Root Cause**: PostgreSQL service is stopped or port `5432` is blocked.
- **Resolution**:
  - Check PostgreSQL service status: `sudo systemctl status postgresql` or Windows Services.
  - Verify `DATABASE_URL` in `.env`.
  - For Docker: verify container `anpr-postgres` is healthy (`docker compose ps`).

### 1.2 Docker Build & Compose Errors
- **Symptom**: `Error response from daemon: port is already allocated`
- **Root Cause**: Host port `3000`, `8000`, or `5432` is occupied by another local service.
- **Resolution**: Stop local Uvicorn/Nginx/Postgres instances or update host port mappings in `docker-compose.yml`.

### 1.3 CUDA & TensorRT Errors
- **Symptom**: `TensorRT Python bindings ('tensorrt') not found` or `.engine deserialization failed`
- **Root Cause**: Attempting to generate `.engine` files on Windows or incompatible CUDA version.
- **Resolution**: Do not build TensorRT engines on Windows. Compile engines natively on target NVIDIA Jetson Linux device (`bash deployment/generate_engine.sh`).

### 1.4 Model Loading Errors
- **Symptom**: `FileNotFoundError: yolo11n.pt`
- **Root Cause**: Model weights file is missing from `backend/`.
- **Resolution**: Ensure `yolo11n.pt` is present in `backend/` or update `VEHICLE_MODEL_PATH` in `.env`.

### 1.5 OpenCV & EasyOCR Errors
- **Symptom**: `ImportError: libGL.so.1: cannot open shared object file` inside Linux Docker container.
- **Root Cause**: Missing system OpenCV dependency libraries (`libgl1-mesa-glx`, `libglib2.0-0`).
- **Resolution**: Ensure `backend/Dockerfile` includes `apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx`.

---

## 2. System Hardware Diagnostic Utility

Run the automated diagnostic suite:
```bash
python deployment/system_check.py
```
This utility tests PyTorch, OpenCV, ONNX Runtime, EasyOCR, CUDA GPU availability, and TensorRT status, reporting an overall diagnostic verdict (`PASS`).
