# Industrial Vehicle Trip Management System - Complete End User Manual

This manual provides operating instructions for all 28 views and functional modules of the React web interface.

---

## 1. Introduction

### Purpose
The Industrial Vehicle Trip Management System automates gate access control, vehicle trip scheduling, license plate recognition (ANPR), security authorization, and plant dwell-time tracking.

### Target Users
- **Gate Operators & Security Guards**: Monitor live gate feeds, inspect ANPR plate scans, and control boom barriers.
- **Logistics Dispatchers**: Schedule vehicle trips, assign drivers, and monitor plant dwell time.
- **Plant Security Managers**: Manage vehicle whitelists, watchlists, and review gate authorization logs.
- **System Administrators**: Manage transporters, vehicle master data, users, and performance telemetry.

### Industrial Use Cases
- Manufacturing plants, steel mills, mining quarries, freight terminals, and logistics parks.

### System Requirements
- Modern web browser (Google Chrome 110+, Microsoft Edge 110+, Mozilla Firefox 110+).

---

## 2. Getting Started

### 2.1 Login & Authentication
1. Open web browser to `http://localhost:3000` (or host IP).
2. Enter your assigned Username and Password.
3. Click **Sign In** to generate a secure JWT token and enter the dashboard.

### 2.2 Navigation Overview
- **Sidebar**: Access 5 operational groups (Master Data, Gate & Operations, Data Engineering Pipeline, Authorization & Security, Enterprise Admin).
- **Top Bar**: System status indicator, active gate selector, user profile, and theme controls.

---

## 3. Transporter Management (`/transporters`)
- **Purpose**: Manage logistics vendors and transport partners.
- **Create**: Click **Add Transporter**, fill Code, Name, Email, Phone, Address, click **Save**.
- **Update**: Click **Edit** icon next to any transporter record.
- **Search**: Type transporter name or code in top search filter.
- **Deactivate**: Toggle status switch to **Inactive** to suspend transporter.

---

## 4. Vehicle Management (`/vehicles`)
- **Purpose**: Register plant fleet vehicles, fuel types, and categories.
- **Create Vehicle**: Click **Register Vehicle**, enter Registration Plate (e.g., `KA01AB1234`), select Vehicle Type (Car, SUV, Heavy Truck, etc.), and assign Transporter.
- **Deactivate Vehicle**: Deactivate retired vehicles to prevent trip scheduling.

---

## 5. Vehicle Plate Management (`/vehicle-plates`)
- **Purpose**: Manage license plate classifications, state codes, and validation status.
- **Plate Types**: Standard White, Commercial Yellow, Special Permit.
- **Validation**: Indian plate regex matcher automatically validates state code format.

---

## 6. Driver Management (`/drivers`)
- **Purpose**: Register commercial truck drivers, license numbers, and safety training dates.
- **Create Driver**: Click **Add Driver**, enter Name, Commercial License Number, Mobile Phone, and assigned Transporter.

---

## 7. Gate Management & Camera Assignment (`/gates`)
- **Purpose**: Configure plant entry/exit gates, RTSP IP camera streams, and gate rules.
- **Create Gate**: Define Gate Name (e.g., `Gate 1 - North Inbound`), Direction (`ENTRY`, `EXIT`, `BIDIRECTIONAL`).
- **Assign Cameras**: Enter RTSP URL (`rtsp://192.168.1.100:554/stream1`) and associate with gate ID.

---

## 8. AI Recognition (`/vehicle-recognition`)
- **Image Recognition**: Drag and drop a vehicle test image to inspect vehicle detection bounding boxes, plate crops, and OCR extracted text.
- **Video Recognition**: Process video files to observe DeepSORT vehicle tracking IDs across frames.
- **Recognition History**: Search past ANPR recognition events by plate text, confidence score, or camera ID.

---

## 9. Trip Management (`/trips`)
- **Create Trip**: Click **Schedule Trip**, enter Trip Ticket Number, assign Vehicle and Driver, specify Material Type, Destination, and Expected Arrival.
- **Status Lifecycle**: `PLANNED` → `REGISTERED` → `IN_PLANT` → `COMPLETED` / `CANCELLED`.
- **Dwell Time Alert**: Automatic warning highlights vehicles exceeding max allowed plant duration.

---

## 10. Entry / Exit Engine (`/entry-exit`)
- **Vehicle Entry**: ANPR camera scans vehicle plate at entry gate. System validates active trip, registers entry timestamp, and opens barrier.
- **Vehicle Exit**: Exit camera scans plate, computes plant dwell time, marks trip `COMPLETED`, and raises exit barrier.
- **Vehicles Inside**: Live counter displaying total vehicles currently inside plant premises.

---

## 11. Authorization Engine (`/authorization-dashboard`, `/whitelist`, `/watchlist`, `/manual-review`)
- **Whitelist**: Register VIP, employee, or regular fleet vehicles for instant `ALLOW` decisions.
- **Watchlist**: Register blocked, stolen, or flagged vehicles for immediate security alert triggers.
- **Manual Review**: Low-confidence OCR scans (< 70% confidence) enter the queue for human operator review and correction.

---

## 12. Analytics, Reports & Performance (`/analytics`, `/reports`, `/performance-dashboard`)
- **Analytics Dashboard**: Visual charts for trip volume, peak hour traffic, dwell-time distribution, and gate activity.
- **Reports**: Generate and download PDF/Excel operational reports.
- **Performance Dashboard**: Real-time pipeline latency breakdown, FPS, CPU, RAM, and GPU gauges.

---

## 13. System Settings & Health (`/system-health`)
- Inspect active backend (`TensorRT`, `ONNX`, `PyTorch`), CUDA GPU status, database connection state, and uptime telemetry.

---

## 14. Troubleshooting & FAQ
- **Q: What if a license plate is damaged or unrecognized?**
  - A: The scan automatically lands in the **Manual Review Queue** (`/manual-review`) where operators can manually verify and submit correction.
