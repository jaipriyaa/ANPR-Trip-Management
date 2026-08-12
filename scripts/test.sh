#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Automated Test Suite Runner (Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

VENV_PYTHON="${PROJECT_ROOT}/backend/venv/bin/python"
if [ ! -f "${VENV_PYTHON}" ]; then
    if [ -f "${PROJECT_ROOT}/backend/venv/Scripts/python.exe" ]; then
        VENV_PYTHON="${PROJECT_ROOT}/backend/venv/Scripts/python.exe"
    else
        VENV_PYTHON="python3"
    fi
fi

echo "======================================================================"
echo "  ANPR & TRIP MANAGEMENT PLATFORM - AUTOMATED REGRESSION TEST SUITE"
echo "  Project Root: ${PROJECT_ROOT}"
echo "======================================================================"

cd "${PROJECT_ROOT}"

if [ "$#" -gt 0 ]; then
    echo "Running pytest with custom arguments: $@"
    "${VENV_PYTHON}" -m pytest "$@"
else
    echo "Running full test suite across all target modules (tests/)..."
    "${VENV_PYTHON}" -m pytest tests/
fi

echo -e "\n======================================================================"
echo "  ✓ TEST SUITE EXECUTION COMPLETE!"
echo "======================================================================"
