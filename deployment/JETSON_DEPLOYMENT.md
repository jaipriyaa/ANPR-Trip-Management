# NVIDIA Jetson Production Deployment Runbook

This guide details the complete deployment process for setting up the Industrial Vehicle Trip Management System on NVIDIA Jetson Edge devices.

---

## 1. Step-by-Step Deployment Workflow

```
1. Clone Project Repo -> 2. Install Python Deps -> 3. Run System Check -> 4. Generate TensorRT Engines -> 5. Launch FastAPI Service
```

### Step 1: Clone Repository on Jetson
```bash
git clone https://github.com/your-organization/ANPR-Trip-Management.git
cd ANPR-Trip-Management
```

### Step 2: Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
```

### Step 3: Run System Check
```bash
python deployment/system_check.py
```

Expected Output:
```
=========================================================
INDUSTRIAL ANPR TRIP MANAGEMENT SYSTEM - SYSTEM DIAGNOSTICS
=========================================================
  PyTorch             : PASS
  OpenCV              : PASS
  ONNX Runtime        : PASS
  EasyOCR             : PASS
  CUDA                : PASS
  GPU Hardware        : PASS
  TensorRT            : PASS
=========================================================
OVERALL STATUS: PASS - Core AI Pipeline & Inference Infrastructure Healthy!
```

### Step 4: Export ONNX & Generate TensorRT Engines
```bash
# Export ONNX Models (if not pre-exported)
python deployment/export_onnx.py

# Compile TensorRT Engines on Jetson Hardware
bash deployment/generate_engine.sh
```

### Step 5: Configure Production Environment (`.env`)
```bash
cp .env.example .env
```
Ensure `.env` contains:
```env
MODEL_BACKEND=AUTO
GPU_ENABLED=true
GPU_DEVICE=0
TENSORRT_ENGINE_PATH=models/
```

### Step 6: Launch Application Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## 2. Systemd Production Service Setup

Create `/etc/systemd/system/anpr-backend.service`:

```ini
[Unit]
Description=Industrial ANPR Trip Management System FastAPI Service
After=network.target nvidia-persistenced.service

[Service]
Type=simple
User=jetson
WorkingDirectory=/home/jetson/ANPR-Trip-Management/backend
ExecStart=/home/jetson/ANPR-Trip-Management/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
Environment=MODEL_BACKEND=AUTO
Environment=GPU_ENABLED=true

[Install]
WantedBy=multi-user.target
```

Enable & Start Service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable anpr-backend
sudo systemctl start anpr-backend
sudo systemctl status anpr-backend
```

---

## 3. Jetson Performance Tuning

To maximize FPS and lower latency on Jetson hardware:

```bash
# Set Maximum Clock Speeds
sudo jetson_clocks

# Set Power Mode to Maximum
sudo nvpmodel -m 0
```
