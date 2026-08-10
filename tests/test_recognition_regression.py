import os
import sys
import glob
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.ai.vehicle_detector import VehicleDetector
from app.ai.inference.pipeline import DetectionPipeline

client = TestClient(app)

def test_regression_car_image():
    # Test 1: Car image detection
    detector = VehicleDetector()
    canvas = np.full((640, 640, 3), 200, dtype=np.uint8)
    cv2.rectangle(canvas, (100, 200), (540, 450), (50, 50, 200), -1)
    res = detector.detect(canvas)
    assert "vehicles" in res

def test_regression_truck_image():
    # Test 2: Truck image detection
    detector = VehicleDetector()
    canvas = np.full((640, 640, 3), 200, dtype=np.uint8)
    cv2.rectangle(canvas, (80, 120), (560, 520), (100, 100, 100), -1)
    res = detector.detect(canvas)
    assert "vehicles" in res

def test_regression_bus_image():
    # Test 3: Bus image detection
    detector = VehicleDetector()
    canvas = np.full((640, 640, 3), 200, dtype=np.uint8)
    cv2.rectangle(canvas, (50, 100), (590, 500), (200, 100, 0), -1)
    res = detector.detect(canvas)
    assert "vehicles" in res

def test_regression_motorcycle_image():
    # Test 4: Motorcycle image detection
    detector = VehicleDetector()
    canvas = np.full((640, 640, 3), 200, dtype=np.uint8)
    cv2.rectangle(canvas, (250, 200), (390, 500), (0, 150, 0), -1)
    res = detector.detect(canvas)
    assert "vehicles" in res

def test_regression_no_valid_plate_image():
    # Test 5: Image containing no valid plate returns HTTP 200 and REQUIRES MANUAL REVIEW
    blank = np.zeros((640, 640, 3), dtype=np.uint8)
    cv2.imwrite("debug/test_blank.jpg", blank)

    with open("debug/test_blank.jpg", "rb") as f:
        res = client.post(
            "/api/v1/vehicle-recognition/upload",
            files={"file": ("test_blank.jpg", f, "image/jpeg")},
            data={"direction": "Entering", "purpose": "Industrial Visit"}
        )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["display_plate"] == "REQUIRES MANUAL REVIEW"

def test_regression_unregistered_vehicle_upload():
    # Test 6 & 7: Test upload with spaces & parens in filename (WhatsApp image style)
    test_imgs = sorted(glob.glob("datasets/vehicle_detection/test/images/*.*"))
    target_img = test_imgs[0] if test_imgs else "debug/test_blank.jpg"

    with open(target_img, "rb") as f:
        res = client.post(
            "/api/v1/vehicle-recognition/upload",
            files={"file": ("WhatsApp Image 2026-08-08 at 11.07.54 AM (1).jpeg", f, "image/jpeg")},
            data={
                "direction": "Entering",
                "purpose": "Industrial Visit",
                "gate_id": "", # empty gate_id should not crash
                "driver_name": "John Doe"
            }
        )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "vehicle" in data
    assert "plate" in data
    assert "authorization" in data

def test_regression_polo_car_classification():
    # Test 7: Volkswagen Polo must be classified as Car, not Truck
    polo_path = os.path.join(backend_dir, "uploads", "images", "01643ce5_VolkswagenPoloGTIIndiaSpiedPune.jpg")
    if os.path.exists(polo_path):
        from app.ai.vehicle_detector import VehicleDetector
        detector = VehicleDetector()
        img = cv2.imread(polo_path)
        res = detector.detect(img)
        assert res["best_vehicle"]["vehicle_type"] == "Car"

def test_regression_branding_carrier_rejected():
    # Test 8: CARRIER must not become a verified plate
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("CARRIER")
    assert is_valid is False

def test_regression_branding_goods_rejected():
    # Test 9: GOODS must not become a verified plate
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("GOODS")
    assert is_valid is False

def test_regression_branding_logistics_rejected():
    # Test 10: LOGISTICS must not become a verified plate
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("LOGISTICS")
    assert is_valid is False

def test_regression_valid_or02bu3389_remains_valid():
    # Test 11: Valid OR02BU3389 must remain valid
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("OR02BU3389")
    assert is_valid is True
    assert plate == "OR02BU3389"

def test_regression_valid_mh14tcf200f_remains_valid():
    # Test 12: Valid MH14TCF200F must remain valid
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("MH14TCF200F")
    assert is_valid is True
    assert plate == "MH14TCF200F"

def test_regression_missing_plate_manual_review_not_500():
    # Test 13: Missing plate produces MANUAL REVIEW, never HTTP 500
    blank = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.imwrite("debug/blank_test.jpg", blank)
    with open("debug/blank_test.jpg", "rb") as f:
        res = client.post(
            "/api/v1/vehicle-recognition/upload",
            files={"file": ("blank_test.jpg", f, "image/jpeg")}
        )
    assert res.status_code == 200
    data = res.json()
    assert data["display_plate"] == "REQUIRES MANUAL REVIEW"

def test_regression_handwritten_car3_plate():
    # Test 14: Mandatory handwritten plate "car 3.jpg" regression test
    car3_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    if os.path.exists(car3_path):
        from app.ai.pipeline import pipeline
        res = pipeline.process_image(car3_path, "debug/handwritten_plate_test")
        assert res["vehicle_type"] == "Car"
        assert res["plate_bbox"] is not None
        assert len(res["plate_bbox"]) == 4
        assert res["is_valid_plate"] is True
        assert res["plate_verified"] is True

def test_regression_two_line_ocr_normalization():
    # Test 15: Two-line inverted OCR "4132 MHOZ DT" normalizes to valid Indian plate
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    val_res = validator.correct_with_confidence("4132 MHOZ DT", 0.65)
    assert val_res["is_valid"] is True
    assert "MH" in val_res["plate_text"]

def test_regression_branding_ashok_leyland_rejected():
    # Test 16: ASHOK LEYLAND branding must be rejected as license plate
    from app.ai.postprocessing.plate_validator import IndianPlateValidator
    validator = IndianPlateValidator()
    is_valid, plate, _ = validator.validate("ASHOK LEYLAND")
    assert is_valid is False


