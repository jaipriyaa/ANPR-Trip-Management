# API Testing & Consumer Integration Guide

This guide provides code snippets and testing instructions for interacting with the backend APIs via cURL, Python `requests`, JavaScript `fetch`, and Postman.

---

## 1. Testing with cURL Command Line

### 1.1 GET Request: Check System Health
```bash
curl -X GET "http://localhost:8000/api/system/health" \
     -H "accept: application/json"
```

### 1.2 POST Request: Process Vehicle Image via AI ANPR
```bash
curl -X POST "http://localhost:8000/api/v1/vehicle-recognition/process-image" \
     -H "accept: application/json" \
     -F "file=@/path/to/vehicle_test.jpg"
```

### 1.3 POST Request: Create Transporter Record
```bash
curl -X POST "http://localhost:8000/api/v1/transporters" \
     -H "Content-Type: application/json" \
     -d '{
           "code": "TR-999",
           "name": "Express Logistics Ltd",
           "contact_email": "ops@express.com",
           "phone": "+91-9876500000",
           "is_active": true
         }'
```

---

## 2. Testing with Python (`requests` Library)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Health Check
res = requests.get("http://localhost:8000/api/system/health")
print("Health Status:", res.json())

# 2. Upload Image for ANPR Processing
with open("test_vehicle.jpg", "rb") as f:
    files = {"file": ("test_vehicle.jpg", f, "image/jpeg")}
    response = requests.post(f"{BASE_URL}/vehicle-recognition/process-image", files=files)
    print("ANPR Prediction:", response.json())

# 3. Create Vehicle Master Record
vehicle_payload = {
    "registration_number": "KA01AB9999",
    "vehicle_type": "Heavy Truck",
    "transporter_id": 1,
    "is_active": True
}
res = requests.post(f"{BASE_URL}/vehicles", json=vehicle_payload)
print("Create Vehicle Status Code:", res.status_code)
```

---

## 3. Testing with JavaScript (`fetch` / Axios)

```javascript
// Test System Performance Endpoint
async function getSystemPerformance() {
  const response = await fetch('http://localhost:8000/api/system/performance');
  const data = await response.json();
  console.log('CPU Usage:', data.cpu.usage_percent + '%');
  console.log('Active Backend:', data.runtime.active_backend);
}

getSystemPerformance();
```
