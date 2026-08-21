# Installation Guide

This guide provides instructions for installing and running the **Industrial Vehicle Trip Management System** across different environments, including local development setups and containerized Docker deployments.

---

## System Requirements

### Hardware Requirements
- **CPU**: x86_64 or ARM64 (quad-core minimum, 8+ cores recommended)
- **RAM**: Minimum 8 GB (16 GB recommended)
- **GPU** *(Optional for acceleration)*: NVIDIA GPU with CUDA 11.8+ / 12.2+ or NVIDIA Jetson Edge Device (Xavier / Orin)
- **Disk Space**: 10 GB free storage

### Software Prerequisites
- **Python**: 3.11.x (or 3.8 - 3.11)
- **Node.js**: 18.x or 20.x LTS & `npm`
- **Docker & Docker Compose**: *(Optional, for containerized execution)*
- **Git**: 2.30+

---

## 1. Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/jaipriyaa/ANPR-Trip-Management.git
cd ANPR-Trip-Management
```

### Step 2: Backend Setup (FastAPI & AI Engine)

1. Navigate to the backend directory or work from root:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. Install required Python packages:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. Initialize database schema & run migrations:
   ```bash
   python run_migrations.py
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *The API will be available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### Step 3: Frontend Setup (React & Vite)

1. In a separate terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install JavaScript dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The Web Interface will be available at `http://localhost:5173`.*

---

## 2. Docker Containerized Setup (Recommended for Production)

The repository provides production-ready Docker Compose configurations supporting both CPU and GPU execution.

### Single-Command Start
Run the cross-platform start script from the root directory:
```bash
bash start.sh
```
Or directly using Docker Compose:

### Production Deployment
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Standard Deployment
```bash
docker compose up --build -d
```

To view running containers and logs:
```bash
docker compose ps
docker compose logs -f backend
```

---

## 3. Environment Configuration (`.env`)

Copy `.env.example` to `.env` in the root directory and configure options as required:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=sqlite:///./sql_app.db
# PostgreSQL Example: postgresql://user:password@localhost:5432/anpr_db

# Hardware & AI Acceleration Configuration
MODEL_BACKEND=AUTO          # Options: AUTO, PYTORCH, ONNX, TENSORRT
GPU_ENABLED=true
GPU_DEVICE=0
TENSORRT_ENGINE_PATH=models/

# Application Features
MAX_UPLOAD_SIZE_MB=50
ALERT_WEBHOOK_URL=
```

---

## 4. Verification

After installation, verify that the application components are running properly:

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/api/system/health
   ```
2. **PyTest Verification Suite**:
   ```bash
   pytest tests/
   ```
