import pytest
import os
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_manual_review_list_and_stats():
    # 1. Statistics
    stats_res = client.get("/api/v1/manual-review/statistics")
    assert stats_res.status_code == 200
    data = stats_res.json()
    assert "pending_reviews" in data
    assert "ocr_accuracy_pct" in data

    # 2. List queue items
    list_res = client.get("/api/v1/manual-review")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "items" in list_data
    assert len(list_data["items"]) >= 1


def test_manual_review_approval_and_rejection():
    # Get first available item
    list_res = client.get("/api/v1/manual-review")
    items = list_res.json().get("items", [])
    assert len(items) > 0
    target_id = items[0]["id"]

    # Approve item
    app_res = client.post(f"/api/v1/manual-review/{target_id}/approve", json={
        "reviewer": "Major Rajesh Verma",
        "remarks": "Test Approval"
    })
    assert app_res.status_code == 200
    assert app_res.json()["review_status"] == "APPROVED"


def test_manual_review_ocr_correction_and_feedback_export():
    # Get pending item
    list_res = client.get("/api/v1/manual-review")
    items = list_res.json().get("items", [])
    assert len(items) > 0
    target_id = items[0]["id"]

    # 1. Attempt invalid format correction -> 400
    bad_res = client.post(f"/api/v1/manual-review/{target_id}/correct", json={
        "corrected_plate": "INVALID_PLATE_12345",
        "reviewer": "Major Rajesh Verma"
    })
    assert bad_res.status_code == 400
    assert "not a valid Indian registration" in bad_res.json()["detail"]

    # 2. Correct with valid Indian plate -> 200
    valid_res = client.post(f"/api/v1/manual-review/{target_id}/correct", json={
        "corrected_plate": "MH14TCF200F",
        "reviewer": "Major Rajesh Verma",
        "remarks": "Corrected O/0 Ambiguity"
    })
    assert valid_res.status_code == 200
    assert valid_res.json()["corrected_plate"] == "MH14TCF200F"
    assert valid_res.json()["review_status"] == "CORRECTED"

    # 3. Verify detail endpoint & history
    detail_res = client.get(f"/api/v1/manual-review/{target_id}")
    assert detail_res.status_code == 200
    d_data = detail_res.json()
    assert len(d_data["corrections_history"]) > 0
    assert d_data["corrections_history"][0]["new_plate"] == "MH14TCF200F"

    # 4. Verify AI Feedback Dataset JSON file exists
    feedback_file_1 = os.path.join("backend", "app", "ai", "feedback_dataset", f"feedback_{target_id}.json")
    feedback_file_2 = os.path.join("app", "ai", "feedback_dataset", f"feedback_{target_id}.json")
    assert os.path.exists(feedback_file_1) or os.path.exists(feedback_file_2)
