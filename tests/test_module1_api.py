import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_transporter_crud_lifecycle():
    suffix = uuid.uuid4().hex[:6]
    code = f"TR-LOG-{suffix}"
    
    # 1. Create Transporter
    payload = {
        "code": code,
        "company_name": f"Apex Logistics {suffix}",
        "contact_person": "John Doe",
        "phone": "+91 9876543210",
        "email": f"contact-{suffix}@apexlogistics.com",
        "is_active": True
    }
    response = client.post("/api/v1/transporters", json=payload)
    assert response.status_code == 201
    data = response.json()
    transporter_id = data["id"]
    assert data["code"] == code

    # 2. Prevent Duplicate Code
    duplicate_res = client.post("/api/v1/transporters", json=payload)
    assert duplicate_res.status_code == 400

    # 3. List Transporters
    list_res = client.get(f"/api/v1/transporters?search={code}")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1

    # 4. Get Transporter by ID
    get_res = client.get(f"/api/v1/transporters/{transporter_id}")
    assert get_res.status_code == 200

    # 5. Update Transporter
    update_res = client.put(f"/api/v1/transporters/{transporter_id}", json={"contact_person": "Jane Smith"})
    assert update_res.status_code == 200
    assert update_res.json()["contact_person"] == "Jane Smith"


def test_vehicle_and_plate_lifecycle():
    suffix = uuid.uuid4().hex[:6]
    t_res = client.post("/api/v1/transporters", json={
        "code": f"TR-FLEET-{suffix}",
        "company_name": f"FastTrack Logistics {suffix}"
    })
    assert t_res.status_code == 201
    transporter_id = t_res.json()["id"]

    # 1. Create Vehicle
    veh_num = f"KA01AB{suffix.upper()[:4]}"
    v_payload = {
        "vehicle_number": veh_num,
        "vehicle_type": "Truck",
        "make_model": "Volvo FH16",
        "color": "White",
        "capacity_tons": 25.5,
        "transporter_id": transporter_id,
        "is_active": True,
        "is_blacklisted": False
    }
    response = client.post("/api/v1/vehicles", json=v_payload)
    assert response.status_code == 201
    v_data = response.json()
    vehicle_id = v_data["id"]
    assert v_data["vehicle_number"] == veh_num
    assert len(v_data["plates"]) == 1

    # 2. Add secondary plate
    sec_plate = f"KA01TR{suffix.upper()[:4]}"
    p_payload = {
        "vehicle_id": vehicle_id,
        "plate_number": sec_plate,
        "plate_type": "Commercial",
        "is_primary": False
    }
    p_res = client.post("/api/v1/vehicle-plates", json=p_payload)
    assert p_res.status_code == 201

    # 3. Get Vehicle to verify plates list
    get_v = client.get(f"/api/v1/vehicles/{vehicle_id}")
    assert get_v.status_code == 200
    assert len(get_v.json()["plates"]) == 2


def test_driver_lifecycle():
    suffix = uuid.uuid4().hex[:6]
    lic_num = f"DL-{suffix.upper()}"
    d_payload = {
        "full_name": f"Robert Miller {suffix}",
        "license_number": lic_num,
        "phone_number": "+91 9123456789",
        "identity_card_no": f"ID-{suffix}"
    }
    response = client.post("/api/v1/drivers", json=d_payload)
    assert response.status_code == 201
    d_data = response.json()
    driver_id = d_data["id"]
    assert d_data["license_number"] == lic_num

    # 2. Duplicate License check
    dup_res = client.post("/api/v1/drivers", json=d_payload)
    assert dup_res.status_code == 400

    # 3. List Drivers
    l_res = client.get(f"/api/v1/drivers?search={lic_num}")
    assert l_res.status_code == 200
    assert l_res.json()["total"] >= 1
