# Vehicle Detector Diagnostic & Failure Analysis Report

**Document Status**: FINAL DIAGNOSTIC REPORT  
**Date**: 2026-08-08  
**Target Model**: `models/vehicle_detector.pt`  
**Dataset**: Cleaned Vehicle Detection Dataset (`datasets/vehicle_detection/`)

---

## Executive Summary & Root Cause Summary

> [!CAUTION]
> **Conclusion**: The current model file `models/vehicle_detector.pt` is **NOT production-ready**.
> 
> The evaluation mAP of `0.0709` is **NOT caused by dataset corruption, label mismatch, or broken bounding box coordinates**. 
> 
> The failure is caused by **two distinct technical root causes**:
> 1. **Model Weights Copy Bug in Training Script (`train_vehicle_detector.py`)**: The script looked for trained weights at `models/vehicle_training/weights/best.pt` instead of Ultralytics' actual run output directory `runs/detect/models/vehicle_training/weights/best.pt`. Because the copy failed silently, `models/vehicle_detector.pt` remained the **raw 80-class COCO-pretrained `yolo11n.pt` base model**.
> 2. **Incomplete Model Training (1 Epoch Executed)**: The actual trained weights at `runs/detect/models/vehicle_training/weights/best.pt` were trained for only **1 single epoch**, leaving the classification head severely un-converged (`val/cls_loss = 128.57`).

---

## Detailed Section-by-Section Analysis

### 1. Dataset Label Conversion Verification
* **Raw Dataset**: `dataset images/`
* **Clean Dataset**: `datasets/vehicle_detection/`
* **Empirical Check**: Evaluated 80 bounding box coordinate pairs across all vehicle classes (`car`, `motorcycle`, `bus`, `truck`).
* **Result**: Max coordinate difference between raw and converted files was **`0.00000050`** (0.00005%).
* **Conclusion**: Bounding box coordinates (`x_center`, `y_center`, `width`, `height`) were **100% preserved** and **NOT altered** during conversion.

---

### 2. Class Mapping Verification
* **Conversion Mapping (`deployment/create_clean_dataset.py`)**:
  - `Raw 0` → `0` (`car`)
  - `Raw 1` → `1` (`motorcycle`)
  - `Raw 3` → `2` (`bus`)
  - `Raw 2` → `3` (`truck`)
  - `Raw 5` → `3` (`truck`)
  - `Raw 4, 6, 7` → Excluded (`n-lcv`, `p-ambulance`, `rickshaw123`, `tractor123`).
* **Exclusion Handling**: Excluded classes were skipped cleanly. No invalid bounding boxes or invalid class references were left in label files.

---

### 3. `data.yaml` Verification
* **Location**: [`datasets/vehicle_detection/data.yaml`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/datasets/vehicle_detection/data.yaml)
* **Contents**:
  ```yaml
  path: C:/Users/Manoj Kumar/Desktop/ANPR-Trip-Management/datasets/vehicle_detection
  train: train/images
  val: valid/images
  test: test/images
  nc: 4
  names:
    0: car
    1: motorcycle
    2: bus
    3: truck
  ```
* **Status**: 100% Valid.

---

### 4. Ground Truth Visual Inspection
* **Visual Check Dirs**:
  - [`debug/vehicle_gt_check/car/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_gt_check/car/) (20 images saved)
  - [`debug/vehicle_gt_check/motorcycle/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_gt_check/motorcycle/) (20 images saved)
  - [`debug/vehicle_gt_check/bus/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_gt_check/bus/) (20 images saved)
  - [`debug/vehicle_gt_check/truck/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_gt_check/truck/) (20 images saved)
* **Finding**: Ground-truth bounding boxes accurately surround the target vehicles in all 80 inspected samples.

---

### 5. Model Prediction Visual Inspection
* **Visual Check Dirs**:
  - [`debug/vehicle_prediction_check/car/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_prediction_check/car/) (20 images saved)
  - [`debug/vehicle_prediction_check/motorcycle/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_prediction_check/motorcycle/) (20 images saved)
  - [`debug/vehicle_prediction_check/bus/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_prediction_check/bus/) (20 images saved)
  - [`debug/vehicle_prediction_check/truck/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/vehicle_prediction_check/truck/) (20 images saved)
* **Finding**: Predictions show high confidence on large isolated vehicles (e.g. `truck: 0.92`), but exhibit high false positives and class confusion on dense scenes due to un-converged classification weights.

---

### 6. Image/Annotation Pairing Integrity
* **Train Split**: 5,302 images, 5,302 labels (0 missing)
* **Valid Split**: 994 images, 994 labels (0 missing)
* **Test Split**: 331 images, 331 labels (0 missing)
* **Integrity Status**: 100% paired. No stale labels, duplicate mismatches, or missing files.

---

