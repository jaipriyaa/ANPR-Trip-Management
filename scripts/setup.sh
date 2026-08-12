#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Environment Setup Script (Bash)
# ==============================================================================
set -e

# Detect project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo "  ANPR & TRIP MANAGEMENT PLATFORM - SYSTEM SETUP"
echo "  Project Root: ${PROJECT_ROOT}"
echo "======================================================================"

# 1. Environment file setup
echo -e "\n[1/5] Checking Environment Configuration (.env)..."
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    if [ -f "${PROJECT_ROOT}/.env.example" ]; then
        cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
        echo "✓ Created .env file from .env.example"
    else
        echo "⚠ Warning: .env.example not found!"
    fi
else
    echo "✓ .env file already exists."
fi

# 2. Python Virtual Environment Setup
echo -e "\n[2/5] Setting up Python Virtual Environment..."
VENV_DIR="${PROJECT_ROOT}/backend/venv"

if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment at ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}" || python -m venv "${VENV_DIR}"
    echo "✓ Virtual environment created."
else
    echo "✓ Virtual environment already exists at ${VENV_DIR}"
fi

# Determine python and pip paths inside venv
if [ -f "${VENV_DIR}/bin/python" ]; then
    VENV_PYTHON="${VENV_DIR}/bin/python"
    VENV_PIP="${VENV_DIR}/bin/pip"
elif [ -f "${VENV_DIR}/Scripts/python.exe" ]; then
    VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"
    VENV_PIP="${VENV_DIR}/Scripts/pip.exe"
else
    VENV_PYTHON="python3"
    VENV_PIP="pip3"
fi

echo -e "\n[3/5] Installing Backend Python Dependencies..."
"${VENV_PIP}" install --upgrade pip setuptools wheel
"${VENV_PIP}" install -r "${PROJECT_ROOT}/backend/requirements.txt"
echo "✓ Backend Python dependencies installed successfully."

# 3. Database Initialization
echo -e "\n[4/5] Running Database Migrations & Initializing Schema..."
cd "${PROJECT_ROOT}/backend"
"${VENV_PYTHON}" run_migrations.py || {
    echo "⚠ Database migration step completed with warnings (verify DB server status if using PostgreSQL)."
}

# 4. Frontend Package Setup
echo -e "\n[5/5] Installing Frontend Node.js Dependencies..."
if command -v npm &> /dev/null; then
    cd "${PROJECT_ROOT}/frontend"
    npm install
    echo "✓ Frontend Node.js dependencies installed successfully."
else
    echo "⚠ Warning: npm is not installed or not in PATH. Skipping frontend npm install."
fi

echo -e "\n======================================================================"
echo "  ✓ SETUP COMPLETE SUCCESSFUL!"
echo "======================================================================"
echo "Next steps:"
echo "  - Start Local Services: bash scripts/start.sh"
echo "  - Run Test Suite:       bash scripts/test.sh"
echo "  - Run Benchmarks:       bash scripts/benchmark.sh"
echo "  - Launch via Docker:    bash scripts/docker_run.sh up"
echo "======================================================================"
