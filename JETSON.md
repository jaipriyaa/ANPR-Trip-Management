# NVIDIA Jetson Edge Deployment Guide

This guide details the deployment, configuration, TensorRT engine compilation, and performance optimization for running the **Industrial Vehicle Trip Management System** on NVIDIA Jetson Edge devices.

---

## 1. Supported Jetson Hardware Matrix

The system is optimized for NVIDIA Jetson ARM64 SoCs, leveraging CUDA, cuDNN, and TensorRT for low-latency (< 30 ms) edge inference.

| Jetson Hardware Model | SoC Architecture | CUDA Cores | Tensor Cores | Recommended Precision |
| :--- | :--- | :--- | :--- | :--- |
| **NVIDIA Jetson Nano** | Maxwell (4GB) | 128 | 0 | FP32 / ONNX CPU Fallback |
| **NVIDIA Jetson Xavier NX** | Volta (8GB/16GB) | 384 | 48 | FP16 TensorRT |
| **NVIDIA Jetson AGX Xavier** | Volta (16GB/32GB)| 512 | 64 | FP16 TensorRT |
| **NVIDIA Jetson Orin Nano** | Ampere (4GB/8GB) | 512 / 1024 | 16 / 32 | FP16 TensorRT |
| **NVIDIA Jetson Orin NX** | Ampere (8GB/16GB)| 1024 / 1792| 32 / 56 | FP16 TensorRT |
| **NVIDIA Jetson AGX Orin** | Ampere (32GB/64GB)| 1792 / 2048| 56 / 64 | FP16 / INT8 TensorRT |

---

## 2. Software Requirements & JetPack Compatibility

Ensure your Jetson hardware is flashed with a supported JetPack OS version:

- **L4T / Linux OS**: Ubuntu 20.04 LTS (L4T 35.4.1+) or Ubuntu 22.04 LTS (L4T 36.3.0+)
- **JetPack Version**: JetPack 5.1.2+ or JetPack 6.0+
- **CUDA Toolkit**: CUDA 11.8+ or CUDA 12.2+
- **cuDNN**: cuDNN 8.6+ or 8.9+
- **TensorRT**: TensorRT 8.5.2+ or 8.6.1+
- **Python**: Python 3.8, 3.10, or 3.11

---

## 3. Jetson Deployment Workflow

```
[ Flash Jetson Board (JetPack 5.1 / 6.0) ]
                    │
                    ▼
[ Install Dependencies & Clone Repository ]
                    │
                    ▼
[ Export ONNX Models (export_onnx.py) ]
                    │
                    ▼
[ Compile Native TensorRT Engines (generate_engine.sh) ]
                    │
                    ▼
[ System Verification (system_check.py) ]
                    │
                    ▼
[ Launch Application (Docker Compose / Native Uvicorn) ]
```

---

## 4. Step-by-Step Installation Runbook

### Step 1: Clone Repository
```bash
git clone https://github.com/jaipriyaa/ANPR-Trip-Management.git
cd ANPR-Trip-Management
```

### Step 2: Virtual Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
```

### Step 3: Database Migration
```bash
cd backend
python run_migrations.py
cd ..
```

### Step 4: Environment Variables (`.env`)
Copy and adjust `.env`:
```bash
cp .env.example .env
```
Ensure `.env` contains:
```env
MODEL_BACKEND=TENSORRT
GPU_ENABLED=true
GPU_DEVICE=0
TENSORRT_ENGINE_PATH=models/
```

### Step 5: Export ONNX Models & Build TensorRT Engines
Run the ONNX export script followed by TensorRT FP16 engine generation:
```bash
# 1. Export PyTorch checkpoints to ONNX
python deployment/export_onnx.py

# 2. Compile native FP16 TensorRT engines on Jetson GPU
bash deployment/generate_engine.sh
```

---

## 5. Running the Application on Jetson

### Option A: Docker Container (Recommended)
```bash
docker compose up --build -d
```

### Option B: Native Execution
- **Backend**:
  ```bash
  cd backend
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
  ```
- **Frontend**:
  ```bash
  cd frontend
  npm run dev
  ```

---

## 6. Jetson Edge Optimization Best Practices

1. **Set Maximum Performance Mode**:
   ```bash
   sudo nvpmodel -m 0
   sudo jetson_clocks
   ```
2. **Use FP16 Precision**: TensorRT FP16 yields a **~4x speedup** over FP32 on Jetson Tensor Cores with zero loss in recognition accuracy.
3. **Hardware-Accelerated Video Decoding**:
   Utilize GStreamer hardware decoders (`nvv4l2decoder`) for high-resolution camera RTSP streams to offload CPU decoding:
   ```bash
   rtspsrc location=rtsp://camera_ip:554/live ! rtph264depay ! nvv4l2decoder ! nvvidconv ! video/x-raw, format=BGRx ! appsink
   ```
