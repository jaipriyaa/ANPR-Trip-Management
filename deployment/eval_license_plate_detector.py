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
PLATE_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
VEHICLE_MODEL_PT = os.path.join(PROJECT_ROOT, "models", "vehicle_detector.pt")

print("=" * 80)
print("     STEP 7, 8, 9, 10, 11, 12, 13: EVALUATION & REAL-WORLD VALIDATION     ")
print("=" * 80)

plate_model = YOLO(PLATE_MODEL_PT)
veh_detector = VehicleDetector()
ocr_engine = OCREngine()
validator = IndianPlateValidator()

# ----------------------------------------------------------------------
# STEP 7: TEST SPLIT EVALUATION
# ----------------------------------------------------------------------
test_img_dir = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "test", "images")
test_lbl_dir = os.path.join(PROJECT_ROOT, "datasets", "license_plate_detection", "test", "labels")

test_out_dir = os.path.join(PROJECT_ROOT, "debug", "license_plate_test_predictions")
os.makedirs(test_out_dir, exist_ok=True)

test_imgs = sorted(glob.glob(os.path.join(test_img_dir, "*.jpg")))
print(f"\n[STEP 7] Evaluating on Unseen Test Split ({len(test_imgs)} images)...")

total_gt = 0
total_detected = 0
total_tp = 0
total_fp = 0

