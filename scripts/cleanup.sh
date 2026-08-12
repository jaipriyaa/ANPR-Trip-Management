#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Cleanup Script (Bash)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo "  ANPR & TRIP MANAGEMENT PLATFORM - REPOSITORY CLEANUP"
echo "  Project Root: ${PROJECT_ROOT}"
echo "======================================================================"

cd "${PROJECT_ROOT}"

echo "[1/4] Removing Python bytecode cache (__pycache__, *.pyc, *.pyo)..."
find . -type d -name "__pycache__" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -delete 2>/dev/null || true
echo "✓ Python byte code cache cleaned."

echo "[2/4] Removing Pytest & Test Coverage caches (.pytest_cache, .coverage)..."
rm -rf .pytest_cache .coverage htmlcov coverage.xml backend/.pytest_cache 2>/dev/null || true
echo "✓ Pytest cache cleaned."

echo "[3/4] Cleaning Frontend build & log artifacts..."
rm -rf frontend/dist frontend/node_modules/.vite 2>/dev/null || true
rm -f frontend/vite_stderr.log frontend/vite_stdout.log 2>/dev/null || true
echo "✓ Frontend build cache & log files cleaned."

echo "[4/4] Removing OS & temporary debug files (.DS_Store, Thumbs.db)..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
echo "✓ OS temporary files cleaned."

echo -e "\n======================================================================"
echo "  ✓ REPOSITORY CLEANUP COMPLETE!"
echo "======================================================================"
