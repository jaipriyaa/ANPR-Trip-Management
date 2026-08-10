# TensorRT Inference Optimization Guide

This guide provides deep technical documentation on TensorRT optimization, precision modes, memory management, and execution provider configuration for the Industrial ANPR Trip Management System.

---

## 1. Precision Modes & Acceleration

TensorRT provides massive latency reductions through low-precision quantization on Tensor Cores:

| Precision | Bit Width | Speedup vs FP32 | Accuracy Drop | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **FP32** | 32-bit float | 1.0x (Baseline) | 0.0% | Development / Debugging |
| **FP16** | 16-bit half | **2.5x - 4.0x** | < 0.1% | **Production Default for Jetson** |
| **INT8** | 8-bit integer | **4.5x - 7.0x** | < 0.5% (with Calibration) | Ultra High-Throughput Multi-Camera |

---

## 2. Generating TensorRT Engines with `trtexec`

### FP16 Precision Command (Standard Jetson Build)
```bash
trtexec --onnx=models/vehicle_detector.onnx \
        --saveEngine=models/vehicle_detector.engine \
        --fp16 \
        --workspace=2048 \
        --verbose
```

### Dynamic Input Shape Optimization
If batch sizes or image resolutions vary dynamically:
```bash
trtexec --onnx=models/vehicle_detector.onnx \
        --saveEngine=models/vehicle_detector.engine \
        --minShapes=images:1x3x640x640 \
        --optShapes=images:4x3x640x640 \
        --maxShapes=images:8x3x640x640 \
        --fp16
```

---

## 3. Execution Provider Fallback Architecture

The ANPR AI pipeline utilizes a tri-level fallback hierarchy managed by `backend_selector.py`:

```
┌──────────────────────────────────────────────────────────┐
│ 1. TensorRT Engine (.engine / TensorrtExecutionProvider)  │  <- Lowest Latency (< 8ms)
└──────────────────────────┬───────────────────────────────┘
                           │ Fallback if engine missing / unsupported
                           ▼
┌──────────────────────────────────────────────────────────┐
│ 2. ONNX Runtime (.onnx / CUDAExecutionProvider)          │  <- Accelerated GPU (< 20ms)
└──────────────────────────┬───────────────────────────────┘
                           │ Fallback if ONNX fails / GPU unavailable
                           ▼
┌──────────────────────────────────────────────────────────┐
│ 3. PyTorch YOLO (.pt / CPU Execution)                    │  <- Universal Fallback
└──────────────────────────────────────────────────────────┘
```

---

## 4. Benchmarks & Expected Performance on Jetson AGX Orin

| Model Component | Batch Size | Backend | Resolution | Inference Latency |
| :--- | :--- | :--- | :--- | :--- |
| Vehicle Detector | 1 | PyTorch (CPU) | 640x640 | ~140.0 ms |
| Vehicle Detector | 1 | ONNX (CUDA) | 640x640 | ~18.5 ms |
| Vehicle Detector | 1 | **TensorRT (FP16)** | 640x640 | **~4.2 ms** |
| Plate Detector | 1 | **TensorRT (FP16)** | 640x640 | **~3.8 ms** |
