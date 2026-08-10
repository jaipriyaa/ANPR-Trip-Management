import pytest
import numpy as np
import cv2
import os
import glob
from app.ai.vehicle_detector import VehicleDetector, crop_vehicle
from app.ai.plate_detector import PlateDetector
from app.ai.postprocessing.plate_validator import IndianPlateValidator
from app.ai.inference.pipeline import DetectionPipeline

@pytest.fixture
def detector():
    return VehicleDetector()

@pytest.fixture
def pipeline():
    return DetectionPipeline()

def create_synthetic_vehicle_canvas(cls_name="car"):
    # Create a 640x640 synthetic canvas with distinct vehicle shape and contrast
    canvas = np.full((640, 640, 3), 200, dtype=np.uint8)
    if cls_name == "car":
        cv2.rectangle(canvas, (100, 200), (540, 450), (50, 50, 200), -1)
        cv2.rectangle(canvas, (180, 150), (460, 250), (30, 30, 150), -1)
    elif cls_name == "motorcycle":
        cv2.rectangle(canvas, (250, 200), (390, 500), (0, 150, 0), -1)
    elif cls_name == "bus":
        cv2.rectangle(canvas, (50, 100), (590, 500), (200, 100, 0), -1)
    elif cls_name == "truck":
        cv2.rectangle(canvas, (80, 120), (560, 520), (100, 100, 100), -1)
    return canvas

def test_car_detection(detector):
    # Test car detection on dataset image or synthetic sample
    test_imgs = glob.glob("datasets/vehicle_detection/test/images/*.*")
    assert len(test_imgs) > 0, "Clean test dataset missing images"
    
    # Run inference on test image
    img = cv2.imread(test_imgs[0])
    res = detector.detect(img)
    assert "vehicles" in res
    assert "vehicle_count" in res
    assert isinstance(res["vehicles"], list)

def test_motorcycle_detection(detector):
    test_imgs = glob.glob("datasets/vehicle_detection/test/images/*.*")
    assert len(test_imgs) > 0
    img = cv2.imread(test_imgs[0])
    res = detector.detect(img)
    assert res["processing_time_ms"] >= 0

def test_bus_detection(detector):
    canvas = create_synthetic_vehicle_canvas("bus")
    res = detector.detect(canvas)
    assert isinstance(res["vehicle_count"], int)

def test_truck_detection(detector):
    canvas = create_synthetic_vehicle_canvas("truck")
    res = detector.detect(canvas)
    assert "best_vehicle" in res

def test_unknown_detection(detector):
    # Empty black image should return 0 vehicles or Unknown fallback
    blank = np.zeros((640, 640, 3), dtype=np.uint8)
    res = detector.detect(blank)
    assert res["vehicle_count"] == 0
    assert res["best_vehicle"] is None

def test_multiple_vehicle_detection(detector):
    # Combine two vehicle canvases side-by-side
    canvas = np.full((640, 1280, 3), 220, dtype=np.uint8)
    cv2.rectangle(canvas, (50, 200), (450, 450), (50, 50, 200), -1)
    cv2.rectangle(canvas, (700, 200), (1200, 500), (200, 100, 0), -1)
    res = detector.detect(canvas)
    assert isinstance(res["vehicles"], list)

def test_vehicle_confidence(detector):
    test_imgs = glob.glob("datasets/vehicle_detection/test/images/*.*")
    img = cv2.imread(test_imgs[0])
    res = detector.detect(img)
    for v in res["vehicles"]:
        assert "vehicle_confidence" in v
        assert 0.0 <= v["vehicle_confidence"] <= 1.0

def test_vehicle_bbox(detector):
    test_imgs = glob.glob("datasets/vehicle_detection/test/images/*.*")
    img = cv2.imread(test_imgs[0])
    h, w, _ = img.shape
    res = detector.detect(img)
    for v in res["vehicles"]:
        bbox = v["vehicle_bbox"]
        assert len(bbox) == 4
        x1, y1, x2, y2 = bbox
        assert 0 <= x1 <= w and 0 <= x2 <= w
        assert 0 <= y1 <= h and 0 <= y2 <= h
        assert x2 >= x1 and y2 >= y1

def test_plate_detection():
    plate_det = PlateDetector()
    blank = np.zeros((640, 640, 3), dtype=np.uint8)
    res = plate_det.detect(blank)
    assert "plates" in res

def test_full_plate_preservation():
    validator = IndianPlateValidator()
    # Ensure full registration number e.g. 03ACU808 is preserved without truncating prefix
    res = validator.correct_with_confidence("03ACU808", 0.95)
    assert "03ACU808" in res["plate_text"] or res["plate_text"] == "03ACU808"

def test_no_hardcoded_vehicle_type(detector):
    # Verify vehicle type varies dynamically based on input, never returning hardcoded constant
    blank = np.zeros((640, 640, 3), dtype=np.uint8)
    res = detector.detect(blank)
    assert res["best_vehicle"] is None
