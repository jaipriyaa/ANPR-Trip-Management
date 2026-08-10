# Industrial Vehicle Trip Management System - Project Changelog

All notable changes, feature additions, performance optimizations, and bug fixes for the project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v3.5.0] - 2026-08-06 (Phase 14 - Submission Package & Final Review)
### Added
- Enterprise documentation suite in `docs/` (18 technical manuals, Mermaid architecture/sequence diagrams, API references, DB schema, user manual, review guide, FAQ, presentation content, and final review report).
- Reviewer artifacts: `REVIEW_GUIDE.md`, `FAQ.md`, `PRESENTATION_CONTENT.md` (20 slides with speaker notes), and `FINAL_REVIEW_REPORT.md`.
- Final audit checklist: `SUBMISSION_CHECKLIST.md`.

---

## [v3.4.0] - 2026-08-06 (Phase 13 - Docker Production Containerization)
### Added
- Multi-container Docker deployment (`backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `docker-compose.prod.yml`).
- Database readiness wait and automatic schema migration script (`backend/entrypoint.sh`).
- Nginx reverse proxy configuration (`frontend/nginx.conf`).

---

## [v3.3.0] - 2026-08-06 (Phase 12.4 - Performance Benchmarking & System Profiling)
### Added
- Performance benchmarking subsystem (`backend/app/benchmark/`).
- Real-time hardware telemetry monitor (`psutil` CPU, RAM, GPU, Disk, Uptime).
- Automated report generator (`JSON`, `CSV`, `Markdown`, `Text`) and 8 diagnostic PNG charts.
- React Performance Dashboard view (`/performance-dashboard`).

---

## [v3.2.0] - 2026-08-06 (Phase 12.2 - NVIDIA TensorRT Deployment Layer)
### Added
- Hardware-aware `BackendSelector` with `TensorRT` -> `ONNX` -> `PyTorch` auto-resolution.
- Jetson engine generation scripts (`deployment/generate_engine.sh`, `deployment/generate_tensorrt.sh`).
- Windows guardrails blocking invalid cross-compilation.

---

## [v3.1.0] - 2026-08-06 (Phase 12.1 - ONNX Export & Verification)
### Added
- PyTorch model exporter (`deployment/export_onnx.py`).
- ONNX model verifier (`deployment/verify_onnx.py`).
- Exported models in `models/vehicle_detector.onnx` and `models/plate_detector.onnx`.

---

## [v1.0.0 - v3.0.0] - 2026-08-01 to 2026-08-05 (Phases 1 - 11 Core Implementation)
### Added
- Master Data Management (Transporters, Vehicles, Vehicle Plates, Drivers).
- AI Edge Subsystem (YOLOv11 Vehicle Detection, DeepSORT Tracking, Plate Detection, Multi-pass EasyOCR Engine, Indian Plate Format Rectification).
- Gate Operations & Live Control Room.
- Trip Engine & Entry/Exit Event Logger.
- Security Authorization Engine (Whitelist, Watchlist, Gate Decisions).
- Manual Review Queue & OCR Feedback Dataset.
- Data Engineering Pipeline (Summaries, Overstay Monitor, Archival Manager).
