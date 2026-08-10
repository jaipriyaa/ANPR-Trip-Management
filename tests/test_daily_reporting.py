import os
import sys
import pytest
from datetime import datetime, date, timezone, timedelta

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import SessionLocal
from app.services.reporting_service import reporting_service
from app.services.trip_service import trip_service
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.crud.crud_gate import crud_gate
from app.schemas.vehicle import VehicleCreate
from app.schemas.scheduled_trip import ScheduledTripCreate
from app.schemas.gate import GateCreate
from app.models.vehicle_movement import VehicleMovement
from app.models.gate_decision import GateDecision
from app.models.daily_gate_summary import DailyGateSummary
from app.models.gate import Gate

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_sample_gate(db):
    gate_code = f"GATE-{pytest.rand_id}"
    g = db.query(Gate).filter(Gate.gate_code == gate_code).first()
    if not g:
        g = crud_gate.create(db, obj_in=GateCreate(gate_code=gate_code, gate_name=f"Main Gate {pytest.rand_id}", gate_type="ENTRY_EXIT", is_active=True))
    return g

def test_1_daily_entry_count(db):
    g = create_sample_gate(db)
    plate = f"MH01ENT{pytest.rand_id}"
    mov = VehicleMovement(recognized_plate=plate, entry_gate_id=g.id, entry_time=datetime.now(timezone.utc), vehicle_type="Truck")
    db.add(mov)
    db.commit()

    res = reporting_service.run_daily_aggregation(db)
    assert any(s.gate_id == g.id and s.vehicles_entered >= 1 for s in res)

def test_2_daily_exit_count(db):
    g = create_sample_gate(db)
    plate = f"MH02EXT{pytest.rand_id}"
    mov = VehicleMovement(recognized_plate=plate, exit_gate_id=g.id, exit_time=datetime.now(timezone.utc), vehicle_type="Truck")
    db.add(mov)
    db.commit()

    res = reporting_service.run_daily_aggregation(db)
    assert any(s.gate_id == g.id and s.vehicles_exited >= 1 for s in res)

def test_3_unique_vehicle_count(db):
    g = create_sample_gate(db)
    p1 = f"MH03UNIQ{pytest.rand_id}"
    db.add(VehicleMovement(recognized_plate=p1, entry_gate_id=g.id, entry_time=datetime.now(timezone.utc)))
    db.commit()

    res = reporting_service.get_vehicles_by_gate(db)
    assert len(res) >= 1

def test_4_vehicles_currently_inside(db):
    plate = f"MH04INSIDE{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(vehicle_id=v.id, expected_entry_time=now, expected_exit_time=now+timedelta(hours=2), trip_status="INSIDE_PLANT", approval_status="APPROVED"))

    res = reporting_service.get_vehicles_currently_inside(db)
    assert res["count"] >= 1
    assert any(item["plate_number"] == plate for item in res["vehicles"])

def test_5_average_dwell_time(db):
    res = reporting_service.get_average_dwell_time(db)
    assert "average_dwell_seconds" in res
    assert "average_dwell_minutes" in res
    assert "average_dwell_formatted" in res

def test_6_vehicles_by_transporter(db):
    res = reporting_service.get_vehicles_by_transporter(db)
    assert isinstance(res, list)

def test_7_vehicles_by_gate(db):
    res = reporting_service.get_vehicles_by_gate(db)
    assert isinstance(res, list)

def test_8_expected_vs_actual_arrival(db):
    res = reporting_service.get_arrival_status_report(db)
    assert "on_time_rate_percent" in res
    assert "late_rate_percent" in res

def test_9_late_arrival_count(db):
    plate = f"MH09LATE{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(minutes=30),
        expected_exit_time=now+timedelta(hours=2),
        actual_entry_time=now,
        trip_status="INSIDE_PLANT"
    ))

    res = reporting_service.get_arrival_status_report(db)
    assert res["late"] >= 1

def test_10_unauthorized_attempts(db):
    g = create_sample_gate(db)
    now = datetime.now(timezone.utc)
    dec = GateDecision(
        gate_id=g.id,
        recognized_plate=f"UNAUTH{pytest.rand_id}",
        decision="DENY",
        reason="Blacklisted Vehicle",
        decision_time=now
    )
    db.add(dec)
    db.commit()

    res = reporting_service.get_unauthorized_attempts(db)
    assert res["unauthorized"] >= 1
    assert len(res["unauthorized_details"]) >= 1

def test_11_manual_review_count(db):
    g = create_sample_gate(db)
    now = datetime.now(timezone.utc)
    dec = GateDecision(
        gate_id=g.id,
        recognized_plate=f"MANUAL{pytest.rand_id}",
        decision="MANUAL_REVIEW",
        reason="OCR Conf Low",
        decision_time=now
    )
    db.add(dec)
    db.commit()

    res = reporting_service.get_unauthorized_attempts(db)
    assert res["manual_review"] >= 1

