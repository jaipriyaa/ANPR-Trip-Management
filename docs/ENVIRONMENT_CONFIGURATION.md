# Environment Configuration Specification

This document provides a detailed reference for all environment variables used across the backend, database, AI edge pipeline, and containerization layers.

---

## 1. Environment Variable Reference Matrix

| Variable Name | Purpose / Description | Default Value | Example Value |
| :--- | :--- | :--- | :--- |
| **`DATABASE_URL`** | PostgreSQL database connection string | `postgresql://postgres:1234@localhost:5432/anpr_db` | `postgresql://user:pass@postgres:5432/anpr_db` |
| **`SECRET_KEY`** | Secret key used for signing JWT authentication tokens | `supersecretkey123456789` | `e9f8a7b6c5d4e3f2a1` |
| **`API_V1_STR`** | API URL route prefix | `/api/v1` | `/api/v1` |
| **`MODEL_BACKEND`** | Primary AI inference backend mode (`AUTO`, `TENSORRT`, `ONNX`, `PYTORCH`) | `AUTO` | `AUTO` |
| **`VEHICLE_MODEL_PATH`** | File path to base PyTorch YOLOv11 vehicle model | `yolo11n.pt` | `backend/yolo11n.pt` |
| **`PLATE_MODEL_PATH`** | File path to base PyTorch YOLOv11 license plate model | `yolo11n.pt` | `backend/yolo11n.pt` |
| **`ONNX_MODEL_PATH`** | Directory path storing exported `.onnx` models | `models/` | `models/` |
| **`TENSORRT_ENGINE_PATH`**| Directory path storing compiled `.engine` TensorRT models | `models/` | `models/` |
| **`GPU_ENABLED`** | Enables CUDA GPU acceleration flag | `false` | `true` |
| **`GPU_DEVICE`** | Target CUDA GPU device ID | `0` | `0` |
| **`UPLOAD_FOLDER`** | File storage path for uploaded vehicle scans & crops | `uploads/` | `uploads/` |
| **`LOG_LEVEL`** | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` | `DEBUG` |
| **`OCR_THRESHOLD`** | Minimum confidence score threshold for EasyOCR plate text | `0.60` | `0.70` |
| **`DUPLICATE_WINDOW`** | Time window (seconds) for ignoring duplicate plate scans | `30` | `60` |

---

## 2. Configuration Profiles

### Development Configuration (`.env`)
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/anpr_db
MODEL_BACKEND=AUTO
GPU_ENABLED=false
GPU_DEVICE=0
LOG_LEVEL=DEBUG
```

### NVIDIA Jetson Hardware Configuration (`.env`)
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/anpr_db
MODEL_BACKEND=AUTO
GPU_ENABLED=true
GPU_DEVICE=0
TENSORRT_ENGINE_PATH=models/
LOG_LEVEL=INFO
```

### Docker Compose Container Configuration (`.env`)
```env
DATABASE_URL=postgresql://postgres:1234@postgres:5432/anpr_db
MODEL_BACKEND=AUTO
GPU_ENABLED=false
LOG_LEVEL=INFO
```
