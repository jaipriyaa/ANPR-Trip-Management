# Industrial Vehicle Trip Management System - 8-10 Minute Presentation & Live Demonstration Plan

This document provides a step-by-step presentation script, screen actions, talking points, expected outputs, and demonstration tips for the **TFrenzy Final Evaluation Review**.

---

## ⏱️ Presentation Timing & Steps Overview (8 - 10 Minutes Total)

| Step # | Topic / Module | Time | Screen View | Talking Points & Expected Output |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Introduction** | 0:25 min | Slides / Cover | Introduce project goal: Sub-30ms ANPR, gate automation & trip management. |
| **2** | **Project Overview** | 0:25 min | Architecture Slide | Explain edge-native AI architecture and multi-backend acceleration. |
| **3** | **Login & Navigation** | 0:25 min | Login Screen -> Web UI | Demonstrate JWT authentication and 5 operational sidebar groups. |
| **4** | **Dashboard Overview** | 0:25 min | Analytics Dashboard | Show live KPI cards, gate movement charts, and dwell-time metrics. |
| **5** | **Transporter Management** | 0:25 min | `/transporters` | Show registered transporter "Apex Logistics Services" and CRUD controls. |
| **6** | **Vehicle Management** | 0:25 min | `/vehicles` | Show registered vehicle "KA01AB1234", vehicle category, and transporter binding. |
| **7** | **Driver Management** | 0:25 min | `/drivers` | Show commercial driver profile, license verification, and status controls. |
| **8** | **Vehicle Recognition** | 0:30 min | `/vehicle-recognition` | Upload image: Show bounding box, plate crop, and extracted text. |
| **9** | **Plate Detection** | 0:25 min | `/vehicle-recognition` | Explain YOLOv11 plate localization across commercial & standard plates. |
| **10** | **OCR Recognition** | 0:30 min | `/vehicle-recognition` | Highlight multi-pass EasyOCR, CLAHE homography, and regex correction. |
| **11** | **Multi-Frame Fusion** | 0:30 min | `/vehicle-recognition` | Show DeepSORT vehicle tracking IDs maintaining tracklet persistence. |
| **12** | **Trip Creation** | 0:30 min | `/trips` | Schedule new trip ticket (`PLANNED` -> `REGISTERED` -> `IN_PLANT`). |
| **13** | **Entry / Exit Engine** | 0:30 min | `/entry-exit` | Demonstrate entry scan, dwell-time tracking, and exit trip completion. |
| **14** | **Authorization Engine** | 0:30 min | `/authorization-dashboard` | Show `ALLOW` for Whitelist and security alert trigger for Watchlist scan. |
| **15** | **Manual Review** | 0:30 min | `/manual-review` | Demonstrate low-confidence OCR queue, operator correction, and dataset save. |
| **16** | **Reports & Analytics** | 0:25 min | `/reports` | Export PDF/Excel trip reports and operational summaries. |
| **17** | **Performance Dashboard** | 0:30 min | `/performance-dashboard` | Show live FPS, latency breakdown, hardware gauges, and backend matrix. |
| **18** | **Docker Deployment** | 0:30 min | Terminal / Docker | Demonstrate single-command launch (`docker compose up --build`). |
| **19** | **Jetson Deployment** | 0:25 min | Jetson Runbook | Explain native TensorRT FP16 compilation delivering 4.1ms latency (243 FPS). |
| **20** | **Questions & Conclusion**| 0:30 min | Final Slide / Q&A | Summarize key achievements and open the floor for evaluator questions. |

---

## 💡 Live Demonstration Tips

1. **Pre-flight Check**: Run `python deployment/system_check.py` before starting to ensure all services are healthy.
2. **Sample Preparation**: Have sample test images (`Car`, `SUV`, `Heavy Truck`, `Damaged Plate`) saved on Desktop for instant drag-and-drop.
3. **Smooth Transitions**: Keep browser tabs open to `/live-gate`, `/vehicle-recognition`, `/trips`, `/performance-dashboard`, and `/authorization-dashboard`.
