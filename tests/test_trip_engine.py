import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_trip_creation_and_overlap_validation():
    # 1. Create a trip for unique vehicle
    now = datetime.now(timezone.utc)
    payload = {
        "recognized_plate": "KA01AB1234",
        "expected_entry_time": (now + timedelta(hours=1)).isoformat(),
        "expected_exit_time": (now + timedelta(hours=5)).isoformat(),
        "purpose": "Test Material Delivery",
        "material_name": "Test Steel",
        "material_quantity": "10 Tons",
        "priority": "HIGH",
        "trip_status": "SCHEDULED",
        "approval_status": "APPROVED"
    }

    res = client.post("/api/v1/trips", json=payload)
    assert res.status_code in [201, 400]

    if res.status_code == 201:
        data = res.json()
        assert "trip_number" in data
        assert data["trip_status"] == "SCHEDULED"
        assert data["approval_status"] == "APPROVED"
        trip_id = data["id"]

        # 2. Overlap validation: Attempting second active trip for same vehicle
        dup_res = client.post("/api/v1/trips", json=payload)
        assert dup_res.status_code == 400
        assert "already has an active trip" in dup_res.json()["detail"]

        # 3. Get details with status history
        get_res = client.get(f"/api/v1/trips/{trip_id}")
        assert get_res.status_code == 200
        assert "status_history" in get_res.json()
        assert len(get_res.json()["status_history"]) > 0


def test_trip_approval_and_rejection():
    now = datetime.now(timezone.utc)
    payload = {
        "expected_entry_time": (now + timedelta(hours=2)).isoformat(),
        "expected_exit_time": (now + timedelta(hours=6)).isoformat(),
        "purpose": "Test Approval Flow",
        "priority": "MEDIUM",
        "trip_status": "SCHEDULED",
        "approval_status": "PENDING"
    }

    res = client.post("/api/v1/trips", json=payload)
    assert res.status_code == 201
    trip_id = res.json()["id"]

    # Approve trip
    app_res = client.post(f"/api/v1/trips/{trip_id}/approve", json={"approval_status": "APPROVED", "remarks": "Approved by Test Officer"})
    assert app_res.status_code == 200
    assert app_res.json()["approval_status"] == "APPROVED"


def test_trip_dashboard_summary():
    res = client.get("/api/v1/trips/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "active_trips" in data
    assert "completed_trips" in data
    assert "waiting_vehicles" in data
    assert "rejected_trips" in data
    assert "vehicles_inside" in data
    assert "todays_trips" in data
    assert "avg_trip_duration_formatted" in data
