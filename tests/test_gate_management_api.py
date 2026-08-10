import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_get_gate():
    payload = {
        "gate_code": "TEST-GATE-01",
        "gate_name": "Test Factory Gate 1",
        "gate_type": "Entry & Exit",
        "location": "Testing Area",
        "description": "Gate created for API testing.",
        "status": "ACTIVE",
        "is_active": True
    }
    response = client.post("/api/v1/gates", json=payload)
    assert response.status_code in [201, 400]

    if response.status_code == 201:
        data = response.json()
        assert data["gate_code"] == "TEST-GATE-01"
        assert data["gate_name"] == "Test Factory Gate 1"
        gate_id = data["id"]

        # Duplicate code test
        dup_res = client.post("/api/v1/gates", json=payload)
        assert dup_res.status_code == 400
        assert "already exists" in dup_res.json()["detail"]

        # Get by ID
        get_res = client.get(f"/api/v1/gates/{gate_id}")
        assert get_res.status_code == 200
        assert get_res.json()["gate_code"] == "TEST-GATE-01"


def test_assign_camera_to_gate():
    # First get list of gates
    gates_res = client.get("/api/v1/gates")
    assert gates_res.status_code == 200
    gates = gates_res.json()["items"]
    assert len(gates) > 0
    gate_id = gates[0]["id"]

    camera_payload = {
        "gate_id": gate_id,
        "camera_name": "Test ANPR Cam 1",
        "camera_position": "Entry Camera",
        "rtsp_url": "rtsp://192.168.1.200:554/live",
        "ip_address": "192.168.1.200",
        "camera_status": "Online",
        "resolution": "1080p",
        "fps": 30,
        "is_active": True
    }
    res = client.post("/api/v1/gate-cameras", json=camera_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["camera_name"] == "Test ANPR Cam 1"
    assert data["gate_id"] == gate_id

    # Invalid RTSP URL validation test
    invalid_payload = dict(camera_payload)
    invalid_payload["rtsp_url"] = "ftp://invalid-url"
    inv_res = client.post("/api/v1/gate-cameras", json=invalid_payload)
    assert inv_res.status_code == 422


def test_configure_and_get_gate_rules():
    gates_res = client.get("/api/v1/gates")
    assert gates_res.status_code == 200
    gates = gates_res.json()["items"]
    assert len(gates) > 0
    gate_id = gates[0]["id"]

    rule_payload = {
        "gate_id": gate_id,
        "allow_entry": True,
        "allow_exit": False,
        "allow_trucks": True,
        "allow_buses": False,
        "allow_cars": True,
        "allow_two_wheelers": False,
        "maximum_vehicle_height": 4.2,
        "maximum_vehicle_weight": 35.0,
        "authorized_only": True,
        "working_hours_start": "07:00",
        "working_hours_end": "19:00",
        "remarks": "Automated security rule testing."
    }
    res = client.post("/api/v1/gate-rules", json=rule_payload)
    assert res.status_code in [200, 201]

    # Get rules for gate
    get_res = client.get(f"/api/v1/gate-rules/{gate_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["allow_entry"] is True
    assert data["allow_exit"] is False
    assert data["maximum_vehicle_height"] == 4.2
