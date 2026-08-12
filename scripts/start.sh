#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Service Startup Script (Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODE="${1:-all}"

VENV_PYTHON="${PROJECT_ROOT}/backend/venv/bin/python"
if [ ! -f "${VENV_PYTHON}" ]; then
    if [ -f "${PROJECT_ROOT}/backend/venv/Scripts/python.exe" ]; then
        VENV_PYTHON="${PROJECT_ROOT}/backend/venv/Scripts/python.exe"
    else
        VENV_PYTHON="python3"
    fi
fi

start_backend() {
    echo -e "\n[Backend] Starting FastAPI Server on http://0.0.0.0:8000..."
    cd "${PROJECT_ROOT}/backend"
    "${VENV_PYTHON}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

start_frontend() {
    echo -e "\n[Frontend] Starting React/Vite Dev Server on http://localhost:3000..."
    cd "${PROJECT_ROOT}/frontend"
    npm run dev
}

start_docker() {
    echo -e "\n[Docker] Launching Full Container Stack via Docker Compose..."
    cd "${PROJECT_ROOT}"
    docker compose up --build
}

case "${MODE}" in
    backend|--backend|-b)
        start_backend
        ;;
    frontend|--frontend|-f)
        start_frontend
        ;;
    docker|--docker|-d)
        start_docker
        ;;
    all|--all|*)
        echo "======================================================================"
        echo "  LAUNCHING ALL SERVICES (FastAPI Backend + React Frontend)"
        echo "======================================================================"
        echo "Starting Backend API server in background..."
        cd "${PROJECT_ROOT}/backend"
        "${VENV_PYTHON}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        echo "✓ Backend server launched (PID: ${BACKEND_PID}). API: http://localhost:8000/docs"

        trap 'echo -e "\nStopping processes..."; kill ${BACKEND_PID} 2>/dev/null || true; exit 0' INT TERM EXIT

        echo "Starting Frontend Development server..."
        cd "${PROJECT_ROOT}/frontend"
        npm run dev
        ;;
esac
