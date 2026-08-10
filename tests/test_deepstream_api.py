"""
Automated Pytest Suite for NVIDIA DeepStream 7.x API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_deepstream_streams():
    response = client.get("/api/v1/deepstream/streams")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert data[0]["id"] == "stream-0"
    assert "rtsp_url" in data[0]


def test_get_deepstream_metrics():
    response = client.get("/api/v1/deepstream/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["pipeline_status"] == "RUNNING"
    assert data["deepstream_version"] == "7.0.0"
    assert "total_throughput_fps" in data
    assert "gpu_memory_used_mb" in data


def test_add_and_remove_deepstream_stream():
    # 1. Add new dynamic RTSP stream
    add_payload = {
        "name": "North Gate Auxiliary Camera",
        "rtsp_url": "rtsp://192.168.1.150:554/stream1",
        "gate_id": "GATE-NORTH-01",
        "camera_type": "GATE_IN"
    }
    add_res = client.post("/api/v1/deepstream/streams", json=add_payload)
    assert add_res.status_code == 201
    created_stream = add_res.json()
    stream_id = created_stream["id"]
    assert created_stream["name"] == add_payload["name"]

    # 2. Verify stream is listed
    list_res = client.get("/api/v1/deepstream/streams")
    stream_ids = [s["id"] for s in list_res.json()]
    assert stream_id in stream_ids

    # 3. Remove dynamic RTSP stream
    del_res = client.delete(f"/api/v1/deepstream/streams/{stream_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "SUCCESS"

    # 4. Verify stream is removed
    list_res_after = client.get("/api/v1/deepstream/streams")
    stream_ids_after = [s["id"] for s in list_res_after.json()]
    assert stream_id not in stream_ids_after


def test_deepstream_webhook_event():
    webhook_payload = {
        "stream_id": "stream-0",
        "camera_id": "GATE_IN_CAM_01",
        "gate_id": "GATE-ENTRY-01",
        "license_plate": "03ACU808",
        "confidence": 0.96,
        "vehicle_type": "Truck",
        "tracking_id": 1042,
        "roi_zone": "roi-gate-entry",
        "line_crossing_event": "line-crossing-entry"
    }
    res = client.post("/api/v1/deepstream/webhook", json=webhook_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["license_plate"] == "03ACU808"
    assert "authorization_decision" in data
