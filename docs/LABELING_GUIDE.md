# Data Annotation & Labeling Guide
## Industrial ANPR & Vehicle Trip Management Platform

**Document Version:** 1.0  
**Target Architecture:** YOLOv8 / YOLOv11 (Edge Object Detectors) & EasyOCR (Sequence Recognition)  
**Applicable Datasets:** Vehicle Detection (`datasets/vehicle_detection`), License Plate Detection (`datasets/license_plate_detection`), OCR Ground Truth Dataset  

---

## 1. Overview & Objectives

This specification defines the enterprise data annotation standards for the **Industrial ANPR Trip Management Platform**. Accurate, consistent, and standardized bounding boxes and OCR ground truth strings are critical for achieving high precision, low false-alarm rates, and real-time performance on edge hardware (NVIDIA Jetson, Intel Core edge nodes).

---

## 2. Class Taxonomy & Definitions

### 2.1. Vehicle Detector (4-Class Taxonomy)

| Class ID | Class Name | Description & Included Subtypes | Exclusion Criteria |
| :---: | :--- | :--- | :--- |
| **0** | `car` | Sedans, Hatchbacks, SUVs, MUVs, Minivans, Compact Pickups, Jeeps. | Commercial heavy buses, two-wheelers, heavy multi-axle trucks. |
| **1** | `motorcycle` | Motorcycles, Scooters, Mopeds, Two-wheelers. | Three-wheelers (Auto-rickshaws), Bicycles. |
| **2** | `bus` | Passenger Buses, School Buses, Private Shuttles, Mini-buses, Volvo Coaches. | Heavy cargo trucks, vans used solely for goods. |
| **3** | `truck` | Light Commercial Vehicles (LCV), Heavy Goods Vehicles (HGV), Tipper/Dumper Trucks, Container Trailers, Tankers, Multi-axle Lorries. | Passenger cars, pickup trucks classified under private car usage. |

*Note: Special vehicles like ambulances, auto-rickshaws, and tractors are excluded from the core 4-class deployment dataset to maximize precision for industrial logistics traffic.*

---

### 2.2. License Plate Detector (1-Class Taxonomy)

| Class ID | Class Name | Included Plate Varieties | Target Bounding Box Characteristics |
| :---: | :--- | :--- | :--- |
| **0** | `license_plate` | Standard White/Yellow Private & Commercial Plates, HSRP (High Security Registration Plates), Green EV Plates, BH (Bharat) Series, Military (Arrow) Plates, Temporary Stickers, Double-Line Stacked Plates. | Tightly fitted rectangle encapsulating the entire license plate border and characters. |

---

## 3. Bounding Box Annotation Rules

### 3.1. General Principles
1. **Tightness**: Bounding boxes must strictly fit the extreme boundaries of the object. Do not include unnecessary padding or empty background pixels.
2. **Occlusion & Truncation**:
   - If an object is partially occluded (< 50% hidden), extend the bounding box to cover the visible parts tightly.
   - If an object is truncated at the frame boundary, bound the visible portion as long as the object is recognizable.
   - If an object is > 70% occluded or unidentifiable, do **not** annotate it.
3. **Overlapping Vehicles**: Draw separate, distinct bounding boxes for overlapping vehicles in multi-lane factory gate views.

---

### 3.2. License Plate Specific Rules

```
┌──────────────────────────────────────────────────────────┐
│  [IND]  MH 12 CD 4321                                   │  <-- GOOD: Tight Bounding Box
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                                                          │
│  [IND]  MH 12 CD 4321                                   │  <-- BAD: Excessive Top/Bottom Margin
│                                                          │
└──────────────────────────────────────────────────────────┘
```

1. **Entire Plate Boundary**: Include the plate border frame and the country identifier badge (`IND` hologram if present), but exclude bumper, grille, or vehicle mounting bracket.
2. **Double-Line / Stacked Plates**:
   - Draw a **single** bounding box around both lines of text on two-row Indian vehicle plates (e.g. State/RTO code on top, 4-digit number on bottom).
   - Do **not** split stacked plates into two separate bounding boxes.
3. **Aspect Ratio Constraints**:
   - License plate aspect ratio ($W/H$) typically ranges between `1.2` and `7.5` (Average Indian plate aspect ratio $\approx 3.56$).
   - Minimum dimensions: `30px` width, `8px` height.
