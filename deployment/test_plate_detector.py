import os
import sys
import json
import cv2
from ultralytics import YOLO

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PT = os.path.join(PROJECT_ROOT, "models", "license_plate_detector.pt")
OUT_DIR = os.path.join(PROJECT_ROOT, "debug", "plate_model_validation")
TRUCK_TEST_DIR = os.path.join(PROJECT_ROOT, "debug", "current_truck_test")

print("=" * 80)
print("     INDEPENDENT LICENSE PLATE DETECTOR DIAGNOSTIC TEST (PHASE 13-15)     ")
print("=" * 80)

if not os.path.exists(MODEL_PT):
    print(f"[ERROR] License plate model not found: {MODEL_PT}")
    sys.exit(1)

model = YOLO(MODEL_PT)
print(f"Loaded License Plate Model: {MODEL_PT}")
print(f"Model Class Dictionary    : {model.names}")
print(f"Number of Classes          : {len(model.names)}")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TRUCK_TEST_DIR, exist_ok=True)

test_img_path = os.path.join(PROJECT_ROOT, "backend", "test_plate.jpg")
if not os.path.exists(test_img_path):
    print(f"[WARNING] Sample image not found at {test_img_path}")
else:
    image = cv2.imread(test_img_path)
    results = model(image, conf=0.20, verbose=False)
    
    annotated = image.copy()
    detections = []
    
    if results and len(results) > 0 and hasattr(results[0], "boxes"):
        for idx, box in enumerate(results[0].boxes):
            bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = model.names.get(cls_id, f"cls_{cls_id}")
            
            print(f"Detection #{idx+1}: class={cls_name}, conf={conf:.4f}, bbox=[{bx1}, {by1}, {bx2}, {by2}], w={bx2-bx1}, h={by2-by1}")
            detections.append({
                "class": cls_name,
                "confidence": conf,
                "bbox": [bx1, by1, bx2, by2],
                "width": bx2 - bx1,
                "height": by2 - by1
            })
            
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
            cv2.putText(annotated, f"{cls_name} {conf:.2f}", (bx1, max(15, by1 - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
            # Save cropped plate
            plate_crop = image[by1:by2, bx1:bx2]
            if plate_crop.size > 0:
                cv2.imwrite(os.path.join(TRUCK_TEST_DIR, "plate.jpg"), plate_crop)

    # Save validation images
    cv2.imwrite(os.path.join(OUT_DIR, "sample_plate_detection.jpg"), annotated)
    cv2.imwrite(os.path.join(TRUCK_TEST_DIR, "original.jpg"), image)
    cv2.imwrite(os.path.join(TRUCK_TEST_DIR, "vehicle.jpg"), image)
    cv2.imwrite(os.path.join(TRUCK_TEST_DIR, "annotated.jpg"), annotated)
    
    with open(os.path.join(TRUCK_TEST_DIR, "results.json"), "w") as jf:
        json.dump({
            "model_path": MODEL_PT,
            "classes": model.names,
            "detections": detections
        }, jf, indent=2)
        
    print(f"\nSaved test outputs to:")
    print(f" - {OUT_DIR}/sample_plate_detection.jpg")
    print(f" - {TRUCK_TEST_DIR}/ (original.jpg, vehicle.jpg, plate.jpg, annotated.jpg, results.json)")

print("=" * 80)
