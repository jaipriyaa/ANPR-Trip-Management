# Industrial ANPR System - Architectural FAQ & Technical Q&A

This document provides answers to technical architecture, design, and deployment questions commonly asked during code reviews and evaluation sessions.

---

## 1. Core Technology Selection FAQs

### Q1: Why FastAPI over Flask or Django for the Backend?
**Answer**: FastAPI provides asynchronous I/O (`asyncdef` concurrency), automatic OpenAPI / Swagger documentation generation, and high data validation performance powered by Pydantic V2. This is critical for handling non-blocking AI inference requests and real-time gate camera streams.

### Q2: Why React 18 for the Frontend Interface?
**Answer**: React's component-based virtual DOM architecture enables modular development across 28 operational views. TanStack Query (React Query) handles server state caching, ensuring smooth real-time updates for live gate feeds without page reloads.

### Q3: Why PostgreSQL 16 for the Database Layer?
**Answer**: PostgreSQL provides robust ACID compliance, structured relational integrity across foreign key dependencies (Transporters -> Vehicles -> Trips -> Movements), advanced B-Tree indexing, and scale readiness for enterprise logistics operations.

### Q4: Why YOLOv11 for Vehicle & Plate Detection?
**Answer**: YOLOv11 (Ultralytics) provides state-of-the-art single-pass object detection speed and accuracy. The small model size (10.2 MB) letterboxed to 640x640 resolution delivers sub-10ms detection on edge hardware while maintaining > 98% accuracy.

---

## 2. AI Edge Pipeline & Optimization FAQs

### Q5: Why ONNX Runtime?
**Answer**: ONNX (Open Neural Network Exchange) decouples model training (PyTorch) from edge inference execution. ONNX Runtime provides cross-platform execution providers (CPU, CUDA, TensorRT) with ~2x speedups over raw PyTorch execution.

### Q6: Why NVIDIA TensorRT?
**Answer**: NVIDIA TensorRT optimizes neural network graphs specifically for NVIDIA GPU hardware by quantizing weights to FP16 precision, fusing layer operations, and selecting optimal GPU kernels. This reduces pipeline latency down to 4.1ms (243 FPS) on Jetson AGX Orin.

### Q7: Why can't TensorRT `.engine` files generated on Windows be transferred to Jetson?
**Answer**: TensorRT engine files contain compiled GPU assembly instructions tied directly to the host GPU compute architecture (e.g., SM 8.9 Ada Lovelace vs SM 8.7 Jetson Orin) and L4T Linux driver versions. Cross-compiling across OS/SM boundaries causes deserialization failures; engines must be compiled natively on target Jetson hardware via `trtexec`.

### Q8: How does Multi-frame Recognition & Fusion work?
**Answer**: The system uses DeepSORT tracking to maintain unique vehicle tracklet IDs across consecutive video frames. Instead of relying on a single frame scan, the multi-frame fusion engine pools OCR text predictions across 5+ frames, selects character consensus via confidence voting, and eliminates frame noise.

### Q9: How is OCR text validated and corrected?
**Answer**: License plate crops undergo homography perspective rectification and CLAHE contrast enhancement before EasyOCR reading. Extracted text is evaluated against Indian state plate regex formats (`State Code + 2 Digits + 2 Letters + 4 Digits`). Ambiguous characters undergo confusion matrix correction (`0`<->`O`, `1`<->`I`, `8`<->`B`, `5`<->`S`).

### Q10: How are duplicate scans removed?
**Answer**: A configurable deduplication window (default: 30 seconds) ignores repeated scans of the same vehicle plate at the same gate ID, preventing duplicate movement database entries.

---

## 3. Operations & Authorization FAQs

### Q11: How does the Authorization Engine work?
**Answer**: When a plate is scanned, the Authorization Engine checks rules in priority order:
1. **Watchlist Match**: If plate is listed on active Watchlist, immediately issue `DENY` and trigger security alert.
2. **Whitelist Match**: If plate is listed on active Whitelist, issue `ALLOW` and open barrier.
3. **Active Trip Match**: If vehicle has a valid `PLANNED` or `REGISTERED` trip ticket for the current gate, issue `ALLOW`. Otherwise issue `DENY`.

### Q12: How does Entry/Exit Trip Lifecycle matching work?
**Answer**: On entry gate passage, system transitions trip status from `PLANNED`/`REGISTERED` -> `IN_PLANT` and logs entry timestamp. On exit gate passage, system matches the active `IN_PLANT` trip, computes dwell time, transitions trip status -> `COMPLETED`, and logs exit timestamp.