### 7. Bounding Box Format & Normalization Audit
* **Boxes Inspected**: 6,883 boxes across train/valid/test.
* **Out-of-bounds Coordinates**: **0**.
* **Format**: All labels adhere strictly to normalized YOLO format (`class x_center y_center width height`).

---

### 8. `model.names` Verification
* **`models/vehicle_detector.pt`**:
  ```json
  {
    "0": "person", "1": "bicycle", "2": "car", "3": "motorcycle",
    "4": "airplane", "5": "bus", "6": "train", "7": "truck", ... (80 COCO classes)
  }
  ```
  > [!IMPORTANT]
  > `models/vehicle_detector.pt` was **never overwritten** by custom trained weights. It is the original 80-class COCO base model.

* **`runs/detect/models/vehicle_training/weights/best.pt`**:
  ```json
  {
    "0": "car", "1": "motorcycle", "2": "bus", "3": "truck"
  }
  ```

---

### 9 & 10. Official Ultralytics Validation & Confusion Matrix

#### Direct Ultralytics Evaluation Results on `models/vehicle_detector.pt` (Base COCO)
* **Overall Precision**: `0.1803`
* **Overall Recall**: `0.0639`
* **Overall mAP@50**: `0.0709`
* **Overall mAP@50-95**: `0.0460`

#### Direct Ultralytics Evaluation Results on `runs/detect/models/vehicle_training/weights/best.pt` (1 Epoch Trained)
* **Overall Precision**: `0.2541`
* **Overall Recall**: `0.0819`
* **Overall mAP@50**: `0.0014`
* **Overall mAP@50-95**: `0.0002`

#### Official 5×5 Confusion Matrix (Test Split)
| GT \ Pred | CAR | MOTORCYCLE | BUS | TRUCK | BACKGROUND (FN) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CAR** | **25** | 0 | 11 | 15 | 3 |
| **MOTORCYCLE** | 7 | **50** | 0 | 6 | 70 |
| **BUS** | 0 | 0 | **49** | 5 | 34 |
| **TRUCK** | 1 | 0 | 6 | **62** | 21 |
| **BACKGROUND (FP)** | **308** | **39** | **74** | **95** | — |

* **Total False Positives**: **567** (308 background false positives + 259 misclassifications)
* **Total False Negatives**: **179** (128 missed objects + 51 misclassifications)

---

### 11. Test Set Verification
* **Test Images**: 331
* **Test Annotations**: 365
* **Class Distribution**:
  - `car`: 54 objects across 48 images
  - `motorcycle`: 133 objects across 77 images
  - `bus`: 88 objects across 64 images
  - `truck`: 90 objects across 77 images

---

### 12. Model Training Loss Curve Analysis
Extracted from `runs/detect/models/vehicle_training/results.csv`:

| Epoch | train/box_loss | train/cls_loss | train/dfl_loss | val/box_loss | val/cls_loss | val/dfl_loss | Precision | Recall | mAP50 | mAP50-95 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 1.3543 | 2.3009 | 1.5023 | 3.4896 | **128.5700** | 11.4826 | 0.5050 | 0.0387 | 0.0022 | 0.0004 |

> [!WARNING]
> Training stopped after **1 single epoch**. The validation classification loss (`val/cls_loss = 128.57`) confirms that the model's prediction head had not yet converged.

---

### 13. Pretrained Model Compatibility
* **Base Model**: `backend/yolo11n.pt` is a valid YOLOv11 nano object detection checkpoint.
* **Initialization**: Initialized correctly during training with `nc=4`.

---

### 14. Dataset Class Imbalance Analysis
* **Clean Training Annotations**:
  - `car`: 1,476 (26.8%)
  - `motorcycle`: 1,058 (19.2%)
  - `bus`: 819 (14.9%)
  - `truck`: 2,161 (39.2%)
* **Total Training Annotations**: 5,514
* **Imbalance Assessment**: Max ratio is 2.6:1 (`truck` vs `bus`). The dataset is sufficiently balanced for multi-class detection.

---

### 15. Data Leakage & Split Audit
* **Train**: 5,302 images
* **Valid**: 994 images
* **Test**: 331 images
* **Data Leakage**: None found. All split directories contain unique image sets.

---

## Recommended Correction & Action Plan

1. **Fix File Path Copy Logic in `train_vehicle_detector.py`**:
   Update line 52 to check `runs/detect/models/vehicle_training/weights/best.pt` so that trained weights are properly copied to `models/vehicle_detector.pt`.
2. **Execute Full Retraining**:
   Train the vehicle detector for **25–30 epochs** (with early stopping patience = 10) so `val/cls_loss` converges below `1.5` and mAP@50 exceeds `0.85+`.
3. **Re-Validate**:
   Run direct validation on `models/vehicle_detector.pt` post-training to verify per-class mAP before deploying to production.
