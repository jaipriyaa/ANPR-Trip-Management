import os
import sys
import json
import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.services.trip_service import trip_service
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.crud.crud_vehicle import crud_vehicle
from app.schemas.scheduled_trip import ScheduledTripCreate
from app.schemas.vehicle import VehicleCreate
from app.models.trip_status_history import TripStatusHistory

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_test_vehicle_and_trip(db, plate: str):
    v = crud_vehicle.get_by_number(db, plate)
    if not v:
        v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))

    now = datetime.now(timezone.utc)
    trip_in = ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now - timedelta(minutes=10),
        expected_exit_time=now + timedelta(hours=2),
        purpose="Industrial Delivery",
        trip_status="SCHEDULED",
        approval_status="PENDING"
    )
    trip = crud_scheduled_trip.create(db, obj_in=trip_in)
    return v, trip

def test_1_scheduled_to_arrived(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH01TRIP{pytest.rand_id}")
    res = trip_service.transition_state(db, trip, "ARRIVED")
    assert res.trip_status == "ARRIVED"

def test_2_arrived_to_entry_approved(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH02TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "ARRIVED")
    res = trip_service.transition_state(db, trip, "ENTRY_APPROVED")
    assert res.trip_status == "ENTRY_APPROVED"

def test_3_entry_approved_to_inside_plant(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH03TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "ARRIVED")
    trip_service.transition_state(db, trip, "ENTRY_APPROVED")
    res = trip_service.transition_state(db, trip, "INSIDE_PLANT")
    assert res.trip_status == "INSIDE_PLANT"

def test_4_inside_plant_to_at_destination(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH04TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "INSIDE_PLANT")
    res = trip_service.transition_state(db, trip, "AT_DESTINATION")
    assert res.trip_status == "AT_DESTINATION"

def test_5_at_destination_to_exit_detected(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH05TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "INSIDE_PLANT")
    trip_service.transition_state(db, trip, "AT_DESTINATION")
    res = trip_service.transition_state(db, trip, "EXIT_DETECTED")
    assert res.trip_status == "EXIT_DETECTED"

def test_6_exit_detected_to_completed(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH06TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "INSIDE_PLANT")
    trip_service.transition_state(db, trip, "EXIT_DETECTED")
    res = trip_service.transition_state(db, trip, "COMPLETED")
    assert res.trip_status == "COMPLETED"

def test_7_invalid_transition_completed_to_inside_plant(db):
    _, trip = create_test_vehicle_and_trip(db, f"MH07TRIP{pytest.rand_id}")
    trip_service.transition_state(db, trip, "INSIDE_PLANT")
    trip_service.transition_state(db, trip, "COMPLETED")
    with pytest.raises(HTTPException) as exc_info:
        trip_service.transition_state(db, trip, "INSIDE_PLANT")
    assert exc_info.value.status_code == 400
    assert "Invalid state transition" in exc_info.value.detail

def test_8_scheduled_trip_matching_plate(db):
    plate = f"MH08MATCH{pytest.rand_id}"
    v, trip = create_test_vehicle_and_trip(db, plate)
    res_trip = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.90, direction="Entering")
    assert res_trip is not None
    assert res_trip.id == trip.id
    assert res_trip.trip_status in ["INSIDE_PLANT", "INSIDE"]

def test_9_unknown_plate_handling(db):
    unknown_plate = f"UNKNOWN{pytest.rand_id}"
    res = trip_service.process_ai_recognition_event(db, plate_number=unknown_plate, ocr_confidence=0.85)
    assert res is None

def test_10_entry_and_exit_same_vehicle_one_completed_trip(db):
    plate = f"MH10FULL{pytest.rand_id}"
    v, trip = create_test_vehicle_and_trip(db, plate)
    
    # Entry
    entry_trip = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.92, direction="Entering")
    assert entry_trip.trip_status in ["INSIDE_PLANT", "INSIDE"]
    
    # Exit
    exit_trip = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Exiting")
    assert exit_trip.trip_status == "COMPLETED"

def test_11_entry_without_exit(db):
    plate = f"MH11NOEXIT{pytest.rand_id}"
    v, trip = create_test_vehicle_and_trip(db, plate)
    res = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.90, direction="Entering")
    assert res.trip_status in ["INSIDE_PLANT", "INSIDE"]

def test_12_exit_without_entry(db):
    from app.services.entry_exit_service import entry_exit_service
    plate = f"MH12UNTRACKED{pytest.rand_id}"
    res = entry_exit_service.process_recognition_event(db, plate_number=plate, ocr_confidence=0.88)
    assert res is not None

def test_13_entry_and_exit_timestamps_dwell_time(db):
    now = datetime.now(timezone.utc)
    entry_t = now - timedelta(minutes=45)
    sec, mins, fmt = trip_service.calculate_dwell_time(entry_t, now)
    assert sec >= 2700.0
    assert mins >= 45.0
    assert "45 Minute" in fmt or "Minute" in fmt

def test_14_late_arrival(db):
    now = datetime.now(timezone.utc)
    expected_entry = now - timedelta(minutes=40)
    status, delay = trip_service.calculate_late_arrival(expected_entry, now)
    assert status == "LATE"
    assert delay >= 2400

def test_15_normal_arrival(db):
    now = datetime.now(timezone.utc)
    expected_entry = now + timedelta(minutes=5)
    status, delay = trip_service.calculate_late_arrival(expected_entry, now)
    assert status == "ON_TIME"

def test_16_overstay_detection(db):
    now = datetime.now(timezone.utc)
    exp_entry = now - timedelta(hours=5)
    exp_exit = now - timedelta(hours=3) # 2 hrs expected stay
    dwell_seconds = 14400.0 # 4 hrs actual stay
    is_overstay, excess = trip_service.check_overstay(dwell_seconds, exp_entry, exp_exit)
    assert is_overstay is True
    assert excess > 0

def test_17_duplicate_exit_frames(db):
    plate = f"MH17DEDUP{pytest.rand_id}"
    v, trip = create_test_vehicle_and_trip(db, plate)
    trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.90, direction="Entering")
    
    # Repeated exit recognitions
    t1 = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.90, direction="Exiting")
    t2 = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.92, direction="Exiting")
    assert t1.id == t2.id
    assert t2.trip_status == "COMPLETED"

def test_18_two_simultaneous_vehicles_independent_trips(db):
    p1 = f"MH18VEH1{pytest.rand_id}"
    p2 = f"MH18VEH2{pytest.rand_id}"
    v1, t1 = create_test_vehicle_and_trip(db, p1)
    v2, t2 = create_test_vehicle_and_trip(db, p2)
    assert t1.id != t2.id

def test_19_trip_history_recorded(db):
    plate = f"MH19HIST{pytest.rand_id}"
    v, trip = create_test_vehicle_and_trip(db, plate)
    trip_service.transition_state(db, trip, "ARRIVED", remarks="Testing history record")
    
    histories = db.query(TripStatusHistory).filter(TripStatusHistory.trip_id == trip.id).all()
    assert len(histories) >= 2

def test_20_existing_image_recognition_regression():
    from app.ai.pipeline import pipeline
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res["vehicle_type"] == "Car"

def test_21_existing_video_recognition_regression():
    from app.ai.pipeline import pipeline
    video_path = os.path.join(backend_dir, "uploads", "videos", "00896225_14703755_1920_1080_30fps.mp4")
    res = pipeline.process_video(video_path, "debug", max_frames=10)
    assert res["tracked_vehicle_count"] >= 1

@pytest.fixture(autouse=True)
def rand_id_fixture(request):
    import random
    pytest.rand_id = str(random.randint(1000, 9999))
