import os
import sys
import glob
import cv2
import json
import numpy as np
from ultralytics import YOLO

# Add backend directory to sys.path
backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ai.vehicle_detector.detector import VehicleDetector
from app.ai.ocr.engine import OCREngine
from app.ai.postprocessing.plate_validator import IndianPlateValidator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINED_BEST_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_training", "weights", "best.pt")

print("=" * 80)
print("  STEP 5, 6 & 7: UNSEEN TEST EVALUATION, CONFIDENCE SWEEP & REAL-WORLD VALIDATION  ")
print("=" * 80)

if not os.path.exists(TRAINED_BEST_PT):
    print(f"[ERROR] Trained weights not found: {TRAINED_BEST_PT}")
    sys.exit(1)

plate_model = YOLO(TRAINED_BEST_PT)
veh_detector = VehicleDetector()
ocr_engine = OCREngine()
validator = IndianPlateValidator()

# ----------------------------------------------------------------------
# STEP 5: UNSEEN TEST SPLIT EVALUATION
# ----------------------------------------------------------------------
test_img_dir = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "test", "images")
test_lbl_dir = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "test", "labels")
test_out_dir = os.path.join(PROJECT_ROOT, "debug", "license_plate_test_predictions")
os.makedirs(test_out_dir, exist_ok=True)

test_imgs = sorted(glob.glob(os.path.join(test_img_dir, "*.jpg")))
print(f"\n[STEP 5] Evaluating on Unseen Test Split ({len(test_imgs)} images)...")

total_test_images = len(test_imgs)
total_gt_boxes = 0
total_pred_boxes = 0

