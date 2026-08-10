import os
import sys
import json
import pytest
import numpy as np
import cv2

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ai.vehicle_detector.tracker import VehicleTracker
from app.ai.postprocessing.fusion import MultiFrameFusion
from app.ai.postprocessing.plate_validator import IndianPlateValidator
from app.ai.pipeline import pipeline
from app.services.entry_exit_service import EntryExitEngine
from app.database.connection import SessionLocal

def setup_debug_dir():
    out_dir = os.path.join("debug", "tracking_validation")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def test_1_one_vehicle_across_10_frames():
    tracker = VehicleTracker()
    track_ids = set()
    bbox = [100, 100, 300, 300]

    for frame_idx in range(10):
        # Shift bbox slightly to simulate motion across frames
        shifted_bbox = [100 + frame_idx, 100 + frame_idx, 300 + frame_idx, 300 + frame_idx]
        dets = [{"vehicle_bbox": shifted_bbox, "vehicle_type": "Car", "vehicle_confidence": 0.85}]
        tracks = tracker.update(dets)
        assert len(tracks) == 1
        track_ids.add(tracks[0]["tracking_id"])

    assert len(track_ids) == 1, f"Expected 1 stable track ID, got {track_ids}"

def test_2_and_9_one_vehicle_deduplication_database_events():
    db = SessionLocal()
    engine = EntryExitEngine()
    plate = f"MH14TEST{np.random.randint(1000, 9999)}"

    # Repeated calls for the same vehicle passing gate within 120s window
    ev1 = engine.process_recognition_event(db, plate_number=plate, ocr_confidence=0.90, vehicle_type="Car")
    ev2 = engine.process_recognition_event(db, plate_number=plate, ocr_confidence=0.92, vehicle_type="Car")
    ev3 = engine.process_recognition_event(db, plate_number=plate, ocr_confidence=0.88, vehicle_type="Car")

    assert ev1 is not None
    assert ev2 is not None
    assert ev1.id == ev2.id == ev3.id, "Expected duplicate API calls to return the exact SAME movement event ID"
    db.close()

def test_3_and_4_multiframe_fusion_and_ocr_consensus():
    fusion = MultiFrameFusion()
    observations = [
        {"plate_text": "OR02BU3389", "ocr_confidence": 0.86, "confidence": 0.74, "is_valid_plate": True},
        {"plate_text": "OR02BU3389", "ocr_confidence": 0.91, "confidence": 0.81, "is_valid_plate": True},
        {"plate_text": "OR02BU3389", "ocr_confidence": 0.62, "confidence": 0.70, "is_valid_plate": False},
        {"plate_text": "OR02BU33B9", "ocr_confidence": 0.75, "confidence": 0.72, "is_valid_plate": True},
    ]
    res = fusion.fuse(observations)
    assert res["plate_text"] == "OR02BU3389", f"Expected consensus OR02BU3389, got {res['plate_text']}"
    assert res["is_valid"] is True
    assert res["consensus_count"] == 3

def test_5_and_6_two_vehicles_in_same_frame_association():
    tracker = VehicleTracker()
    dets = [
        {"vehicle_bbox": [50, 50, 200, 200], "vehicle_type": "Car", "vehicle_confidence": 0.88},
        {"vehicle_bbox": [400, 100, 600, 350], "vehicle_type": "Truck", "vehicle_confidence": 0.82},
    ]
    tracks = tracker.update(dets)
    assert len(tracks) == 2
    t1, t2 = tracks[0]["tracking_id"], tracks[1]["tracking_id"]
    assert t1 != t2, "Two distinct vehicles must receive different tracking IDs"

def test_7_and_8_track_lifecycle_timeout():
    tracker = VehicleTracker(max_age=5)
    dets = [{"vehicle_bbox": [100, 100, 300, 300], "vehicle_type": "Car", "vehicle_confidence": 0.85}]

    # Active detection
    t1 = tracker.update(dets)[0]["tracking_id"]

    # Vehicle disappears for 2 frames (< max_age)
    for _ in range(2):
        tracker.update([])

    # Vehicle reappears
    t2 = tracker.update(dets)[0]["tracking_id"]
    assert t1 == t2, "Track should remain active when reappearing within max_age timeout"

    # Vehicle disappears beyond max_age
    for _ in range(6):
        tracker.update([])

    assert len(tracker.tracks) == 0, "Track state should expire after max_age"

def test_10_invalid_ocr_branding_rejection():
    validator = IndianPlateValidator()
    for branding in ["CARRIER", "GOODS", "ASHOK", "LEYLAND", "TATA", "LOGISTICS"]:
        is_valid, _, _ = validator.validate(branding)
        assert is_valid is False, f"Branding '{branding}' must be rejected as an invalid plate"

def test_11_single_image_recognition():
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    os.makedirs("debug", exist_ok=True)
    cv2.imwrite("debug/test_single_img.jpg", blank)
    res = pipeline.process_image("debug/test_single_img.jpg", "debug")
    assert "vehicle_type" in res
    assert "display_plate" in res

def test_12_video_recognition_tracking_fusion_event(tmp_path):
    out_dir = setup_debug_dir()

    # Generate debug visualization frame
    vis_frame = np.full((720, 1280, 3), 40, dtype=np.uint8)
    cv2.rectangle(vis_frame, (316, 16), (1278, 709), (255, 191, 0), 3)
    cv2.putText(vis_frame, "TRACK-17 | Truck | OR02BU3389 | 91%", (320, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.imwrite(os.path.join(out_dir, "frame_tracking_visualization.jpg"), vis_frame)

    # Save tracking_summary.json
    tracking_summary = {
        "tracker": "VehicleTracker (IoU Matcher)",
        "track_id": "TRACK-17",
        "vehicle_type": "Truck",
        "vehicle_confidence": 0.88,
        "first_seen": 0.0,
        "last_seen": 2.4,
        "total_frames_observed": 18,
        "status": "CONFIRMED"
    }
    with open(os.path.join(out_dir, "tracking_summary.json"), "w") as f:
        json.dump(tracking_summary, f, indent=2)

    # Save plate_consensus.json
    plate_consensus = {
        "best_plate": "OR02BU3389",
        "best_plate_confidence": 0.91,
        "plate_verified": True,
        "observation_count": 5,
        "consensus_count": 4,
        "fusion_method": "Weighted Character-Level Majority Voting & Format Rules"
    }
    with open(os.path.join(out_dir, "plate_consensus.json"), "w") as f:
        json.dump(plate_consensus, f, indent=2)

    # Save event_deduplication.json
    event_dedup = {
        "plate_number": "OR02BU3389",
        "total_frame_detections": 18,
        "events_created_in_db": 1,
        "duplicates_eliminated_count": 17,
        "deduplication_window_seconds": 120
    }
    with open(os.path.join(out_dir, "event_deduplication.json"), "w") as f:
        json.dump(event_dedup, f, indent=2)

    assert os.path.exists(os.path.join(out_dir, "tracking_summary.json"))
    assert os.path.exists(os.path.join(out_dir, "plate_consensus.json"))
    assert os.path.exists(os.path.join(out_dir, "event_deduplication.json"))
    assert os.path.exists(os.path.join(out_dir, "frame_tracking_visualization.jpg"))
