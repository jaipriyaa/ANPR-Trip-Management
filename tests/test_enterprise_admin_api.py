import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analytics_dashboard_api():
    res = client.get("/api/v1/admin/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "charts" in data
    assert "vehicles_entered_today" in data["kpis"]
    assert "hourly_counts" in data["charts"]


def test_reports_api_json_and_csv():
    # 1. JSON Report
    res = client.get("/api/v1/admin/reports?report_type=Daily%20Vehicle%20Report&export_format=JSON")
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "Daily Vehicle Report"
    assert "rows" in data

    # 2. CSV Export Stream
    csv_res = client.get("/api/v1/admin/reports?report_type=Daily%20Vehicle%20Report&export_format=CSV")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]


def test_user_management_and_rbac_api():
    # List users
    get_res = client.get("/api/v1/admin/users")
    assert get_res.status_code == 200
    assert isinstance(get_res.json(), list)

    # Create user
    new_user = {
        "username": "test_security_officer",
        "email": "officer@test.com",
        "full_name": "Officer Test",
        "role": "Security Officer"
    }
    create_res = client.post("/api/v1/admin/users", json=new_user)
    assert create_res.status_code in [201, 400]

    # Roles matrix
    roles_res = client.get("/api/v1/admin/roles")
    assert roles_res.status_code == 200
    assert len(roles_res.json()) >= 5


def test_audit_logs_api():
    res = client.get("/api/v1/admin/audit")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data


def test_camera_and_model_health_api():
    # Camera health
    c_res = client.get("/api/v1/admin/camera-health")
    assert c_res.status_code == 200
    assert isinstance(c_res.json(), list)

    # Model health
    m_res = client.get("/api/v1/admin/model-health")
    assert m_res.status_code == 200
    m_data = m_res.json()
    assert "model_version" in m_data
    assert "average_inference_ms" in m_data


def test_system_settings_api():
    # Get settings
    get_res = client.get("/api/v1/admin/settings")
    assert get_res.status_code == 200

    # Put settings
    put_res = client.put("/api/v1/admin/settings", json={"recognition_confidence_threshold": "0.80"})
    assert put_res.status_code == 200
    assert put_res.json()["settings"]["recognition_confidence_threshold"] == "0.80"
