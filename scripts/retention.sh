#!/usr/bin/env bash
# ==============================================================================
# Edge ANPR & Vehicle Trip Management Platform - Data Retention & Archival Script (Bash)
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

MODE="${1:---dry-run}"
DRY_RUN="True"

if [ "${MODE}" == "--active" ] || [ "${MODE}" == "active" ] || [ "${MODE}" == "--force" ]; then
    DRY_RUN="False"
    echo "======================================================================"
    echo "  RUNNING ACTIVE DATA RETENTION & ARCHIVAL CLEANUP (RECORDS WILL BE ARCHIVED/DELETED)"
    echo "======================================================================"
else
    echo "======================================================================"
    echo "  RUNNING DATA RETENTION CLEANUP IN DRY-RUN MODE (NO RECORDS DELETED)"
    echo "======================================================================"
fi

cd "${PROJECT_ROOT}/backend"
"${VENV_PYTHON}" -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from app.database.connection import SessionLocal
from app.services.retention_service import retention_service

db = SessionLocal()
try:
    res = retention_service.run_retention_job(db, dry_run=${DRY_RUN})
    print('Retention Job Result:', res)
finally:
    db.close()
"

echo -e "\n======================================================================"
echo "  ✓ RETENTION JOB EXECUTED SUCCESSFULLY!"
echo "======================================================================"
