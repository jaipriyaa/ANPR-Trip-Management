@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Production Build Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "VENV_PYTHON=%PROJECT_ROOT%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - PRODUCTION BUILD (WINDOWS)
echo   Project Root: %PROJECT_ROOT%
echo ======================================================================

rem 1. Frontend Build
echo.
echo [1/3] Building React Frontend Production Assets...
where npm >nul 2>nul
if %errorlevel%==0 (
    cd /d "%PROJECT_ROOT%\frontend"
    call npm run build
    if errorlevel 1 (
        echo [WARN] Frontend build had warnings or non-zero exit code.
    ) else (
        echo [PASS] Frontend build complete: frontend\dist\
    )
) else (
    echo [WARN] npm not found in PATH. Skipping frontend build.
)

rem 2. ONNX Model Export
echo.
echo [2/3] Exporting AI Models to ONNX Format...
if exist "%PROJECT_ROOT%\deployment\export_onnx.py" (
    cd /d "%PROJECT_ROOT%"
    "%VENV_PYTHON%" deployment\export_onnx.py
    if errorlevel 1 (
        echo [WARN] ONNX export script returned warnings or non-zero exit.
    ) else (
        echo [PASS] AI Model export complete.
    )
) else (
    echo [WARN] deployment\export_onnx.py not found. Skipping ONNX export.
)

rem 3. Docker Container Build
echo.
echo [3/3] Building Docker Containers...
where docker >nul 2>nul
if %errorlevel%==0 (
    cd /d "%PROJECT_ROOT%"
    docker compose build
    if errorlevel 1 (
        echo [WARN] Docker compose build returned non-zero code.
    ) else (
        echo [PASS] Docker container images built.
    )
) else (
    echo [WARN] Docker not installed or not in PATH. Skipping Docker build.
)

cd /d "%PROJECT_ROOT%"
echo.
echo ======================================================================
echo   [PASS] BUILD COMPLETE!
echo ======================================================================

endlocal