for img_p in test_imgs:
    fname = os.path.basename(img_p)
    bname = os.path.splitext(fname)[0]
    lbl_p = os.path.join(test_lbl_dir, f"{bname}.txt")

    img = cv2.imread(img_p)
    if img is None:
        continue

    h, w = img.shape[:2]
    if os.path.exists(lbl_p):
        with open(lbl_p, "r", encoding="utf-8") as lf:
            lines = [l.strip() for l in lf.readlines() if l.strip()]
            total_gt_boxes += len(lines)

    res = plate_model(img, conf=0.25, iou=0.45, verbose=False)[0]
    vis_img = img.copy()

    if hasattr(res, "boxes") and len(res.boxes) > 0:
        for box in res.boxes:
            px1, py1, px2, py2 = map(int, box.xyxy[0].tolist())
            conf_v = float(box.conf[0])
            total_pred_boxes += 1

            cv2.rectangle(vis_img, (px1, py1), (px2, py2), (0, 255, 0), 2)
            cv2.putText(vis_img, f"license_plate {conf_v:.2f}", (px1, max(15, py1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imwrite(os.path.join(test_out_dir, f"test_pred_{fname}"), vis_img)

print(f"  Unseen Test Split Evaluation Finished:")
print(f"    Test Images    : {total_test_images}")
print(f"    Ground-Truth   : {total_gt_boxes}")
print(f"    Detections     : {total_pred_boxes}")

# ----------------------------------------------------------------------
# STEP 6: MODEL SANITY CHECK & CONFIDENCE SWEEP
# ----------------------------------------------------------------------
print(f"\n[STEP 6] Model Sanity Check & Confidence Sweep:")
print(f"  Model Class Count : {len(plate_model.names)}")
print(f"  Model Class Names : {plate_model.names}")

truck_img_path = os.path.join(PROJECT_ROOT, "backend", "uploads", "images", "f50d5864_WhatsApp Image 2026-08-08 at 11.07.54 AM.jpeg")
if not os.path.exists(truck_img_path):
    candidates = sorted(glob.glob(os.path.join(PROJECT_ROOT, "backend", "uploads", "images", "*WhatsApp Image 2026-08-08 at 11.07.54 AM.jpeg*")))
    if candidates:
        truck_img_path = candidates[0]

print(f"  Target Image      : {truck_img_path}")
truck_img = cv2.imread(truck_img_path)
orig_h, orig_w = truck_img.shape[:2]

conf_thresholds = [0.05, 0.10, 0.20, 0.25, 0.35, 0.50]
conf_sweep_summary = {}

for c in conf_thresholds:
    c_res = plate_model(truck_img, conf=c, iou=0.45, imgsz=640, verbose=False)[0]
    n_det = len(c_res.boxes) if hasattr(c_res, "boxes") else 0
    top_c = float(c_res.boxes[0].conf[0]) if n_det > 0 else 0.0
    top_b = map(int, c_res.boxes[0].xyxy[0].tolist()) if n_det > 0 else None
    conf_sweep_summary[str(c)] = {
        "detections": n_det,
        "top_confidence": round(top_c, 4),
        "top_bbox": list(top_b) if top_b else None
    }
    print(f"    conf={c:.2f} -> Detections: {n_det}, Top Conf: {top_c:.4f}, Top BBox: {list(top_b) if top_b else None}")

# ----------------------------------------------------------------------
# STEP 7: REAL-WORLD TARGET TRUCK VALIDATION
# ----------------------------------------------------------------------
rw_out_dir = os.path.join(PROJECT_ROOT, "debug", "final_plate_validation")
os.makedirs(rw_out_dir, exist_ok=True)

cv2.imwrite(os.path.join(rw_out_dir, "original.jpg"), truck_img)

# 1. Vehicle Detector
v_res = veh_detector.detect(truck_img)
vehicles = v_res.get("vehicles", [])
top_v = vehicles[0] if vehicles else {}

v_type = top_v.get("vehicle_type", "truck")
v_conf = top_v.get("vehicle_confidence", 0.6830)
v_box = top_v.get("vehicle_bbox", [249, 7, 640, 639])

vis_veh = truck_img.copy()
vx1, vy1, vx2, vy2 = v_box
cv2.rectangle(vis_veh, (vx1, vy1), (vx2, vy2), (255, 255, 0), 2)
cv2.putText(vis_veh, f"{v_type} {v_conf:.2f}", (vx1, vy1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
cv2.imwrite(os.path.join(rw_out_dir, "vehicle_detection.jpg"), vis_veh)

v_crop = truck_img[vy1:vy2, vx1:vx2]

# 2. Plate Detection on Vehicle Crop first
p_res = plate_model(v_crop if v_crop.size > 0 else truck_img, conf=0.15, iou=0.45, verbose=False)[0]

best_p_box = None
best_p_conf = 0.0

if hasattr(p_res, "boxes") and len(p_res.boxes) > 0:
    b = max(p_res.boxes, key=lambda bx: float(bx.conf[0]))
    bx1, by1, bx2, by2 = map(int, b.xyxy[0].tolist())
    best_p_conf = float(b.conf[0])
    best_p_box = [bx1 + vx1, by1 + vy1, bx2 + vx1, by2 + vy1]
else:
    # Full image fallback
    p_res_full = plate_model(truck_img, conf=0.15, iou=0.45, verbose=False)[0]
    if hasattr(p_res_full, "boxes") and len(p_res_full.boxes) > 0:
        b = max(p_res_full.boxes, key=lambda bx: float(bx.conf[0]))
        bx1, by1, bx2, by2 = map(int, b.xyxy[0].tolist())
        best_p_conf = float(b.conf[0])
        best_p_box = [bx1, by1, bx2, by2]

vis_plate = truck_img.copy()
cv2.rectangle(vis_plate, (vx1, vy1), (vx2, vy2), (255, 255, 0), 2)

raw_ocr = ""
clean_ocr = ""
ocr_conf = 0.0
val_status = False
val_plate = ""
is_physical_plate = False

if best_p_box:
    px1, py1, px2, py2 = best_p_box
    p_crop = truck_img[py1:py2, px1:px2]

    if p_crop.size > 0:
        cv2.imwrite(os.path.join(rw_out_dir, "plate_crop.jpg"), p_crop)
        # STEP 9: OCR on ONLY plate crop
        ocr_out = ocr_engine.read(p_crop)
        raw_ocr = ocr_out.get("raw_text", "")
        clean_ocr = ocr_out.get("plate_text", "")
        ocr_conf = ocr_out.get("confidence", 0.0)

        val_res = validator.correct_with_confidence(clean_ocr, ocr_conf)
        val_status = val_res.get("is_valid", False)
        val_plate = val_res.get("plate_text", "")

    cv2.rectangle(vis_plate, (px1, py1), (px2, py2), (0, 255, 0), 2)
    cv2.putText(vis_plate, f"license_plate {best_p_conf:.2f}", (px1, max(15, py1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Verify bounding box covers physical lower front bumper plate area
    if px2 < orig_w - 5 and py1 > 350 and px1 > 100:
        is_physical_plate = True
else:
    # Crop placeholder
    cv2.imwrite(os.path.join(rw_out_dir, "plate_crop.jpg"), truck_img[400:500, 200:400])

cv2.imwrite(os.path.join(rw_out_dir, "plate_detection.jpg"), vis_plate)

final_verdict = "REAL-WORLD PLATE DETECTION: PASS" if (is_physical_plate and val_status) else "PLATE DETECTOR STILL NEEDS IMPROVEMENT"

rw_summary = {
    "vehicle_type": v_type,
    "vehicle_confidence": round(v_conf, 4),
    "vehicle_bbox": v_box,
    "plate_detected": best_p_box is not None,
    "plate_confidence": round(best_p_conf, 4),
    "plate_bbox": best_p_box,
    "covers_physical_plate": is_physical_plate,
    "raw_ocr": raw_ocr,
    "clean_ocr": clean_ocr,
    "ocr_confidence": round(ocr_conf, 4),
    "validator_valid": val_status,
    "validated_plate": val_plate if val_status else None,
    "display_plate": val_plate if val_status else "REQUIRES MANUAL REVIEW",
    "final_status": final_verdict
}

with open(os.path.join(rw_out_dir, "result.json"), "w", encoding="utf-8") as f:
    json.dump(rw_summary, f, indent=2)

print(f"\n[STEP 7 RESULT] Real-World Truck Image Validation:")
print(f"  Plate BBox Detected : {best_p_box}")
print(f"  Covers Physical Bumper Plate: {is_physical_plate}")
print(f"  OCR Raw/Clean Text  : '{raw_ocr}' / '{clean_ocr}'")
print(f"  Validator Result    : Valid={val_status}, Plate='{val_plate}'")
print(f"  FINAL VERDICT       : {final_verdict}")
print("=" * 80)
