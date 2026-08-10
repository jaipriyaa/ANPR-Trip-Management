# REAL-WORLD LICENSE PLATE DATASET AUDIT REPORT

**Dataset Source:** `dataset plates/`  
**Audit Date:** 2026-08-09  
**Status:** **PASSED & VALIDATED**

---

## DATASET OVERVIEW

| Split | Images Count | Labels Count | Total License Plate Annotations |
| :--- | :---: | :---: | :---: |
| **Train** | 583 | 583 | 688 |
| **Valid** | 167 | 167 | 194 |
| **Test** | 83 | 83 | 99 |
| **TOTAL** | **833** | **833** | **981** |

---

## ANNOTATION QUALITY AUDIT

- **Annotation Format:** Standard YOLO Normalized (`class_id x_center y_center width height`)
- **Number of Classes:** 1 (Classes found: `{0: 981}`)
- **Missing Image/Label Pairs:** 0
- **Out of Bounds Coordinates:** 0
- **Zero-Area Bounding Boxes:** 0
- **Small Bounding Boxes (<0.1% area):** 1

---

## GEOMETRIC STATISTICS

- **Average Normalized Bounding Box Width:** `0.4202`
- **Average Normalized Bounding Box Height:** `0.1992`
- **Average Normalized Bounding Box Area:** `0.1272`
- **Average Aspect Ratio (W/H):** `3.56`

---

## VISUAL AUDIT ARTIFACTS
Generated 15 visual audit sample images in:
[`debug/license_plate_dataset_audit/`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/debug/license_plate_dataset_audit/)
