# Industrial Vehicle Trip Management System - System Architecture Specification

This document details the high-level architecture, module breakdowns, and visual diagrams for the complete enterprise platform.

---

## 1. Overall Enterprise Architecture

```mermaid
graph TD
    Client[ReactJS Web Frontend / Gate Kiosk UI] -->|HTTP REST / WebSocket| Nginx[Nginx Reverse Proxy / Load Balancer @ Port 3000]
    Nginx -->|Proxy /api/*| FastAPI[FastAPI Backend Application @ Port 8000]
    
    subgraph Business Service Layer
        FastAPI --> AuthEngine[Authorization & Security Engine]
        FastAPI --> TripEngine[Trip Lifecycle Engine]
        FastAPI --> GateEngine[Entry / Exit Gate Engine]
        FastAPI --> DataPipeline[Data Engineering & Summaries]
    end

    subgraph AI Inference Subsystem
        FastAPI --> BackendSel[Backend Selector: TensorRT -> ONNX -> PyTorch]
        BackendSel --> TRTEngine[NVIDIA TensorRT Engine (FP16)]
        BackendSel --> ONNXEngine[ONNX Runtime Engine]
        BackendSel --> PyTorchEngine[PyTorch YOLOv11 Engine]
        BackendSel --> EasyOCR[Multi-pass EasyOCR Engine]
    end

    subgraph Storage & Persistence Tier
        FastAPI --> Postgres[(PostgreSQL 16 Relational DB)]
        FastAPI --> Redis[(Redis 7 Cache)]
        FastAPI --> Disk[Local Media / Docker Volume]
    end
```

---

## 2. AI Recognition Pipeline Architecture

```mermaid
graph LR
    Input[Frame / RTSP Stream] --> Preproc[Letterbox Resize & Preprocessing]
    Preproc --> VehDet[YOLOv11 Vehicle Detector]
    VehDet --> Tracker[DeepSORT Vehicle Tracker]
    Tracker --> PltDet[YOLOv11 License Plate Detector]
    PltDet --> Crop[Plate Crop Extraction]
    Crop --> Rectify[Homography & Perspective Correction]
    Rectify --> OCR[Multi-pass EasyOCR Ensemble]
    OCR --> RegexVal[Indian Plate Format Validation]
    RegexVal --> Output[JSON ANPR Prediction Payload]
```

---

## 3. Database Entity Relationship (ER) Diagram

```mermaid
erDiagram
    TRANSPORTERS ||--o{ VEHICLES : owns
    TRANSPORTERS ||--o{ DRIVERS : employs
    VEHICLES ||--o{ VEHICLE_PLATES : registers
    VEHICLES ||--o{ TRIPS : scheduled
    DRIVERS ||--o{ TRIPS : drives
    GATES ||--o{ GATE_CAMERAS : mounts
    GATES ||--o{ VEHICLE_MOVEMENTS : logs
    TRIPS ||--o{ VEHICLE_MOVEMENTS : records
    VEHICLES ||--o{ WHITELIST : listed
    VEHICLES ||--o{ WATCHLIST : tracked

    TRANSPORTERS {
        int id PK
        string code UK
        string name
        boolean is_active
    }
    VEHICLES {
        int id PK
        string registration_number UK
        string vehicle_type
        int transporter_id FK
    }
    DRIVERS {
        int id PK
        string license_number UK
        string name
    }
    GATES {
        int id PK
        string name
        string gate_type
    }
    TRIPS {
        int id PK
        string trip_number UK
        int vehicle_id FK
        string status
    }
    VEHICLE_MOVEMENTS {
        int id PK
        int gate_id FK
        string plate_number
        string movement_type
        timestamp timestamp
    }
```

---

## 4. Recognition Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor GateCamera as IP Camera / Operator
    participant API as FastAPI Backend
    participant AI as AI Inference Engine
    participant DB as PostgreSQL DB

    GateCamera->>API: Upload Image / Stream Frame
    API->>AI: Execute Pipeline (Vehicle -> Plate -> OCR)
    AI-->>API: Return Bounding Boxes, Text ("KA01AB1234") & Confidence
    API->>DB: Save Recognition Event & Crop Image Path
    API-->>GateCamera: Return Recognition Result Payload
```

---

## 5. Entry / Exit Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Vehicle as Gate Vehicle Scan
    participant Gate as Gate Controller
    participant Auth as Auth Engine
    participant Trip as Trip Engine
    participant Barrier as Boom Barrier

    Vehicle->>Gate: Plate Scanned ("KA01AB1234")
    Gate->>Auth: Verify Access Rules
    Auth-->>Gate: Decision: ALLOW (Whitelisted / Valid Trip)
    Gate->>Trip: Update Trip Status (REGISTERED -> IN_PLANT)
    Gate->>Barrier: Send Relay Open Signal
    Barrier-->>Vehicle: Boom Barrier Raised
```

---

## 6. Trip Engine Workflow Diagram

```mermaid
stateDiagram-v2
    [*] --> PLANNED: Trip Schedule Created
    PLANNED --> REGISTERED: Vehicle Arrives at Security Checkpost
    REGISTERED --> IN_PLANT: Entry Gate Scan Verified & Barrier Raised
    IN_PLANT --> COMPLETED: Exit Gate Departure Logged
    COMPLETED --> [*]
    REGISTERED --> CANCELLED: Trip Cancelled by Dispatcher
    IN_PLANT --> OVERSTAY_ALERT: Plant Dwell Time Exceeds Limit
```

---

## 7. Authorization Workflow Diagram

```mermaid
flowchart TD
    Start[Plate Scanned at Gate] --> CheckWatchlist{Is Plate on Watchlist?}
    CheckWatchlist -- Yes --> DenyWatchlist[Decision: DENY - Security Threat Triggered]
    CheckWatchlist -- No --> CheckWhitelist{Is Plate on Whitelist?}
    CheckWhitelist -- Yes --> AllowWhitelist[Decision: ALLOW - VIP / Authorized Fleet]
    CheckWhitelist -- No --> CheckActiveTrip{Has Active Approved Trip?}
    CheckActiveTrip -- Yes --> AllowTrip[Decision: ALLOW - Valid Plant Trip Ticket]
    CheckActiveTrip -- No --> DenyNoTrip[Decision: DENY - No Active Trip Schedule]
```

---

## 8. Docker Deployment Architecture Diagram

```mermaid
graph TD
    subgraph Docker Bridge Network: anpr-bridge-network
        FE[Frontend Container: Nginx + React @ Port 3000]
        BE[Backend Container: FastAPI + AI @ Port 8000]
        DB[PostgreSQL Container: Postgres 16 @ Port 5432]
        Redis[Redis Container: Cache @ Port 6379]
    end

    FE -->|Proxy /api/*| BE
    BE -->|SQLAlchemy ORM| DB
    BE -->|Redis-py| Redis

    subgraph Host Storage Volumes
        DB --- Vol1[(anpr_postgres_data)]
        BE --- Vol2[(anpr_uploads_data)]
        BE --- Vol3[(anpr_models_data)]
        BE --- Vol4[(anpr_logs_data)]
    end
```
