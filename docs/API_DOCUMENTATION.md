# Industrial Vehicle Trip Management System - REST API Specification

Base URL: `http://localhost:8000/api/v1`

---

## 1. Sequence Diagrams

### 1.1 User Login & Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as FastAPI Auth Endpoint
    participant DB as PostgreSQL DB

    User->>API: POST /api/v1/auth/login {username, password}
    API->>DB: Query User & Validate Hashed Password
    DB-->>API: User Verified
    API-->>User: Return JWT Access Token {access_token, token_type: "bearer"}
```

### 1.2 Vehicle Registration Flow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Admin / User
    participant API as FastAPI Vehicles Endpoint
    participant DB as PostgreSQL DB

    Admin->>API: POST /api/v1/vehicles {registration_number, vehicle_type, transporter_id}
    API->>DB: Check Unique Registration Number
    API->>DB: Insert Vehicle Record
    DB-->>API: Record Created (ID: 101)
    API-->>Admin: HTTP 201 Created Payload
```

### 1.3 Vehicle Recognition Flow

```mermaid
sequenceDiagram
    autonumber
    actor Camera as Camera / Client Upload
    participant API as FastAPI Recognition Endpoint
    participant AI as AI Inference Subsystem
    participant DB as PostgreSQL DB

    Camera->>API: POST /api/v1/vehicle-recognition/process-image (Multipart File)
    API->>AI: Execute Pipeline (YOLO Vehicle -> Plate Crop -> EasyOCR)
    AI-->>API: Extracted Text "KA01AB1234", Confidence 0.95, BBoxes
    API->>DB: Log Detection Event & Save Crop File
    API-->>Camera: HTTP 200 JSON Prediction Payload
```

### 1.4 Trip Creation Flow

```mermaid
sequenceDiagram
    autonumber
    actor Dispatcher as Dispatcher
    participant API as FastAPI Trips Endpoint
    participant DB as PostgreSQL DB

    Dispatcher->>API: POST /api/v1/trips {trip_number, vehicle_id, driver_id}
    API->>DB: Validate Vehicle & Driver Status
    API->>DB: Insert Trip Record (Status: PLANNED)
    DB-->>API: Trip Created
    API-->>Dispatcher: HTTP 201 Created Payload
```

### 1.5 Entry Approval Flow

```mermaid
sequenceDiagram
    autonumber
    actor GateCam as Entry Gate Camera
    participant API as FastAPI Gate / Auth Endpoint
    participant Auth as Auth Engine
    participant DB as PostgreSQL DB
    participant Barrier as Boom Barrier

    GateCam->>API: POST /api/v1/movements (Plate: "KA01AB1234", Gate: 1, Type: ENTRY)
    API->>Auth: Verify Access Rules & Active Trip
    Auth-->>API: Decision: ALLOW
    API->>DB: Update Trip Status to IN_PLANT & Log Movement
    API->>Barrier: Trigger Relay Open
    API-->>GateCam: HTTP 200 Decision Allowed
```

### 1.6 Exit Approval Flow

```mermaid
sequenceDiagram
    autonumber
    actor GateCam as Exit Gate Camera
    participant API as FastAPI Gate / Auth Endpoint
    participant DB as PostgreSQL DB
    participant Barrier as Boom Barrier

    GateCam->>API: POST /api/v1/movements (Plate: "KA01AB1234", Gate: 2, Type: EXIT)
    API->>DB: Find Active IN_PLANT Trip
    API->>DB: Compute Dwell Time & Update Trip Status to COMPLETED
    API->>Barrier: Trigger Relay Open
    API-->>GateCam: HTTP 200 Exit Complete Payload
```

### 1.7 Authorization Flow

```mermaid
sequenceDiagram
    autonumber
    actor GateClient as Gate Scan Event
    participant AuthAPI as FastAPI Authorization Endpoint
    participant Rules as Rule Evaluator
    participant DB as PostgreSQL DB

    GateClient->>AuthAPI: POST /api/v1/authorization/verify {plate_number, gate_id}
    AuthAPI->>Rules: Check Watchlist -> Whitelist -> Active Trips
    Rules->>DB: Query Security Tables
    DB-->>Rules: Security Records
    Rules-->>AuthAPI: Rule Decision Payload
    AuthAPI-->>GateClient: HTTP 200 {decision: "ALLOW", barrier_open_signal: true}
```

---

## 2. API Endpoint Specification

### 2.1 Master Data APIs (`/transporters`, `/vehicles`, `/drivers`)

#### `GET /api/v1/transporters`
- **Method**: `GET`
- **Purpose**: Retrieves list of registered logistics transporters.
- **Response `200 OK`**:
```json
[
  {
    "id": 1,
    "code": "TR-1001",
    "name": "Apex Logistics Services",
    "contact_email": "ops@apexlogistics.com",
    "phone": "+91-9876543210",
    "is_active": true
  }
]
```

#### `POST /api/v1/transporters`
- **Method**: `POST`
- **Purpose**: Creates a new transporter.
- **Request Body**:
```json
{
  "code": "TR-1002",
  "name": "Vanguard Freight Carriers",
  "contact_email": "info@vanguard.com",
  "phone": "+91-9123456789",
  "address": "GURGAON, HARYANA",
  "is_active": true
}
```
- **Response `201 Created`**: Returns created object with assigned ID.

---

### 2.2 AI Recognition APIs (`/vehicle-recognition`)

#### `POST /api/v1/vehicle-recognition/process-image`
- **Method**: `POST`
- **Form Data**: `file` (Image binary)
- **Response `200 OK`**:
```json
{
  "processing_time": 0.028,
  "vehicles": [
    {
      "tracking_id": "TEMP-001",
      "vehicle_type": "Heavy Truck",
      "vehicle_confidence": 0.9421,
      "vehicle_bbox": [300, 200, 980, 580],
      "plates": [
        {
          "plate_bbox": [540, 480, 740, 540],
          "confidence": 0.925,
          "plate_text": "KA01AB1234",
          "raw_text": "KA01AB1234",
          "corrected_plate": "KA01AB1234",
          "is_valid_plate": true
        }
      ]
    }
  ],
  "plate_text": "KA01AB1234",
  "confidence": 0.925,
  "is_valid_plate": true,
  "vehicle_count": 1
}
```

---

### 2.3 System & Performance APIs (`/system`, `/benchmark`)

#### `GET /api/v1/system/health`
- **Method**: `GET`
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "backend": "ONNX",
  "inference_backend": "ONNX (CPU)",
  "tensorrt_available": false,
  "onnx_available": true,
  "pytorch_available": true,
  "cuda_available": false,
  "gpu": "N/A",
  "gpu_enabled": false,
  "model_version": "v11.0-edge-anpr"
}
```

#### `GET /api/v1/system/performance`
- **Method**: `GET`
- **Response `200 OK`**: Returns live CPU %, RAM MB, GPU %, Disk usage, and application uptime.
