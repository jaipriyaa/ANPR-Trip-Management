@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Automated Test Suite Runner (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "VENV_PYTHON=%PROJECT_ROOT%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - REGRESSION TEST SUITE (WINDOWS)
echo   Project Root: %PROJECT_ROOT%
echo ======================================================================

cd /d "%PROJECT_ROOT%"

if not "%~1"=="" (
    echo Running pytest with specified targets / arguments: %*
    "%VENV_PYTHON%" -m pytest %*
) else (
    echo Running full regression test suite across all target modules (tests\)...
    "%VENV_PYTHON%" -m pytest tests/
)

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo   [FAIL] ONE OR MORE TESTS FAILED!
    echo ======================================================================
    exit /b 1
) else (
    echo.
    echo ======================================================================
    echo   [PASS] ALL TESTS PASSED SUCCESSFULLY!
    echo ======================================================================
)

endlocal
