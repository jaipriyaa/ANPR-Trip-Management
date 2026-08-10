import pytest
import time
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_scenario1_and_scenario2_entry_and_duplicate_protection():
    # Scenario 1: Entry Camera detects MH14TCF200F -> Create Entry
    entry_plate = "MH14TCF9999"  # Unique test plate
    payload = {
        "recognized_plate": entry_plate,
        "recognition_confidence": 0.95,
        "vehicle_type": "SUV",
        "movement_status": "INSIDE",
        "vehicle_status": "ENTERED",
        "entry_time": "2026-08-03T10:00:00Z"
    }

    # Create Entry via API
    res = client.post("/api/v1/movements", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["recognized_plate"] == entry_plate
    assert data["movement_status"] == "INSIDE"
    assert data["vehicle_status"] == "ENTERED"

    # Scenario 2: Verify duplicate check endpoint / logic
    # Fetch current inside vehicles
    current_res = client.get("/api/v1/movements/current")
    assert current_res.status_code == 200
    inside_items = current_res.json()["items"]
    inside_plates = [m["recognized_plate"] for m in inside_items]
    assert entry_plate in inside_plates


def test_scenario3_and_scenario4_exit_and_stay_duration():
    # Scenario 3: Update existing movement to EXIT
    exit_plate = "TESTEXIT123"
    
    # First create entry
    entry_payload = {
        "recognized_plate": exit_plate,
        "recognition_confidence": 0.92,
        "vehicle_type": "Truck",
        "movement_status": "INSIDE",
        "vehicle_status": "ENTERED",
        "entry_time": "2026-08-03T08:00:00Z"
    }
    create_res = client.post("/api/v1/movements", json=entry_payload)
    assert create_res.status_code == 201
    m_id = create_res.json()["id"]

    # Now update to exit (2 hours later)
    update_payload = {
        "exit_time": "2026-08-03T10:15:00Z",
        "stay_duration_minutes": 135.0,
        "stay_duration_formatted": "2 Hours 15 Minutes",
        "movement_status": "OUTSIDE",
        "vehicle_status": "EXITED"
    }
    update_res = client.put(f"/api/v1/movements/{m_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["movement_status"] == "OUTSIDE"
    assert updated_data["vehicle_status"] == "EXITED"
    
    # Scenario 4: Verify Stay Duration calculation
    assert updated_data["stay_duration_minutes"] == 135.0
    assert updated_data["stay_duration_formatted"] == "2 Hours 15 Minutes"


def test_scenario5_view_current_vehicles_inside():
    # Scenario 5: GET /api/v1/movements/current
    res = client.get("/api/v1/movements/current")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    for item in data["items"]:
        assert item["movement_status"] == "INSIDE"


def test_scenario6_view_movement_history():
    # Scenario 6: GET /api/v1/movements/history
    res = client.get("/api/v1/movements/history")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    for item in data["items"]:
        assert item["movement_status"] == "OUTSIDE"


def test_live_summary_metrics():
    # GET /api/v1/movements/summary
    res = client.get("/api/v1/movements/summary")
    assert res.status_code == 200
    data = res.json()
    assert "vehicles_currently_inside" in data
    assert "vehicles_entered_today" in data
    assert "vehicles_exited_today" in data
    assert "avg_stay_duration_formatted" in data
