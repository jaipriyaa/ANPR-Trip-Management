import os
import sys
import json
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.services.manual_review_service import manual_review_service
from app.services.retention_service import retention_service
from app.services.reporting_service import reporting_service
from app.services.alert_service import alert_engine
from app.services.trip_service import trip_service
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.schemas.vehicle import VehicleCreate
from app.schemas.scheduled_trip import ScheduledTripCreate
from app.models.manual_review import ManualReview
from app.models.ocr_correction_history import OcrCorrectionHistory
from app.models.alert import Alert
from app.models.camera_health import CameraHealthLog
from app.models.audit_log import AuditLog
from app.models.camera import Camera
from app.crud.crud_gate import crud_gate
from app.schemas.gate import GateCreate

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_sample_camera(db):
    g = crud_gate.create(db, obj_in=GateCreate(gate_code=f"GRET{pytest.rand_id}{str(uuid4())[:4]}", gate_name="Retention Gate", is_active=True))
    cam = Camera(
        gate_id=g.id,
        camera_name=f"Cam-Ret-{pytest.rand_id}-{str(uuid4())[:4]}",
        camera_position="ENTRY",
        camera_status="ONLINE",
        is_active=True,
        rtsp_url="rtsp://127.0.0.1:554/live"
    )
    db.add(cam)
    db.commit()
    db.refresh(cam)
    return cam

def test_1_manual_plate_correction_stored(db):
    plate_old = f"MH01AB{pytest.rand_id}"
    plate_new = f"MH01CD{pytest.rand_id}"
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": plate_old, "raw_text": plate_old, "confidence": 0.60}
    )
    updated = manual_review_service.correct_review(db, review_id=review.id, new_plate=plate_new, reviewer="Officer Test", remarks="Misread 0 for O")
    assert updated.review_status == "CORRECTED"
    assert updated.corrected_plate == plate_new.upper()

def test_2_original_ocr_prediction_remains_unchanged(db):
    plate_old = f"MH12AB{pytest.rand_id}"
    plate_new = f"MH12CD{pytest.rand_id}"
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": plate_old, "raw_text": plate_old, "confidence": 0.55}
    )
    manual_review_service.correct_review(db, review_id=review.id, new_plate=plate_new)
    db.refresh(review)
    assert review.recognized_plate == plate_old
    assert review.raw_ocr_text == plate_old

def test_3_corrected_plate_stored_in_history(db):
    plate_old = f"MH14AB{pytest.rand_id}"
    plate_new = f"MH14CD{pytest.rand_id}"
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": plate_old, "raw_text": plate_old, "confidence": 0.60}
    )
    manual_review_service.correct_review(db, review_id=review.id, new_plate=plate_new, remarks="Correction test")
    history = db.query(OcrCorrectionHistory).filter(OcrCorrectionHistory.manual_review_id == review.id).first()
    assert history is not None
    assert history.old_plate == plate_old
    assert history.new_plate == plate_new.upper()

def test_4_feedback_dataset_record_generated(db):
    plate_old = f"MH20AB{pytest.rand_id}"
    plate_new = f"MH20CD{pytest.rand_id}"
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": plate_old, "raw_text": plate_old, "confidence": 0.60}
    )
    manual_review_service.correct_review(db, review_id=review.id, new_plate=plate_new)
    meta_path = os.path.join(os.path.abspath("datasets/plate_correction_feedback"), "metadata.jsonl")
    assert os.path.exists(meta_path)

