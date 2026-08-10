import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_whitelist_and_watchlist_crud():
    # 1. Whitelist CRUD
    w_res = client.post("/api/v1/whitelist", json={
        "recognized_plate": "TESTPLATE01",
        "allowed_entry_gates": "ALL",
        "status": "ACTIVE",
        "remarks": "Test Whitelist Entry"
    })
    assert w_res.status_code == 201
    assert w_res.json()["recognized_plate"] == "TESTPLATE01"

    get_w = client.get("/api/v1/whitelist")
    assert get_w.status_code == 200
    assert get_w.json()["total"] >= 1

    # 2. Watchlist CRUD
    wat_res = client.post("/api/v1/watchlist", json={
        "plate_number": "WATCHPLATE01",
        "reason": "Test Stolen Vehicle Alert",
        "severity": "CRITICAL",
        "status": "ACTIVE"
    })
    assert wat_res.status_code == 201
    assert wat_res.json()["plate_number"] == "WATCHPLATE01"

    get_wat = client.get("/api/v1/watchlist")
    assert get_wat.status_code == 200
    assert get_wat.json()["total"] >= 1


def test_authorization_gate_check_decision_matrix():
    # 1. Test Watchlist Hit -> DENY
    watch_check = client.post("/api/v1/authorization/check", json={"plate_number": "WATCHPLATE01"})
    assert watch_check.status_code == 200
    w_data = watch_check.json()
    assert w_data["decision"] == "DENY"
    assert w_data["watchlist_hit"] is True

    # 2. Test Whitelist Hit -> ALLOW
    white_check = client.post("/api/v1/authorization/check", json={"plate_number": "TESTPLATE01"})
    assert white_check.status_code == 200
    w_data2 = white_check.json()
    assert w_data2["decision"] == "ALLOW"

    # 3. Test Unknown Vehicle -> UNKNOWN_VEHICLE
    unk_check = client.post("/api/v1/authorization/check", json={"plate_number": "UNREGISTERED99"})
    assert unk_check.status_code == 200
    u_data = unk_check.json()
    assert u_data["decision"] == "UNKNOWN_VEHICLE"


def test_gate_decisions_and_manual_override():
    # Get gate decision history
    hist_res = client.get("/api/v1/gate-decisions")
    assert hist_res.status_code == 200
    data = hist_res.json()
    assert "items" in data
    assert len(data["items"]) > 0

    target_id = data["items"][0]["id"]

    # Process manual override
    override_res = client.post("/api/v1/manual-approval", json={
        "decision_id": target_id,
        "action": "MANUAL_APPROVAL",
        "officer_name": "Major Rajesh Verma",
        "remarks": "Manual Officer Override Test"
    })
    assert override_res.status_code == 200
    assert override_res.json()["decision"] == "MANUAL_APPROVAL"


def test_authorization_dashboard_summary():
    res = client.get("/api/v1/authorization/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "authorized_today" in data
    assert "denied_today" in data
    assert "pending_manual_queue" in data
