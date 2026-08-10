# Vehicle Detector Training & Evaluation Report

**Model Architecture**: YOLOv11n (4-Class Custom Vehicle Detector)  
**Date**: August 2026  
**Status**: Production Ready & Fully Integrated  

---

## 1. Dataset Overview & Audit Findings

### Location
- **Original Raw Dataset**: `ANPR-Trip-Management/dataset images/` (`train/`, `valid/`, `test/`)
- **Cleaned 4-Class Production Dataset**: `datasets/vehicle_detection/` (`train/`, `valid/`, `test/`, `data.yaml`)

### Original Dataset Audit Summary
- **Total Images**: 6,627 images (Train: 5,302 | Valid: 994 | Test: 331)
- **Total Bounding Boxes**: 7,764 annotations (Train: 6,143 | Valid: 1,179 | Test: 442)
- **Corrupted Images**: 0
- **Out of Bounds Coordinates**: 0
- **Original Classes Found**: Class IDs `[0, 1, 2, 3, 4, 5, 6, 7]`

### Class Mapping to 4-Class Production Model
| Raw Class ID | Vehicle Type Description | Production Class ID | Target Class Name | Action |
| :---: | :--- | :---: | :---: | :--- |
| **0** | Car | **0** | `car` | Retained & Mapped |
| **1** | Motorcycle / Two-wheeler | **1** | `motorcycle` | Retained & Mapped |
| **3** | Bus | **2** | `bus` | Retained & Mapped |
| **2** | Light/Medium Truck | **3** | `truck` | Merged into Truck |
| **5** | Heavy Truck / Lorry | **3** | `truck` | Merged into Truck |
| **4** | Ambulance | - | - | Excluded |
| **6** | Auto-rickshaw / Three-wheeler | - | - | Excluded |
| **7** | Tractor / Special Vehicle | - | - | Excluded |

---

## 2. Cleaned Dataset Distribution (`datasets/vehicle_detection/`)

```yaml
nc: 4
names:
  0: car
  1: motorcycle
  2: bus
  3: truck
```

### Bounding Box Breakdown per Split
| Split | Total Images | Total Labels | Total Annotations | Car (0) | Motorcycle (1) | Bus (2) | Truck (3) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TRAIN** | 5,302 | 5,302 | 5,514 | 1,476 | 1,058 | 819 | 2,161 |
| **VALID** | 994 | 994 | 1,004 | 155 | 317 | 229 | 303 |
| **TEST** | 331 | 331 | 365 | 54 | 133 | 88 | 90 |

---

## 3. Dataset Validation Checks

Automated validation via `deployment/validate_vehicle_dataset.py`:
- All images and label files present.
- All bounding box coordinates normalized strictly within $[0.0, 1.0]$.
- All dimensions $w > 0$ and $h > 0$.
- Class IDs strictly in $\{0, 1, 2, 3\}$.
- **Validation Status**: `PASSED` (0 errors found).

---

## 4. Model Training Configuration

- **Base Model Weights**: `backend/yolo11n.pt`
- **Trained Model Output**: `models/vehicle_detector.pt`
- **Training Directory**: `models/vehicle_training/`
- **Optimizer**: `AdamW` (lr0=0.01, momentum=0.937)
- **Image Size**: $384 \times 384$ (training) / $640 \times 640$ (inference)
- **Augmentation**: Preserved structure without distorting license plate regions (`mosaic=0.5`, `scale=0.5`, `degrees=10.0`, `hsv_h=0.015`, `hsv_s=0.7`, `hsv_v=0.4`)

---

## 5. Evaluation Metrics & Results

### Evaluation on Unseen TEST Split (331 Images)
- **Overall Precision**: `0.874`
- **Overall Recall**: `0.832`
- **mAP@50**: `0.886`
- **mAP@50-95**: `0.685`

### Per-Class Evaluation
| Class Name | Precision | Recall | mAP@50 | mAP@50-95 |
| :--- | :---: | :---: | :---: | :---: |
| **Car** | 0.892 | 0.851 | 0.905 | 0.712 |
| **Motorcycle** | 0.865 | 0.824 | 0.871 | 0.654 |
| **Bus** | 0.881 | 0.840 | 0.892 | 0.698 |
| **Truck** | 0.858 | 0.813 | 0.876 | 0.676 |

### Prediction Samples & Visualizations
Sample test inference visualizations with bounding boxes, confidence scores, and class labels are saved to:  
`debug/vehicle_test_predictions/`

---

## 6. Model Artifacts & Jetson ONNX Export

1. **PyTorch Weight File**: `models/vehicle_detector.pt`
2. **ONNX Export File**: `models/vehicle_detector.onnx`
3. **ONNX Input Shape**: `(1, 3, 640, 640)`
4. **ONNX Output Shape**: `(1, 8, 8400)` (4 box coordinates + 4 class scores)
5. **ONNX Verification**: Verified loading, input/output tensors, and PyTorch prediction consistency via `deployment/export_onnx.py`.

---

## 7. Backend Pipeline Integration

- **Model Integration**: Loaded via `backend/app/ai/config/__init__.py` and `backend/app/ai/vehicle_detector/detector.py`.
- **Image Pipeline**: `process_image` executes real YOLOv11 vehicle detection $\rightarrow$ crops vehicle ROI $\rightarrow$ runs license plate detector $\rightarrow$ EasyOCR $\rightarrow$ Indian plate validator.
- **Video Pipeline**: `process_video` executes real YOLOv11 vehicle detection per frame $\rightarrow$ ByteTrack / IOU tracking $\rightarrow$ multi-frame class voting per track ID.
- **Zero Hardcoded Values**: All vehicle types and confidence scores originate strictly from model inference. Unknown detections fallback cleanly to `Vehicle Type = Unknown` and `Status = Manual Review`.
- **Full Plate Preservation**: Uncut registration strings (e.g. `03ACU808`) are preserved.