4. **Branding Blacklist Avoidance**:
   - Do **NOT** annotate vehicle brand logos ("TATA", "ASHOK LEYLAND", "BHARATBENZ"), advertisement slogans ("GOODS CARRIER", "ALL INDIA PERMIT", "SPEED 40 KM/H"), or chassis numbers.

---

## 4. OCR Ground Truth Text Annotation Rules

When annotating character text for plate recognition (OCR ground truth):

### 4.1. Character Set & Whitelist
- **Allowed Characters**: Uppercase English letters (`A-Z`) and Arabic Numerals (`0-9`).
- **Forbidden Characters**: Special symbols (`-`, `.`, `/`, ` `, `*`, `#`), lowercase letters. Remove spaces and hyphens from the final label string.
  - *Example*: `MH-14/TCF 200F` $\rightarrow$ `MH14TCF200F`
  - *Example*: `KA 01 AB 1234` $\rightarrow$ `KA01AB1234`

---

### 4.2. Confusion Matrix & Ambiguity Protocol
When characters are partially degraded, dirty, or low-resolution, follow standard character mapping:

| Visual Character | Primary Character | Alternate Confusion Candidates | Resolution Protocol |
| :---: | :---: | :---: | :--- |
| `0` vs `O` | Context-Based | State Code vs Digits | Position 1-2 are letters (`MH`), Position 3-4 are digits (`12`), Position 5-6 are letters (`CD`), Position 7-10 are digits (`4321`). |
| `1` vs `I` / `L` | Context-Based | Position Rules | Use position-based syntax checking for Indian RTO formats. |
| `8` vs `B` | Context-Based | Visual Features | `8` has symmetrical loops; `B` has flat left vertical stroke. |
| `5` vs `S` | Context-Based | Visual Features | `5` has sharp top-right corner; `S` has smooth curves. |
| `2` vs `Z` | Context-Based | Visual Features | `2` has curved top; `Z` has straight diagonal. |

---

## 5. Dataset File Structure & YOLO Format

### 5.1. Label File Format (YOLO Standard)
For every image `image_0001.jpg`, there must exist a matching label text file `image_0001.txt` in the corresponding labels directory.

Each line in the `.txt` file represents one bounding box in normalized coordinates:
```text
<class_id> <x_center> <y_center> <width> <height>
```
- `<class_id>`: Integer (0 to $N-1$)
- `<x_center>`: Box center X coordinate relative to image width ($0.0$ to $1.0$)
- `<y_center>`: Box center Y coordinate relative to image height ($0.0$ to $1.0$)
- `<width>`: Box width relative to image width ($0.0$ to $1.0$)
- `<height>`: Box height relative to image height ($0.0$ to $1.0$)

*Sample YOLO Label Entry:*
```text
0 0.512431 0.489102 0.320145 0.184512
```

---

### 5.2. Directory Layout
```text
datasets/
├── vehicle_detection/
│   ├── data.yaml
│   ├── train/
│   │   ├── images/  (*.jpg, *.png)
│   │   └── labels/  (*.txt)
│   ├── valid/
│   │   ├── images/
│   │   └── labels/
│   └── test/
│       ├── images/
│       └── labels/
└── license_plate_detection/
    ├── data.yaml
    ├── train/
    ├── valid/
    └── test/
```

---

## 6. Dataset Split Ratios

| Split | Ratio | Purpose |
| :---: | :---: | :--- |
| **Train** | **70%** | Model training & gradient updates |
| **Valid** | **20%** | Hyperparameter tuning, early stopping & checkpoint evaluation |
| **Test** | **10%** | Final unbiased benchmark evaluation & edge metric validation |

*Constraint: Ensure balanced representation of lighting conditions (day, dusk, night IR), weather (clear, rain), and vehicle types across all three splits.*

---

## 7. Quality Control & Audit Workflow

Before ingesting new labeled images into training pipelines, run the automated verification script:

```bash
python backend/venv/Scripts/python.exe -c "
import os, glob
# Verification script checks for missing labels, out-of-bounds coords, zero-area boxes
"
```

Refer to [`docs/LICENSE_PLATE_DATASET_AUDIT.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/LICENSE_PLATE_DATASET_AUDIT.md) for automated audit execution reports.
