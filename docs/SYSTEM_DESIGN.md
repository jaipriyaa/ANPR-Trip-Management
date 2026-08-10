# Industrial Vehicle Trip Management System - Technical System Design Specification

This specification documents the technical architecture, operational layers, and request processing flows.

---

## 1. Architectural Layers Specification

### 1.1 Presentation Layer (ReactJS 18 + Vite + TailwindCSS)
- **Single Page Application (SPA)**: Client-side routing with `react-router-dom` v6.
- **State & Data Ingestion**: Asynchronous REST data fetching via Axios and TanStack Query (React Query).
- **UI Component System**: Modular layout with sidebar navigation, metric cards, modal dialogs, and real-time status badges.

### 1.2 Business Logic Layer (FastAPI Application)
- **REST Endpoints**: FastAPI async controllers organized by domain (`transporters`, `vehicles`, `trips`, `recognition`, `authorization`, `benchmark`).
- **Data Validation**: Strict type checking via Pydantic V2 schemas.
- **Security & Authorization**: JWT token validation, Role-Based Access Control (RBAC), and CORS middleware.

### 1.3 AI Edge Inference Layer
- **YOLOv11 Vehicle Detector**: Object detector categorizing 9 vehicle sub-types.
- **DeepSORT Vehicle Tracker**: Unique tracklet ID tracking across sequential video frames.
- **License Plate Localization**: YOLOv11 plate detector cropping plate bounding boxes.
- **Perspective Rectification & Preprocessing**: Homography perspective transformation and CLAHE contrast enhancement.
- **Multi-pass OCR Subsystem**: EasyOCR ensemble reading raw and preprocessed plate crops.
- **Indian Regex Rectification**: Validation against Indian state plate formats with character confusion correction.

### 1.4 Database & Persistence Layer (PostgreSQL 16)
- **Relational Data Storage**: PostgreSQL 16 enforcing primary keys, foreign keys, and indexes.
- **ORM Tier**: SQLAlchemy 2.0 ORM with Alembic migration version control.

### 1.5 Deployment & Infrastructure Layer
- **Containerization**: Multi-stage Docker build producing lightweight Nginx frontend and Python 3.11 backend containers.
- **NVIDIA Edge Acceleration**: Native FP16 TensorRT compilation for NVIDIA Jetson hardware with dynamic ONNX Runtime fallback.

---

## 2. Request Processing & Functional Flows

### 2.1 Vehicle Detection Flow
1. IP camera streams RTSP video or user uploads an image frame.
2. OpenCV reads image matrix and letterboxes frame to 640x640 resolution.
3. YOLOv11 vehicle detector returns bounding boxes, class labels, and detection confidence.
4. DeepSORT tracker computes IoU overlap and updates vehicle tracking IDs.

### 2.2 Recognition Flow
1. Vehicle bounding box is passed to license plate detector.
2. Plate region is cropped and passed to perspective rectification module.
3. Homography transform squares tilted plates; CLAHE enhances contrast.
4. Multi-pass EasyOCR extracts text; Indian regex validates format (`State Code + 2 Digits + 2 Letters + 4 Digits`).
5. Confusion matrix corrects misreads (`0`<->`O`, `1`<->`I`, `8`<->`B`).

### 2.3 Trip Lifecycle Flow
1. Dispatcher creates trip ticket (`PLANNED`).
2. Vehicle arrives at gate; ANPR scans plate matching active trip (`REGISTERED`).
3. Gate decision engine verifies authorization and raises boom barrier (`IN_PLANT`).
4. Vehicle departs through exit gate; departure time is logged and trip completed (`COMPLETED`).

### 2.4 Entry / Exit Flow
1. Gate camera scans vehicle plate at entry or exit gate.
2. System checks active gate rules and direction (`ENTRY` vs `EXIT`).
3. Entry/exit movement record is persisted in `vehicle_movements` table with timestamp and crop URL.

### 2.5 Authorization Flow
1. System checks `watchlist` table: if matched, trigger immediate security alert (`DENY`).
2. System checks `whitelist` table: if matched, return `ALLOW`.
3. System checks `trips` table: if active trip exists for gate, return `ALLOW`. Otherwise return `DENY`.

### 2.6 Reporting Flow
1. User selects date range and report category (Dwell Time, Gate Summaries, Late Arrivals).
2. Backend queries PostgreSQL aggregated views.
3. Report generator formats data into tabular JSON, CSV, PDF, or Excel export.
