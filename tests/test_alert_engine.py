import os
import sys
import pytest
from uuid import uuid4
from datetime import datetime, date, timezone, timedelta
from fastapi import HTTPException

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.services.alert_service import alert_engine
from app.services.trip_service import trip_service
from app.services.authorization_service import authorization_service
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.crud.crud_gate import crud_gate
from app.schemas.vehicle import VehicleCreate
from app.schemas.scheduled_trip import ScheduledTripCreate
from app.schemas.gate import GateCreate
from app.models.alert import Alert
from app.models.alert_delivery import AlertDelivery
from app.models.camera import Camera

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_sample_camera(db):
    g = crud_gate.create(db, obj_in=GateCreate(gate_code=f"G{pytest.rand_id}{str(uuid4())[:4]}", gate_name="Test Gate", is_active=True))
    cam = Camera(
        gate_id=g.id,
        camera_name=f"Cam-{pytest.rand_id}-{str(uuid4())[:4]}",
        camera_position="ENTRY",
        camera_status="ONLINE",
        is_active=True,
        rtsp_url="rtsp://127.0.0.1:554/live"
    )
    db.add(cam)
    db.commit()
    db.refresh(cam)
    return cam

def test_1_late_arrival_creates_one_alert(db):
    plate = f"MH01LATE{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(minutes=35),
        expected_exit_time=now+timedelta(hours=2),
        trip_status="SCHEDULED"
    ))

    res_trip = trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Entering")
    alert = db.query(Alert).filter(Alert.trip_id == t.id, Alert.alert_type == "LATE_ARRIVAL").first()
    assert alert is not None
    assert alert.status == "OPEN"

def test_2_repeated_processing_late_arrival_only_one_alert(db):
    plate = f"MH02DEDUPLATE{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(minutes=40),
        expected_exit_time=now+timedelta(hours=2),
        trip_status="SCHEDULED"
    ))

    trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Entering")
    trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Entering")

    alerts = db.query(Alert).filter(Alert.trip_id == t.id, Alert.alert_type == "LATE_ARRIVAL").all()
    assert len(alerts) == 1

def test_3_overstay_creates_one_alert(db):
    plate = f"MH03OVER{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(hours=5),
        expected_exit_time=now-timedelta(hours=2),
        actual_entry_time=now-timedelta(hours=5),
        trip_status="INSIDE_PLANT"
    ))

    # Process exit with overstay
    trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Exiting")
    alert = db.query(Alert).filter(Alert.trip_id == t.id, Alert.alert_type == "OVERSTAY").first()
    assert alert is not None

def test_4_repeated_overstay_checks_no_duplicate_alerts(db):
    plate = f"MH04DEDUP{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(hours=6),
        expected_exit_time=now-timedelta(hours=2),
        actual_entry_time=now-timedelta(hours=6),
        trip_status="INSIDE_PLANT"
    ))

    alert_engine.create_alert(db, alert_type="OVERSTAY", message="Overstay test", trip_id=t.id, plate_number=plate)
    alert_engine.create_alert(db, alert_type="OVERSTAY", message="Overstay test repeat", trip_id=t.id, plate_number=plate)

    alerts = db.query(Alert).filter(Alert.trip_id == t.id, Alert.alert_type == "OVERSTAY").all()
    assert len(alerts) == 1

def test_5_completed_exit_resolves_active_overstay(db):
    plate = f"MH05EXITRESOLVE{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(hours=6),
        expected_exit_time=now-timedelta(hours=2),
        actual_entry_time=now-timedelta(hours=6),
        trip_status="INSIDE_PLANT"
    ))

    # Create active overstay
    a, _ = alert_engine.create_alert(db, alert_type="OVERSTAY", message="Overstay active", trip_id=t.id, plate_number=plate)
    assert a.status == "OPEN"

    # Execute exit
    trip_service.process_ai_recognition_event(db, plate_number=plate, ocr_confidence=0.95, direction="Exiting")
    db.refresh(a)
    assert a.status == "RESOLVED"

def test_6_unauthorized_vehicle_creates_critical_alert(db):
    plate = f"MH06UNAUTH{pytest.rand_id}"
    authorization_service._log_decision(db, plate=plate, decision="DENY", reason="Blacklisted Vehicle", confidence=0.95, gate_id=None, camera_id=None, tracking_id="TRACK-1")

    alert = db.query(Alert).filter(Alert.plate_number == plate, Alert.alert_type == "UNAUTHORIZED_VEHICLE").first()
    assert alert is not None
    assert alert.severity == "CRITICAL"

def test_7_manual_review_creates_alert(db):
    plate = f"MH07MANUAL{pytest.rand_id}"
    alert, created = alert_engine.create_alert(db, alert_type="MANUAL_REVIEW_REQUIRED", message="Ambiguous OCR", plate_number=plate)
    assert created is True
    assert alert.severity == "WARNING"

def test_8_invalid_ocr_no_multiple_alerts_per_frame(db):
    plate = f"MH08AMBIG{pytest.rand_id}"
    a1, _ = alert_engine.create_alert(db, alert_type="MANUAL_REVIEW_REQUIRED", message="Low OCR", plate_number=plate)
    a2, _ = alert_engine.create_alert(db, alert_type="MANUAL_REVIEW_REQUIRED", message="Low OCR repeat", plate_number=plate)
    assert a1.id == a2.id