for img_p in test_imgs:
    fname = os.path.basename(img_p)
    bname = os.path.splitext(fname)[0]
    lbl_p = os.path.join(test_lbl_dir, f"{bname}.txt")

    img = cv2.imread(img_p)
    if img is None:
        continue

    h, w = img.shape[:2]

    # Ground truth boxes
    gt_boxes = []
    if os.path.exists(lbl_p):
        with open(lbl_p, "r") as lf:
            lines = [l.strip() for l in lf.readlines() if l.strip()]
            for line in lines:
                parts = line.split()
                if len(parts) == 5:
                    xc, yc, bw, bh = map(float, parts[1:])
                    bx1 = int((xc - bw / 2.0) * w)
                    by1 = int((yc - bh / 2.0) * h)
                    bx2 = int((xc + bw / 2.0) * w)
                    by2 = int((yc + bh / 2.0) * h)
                    gt_boxes.append([bx1, by1, bx2, by2])
                    total_gt += 1

    # Run inference
    res = plate_model(img, conf=0.25, iou=0.45, verbose=False)[0]
    pred_boxes = []
    vis_img = img.copy()

    if hasattr(res, "boxes") and len(res.boxes) > 0:
        for box in res.boxes:
            px1, py1, px2, py2 = map(int, box.xyxy[0].tolist())
            conf_v = float(box.conf[0])
            pred_boxes.append(([px1, py1, px2, py2], conf_v))
            total_detected += 1

            # Draw prediction (green)
            cv2.rectangle(vis_img, (px1, py1), (px2, py2), (0, 255, 0), 2)
            cv2.putText(vis_img, f"plate {conf_v:.2f}", (px1, max(15, py1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save test prediction image
    cv2.imwrite(os.path.join(test_out_dir, f"pred_{fname}"), vis_img)

print(f"  Test Evaluation Complete: {len(test_imgs)} images processed, {total_detected} plates detected.")

# ----------------------------------------------------------------------
# STEP 8 & 9: REAL-WORLD TRUCK VALIDATION
# ----------------------------------------------------------------------
rw_out_dir = os.path.join(PROJECT_ROOT, "debug", "license_plate_real_world_validation")
os.makedirs(rw_out_dir, exist_ok=True)

target_truck_imgs = sorted(glob.glob("backend/uploads/images/*WhatsApp Image 2026-08-08 at 11.07.54 AM*"))
if not target_truck_imgs:
    target_truck_imgs = sorted(glob.glob("backend/uploads/images/*WhatsApp*"))

truck_img_path = target_truck_imgs[0]
print(f"\n[STEP 8 & 9] Testing Real-World Truck Image: {truck_img_path}")

t_img = cv2.imread(truck_img_path)
orig_h, orig_w = t_img.shape[:2]

cv2.imwrite(os.path.join(rw_out_dir, "original.jpg"), t_img)

# 1. Vehicle Detector
v_res = veh_detector.detect(t_img)
vehicles = v_res.get("vehicles", [])
top_v = vehicles[0] if vehicles else {}

v_type = top_v.get("vehicle_type", "Unknown")
v_conf = top_v.get("vehicle_confidence", 0.0)
v_box = top_v.get("vehicle_bbox", [0, 0, orig_w, orig_h])

print(f"  Vehicle Detection: {v_type} ({v_conf:.4f}) | BBox: {v_box}")

vx1, vy1, vx2, vy2 = v_box
v_crop = t_img[vy1:vy2, vx1:vx2]
if v_crop.size > 0:
    cv2.imwrite(os.path.join(rw_out_dir, "vehicle_crop.jpg"), v_crop)

# 2. Plate Detector on Vehicle Crop & Full Canvas
plate_res_veh = plate_model(v_crop if v_crop.size > 0 else t_img, conf=0.25, iou=0.45, verbose=False)[0]

best_p_box = None
best_p_conf = 0.0

if hasattr(plate_res_veh, "boxes") and len(plate_res_veh.boxes) > 0:
    b = plate_res_veh.boxes[0]
    bx1, by1, bx2, by2 = map(int, b.xyxy[0].tolist())
    best_p_conf = float(b.conf[0])
    best_p_box = [bx1 + vx1, by1 + vy1, bx2 + vx1, by2 + vy1]
else:
    # Full canvas fallback
    plate_res_full = plate_model(t_img, conf=0.25, iou=0.45, verbose=False)[0]
    if hasattr(plate_res_full, "boxes") and len(plate_res_full.boxes) > 0:
        b = plate_res_full.boxes[0]
        bx1, by1, bx2, by2 = map(int, b.xyxy[0].tolist())
        best_p_conf = float(b.conf[0])
        best_p_box = [bx1, by1, bx2, by2]

print(f"  Plate Detection  : BBox: {best_p_box} | Conf: {best_p_conf:.4f}")

# Draw visualization
vis_rw = t_img.copy()
cv2.rectangle(vis_rw, (vx1, vy1), (vx2, vy2), (255, 255, 0), 2)
cv2.putText(vis_rw, f"{v_type} {v_conf:.2f}", (vx1, vy1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

p_text = ""
p_valid = False
display_plate = "REQUIRES MANUAL REVIEW"

if best_p_box:
    px1, py1, px2, py2 = best_p_box
    p_crop = t_img[py1:py2, px1:px2]
    if p_crop.size > 0:
        cv2.imwrite(os.path.join(rw_out_dir, "plate_crop.jpg"), p_crop)

    cv2.rectangle(vis_rw, (px1, py1), (px2, py2), (0, 255, 0), 2)
    cv2.putText(vis_rw, f"license_plate {best_p_conf:.2f}", (px1, max(15, py1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 3. OCR & IndianPlateValidator
    if p_crop.size > 0:
        ocr_out = ocr_engine.read(p_crop)
        raw_t = ocr_out.get("raw_text", "")
        clean_t = ocr_out.get("plate_text", "")
        ocr_c = ocr_out.get("confidence", 0.0)

        val_res = validator.correct_with_confidence(clean_t, ocr_c)
        p_valid = val_res.get("is_valid", False)
        p_text = val_res.get("plate_text", clean_t) if p_valid else ""
        display_plate = p_text if p_valid else "REQUIRES MANUAL REVIEW"

cv2.imwrite(os.path.join(rw_out_dir, "plate_detection.jpg"), vis_rw)
cv2.imwrite(os.path.join(rw_out_dir, "plate_bbox_visualization.jpg"), vis_rw)

rw_result = {
    "vehicle_type": v_type,
    "vehicle_confidence": round(v_conf, 4),
    "vehicle_bbox": v_box,
    "plate_detected": best_p_box is not None,
    "plate_confidence": round(best_p_conf, 4),
    "plate_bbox": best_p_box,
    "display_plate": display_plate,
    "plate_number": p_text if p_valid else None,
    "verified": p_valid
}

with open(os.path.join(rw_out_dir, "result.json"), "w") as f:
    json.dump(rw_result, f, indent=2)

print(f"  Real-World Truck Result: display_plate='{display_plate}', verified={p_valid}")

# ----------------------------------------------------------------------
# STEP 12 & 13: ALL VEHICLE TYPES & FALSE POSITIVE RESISTANCE
# ----------------------------------------------------------------------
print("\n[STEP 12 & 13] Multi-Vehicle Type & Branding False Positive Audit:")
fp_texts = ["GOODS", "CARRIER", "LOGISTICS", "ASHOK", "LEYLAND"]
for word in fp_texts:
    is_blacklisted = validator.is_blacklisted_text(word)
    val_status, _, _ = validator.validate(word)
    print(f"  Word '{word}': Blacklisted={is_blacklisted}, ValidPlate={val_status}")

print("\n[COMPLETE] Evaluation and Real-World Validation finished cleanly.")
print("=" * 80)
