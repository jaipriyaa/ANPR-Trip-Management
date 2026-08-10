# Data Annotation & Labeling Guide
## Industrial ANPR & Vehicle Trip Management Platform

**Document Location:** [`docs/LABELING_GUIDE.md`](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/LABELING_GUIDE.md)

---

## Quick Reference Summary

### 1. Vehicle Detector (4-Class Taxonomy)
- `0: car` - Sedans, Hatchbacks, SUVs, MUVs, Minivans, Compact Pickups.
- `1: motorcycle` - Motorcycles, Scooters, Mopeds, Two-wheelers.
- `2: bus` - Passenger Buses, School Buses, Shuttles, Mini-buses.
- `3: truck` - LCVs, HGVs, Tipper/Dumper Trucks, Container Trailers, Tankers, Lorries.

### 2. License Plate Detector (1-Class Taxonomy)
- `0: license_plate` - Standard Private/Commercial Plates, HSRP, Green EV Plates, BH Series, Stacked Double-Line Plates.

### 3. OCR Text Ground Truth Rules
- **Whitelist**: Uppercase `A-Z` and Digits `0-9`.
- **Formatting**: Strip spaces, hyphens, slashes (`MH-14/TCF 200F` $\rightarrow$ `MH14TCF200F`).
- **Branding Avoidance**: Exclude "TATA", "ASHOK LEYLAND", "GOODS CARRIER", "ALL INDIA PERMIT".

### 4. Label Format (YOLO Standard)
```text
<class_id> <x_center> <y_center> <width> <height>
```
Normalized coordinates ($0.0$ to $1.0$).

---
For full details, edge cases, and audit procedures, see the main document:  
👉 **[Full Labeling Guide Document](file:///c:/Users/Manoj%20Kumar/Desktop/ANPR-Trip-Management/docs/LABELING_GUIDE.md)**
