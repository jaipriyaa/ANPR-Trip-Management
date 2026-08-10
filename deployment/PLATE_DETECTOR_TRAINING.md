# Single-Class YOLOv11 License Plate Detector — Technical Training & Deployment Guide

## 1. Overview
This document details the training, validation, export, and deployment of the dedicated **YOLOv11 License Plate Detector** (`models/license_plate_detector.pt` / `.onnx`). The subsystem operates independently from the 80-class COCO vehicle detector (`backend/yolo11n.pt`).

---

## 2. Dataset Architecture & Split

| Parameter | Specification / Value |
|---|---|
| **Dataset Location** | `datasets/license_plate/` |
| **Dataset Format** | Standard YOLO Object Detection (`class_id x_center y_center width height`) |
| **Classes (`nc`)** | `1` (`0: license_plate`) |
| **Train Set Images** | `10 images` (`datasets/license_plate/images/train/`) |
| **Validation Set Images** | `3 images` (`datasets/license_plate/images/val/`) |
| **Test Set Images** | `2 images` (`datasets/license_plate/images/test/`) |
| **Total Annotations** | `15 license plate bounding boxes` |

---

## 3. Training Parameters & Environment

| Parameter | Value |
|---|---|
| **Base Model Checkpoint** | `yolo11n.pt` (PyTorch YOLOv11 Nano) |
| **Image Resolution (`imgsz`)** | `640x640` |
| **Epochs** | `5` |
| **Batch Size** | `4` |
| **Optimizer** | `AdamW` (`lr0=0.002`, `momentum=0.9`) |
| **Compute Device** | `CPU (AMD Ryzen 7 7435HS)` |
| **Training Duration** | `45.4 seconds` |
| **Training Output Path** | `models/license_plate_training/` |

---

## 4. Evaluation Metrics (Validation Gate - Phase 36)

- **`Precision (P)`**: `0.995`
- **`Recall (R)`**: `1.000`
- **`mAP@50`**: **`0.995`** (99.5%)
- **`mAP@50-95`**: `0.399`
- **`Best Checkpoint`**: [`models/license_plate_training/weights/best.pt`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_training/weights/best.pt)
- **`Production PyTorch Model`**: [`models/license_plate_detector.pt`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.pt)

---

## 5. Single-Class ONNX Export & Tensor Shapes

- **Export Tool**: [`deployment/verify_plate_onnx.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/deployment/verify_plate_onnx.py)
- **Production ONNX Model**: [`models/license_plate_detector.onnx`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.onnx)
- **Backend ONNX Mirror**: [`backend/app/ai/weights/plate_detector.onnx`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/backend/app/ai/weights/plate_detector.onnx)
- **Input Tensor Shape**: `[1, 3, 640, 640]`
- **Output Tensor Shape**: **`[1, 5, 8400]`** (5 channels = 4 bbox coords + 1 class probability `license_plate`)

---

## 6. Pipeline Integration & Subsystem Mapping

```
IMAGE / VIDEO
      ↓
YOLOv11 Vehicle Detector (backend/yolo11n.pt / 80 COCO classes)
      ↓
Vehicle ROI Bounding Box ➔ Crop
      ↓
DEDICATED LICENSE PLATE DETECTOR (models/license_plate_detector.pt — 1 class: license_plate)
      ↓
Plate ROI Bounding Box ➔ Crop
      ↓
Image Preprocessing (CLAHE + Denoising + Rescaling)
      ↓
Multi-Pass EasyOCR Engine
      ↓
Structural Indian Plate Regex Validation ➔ Canonical Plate Text
```

---

## 7. Diagnostics & Maintenance Tools

- `deployment/validate_plate_dataset.py`: Validates dataset syntax and bounds.
- `deployment/visualize_plate_dataset.py`: Visualizes ground-truth boxes in `debug/plate_dataset_samples/`.
- `deployment/train_plate_detector.py`: Fine-tunes license plate detector.
- `deployment/test_plate_detector.py`: Tests single-class model inference on test images.
- `deployment/verify_plate_onnx.py`: Verifies single-class ONNX output shapes (`[1, 5, 8400]`).
