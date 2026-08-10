import os
import sys
import json
import time
import cv2
import numpy as np

# Ensure project root and backend directory are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.ai.vehicle_detector.detector import VehicleDetector
from app.ai.plate_detector.detector import PlateDetector
from app.ai.ocr.engine import OCREngine
from app.ai.postprocessing.plate_validator import IndianPlateValidator
from app.ai.preprocessing.plate_enhancer import PlateEnhancer





def run_diagnostic(image_path: str, output_dir: str = "debug/current_test"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n========================================================")
    print(f"DIAGNOSTIC PIPELINE TEST: {image_path}")
    print(f"========================================================")

    if not os.path.exists(image_path):
        print(f"ERROR: Image path does not exist: {image_path}")
        return

    # Read original image
    image = cv2.imread(image_path)
    if image is None:
        print(f"ERROR: Failed to read image: {image_path}")
        return

    orig_h, orig_w = image.shape[:2]
    cv2.imwrite(os.path.join(output_dir, "original.jpg"), image)

    # 1. Vehicle Detector Inspection
    print("\n--- 1. VEHICLE DETECTION INFERENCE ---")
    vd = VehicleDetector()
    vd_result = vd.detect(image)
    
    vehicle_det_img = image.copy()
    vehicles = vd_result.get("vehicles", [])

    
    top_vehicle = None
    if vehicles:
        top_vehicle = vehicles[0]

        v_bbox = top_vehicle["vehicle_bbox"]
        v_type = top_vehicle["vehicle_type"]
        v_conf = top_vehicle["vehicle_confidence"]
        c_id = top_vehicle.get("class_id", -1)
        base_lbl = top_vehicle.get("base_label", "unknown")
        print(f"VEHICLE DETECTED:")
        print(f"  class_id   : {c_id}")
        print(f"  base_label : {base_lbl}")
        print(f"  class_name : {v_type}")
        print(f"  confidence : {v_conf:.4f}")
        print(f"  bbox       : {v_bbox}")
        
        cv2.rectangle(vehicle_det_img, (v_bbox[0], v_bbox[1]), (v_bbox[2], v_bbox[3]), (0, 255, 0), 3)
        cv2.putText(vehicle_det_img, f"{v_type} {v_conf:.2f}", (v_bbox[0], max(30, v_bbox[1]-10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        vx1, vy1, vx2, vy2 = v_bbox
        v_crop = image[vy1:vy2, vx1:vx2]
        if v_crop.size > 0:
            cv2.imwrite(os.path.join(output_dir, "vehicle_crop.jpg"), v_crop)
    else:
        print("NO VEHICLE DETECTED (Using full image ROI)")
        v_bbox = [0, 0, orig_w, orig_h]
        v_crop = image
        v_type = "Unknown"
        v_conf = 0.0

    cv2.imwrite(os.path.join(output_dir, "vehicle_detections.jpg"), vehicle_det_img)

    # 2. Plate Detector Candidate Inspection
    print("\n--- 2. LICENSE PLATE CANDIDATE INFERENCE ---")
    pd = PlateDetector()
    pd_result = pd.detect(image, vehicle_bbox=v_bbox)
    plates = pd_result.get("plates", [])
    print(f"Found {len(plates)} candidate plate box(es):")

    candidates_img = image.copy()
    for idx, p in enumerate(plates):
        pb = p["plate_bbox"]
        p_conf = p["confidence"]
        p_w = p["width"]
        p_h = p["height"]
        p_ar = round(p_w / float(max(p_h, 1)), 2)
        p_area = p_w * p_h
        print(f"  Candidate #{idx+1}: conf={p_conf:.4f}, bbox={pb}, size={p_w}x{p_h}, AR={p_ar}, area={p_area}, method={p.get('method')}")
        
        cv2.rectangle(candidates_img, (pb[0], pb[1]), (pb[2], pb[3]), (0, 165, 255), 2)
        cv2.putText(candidates_img, f"#{idx+1} {p_conf:.2f}", (pb[0], max(20, pb[1]-5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

    cv2.imwrite(os.path.join(output_dir, "plate_candidates.jpg"), candidates_img)

    selected_plate = pd_result.get("best_plate")
    selected_img = image.copy()
    ocr_raw_text = ""
    ocr_conf = 0.0
    valid_plate = False
    norm_plate = None
    validation_reason = "No plate detected"

    if selected_plate:
        sp_box = selected_plate["plate_bbox"]
        print(f"\nSELECTED PLATE BBOX: {sp_box} (conf={selected_plate['confidence']:.4f})")
        cv2.rectangle(selected_img, (sp_box[0], sp_box[1]), (sp_box[2], sp_box[3]), (0, 255, 0), 3)
        
        px1, py1, px2, py2 = sp_box
        plate_crop = image[py1:py2, px1:px2]
        if plate_crop.size > 0:
            cv2.imwrite(os.path.join(output_dir, "selected_plate.jpg"), selected_img)
            cv2.imwrite(os.path.join(output_dir, "ocr_input.jpg"), plate_crop)

            # Preprocessing for OCR
            enhancer = PlateEnhancer()
            enhanced_plate = enhancer.enhance(plate_crop)
            cv2.imwrite(os.path.join(output_dir, "ocr_preprocessed.jpg"), enhanced_plate)


            # 3. OCR Engine Execution
            ocr = OCREngine()
            ocr_res = ocr.read(enhanced_plate)
            ocr_raw_text = ocr_res.get("text", "")
            ocr_conf = ocr_res.get("confidence", 0.0)
            print(f"\n--- 3. OCR INFERENCE RESULT ---")
            print(f"  Raw OCR Text  : '{ocr_raw_text}'")
            print(f"  OCR Confidence: {ocr_conf:.4f}")

            # 4. Indian Format Validation
            validator = IndianPlateValidator()
            is_valid, norm_plate, info = validator.validate(ocr_raw_text)
            valid_plate = is_valid
            validation_reason = f"Validated as {info.get('format')}" if is_valid else "Failed Indian license plate format validation"
            print(f"\n--- 4. FORMAT VALIDATION ---")
            print(f"  Valid Plate   : {valid_plate}")
            print(f"  Normalized    : '{norm_plate}'")
            print(f"  Reason        : {validation_reason}")

    else:
        print("\nNO VALID PLATE CANDIDATE PASSED GEOMETRIC FILTERS!")
        blank = np.zeros((100, 300, 3), dtype=np.uint8)
        cv2.putText(blank, "NO_VALID_PLATE_CROP", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(output_dir, "selected_plate.jpg"), selected_img)
        cv2.imwrite(os.path.join(output_dir, "ocr_input.jpg"), blank)
        cv2.imwrite(os.path.join(output_dir, "ocr_preprocessed.jpg"), blank)

    # 5. Final Result Export
    final_output = {
        "vehicle": {
            "class_id": top_vehicle.get("class_id") if top_vehicle else None,
            "class_name": v_type,
            "confidence": v_conf,
            "bbox": v_bbox,
        },
        "plate_detection": {
            "detected": bool(selected_plate is not None),
            "confidence": selected_plate["confidence"] if selected_plate else 0.0,
            "bbox": selected_plate["plate_bbox"] if selected_plate else None,
        },
        "ocr": {
            "raw_text": ocr_raw_text,
            "confidence": ocr_conf,
        },
        "validation": {
            "valid": valid_plate,
            "normalized_plate": norm_plate if valid_plate else None,
            "reason": validation_reason,
        },
        "final": {
            "vehicle_type": v_type,
            "plate_number": norm_plate if valid_plate else None,
            "display_plate": norm_plate if valid_plate else "REQUIRES MANUAL REVIEW",
            "verified": valid_plate,
        }
    }

    with open(os.path.join(output_dir, "final_result.json"), "w") as f:
        json.dump(final_output, f, indent=2)

    print(f"\nSaved all diagnostic artifacts to {output_dir}/")

if __name__ == "__main__":
    test_img = "debug/real_world_validation/truck/original.jpg"
    if not os.path.exists(test_img):
        test_img = "datasets/license_plate/images/val/plate_001.jpg"
    run_diagnostic(test_img)
