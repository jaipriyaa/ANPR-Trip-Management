# Industrial Vehicle Trip Management System - Project Structure & Directory Walkthrough

This document details the codebase directory structure, module responsibilities, and file locations.

---

## 1. Directory Tree Map

```
ANPR-Trip-Management/
├── .env.example                  # Template for environment configuration
├── .dockerignore                 # Docker build ignore exclusions
├── docker-compose.yml            # Multi-container Docker Compose orchestration
├── docker-compose.prod.yml       # Production Docker Compose extension
├── DEMO_SCRIPT.md                # Presentation & live demo script
├── SUBMISSION_CHECKLIST.md       # Final submission audit checklist
├── README.md                     # Master project README
├── pytest.ini                    # Pytest framework configuration
│
├── backend/                      # FastAPI Backend Service
│   ├── Dockerfile                # Python 3.11 slim backend image
│   ├── entrypoint.sh             # DB wait, table creation & migration startup script
│   ├── requirements.txt          # Python dependencies
│   ├── create_tables.py          # SQLAlchemy table setup script
│   ├── yolo11n.pt                # Base YOLOv11 model weights
│   ├── alembic/                  # Database migration version control
│   └── app/                      # Application source code
│       ├── main.py               # FastAPI application entry point
│       ├── api/v1/               # REST API endpoints & router
│       │   ├── endpoints/        # Feature routers (Transporters, Vehicles, Trips, Recognition, System, Benchmark)
│       │   └── router.py         # Primary API router
│       ├── ai/                   # AI Edge Subsystem
│       │   ├── config/           # AI Settings & model resolution
│       │   ├── vehicle_detector/ # YOLOv11 Vehicle Detector & DeepSORT Tracker
│       │   ├── plate_detector/   # License Plate Detector & Cropper
│       │   ├── ocr/              # Multi-pass EasyOCR Engine
│       │   ├── preprocessing/    # Perspective correction & CLAHE enhancement
│       │   ├── postprocessing/   # Indian Plate Regex & Confusion Matrix Correction
│       │   └── inference/        # Backend Selector & Pipeline Engine
│       ├── benchmark/            # Performance Benchmarking Subsystem
│       │   ├── metrics.py        # Latency & accuracy dataclasses
│       │   ├── system_monitor.py # Real-time psutil & CUDA telemetry
│       │   ├── report_generator.py# Report & chart generator
│       │   └── benchmark_runner.py# Main benchmark orchestrator
│       ├── core/                 # Pydantic Settings & Security
│       ├── crud/                 # Database Repositories
│       ├── database/             # PostgreSQL Session Lifecycle
│       ├── models/               # SQLAlchemy ORM Models
│       └── schemas/              # Pydantic V2 Schemas
│
├── frontend/                     # ReactJS Web Frontend
│   ├── Dockerfile                # Multi-stage Node 20 / Nginx Alpine image
│   ├── nginx.conf                # Nginx SPA server & API reverse proxy
│   ├── package.json              # React dependencies
│   ├── vite.config.js            # Vite build configuration
│   └── src/                      # Source code
│       ├── App.jsx               # Main React layout & routes
│       ├── main.jsx              # React entry point
│       ├── components/           # UI components (Sidebar, Navigation)
│       └── pages/                # 28 Application Page Views
│           └── PerformanceDashboardPage.jsx # Performance Dashboard
│
├── deployment/                   # Deployment Scripts & Diagnostics
│   ├── export_onnx.py            # PyTorch to ONNX exporter script
│   ├── verify_onnx.py            # ONNX Runtime graph verifier
│   ├── system_check.py           # Hardware & environment diagnostic suite
│   ├── generate_engine.sh        # Jetson TensorRT trtexec compilation script
│   ├── generate_tensorrt.sh      # Jetson engine generator wrapper
│   ├── DOCKER_SETUP.md           # Docker deployment guide
│   ├── JETSON_DEPLOYMENT.md      # Jetson deployment guide
│   ├── TENSORRT_GUIDE.md         # TensorRT tuning guide
│   └── BENCHMARK.md              # Benchmarking methodology
│
├── models/                       # Exported AI Engine & ONNX Models
│   ├── vehicle_detector.onnx    # Exported Vehicle Detector ONNX model (10.2 MB)
│   └── plate_detector.onnx      # Exported License Plate Detector ONNX model (10.2 MB)
│
├── weights/                      # Model Weight Files
│   └── yolo11n.pt                # Base YOLOv11 weights
│
├── tests/                        # Automated Pytest Test Suite (44 Passing Tests)
│   ├── test_authorization_engine.py
│   ├── test_data_engineering_pipeline.py
│   ├── test_deepstream_api.py
│   ├── test_enterprise_admin_api.py
│   ├── test_entry_exit_engine.py
│   ├── test_gate_management_api.py
│   ├── test_live_monitor_api.py
│   ├── test_manual_review_system.py
│   ├── test_module1_api.py
│   ├── test_multiframe_tracking_fusion.py
│   └── test_trip_engine.py
│
└── docs/                         # Core Documentation Package
    ├── README.md                 # Master documentation README
    ├── INSTALL.md                # Installation manual
    ├── ARCHITECTURE.md           # Architecture specification & 8 Mermaid diagrams
    ├── SYSTEM_DESIGN.md          # Technical system design specification
    ├── PROJECT_STRUCTURE.md      # Project directory structure
    └── DATABASE_SCHEMA.md        # Database schema specification & ER diagram
```

---

## 2. Important Folder Descriptions

### `backend/`
- **Purpose**: Server application hosting FastAPI REST APIs, business services, database ORM, and AI edge inference engine.
- **Responsibilities**: API handling, validation, database interactions, model execution, benchmark execution.

### `frontend/`
- **Purpose**: Single Page Application providing 28 operational views for web users and gate operators.
- **Responsibilities**: UI rendering, live monitor updates, vehicle management, trip scheduling, benchmark dashboard.

### `deployment/`
- **Purpose**: System diagnostic, model export, and hardware acceleration deployment scripts.
- **Responsibilities**: Exporting ONNX, compiling TensorRT, system checking.

### `models/` & `weights/`
- **Purpose**: Storage of PyTorch weights (`.pt`), ONNX graphs (`.onnx`), and TensorRT compiled engines (`.engine`).

### `tests/`
- **Purpose**: Pytest test suite containing 44 unit, integration, and API tests.
