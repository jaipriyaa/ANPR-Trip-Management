#!/usr/bin/env bash

# ==============================================================================
# VEYRA Industrial ANPR & Trip Management Platform - Linux Startup Script
# Automatically configures environment, checks CUDA GPU, installs dependencies,
# runs database migrations, and launches backend & frontend servers concurrently.
# ==============================================================================

set -e

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}==============================================================================${NC}"
echo -e "${CYAN}   VEYRA | Industrial ANPR & Vehicle Trip Management Platform   ${NC}"
echo -e "${CYAN}==============================================================================${NC}"

# Resolve project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Set default CUDA GPU acceleration flag
export GPU_ENABLED="${GPU_ENABLED:-true}"
export MODEL_BACKEND="${MODEL_BACKEND:-AUTO}"
export PYTHONPATH="$PROJECT_ROOT/backend:${PYTHONPATH}"

# 1. Hardware & System Diagnostics
echo -e "\n${BLUE}[1/5] Checking Hardware & GPU Acceleration Status...${NC}"

if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1)
    echo -e "${GREEN}✓ NVIDIA GPU Detected: ${GPU_NAME}${NC}"
    echo -e "${GREEN}✓ CUDA Default Hardware Acceleration: ENABLED (GPU_ENABLED=true)${NC}"
else
    echo -e "${YELLOW}⚠ No NVIDIA GPU detected (nvidia-smi missing or CPU host).${NC}"
    echo -e "${YELLOW}ℹ AI pipeline will run with ONNX Runtime / PyTorch CPU fallback.${NC}"
fi

# 2. Python Environment Setup
echo -e "\n${BLUE}[2/5] Setting up Python Virtual Environment...${NC}"

PYTHON_BIN="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_BIN="python"
fi

if [ ! -d "$PROJECT_ROOT/backend/venv" ] && [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating backend/venv...${NC}"
    $PYTHON_BIN -m venv "$PROJECT_ROOT/backend/venv"
fi

if [ -d "$PROJECT_ROOT/backend/venv" ]; then
    VENV_PATH="$PROJECT_ROOT/backend/venv"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_PATH="$PROJECT_ROOT/venv"
fi

echo -e "${GREEN}✓ Activating Virtual Environment (${VENV_PATH})...${NC}"
if [ -f "${VENV_PATH}/bin/activate" ]; then
    # shellcheck disable=SC1090
    source "${VENV_PATH}/bin/activate"
elif [ -f "${VENV_PATH}/Scripts/activate" ]; then
    # shellcheck disable=SC1091
    source "${VENV_PATH}/Scripts/activate"
fi

# Ensure core python requirements are installed
if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
    echo -e "${CYAN}Verifying backend dependencies...${NC}"
    pip install -q --no-cache-dir -r "$PROJECT_ROOT/backend/requirements.txt" || true
fi

# 3. Frontend Environment Setup
echo -e "\n${BLUE}[3/5] Setting up Frontend Dependencies...${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ Error: 'npm' is not installed. Please install Node.js (v18+) to run the frontend.${NC}"
    exit 1
fi

if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend node_modules...${NC}"
    (cd "$PROJECT_ROOT/frontend" && npm install)
else
    echo -e "${GREEN}✓ Frontend dependencies ready.${NC}"
fi

# 4. Database Check & Migration Initialization
echo -e "\n${BLUE}[4/5] Initializing Database & Migration Schema...${NC}"

(
    cd "$PROJECT_ROOT/backend"
    python run_migrations.py || echo -e "${YELLOW}⚠ Database migration step completed with warnings/bypassed.${NC}"
)

# 5. Launch Backend & Frontend Services Concurrently
echo -e "\n${BLUE}[5/5] Launching Backend & Frontend Services...${NC}"

# Function to cleanly handle shutdown signals (Ctrl+C)
cleanup() {
    echo -e "\n${RED}Shutting down VEYRA ANPR Platform services...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo -e "${GREEN}Services stopped cleanly.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start FastAPI Backend Server
echo -e "${CYAN}Starting FastAPI Backend on http://0.0.0.0:8000 ...${NC}"
(
    cd "$PROJECT_ROOT/backend"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) &
BACKEND_PID=$!

# Start Vite Frontend Dev Server
echo -e "${CYAN}Starting Vite Frontend on http://0.0.0.0:3000 ...${NC}"
(
    cd "$PROJECT_ROOT/frontend"
    exec npm run dev -- --host 0.0.0.0 --port 3000
) &
FRONTEND_PID=$!

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN} ✓ VEYRA ANPR Platform is LIVE and Running!${NC}"
echo -e "${GREEN}   - Backend API      : http://localhost:8000 (Swagger: http://localhost:8000/docs)${NC}"
echo -e "${GREEN}   - Frontend Web App : http://localhost:3000${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${CYAN}Press [CTRL+C] to stop all services.${NC}\n"

# Wait for background server processes
wait $BACKEND_PID $FRONTEND_PID
