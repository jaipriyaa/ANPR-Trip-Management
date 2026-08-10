# ONNX Model Export & Deployment Guide

This document details the ONNX export mechanism, model verification, environment configuration, and inference backend architecture for the Industrial Vehicle Trip Management System.

---

## 1. Overview & Architecture

The system supports multi-backend inference switching:
- **`PYTORCH`** (Default): Uses PyTorch YOLO model weights (`.pt`).
- **`ONNX`**: Uses ONNX Runtime (`.onnx`) with CPU or GPU (CUDA) execution providers for accelerated inference.
- **`TENSORRT`**: Placeholder architecture for future NVIDIA Jetson TensorRT acceleration.

### Model Pipeline Flow

```
Input Image/Video
       │
       ▼
┌───────────────────────────┐
│       Model Loader        │  (Configured via MODEL_BACKEND env: PYTORCH | ONNX | TENSORRT)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Preprocessing       │  (Letterbox resize to 640x640, RGB conversion, Normalization)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     Inference Engine      │  (Executes PyTorch model.forward() or ONNX session.run())
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Postprocessing       │  (Coordinate re-scaling, Sub-type classification, NMS)
└───────────────────────────┘
```

---

## 2. Expected Folder Structure

```
ANPR-Trip-Management/
├── .env.example                # Environment configuration template
├── deployment/
│   ├── export_onnx.py          # Automatic ONNX export script
│   ├── verify_onnx.py          # ONNX model verification script
│   └── ONNX_EXPORT.md          # Documentation
├── models/
│   ├── vehicle_detector.onnx   # Exported Vehicle Detector ONNX model
│   └── plate_detector.onnx     # Exported License Plate Detector ONNX model
└── backend/
    ├── yolo11n.pt              # Base PyTorch weights
    └── app/
        └── ai/
            ├── config/         # AI Configuration & Model Path Resolvers
            ├── vehicle_detector/
            ├── plate_detector/
            ├── ocr/
            └── weights/
```

---

## 3. How Export Works

The export script `deployment/export_onnx.py`:
1. Locates PyTorch weights dynamically (`VEHICLE_MODEL_PATH` / `PLATE_MODEL_PATH` or `backend/yolo11n.pt`).
2. Loads the model into Ultralytics YOLO.
3. Exports model to ONNX format using `opset=12`, `imgsz=640`, `dynamic=False`.
4. Saves exported `.onnx` files into `models/vehicle_detector.onnx` and `models/plate_detector.onnx`.
5. Verifies file sizes and logs absolute output paths.

### Running Export Command

```bash
# Run from project root directory using Python 3
python deployment/export_onnx.py
```

Expected Output:
```
[ONNX_Exporter] INFO: Starting Industrial Vehicle Trip Management System ONNX Export...
[ONNX_Exporter] INFO: --- Exporting Vehicle Detector ---
[ONNX_Exporter] INFO: ✓ EXPORT SUCCESS: Vehicle Detector -> models/vehicle_detector.onnx
[ONNX_Exporter] INFO: --- Exporting Plate Detector ---
[ONNX_Exporter] INFO: ✓ EXPORT SUCCESS: Plate Detector -> models/plate_detector.onnx
=========================================================
EXPORT SUMMARY
=========================================================
Vehicle Detector ONNX: SUCCESS
  Path: models/vehicle_detector.onnx
Plate Detector ONNX:   SUCCESS
  Path: models/plate_detector.onnx
=========================================================
```

---

## 4. How to Verify ONNX Models

The verification script `deployment/verify_onnx.py`:
1. Inspects file existence and size.
2. Performs ONNX graph integrity check (`onnx.checker.check_model`).
3. Creates ONNX Runtime `InferenceSession`.
4. Validates input shapes (`[1, 3, 640, 640]`) and output shapes.
5. Executes a test inference pass with dummy tensors.

### Running Verification Command

```bash
python deployment/verify_onnx.py
```

Expected Output:
```
=========================================================
INDUSTRIAL ANPR TRIP MANAGEMENT SYSTEM - ONNX VERIFICATION
=========================================================
[Vehicle Detector ONNX] RESULT: PASS
[Plate Detector ONNX] RESULT: PASS
=========================================================
OVERALL STATUS: PASS - All ONNX models verified successfully!
```

---

## 5. Configuring Backend Switching

In `.env` or environment settings:

```env
# Switch between PYTORCH and ONNX backends
MODEL_BACKEND=ONNX

# Hardware Acceleration
GPU_ENABLED=false

# Optional Model Path Overrides
VEHICLE_MODEL_PATH=backend/yolo11n.pt
PLATE_MODEL_PATH=backend/app/ai/weights/plate_detector.pt
ONNX_MODEL_PATH=models/
```

---

## 6. Common Errors & Troubleshooting

### Error 1: `FileNotFoundError: PyTorch model file not found`
- **Cause**: The source `.pt` model weights file is missing from `backend/yolo11n.pt` or `backend/app/ai/weights/`.
- **Solution**: Ensure `yolo11n.pt` exists in `backend/` or set `VEHICLE_MODEL_PATH` in `.env`.

### Error 2: `onnxruntime.capi.onnxruntime_pybind11_state.InvalidGraph`
- **Cause**: Corrupted `.onnx` export or incompatible opset version.
- **Solution**: Re-run `python deployment/export_onnx.py`. Ensure `opset=12` is used.

### Error 3: `NotImplementedError: TensorRT backend is not yet supported`
- **Cause**: `MODEL_BACKEND=TENSORRT` set in environment.
- **Solution**: Set `MODEL_BACKEND=ONNX` or `MODEL_BACKEND=PYTORCH` for Phase 12.1.