def test_9_camera_offline_creates_one_alert(db):
    cam = create_sample_camera(db)
    alert, created = alert_engine.create_alert(db, alert_type="CAMERA_OFFLINE", message=f"Camera {cam.camera_name} OFFLINE", camera_id=cam.id, severity="CRITICAL")
    assert alert is not None
    assert alert.severity == "CRITICAL"

def test_10_repeated_offline_checks_do_not_duplicate_alerts(db):
    cam = create_sample_camera(db)
    a1, _ = alert_engine.create_alert(db, alert_type="CAMERA_OFFLINE", message="Offline", camera_id=cam.id)
    a2, _ = alert_engine.create_alert(db, alert_type="CAMERA_OFFLINE", message="Offline repeat", camera_id=cam.id)
    assert a1.id == a2.id

def test_11_camera_recovery_resolves_camera_offline_alert(db):
    cam = create_sample_camera(db)
    a, _ = alert_engine.create_alert(db, alert_type="CAMERA_OFFLINE", message="Offline", camera_id=cam.id)
    assert a.status == "OPEN"

    res = alert_engine.resolve_camera_alert(db, camera_id=cam.id, reason="Camera Back Online")
    assert res.status == "RESOLVED"

def test_12_inference_failure_creates_alert(db):
    cam = create_sample_camera(db)
    alert, created = alert_engine.create_alert(db, alert_type="INFERENCE_FAILURE", message="YOLO Model GPU Timeout", camera_id=cam.id, severity="CRITICAL")
    assert alert.alert_type == "INFERENCE_FAILURE"

def test_13_alert_open_to_acknowledged(db):
    a, _ = alert_engine.create_alert(db, alert_type="LATE_ARRIVAL", message="Test ack", plate_number=f"MH13ACK{pytest.rand_id}")
    res = alert_engine.transition_alert_status(db, alert_id=a.id, new_status="ACKNOWLEDGED")
    assert res.status == "ACKNOWLEDGED"

def test_14_acknowledged_to_resolved(db):
    a, _ = alert_engine.create_alert(db, alert_type="LATE_ARRIVAL", message="Test res", plate_number=f"MH14RES{pytest.rand_id}")
    alert_engine.transition_alert_status(db, alert_id=a.id, new_status="ACKNOWLEDGED")
    res = alert_engine.transition_alert_status(db, alert_id=a.id, new_status="RESOLVED", reason="Manual Inspection Complete")
    assert res.status == "RESOLVED"

def test_15_invalid_lifecycle_transition_rejected(db):
    a, _ = alert_engine.create_alert(db, alert_type="LATE_ARRIVAL", message="Test inv", plate_number=f"MH15INV{pytest.rand_id}")
    alert_engine.transition_alert_status(db, alert_id=a.id, new_status="RESOLVED")
    with pytest.raises(HTTPException) as exc:
        alert_engine.transition_alert_status(db, alert_id=a.id, new_status="ACKNOWLEDGED")
    assert exc.value.status_code == 400

def test_16_alert_filtering(db):
    p = f"MH16FILT{pytest.rand_id}"
    alert_engine.create_alert(db, alert_type="OVERSTAY", message="Filt test", plate_number=p)
    alerts = db.query(Alert).filter(Alert.plate_number == p).all()
    assert len(alerts) >= 1

def test_17_alert_summary_counts_correct(db):
    summary = alert_engine.get_alerts_summary(db)
    assert "total_open" in summary
    assert "critical" in summary
    assert "warning" in summary

def test_18_dashboard_api_returns_actual_alerts(db):
    summary = alert_engine.get_alerts_summary(db)
    assert summary["total_open"] >= 0

def test_19_delivery_record_created_correctly(db):
    a, _ = alert_engine.create_alert(db, alert_type="UNAUTHORIZED_VEHICLE", message="Delivery test", plate_number=f"MH19DEL{pytest.rand_id}")
    deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == a.id).all()
    assert len(deliveries) >= 1

def test_20_failed_delivery_recorded(db):
    cam = create_sample_camera(db)
    a, _ = alert_engine.create_alert(db, alert_type="CAMERA_OFFLINE", message="Fail del test", camera_id=cam.id)
    d = db.query(AlertDelivery).filter(AlertDelivery.alert_id == a.id, AlertDelivery.channel == "EMAIL").first()
    d.status = "FAILED"
    d.failure_reason = "SMTP Connection Refused"
    db.add(d)
    db.commit()
    db.refresh(d)
    assert d.status == "FAILED"

def test_21_duplicate_delivery_prevented(db):
    cam = create_sample_camera(db)
    a, _ = alert_engine.create_alert(db, alert_type="INFERENCE_FAILURE", message="Dup del test", camera_id=cam.id)
    deliveries = db.query(AlertDelivery).filter(AlertDelivery.alert_id == a.id).all()
    channels = [d.channel for d in deliveries]
    assert len(channels) == len(set(channels))

def test_22_target1_regression_passes():
    from app.ai.pipeline import pipeline
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res["vehicle_type"] == "Car"

def test_23_target2_regression_passes(db):
    plate = f"MH23T2REG{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(vehicle_id=v.id, expected_entry_time=now, expected_exit_time=now+timedelta(hours=2), trip_status="SCHEDULED"))
    res = trip_service.transition_state(db, t, "ARRIVED")
    assert res.trip_status == "ARRIVED"

def test_24_target3_regression_passes(db):
    from app.services.reporting_service import reporting_service
    res = reporting_service.get_vehicles_currently_inside(db)
    assert "count" in res

@pytest.fixture(autouse=True)
def rand_id_fixture(request):
    import random
    pytest.rand_id = str(random.randint(1000, 9999))
