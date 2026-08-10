import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_live_dashboard_endpoint():
    res = client.get("/api/v1/live/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "cameras" in data
    assert "current_vehicle" in data
    assert "inside_vehicles" in data
    assert "timeline" in data
    assert "alerts" in data
    assert "active_trips" in data

    summary = data["summary"]
    assert "vehicles_currently_inside" in summary
    assert "vehicles_entered_today" in summary
    assert "vehicles_exited_today" in summary
    assert "active_trips_count" in summary
    assert "unauthorized_vehicles_count" in summary
    assert "alerts_count" in summary
    assert "avg_stay_time_formatted" in summary


def test_live_events_endpoint():
    res = client.get("/api/v1/live/events")
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
    for evt in events:
        assert "event_type" in evt
        assert "plate_number" in evt
        assert "gate_code" in evt


def test_live_vehicles_inside_endpoint():
    res = client.get("/api/v1/live/vehicles")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data


def test_live_trips_endpoint():
    res = client.get("/api/v1/live/trips")
    assert res.status_code == 200
    trips = res.json()
    assert isinstance(trips, list)
    for t in trips:
        assert "scheduled_vehicle" in t
        assert "current_status" in t


def test_live_alerts_endpoint():
    res = client.get("/api/v1/live/alerts")
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    for alt in alerts:
        assert "title" in alt
        assert "level" in alt