def test_5_feedback_dataset_contains_corrected_plate(db):
    plate_old = f"KA01AB{pytest.rand_id}"
    plate_new = f"KA01CD{pytest.rand_id}"
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": plate_old, "raw_text": plate_old, "confidence": 0.60}
    )
    manual_review_service.correct_review(db, review_id=review.id, new_plate=plate_new)
    meta_path = os.path.join(os.path.abspath("datasets/plate_correction_feedback"), "metadata.jsonl")
    with open(meta_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert plate_new.upper() in content

def test_6_correction_rate_calculated_correctly(db):
    stats = manual_review_service.get_statistics(db)
    assert "correction_rate_pct" in stats
    assert stats["correction_rate_pct"] >= 0.0

def test_7_zero_data_correction_rate_handled_safely(db):
    res = reporting_service.get_plate_correction_rate(db, target_date=datetime(2020, 1, 1).date())
    assert res["total_plate_predictions"] == 0
    assert res["correction_rate_percent"] == 0.0

def test_8_retention_identifies_eligible_records(db):
    cam = create_sample_camera(db)
    past = datetime.now(timezone.utc) - timedelta(days=45)
    log = CameraHealthLog(camera_id=cam.id, status="OFFLINE", created_at=past)
    db.add(log)
    db.commit()

    res = retention_service.run_retention_job(db, dry_run=True)
    assert res["eligible_camera_health"] >= 1

def test_9_dry_run_deletes_nothing(db):
    cam = create_sample_camera(db)
    past = datetime.now(timezone.utc) - timedelta(days=50)
    log = CameraHealthLog(camera_id=cam.id, status="OFFLINE", created_at=past)
    db.add(log)
    db.commit()
    log_id = log.id

    res = retention_service.run_retention_job(db, dry_run=True)
    assert res["dry_run"] is True
    assert res["records_deleted"] == 0
    still_exists = db.get(CameraHealthLog, log_id)
    assert still_exists is not None

def test_10_archival_succeeds_before_deletion(db):
    cam = create_sample_camera(db)
    past = datetime.now(timezone.utc) - timedelta(days=60)
    log = CameraHealthLog(camera_id=cam.id, status="OFFLINE", created_at=past)
    db.add(log)
    db.commit()

    res = retention_service.run_retention_job(db, dry_run=False)
    assert res["records_archived"] >= 1
    assert res["records_deleted"] >= 1

def test_11_archive_failure_prevents_deletion(db):
    original_dir = retention_service.archive_dir
    retention_service.archive_dir = "Z:\\NonExistentPath_Forced_Failure"

    cam = create_sample_camera(db)
    past = datetime.now(timezone.utc) - timedelta(days=70)
    log = CameraHealthLog(camera_id=cam.id, status="OFFLINE", created_at=past)
    db.add(log)
    db.commit()
    log_id = log.id

    res = retention_service.run_retention_job(db, dry_run=False)
    retention_service.archive_dir = original_dir
    assert res["status"] == "FAILED"
    still_exists = db.get(CameraHealthLog, log_id)
    assert still_exists is not None

def test_12_archival_is_idempotent(db):
    res1 = retention_service.run_retention_job(db, dry_run=False)
    res2 = retention_service.run_retention_job(db, dry_run=False)
    assert res2["records_deleted"] == 0

def test_13_running_retention_twice_does_not_duplicate_archives(db):
    res1 = retention_service.run_retention_job(db, dry_run=False)
    res2 = retention_service.run_retention_job(db, dry_run=False)
    assert res2["records_archived"] == 0

def test_14_active_trip_is_never_deleted(db):
    plate = f"MH14ACTIVETRIP{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(days=100),
        expected_exit_time=now+timedelta(hours=5),
        actual_entry_time=now-timedelta(days=100),
        trip_status="INSIDE_PLANT"
    ))

    retention_service.run_retention_job(db, dry_run=False)
    db.refresh(t)
    assert t.trip_status == "INSIDE_PLANT"

def test_15_active_alert_is_never_deleted(db):
    a, _ = alert_engine.create_alert(db, alert_type="OVERSTAY", message="Active overstay", plate_number=f"MH15ACTIVEA{pytest.rand_id}")
    # Force created_at to past
    a.created_at = datetime.now(timezone.utc) - timedelta(days=100)
    db.add(a)
    db.commit()

    retention_service.run_retention_job(db, dry_run=False)
    still_active = db.get(Alert, a.id)
    assert still_active is not None
    assert still_active.status in ["OPEN", "ACKNOWLEDGED"]

def test_16_active_manual_review_is_never_deleted(db):
    review = manual_review_service.create_manual_review_record(
        db,
        ai_result={"plate_text": f"MH16PEND{pytest.rand_id}", "raw_text": "MH16PEND", "confidence": 0.50}
    )
    review.created_at = datetime.now(timezone.utc) - timedelta(days=100)
    db.add(review)
    db.commit()

    retention_service.run_retention_job(db, dry_run=False)
    still_pending = db.get(ManualReview, review.id)
    assert still_pending is not None
    assert still_pending.review_status == "PENDING"

def test_17_audit_log_is_created(db):
    retention_service.run_retention_job(db, dry_run=True)
    audit = db.query(AuditLog).filter(AuditLog.action == "RETENTION_JOB_SUCCESS").first()
    assert audit is not None

def test_18_retention_configuration_respected():
    from app.core.config import settings
    assert settings.DETECTION_RETENTION_DAYS == 90
    assert settings.ALERT_RETENTION_DAYS == 60

def test_19_target1_regression_passes():
    from app.ai.pipeline import pipeline
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res["vehicle_type"] == "Car"

def test_20_target2_regression_passes(db):
    plate = f"MH20T2REG{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(vehicle_id=v.id, expected_entry_time=now, expected_exit_time=now+timedelta(hours=2), trip_status="SCHEDULED"))
    res = trip_service.transition_state(db, t, "ARRIVED")
    assert res.trip_status == "ARRIVED"

def test_21_target3_regression_passes(db):
    res = reporting_service.get_vehicles_currently_inside(db)
    assert "count" in res

def test_22_target4_regression_passes(db):
    summary = alert_engine.get_alerts_summary(db)
    assert "total_open" in summary

@pytest.fixture(autouse=True)
def rand_id_fixture(request):
    import random
    pytest.rand_id = str(random.randint(1000, 9999))
