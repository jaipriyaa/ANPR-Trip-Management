# AI Models & Detection Architecture

This document describes the AI models, neural network architectures, training datasets, OCR pre-processing algorithms, and execution backends utilized in the **Industrial Vehicle Trip Management System**.

---

## 1. Overview of AI Pipeline

```
Raw Camera Frame (1080p)
        │
        ▼
[ 1. Vehicle Detector ] ──(YOLOv11: car, motorcycle, bus, truck)
        │
        ▼ Bounding Box Crop
[ 2. License Plate Detector ] ──(Dedicated 1-Class YOLOv11: license_plate)
        │
        ▼ Plate Crop Bounding Box
[ 3. Pre-processing & Homography ] ──(Bilinear Warping + Dynamic Contrast Adjustment)
        │
        ▼ Enhanced Plate Patch
[ 4. Multi-pass OCR Engine ] ──(EasyOCR / CRNN ONNX + Indian Standard Regex)
        │
        ▼ Plate Text & Confidence
[ 5.SORT Tracker & Deduplication ] ──(State machine trip entry/exit logging)
```

---

## 2. Vehicle Detector Model

- **Architecture**: YOLOv11 Nano / Small (`backend/yolo11n.pt` / `models/vehicle_detector.pt`)
- **Input Dimensions**: `640 x 640 x 3`
- **Output Classes**: 4 Classes
  - `0`: `car`
  - `1`: `motorcycle`
  - `2`: `bus`
  - `3`: `truck`
- **ONNX Export**: `models/vehicle_detector.onnx` (Input: `[1, 3, 640, 640]`, Output: `[1, 8, 8400]`)
- **Primary Function**: Identifies vehicle presence, tracks vehicle bounding boxes across frames using SORT tracking, and determines vehicle classification for gate trip entry logs.

---

## 3. License Plate Detector Model

- **Architecture**: Dedicated 1-Class Custom YOLOv11 License Plate Detector (`models/license_plate_detector.pt`)
- **Input Dimensions**: `640 x 640 x 3`
- **Output Classes**: 1 Class
  - `0`: `license_plate`
- **Training Dataset Details**:
  - **Dataset Size**: 833 real-world license plate images (981 ground-truth annotations)
  - **Train Split**: 583 images (692 bounding boxes)
  - **Validation Split**: 167 images (194 bounding boxes)
  - **Test Split**: 83 images (95 bounding boxes)
- **Validation Metrics**:
  - **Precision**: 90.9%
  - **Recall**: 92.2%
  - **mAP@50**: **95.8%**
  - **mAP@50-95**: 80.9%
- **ONNX Export**: `models/license_plate_detector.onnx`
  - Input Tensor: `[1, 3, 640, 640]`
  - Output Tensor: `[1, 5, 8400]` *(Verified 1-class bounding box & confidence tensor)*

---

## 4. Preprocessing & Homography Transformation

Raw plate bounding box crops undergo an automated enhancement pipeline prior to OCR:

1. **Perspective Homography Warp**: Corrects camera slant and perspective distortion using corner contour detection.
2. **Bilinear/Bicubic Rescaling**: Resizes low-resolution plate crops up to target height (minimum 64px) preserving character edge sharpness.
3. **Adaptive Thresholding & CLAHE**: Dynamic Contrast Limited Adaptive Histogram Equalization to handle shadows, glare, dirt, and nighttime lighting conditions.

---

## 5. OCR Engine & Text Validation

- **Engine Support**: EasyOCR Engine with custom CRNN fallback (`backend/app/ai/ocr/engine.py`).
- **Standard License Plate Regex Validation**:
  Validates recognized strings against standard patterns (e.g., Indian Vehicle Standard: `^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$`).
- **Non-Faking Safeguard**:
  If confidence score is below threshold (`< 85%`) or characters are unreadable, the system returns `display_plate = "REQUIRES MANUAL REVIEW"` and sets `verified = false` rather than guessing incorrect text.

---

## 6. Execution Backends & Export Scripts

Models can be executed across three backends based on hardware support:

| Backend Provider | Model Format | Execution Provider | Ideal Hardware |
| :--- | :--- | :--- | :--- |
| **PyTorch (Native)** | `.pt` | PyTorch CUDA / CPU | Development / Debugging |
| **ONNX Runtime** | `.onnx` | CPU / CUDA Execution Provider | Standard Servers / Containers |
| **NVIDIA TensorRT** | `.engine` | TensorRT FP16 / INT8 Execution Provider | NVIDIA Jetson Edge / Enterprise GPUs |

### Exporting & Compiling Models
- **Export PyTorch to ONNX**:
  ```bash
  python deployment/export_onnx.py
  ```
- **Compile ONNX to TensorRT**:
  ```bash
  bash deployment/generate_engine.sh
  ```
