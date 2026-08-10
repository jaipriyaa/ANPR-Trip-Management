import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_pipeline_statistics():
    res = client.get("/api/v1/pipeline/statistics")
    assert res.status_code == 200
    data = res.json()
    assert "duplicate_events_removed" in data
    assert "vehicles_matched" in data
    assert "ocr_feedback_count" in data


def test_daily_and_gate_summaries_api():
    # 1. Daily summary
    ds_res = client.get("/api/v1/daily-summary")
    assert ds_res.status_code == 200
    ds_data = ds_res.json()
    assert "items" in ds_data
    assert len(ds_data["items"]) >= 1

    # 2. Gate summary
    gs_res = client.get("/api/v1/gate-summary")
    assert gs_res.status_code == 200
    gs_data = gs_res.json()
    assert "items" in gs_data


def test_late_arrivals_and_overstay_scans():
    # Late arrivals
    late_res = client.get("/api/v1/late-arrivals")
    assert late_res.status_code == 200
    assert "items" in late_res.json()

    # Overstay
    over_res = client.get("/api/v1/overstay?max_allowed_mins=60")
    assert over_res.status_code == 200
    assert "items" in over_res.json()


def test_archive_jobs_and_cleanup_trigger():
    # 1. Trigger archival
    arch_res = client.post("/api/v1/archive/run?retention_days=180")
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "SUCCESS"

    # 2. Get archive jobs
    jobs_res = client.get("/api/v1/archive/jobs")
    assert jobs_res.status_code == 200
    assert len(jobs_res.json()["items"]) >= 1

    # 3. Trigger cleanup
    clean_res = client.post("/api/v1/cleanup")
    assert clean_res.status_code == 200
    assert clean_res.json()["success"] is True


def test_ocr_feedback_dataset_api():
    feed_res = client.get("/api/v1/ocr-feedback")
    assert feed_res.status_code == 200
    assert "items" in feed_res.json()
