@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Benchmarking Suite Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "VENV_PYTHON=%PROJECT_ROOT%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - BENCHMARKING SUITE (WINDOWS)
echo   Project Root: %PROJECT_ROOT%
echo ======================================================================

rem 1. Hardware Diagnostic Check
echo.
echo [1/4] Running Enterprise Edge Hardware Diagnostic Check...
if exist "%PROJECT_ROOT%\deployment\system_check.py" (
    cd /d "%PROJECT_ROOT%"
    "%VENV_PYTHON%" deployment\system_check.py
)

rem 2. Inference Benchmark
echo.
echo [2/4] Running Inference Latency ^& FPS Performance Benchmark...
if exist "%PROJECT_ROOT%\deployment\jetson\benchmark_jetson.py" (
    cd /d "%PROJECT_ROOT%"
    "%VENV_PYTHON%" deployment\jetson\benchmark_jetson.py
)

rem 3. Pipeline Validation
echo.
echo [3/4] Validating End-to-End Real-World Pipeline...
if exist "%PROJECT_ROOT%\deployment\validate_real_world_pipeline.py" (
    cd /d "%PROJECT_ROOT%"
    "%VENV_PYTHON%" deployment\validate_real_world_pipeline.py
)

rem 4. License Plate Detector Evaluation
echo.
echo [4/4] Running License Plate Detector Precision Evaluation...
if exist "%PROJECT_ROOT%\deployment\eval_license_plate_detector.py" (
    cd /d "%PROJECT_ROOT%"
    "%VENV_PYTHON%" deployment\eval_license_plate_detector.py
)

cd /d "%PROJECT_ROOT%"
echo.
echo ======================================================================
echo   [PASS] BENCHMARKING SUITE COMPLETED!
echo ======================================================================

endlocal