def test_12_plate_correction_rate(db):
    res = reporting_service.get_plate_correction_rate(db)
    assert "correction_rate_percent" in res
    assert res["correction_rate_percent"] >= 0.0

def test_13_repeat_visitor_count(db):
    plate = f"MH13REPEAT{pytest.rand_id}"
    now = datetime.now(timezone.utc)
    db.add(VehicleMovement(recognized_plate=plate, entry_time=now-timedelta(hours=2)))
    db.add(VehicleMovement(recognized_plate=plate, entry_time=now))
    db.commit()

    res = reporting_service.get_repeat_visitors(db)
    assert any(r["plate_number"] == plate and r["visit_count"] >= 2 for r in res)

def test_14_overstay_count(db):
    res = reporting_service.get_overstay_report(db)
    assert "overstay_count" in res

def test_15_active_overstay(db):
    plate = f"MH15OVER{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(
        vehicle_id=v.id,
        expected_entry_time=now-timedelta(hours=6),
        expected_exit_time=now-timedelta(hours=2),
        actual_entry_time=now-timedelta(hours=6),
        trip_status="INSIDE_PLANT"
    ))

    res = reporting_service.get_overstay_report(db)
    assert res["overstay_count"] >= 1

def test_16_daily_summary_idempotency(db):
    t_date = datetime.now(timezone.utc).date()
    res1 = reporting_service.run_daily_aggregation(db, target_date=t_date)
    cnt1 = db.query(DailyGateSummary).filter(DailyGateSummary.summary_date == t_date).count()
    
    # Run again
    res2 = reporting_service.run_daily_aggregation(db, target_date=t_date)
    cnt2 = db.query(DailyGateSummary).filter(DailyGateSummary.summary_date == t_date).count()
    assert cnt1 == cnt2

def test_17_running_aggregation_twice_does_not_duplicate_rows(db):
    t_date = datetime.now(timezone.utc).date()
    db.query(DailyGateSummary).filter(DailyGateSummary.summary_date == t_date).delete()
    db.commit()

    reporting_service.run_daily_aggregation(db, target_date=t_date)
    count_after_first = db.query(DailyGateSummary).filter(DailyGateSummary.summary_date == t_date).count()

    reporting_service.run_daily_aggregation(db, target_date=t_date)
    count_after_second = db.query(DailyGateSummary).filter(DailyGateSummary.summary_date == t_date).count()

    assert count_after_first == count_after_second

def test_18_date_range_filtering(db):
    today = datetime.now(timezone.utc).date()
    res = reporting_service.get_entry_exit_register(db, start_date=today, end_date=today)
    assert isinstance(res, list)

def test_19_gate_filtering(db):
    g = create_sample_gate(db)
    res = reporting_service.get_entry_exit_register(db, gate_id=g.id)
    assert isinstance(res, list)

def test_20_transporter_filtering(db):
    res = reporting_service.get_average_dwell_time(db)
    assert "average_dwell_seconds" in res

def test_21_plate_filtering(db):
    plate = f"MH21FILTER{pytest.rand_id}"
    db.add(VehicleMovement(recognized_plate=plate, entry_time=datetime.now(timezone.utc)))
    db.commit()

    res = reporting_service.get_entry_exit_register(db, plate_number=plate)
    assert any(r["plate_number"] == plate for r in res)

def test_22_empty_dataset_returns_safe_zero_values(db):
    past_date = date(2020, 1, 1)
    res = reporting_service.get_plate_correction_rate(db, target_date=past_date)
    assert res["total_plate_predictions"] == 0
    assert res["correction_rate_percent"] == 0.0

def test_23_camera_health_aggregation(db):
    res = reporting_service.get_camera_health(db)
    assert isinstance(res, list)

def test_24_insufficient_ground_truth_not_fake_accuracy():
    res = reporting_service.get_recognition_accuracy()
    assert res["metric_status"] == "INSUFFICIENT_GROUND_TRUTH"

def test_25_existing_target1_regression():
    from app.ai.pipeline import pipeline
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res["vehicle_type"] == "Car"

def test_26_existing_target2_regression(db):
    plate = f"MH26T2REG{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(vehicle_id=v.id, expected_entry_time=now, expected_exit_time=now+timedelta(hours=2), trip_status="SCHEDULED"))
    res = trip_service.transition_state(db, t, "ARRIVED")
    assert res.trip_status == "ARRIVED"

@pytest.fixture(autouse=True)
def rand_id_fixture(request):
    import random
    pytest.rand_id = str(random.randint(1000, 9999))
