import os
import sys
import hashlib
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta

backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import torch
import onnx
import onnxruntime as ort
from ultralytics import YOLO

from app.ai.pipeline import pipeline
from app.ai.inference.video_pipeline import video_pipeline
from app.ai.inference.backend_selector import BackendSelector, get_active_backend_info, is_tensorrt_available
from app.database.connection import SessionLocal
from app.services.trip_service import trip_service
from app.services.reporting_service import reporting_service
from app.services.alert_service import alert_engine
from app.services.retention_service import retention_service
from app.crud.crud_vehicle import crud_vehicle
from app.crud.crud_scheduled_trip import crud_scheduled_trip
from app.schemas.vehicle import VehicleCreate
from app.schemas.scheduled_trip import ScheduledTripCreate

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_1_pt_model_integrity():
    v_pt = os.path.abspath("models/vehicle_detector.pt")
    p_pt = os.path.abspath("models/license_plate_detector.pt")
    assert os.path.exists(v_pt)
    assert os.path.exists(p_pt)

    v_model = YOLO(v_pt)
    p_model = YOLO(p_pt)
    assert len(v_model.names) == 4
    assert len(p_model.names) == 1

def test_2_onnx_model_integrity():
    v_onnx = os.path.abspath("models/vehicle_detector.onnx")
    p_onnx = os.path.abspath("models/license_plate_detector.onnx")
    assert os.path.exists(v_onnx)
    assert os.path.exists(p_onnx)

    v_m = onnx.load(v_onnx)
    p_m = onnx.load(p_onnx)
    onnx.checker.check_model(v_m)
    onnx.checker.check_model(p_m)

def test_3_vehicle_onnx_inference():
    v_onnx = os.path.abspath("models/vehicle_detector.onnx")
    sess = ort.InferenceSession(v_onnx)
    assert len(sess.get_inputs()) > 0
    inp_name = sess.get_inputs()[0].name
    dummy_input = {inp_name: torch.randn(1, 3, 640, 640).numpy()}
    outs = sess.run(None, dummy_input)
    assert len(outs) > 0

def test_4_plate_onnx_inference():
    p_onnx = os.path.abspath("models/license_plate_detector.onnx")
    sess = ort.InferenceSession(p_onnx)
    assert len(sess.get_inputs()) > 0
    inp_name = sess.get_inputs()[0].name
    dummy_input = {inp_name: torch.randn(1, 3, 640, 640).numpy()}
    outs = sess.run(None, dummy_input)
    assert len(outs) > 0

def test_5_backend_selection():
    selector = BackendSelector(
        engine_path="models/tensorrt/vehicle_detector_fp16.engine",
        onnx_path="models/vehicle_detector.onnx",
        pt_path="models/vehicle_detector.pt",
        model_name="TestVehicle"
    )
    resolved = selector.resolve_backend()
    assert resolved in ["PYTORCH", "ONNX", "TENSORRT"]

def test_6_tensorrt_fallback():
    # Force TensorRT requested on missing engine file -> should gracefully fallback to ONNX or PYTORCH
    selector = BackendSelector(
        engine_path="models/non_existent_engine.engine",
        onnx_path="models/vehicle_detector.onnx",
        pt_path="models/vehicle_detector.pt",
        model_name="FallbackTest"
    )
    # Simulate requested TensorRT
    os.environ["MODEL_BACKEND"] = "TENSORRT"
    resolved = selector.resolve_backend()
    os.environ["MODEL_BACKEND"] = "AUTO"
    assert resolved in ["ONNX", "PYTORCH"]

def test_7_image_inference_regression():
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res["vehicle_type"] == "Car"
    assert "plate_text" in res

def test_8_video_inference_regression():
    vid_path = os.path.join(backend_dir, "uploads", "videos", "00896225_14703755_1920_1080_30fps.mp4")
    res = video_pipeline.process_video(vid_path)
    assert res["processed_frame_count"] > 0
    assert len(res["vehicles"]) > 0

def test_9_vehicle_class_mapping():
    v_pt = os.path.abspath("models/vehicle_detector.pt")
    v_model = YOLO(v_pt)
    mapping = v_model.names
    assert mapping[0].lower() == "car"
    assert mapping[1].lower() in ["motorcycle", "motorbike"]
    assert mapping[2].lower() == "bus"
    assert mapping[3].lower() == "truck"

def test_10_plate_class_mapping():
    p_pt = os.path.abspath("models/license_plate_detector.pt")
    p_model = YOLO(p_pt)
    mapping = p_model.names
    assert mapping[0].lower() in ["license_plate", "plate"]

def test_11_pipeline_output_contract():
    info = get_active_backend_info()
    assert "status" in info
    assert "backend" in info
    assert "inference_backend" in info

def test_12_target1_regression():
    img_path = os.path.join(backend_dir, "uploads", "images", "3cac5a75_car 3.jpg")
    res = pipeline.process_image(img_path, "debug")
    assert res.get("vehicle_type") == "Car"

def test_13_target2_regression(db):
    plate = f"MH13T6REG{pytest.rand_id}"
    v = crud_vehicle.create(db, obj_in=VehicleCreate(vehicle_number=plate, vehicle_type="Truck", is_active=True))
    now = datetime.now(timezone.utc)
    t = crud_scheduled_trip.create(db, obj_in=ScheduledTripCreate(vehicle_id=v.id, expected_entry_time=now, expected_exit_time=now+timedelta(hours=2), trip_status="SCHEDULED"))
    res = trip_service.transition_state(db, t, "ARRIVED")
    assert res.trip_status == "ARRIVED"

def test_14_target3_regression(db):
    res = reporting_service.get_vehicles_currently_inside(db)
    assert "count" in res

def test_15_target4_regression(db):
    summary = alert_engine.get_alerts_summary(db)
    assert "total_open" in summary

def test_16_target5_regression(db):
    job_res = retention_service.run_retention_job(db, dry_run=True)
    assert job_res["dry_run"] is True

@pytest.fixture(autouse=True)
def rand_id_fixture(request):
    import random
    pytest.rand_id = str(random.randint(1000, 9999))
