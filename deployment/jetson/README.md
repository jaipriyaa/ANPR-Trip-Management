# NVIDIA Jetson Orin / Xavier Edge Deployment & TensorRT Setup Guide

This package provides deployment scripts, TensorRT conversion utilities, and edge hardware verification tools for deploying the **Edge ANPR & Vehicle Trip Management Platform** on NVIDIA Jetson devices (Orin Nano, Orin NX, AGX Orin, Xavier NX).

---

## 1. Prerequisites
- **NVIDIA Jetson Board** with JetPack 5.x or JetPack 6.x (L4T r35.x / r36.x).
- **CUDA 11.4 / 12.2** & **TensorRT 8.5+** pre-installed via JetPack.
- **Python 3.8 / 3.10 / 3.11** environment.

---

## 2. Setup & Installation

Run the automated setup script on your Jetson device:

```bash
chmod +x setup_jetson.sh build_tensorrt.sh
./setup_jetson.sh
```

---

## 3. TensorRT Model Conversion

Convert the PyTorch / ONNX models to optimized TensorRT FP16 engines:

```bash
./build_tensorrt.sh
```

This will generate:
- `models/tensorrt/vehicle_detector_fp16.engine`
- `models/tensorrt/license_plate_detector_fp16.engine`

---

## 4. Hardware Verification & Benchmarking

Verify the deployment and run latency/throughput benchmarks:

```bash
python3 verify_jetson.py
python3 benchmark_jetson.py
```

---

## 5. Environment Variables & Configuration

Set backend mode to `TENSORRT` or `AUTO` in `.env`:

```env
MODEL_BACKEND=TENSORRT
FP16_ENABLED=true
GPU_ENABLED=true
GPU_DEVICE=0
```
