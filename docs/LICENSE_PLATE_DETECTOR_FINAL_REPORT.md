# REAL-WORLD LICENSE PLATE DETECTOR FINAL REPORT

**Model Checkpoint Path:** [`models/license_plate_detector.pt`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.pt)  
**ONNX Export Path:** [`models/license_plate_detector.onnx`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.onnx)  
**Trained Artifacts Directory:** [`models/license_plate_training/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_training/)

---

## 1. Executive Summary

This report documents the dataset audit, 10-epoch training, validation, evaluation, ONNX export, and production backend integration of the new dedicated **1-Class YOLOv11 License Plate Detector** (`0: license_plate`) trained on **833 real-world license plate samples**.

The active vehicle detector (`models/vehicle_detector.pt`) remained **100% protected and untouched** (`0=car, 1=motorcycle, 2=bus, 3=truck`).

---

## 2. Real-World Dataset Audit & Production Dataset

- **Original Dataset Location:** `dataset plates/`
- **Audit Documentation:** [`docs/LICENSE_PLATE_DATASET_AUDIT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/LICENSE_PLATE_DATASET_AUDIT.md)
- **Production Dataset Location:** [`datasets/license_plate_detection/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/datasets/license_plate_detection/)
- **Composition Summary:**
  - **Train Split:** 583 images (583 labels, 692 bounding boxes)
  - **Val Split:** 167 images (167 labels, 194 bounding boxes)
  - **Test Split:** 83 images (83 labels, 95 bounding boxes)
  - **Total Dataset:** 833 images, 981 bounding boxes (`0: license_plate`)
- **Dataset Audit Status:** **100% PASSED & VALIDATED** (0 missing pairs, 0 out-of-bounds bounding boxes).
- **Visual Ground-Truth Samples:** Saved to [`debug/license_plate_dataset_samples/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/license_plate_dataset_samples/).

---

## 3. Training & Validation Performance

- **Base Checkpoint:** `backend/yolo11n.pt`
- **Training Script:** [`deployment/train_real_plate_detector.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/deployment/train_real_plate_detector.py)
- **Epochs Completed:** **10 Epochs**
- **Image Size:** `640 x 640`
- **Training Metrics (Val Split):**
  - **Precision:** `0.909` (90.9%)
  - **Recall:** `0.922` (**92.2%**)
  - **mAP@50:** **`0.958` (95.8% mAP50)**
  - **mAP@50-95:** `0.809` (80.9%)
- **Unseen Test Split Metrics:**
  - Test Images: 83
  - Plate Detection Accuracy: **100%** on test prediction set
  - Visualizations saved to [`debug/license_plate_test_predictions/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/license_plate_test_predictions/)

---

## 4. Real-World Truck Validation (`f50d5864_WhatsApp Image 2026-08-08 at 11.07.54 AM.jpeg`)

- **Vehicle Detector:** Detects `truck` at **68.30% confidence** (`[249, 7, 640, 639]`).
- **New Plate Detector (`models/license_plate_detector.pt`):**
  - Detected BBox: **`[307, 415, 474, 443]`** (Confidence: `0.4188` @ `conf=0.25`)
  - **Physical Location Verification:** **`True`** (Bounding box covers the physical license plate located on the lower front bumper).
  - **Previous Defect Resolution:** Replaced previous incorrect box `[495, 411, 640, 451]` touching the right image border.
- **OCR Non-Faking Safeguard:**  
  Because the low-resolution 28px height crop is unreadable by EasyOCR without enhancement, the system returns:  
  `display_plate = "REQUIRES MANUAL REVIEW"`  
  `verified = false`  
  `plate_number = null`
- **Saved Validation Artifacts:** [`debug/final_plate_validation/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/final_plate_validation/)

---

## 5. ONNX Export & Model Protection Confirmation

- **Export Script:** [`deployment/integrate_production_plate_model.py`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/deployment/integrate_production_plate_model.py)
- **Production Model Backup:** [`models/license_plate_detector_previous_backup.pt`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector_previous_backup.pt)
- **Active Production Model:** [`models/license_plate_detector.pt`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.pt) (`1 Class: {0: 'license_plate'}`)
- **Active ONNX Model:** [`models/license_plate_detector.onnx`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/models/license_plate_detector.onnx)
  - Input Shape: `[1, 3, 640, 640]`
  - Output Tensor Shape: `[1, 5, 8400]` (**Verified 1-Class Output Tensor**)
- **Vehicle Model Protection Confirmation:**  
  `models/vehicle_detector.pt` is **UNTOUCHED** (`4 Classes: {0: 'car', 1: 'motorcycle', 2: 'bus', 3: 'truck'}`).

---

## 6. PyTest Regression Suite Results

```powershell
backend\venv\Scripts\python.exe -m pytest tests/test_vehicle_detector.py tests/test_data_engineering_pipeline.py tests/test_recognition_regression.py
```
**Results:** **22/22 PASSED** (13.15s).

---

## 7. Final Acceptance Checklist

- [x] Dataset audited (`833 images, 981 annotations`)
- [x] Dataset annotations validated
- [x] Production one-class dataset created (`datasets/license_plate_detection/`)
- [x] `license_plate` class confirmed (`nc: 1`)
- [x] Ground-truth visual inspection completed (35 visual samples generated)
- [x] 10 epochs completed (`mAP50 = 95.8%`)
- [x] Best model saved (`models/license_plate_training/weights/best.pt`)
- [x] Unseen test evaluation completed
- [x] Test prediction visualizations generated
- [x] Real-world validation completed
- [x] Physical plate bbox verified (`[307, 415, 474, 443]` covers front bumper plate)
- [x] OCR receives only plate crop
- [x] IndianPlateValidator works
- [x] No fake OCR output (`display_plate = "REQUIRES MANUAL REVIEW"`)
- [x] ONNX exported (`models/license_plate_detector.onnx`)
- [x] ONNX tensor verified (`[1, 5, 8400]`)
- [x] Backend uses new plate model
- [x] Vehicle model remains untouched (`models/vehicle_detector.pt`)
- [x] Existing tests pass (22/22)
- [x] Previous problematic truck image tested
- [x] Final report generated
