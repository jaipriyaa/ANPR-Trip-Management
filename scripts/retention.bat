@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Data Retention Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "VENV_PYTHON=%PROJECT_ROOT%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

set "MODE=%~1"
set "DRY_RUN=True"

if /i "%MODE%"=="--active" set "DRY_RUN=False"
if /i "%MODE%"=="active" set "DRY_RUN=False"
if /i "%MODE%"=="--force" set "DRY_RUN=False"

if "%DRY_RUN%"=="False" (
    echo ======================================================================
    echo   RUNNING ACTIVE DATA RETENTION ^& ARCHIVAL (RECORDS DELETED/ARCHIVED)
    echo ======================================================================
) else (
    echo ======================================================================
    echo   RUNNING DATA RETENTION IN DRY-RUN MODE (NO DELETIONS)
    echo ======================================================================
)

cd /d "%PROJECT_ROOT%\backend"
"%VENV_PYTHON%" -c "import sys; sys.path.insert(0, '.'); from app.database.connection import SessionLocal; from app.services.retention_service import retention_service; db = SessionLocal(); res = retention_service.run_retention_job(db, dry_run=%DRY_RUN%); print('Retention Job Result:', res); db.close()"

if errorlevel 1 (
    echo [WARN] Retention job exited with warnings or errors. Check database availability.
) else (
    echo.
    echo ======================================================================
    echo   [PASS] RETENTION JOB EXECUTED SUCCESSFULLY!
    echo ======================================================================
)

endlocal
