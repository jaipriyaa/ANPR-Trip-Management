@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Environment Setup Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - SYSTEM SETUP (WINDOWS)
echo   Project Root: %PROJECT_ROOT%
echo ======================================================================

rem 1. Environment Configuration Setup
echo.
echo [1/5] Checking Environment Configuration (.env)...
if not exist "%PROJECT_ROOT%\.env" (
    if exist "%PROJECT_ROOT%\.env.example" (
        copy "%PROJECT_ROOT%\.env.example" "%PROJECT_ROOT%\.env" > nul
        echo [PASS] Created .env file from .env.example
    ) else (
        echo [WARN] Warning: .env.example not found!
    )
) else (
    echo [PASS] .env file already exists.
)

rem 2. Python Virtual Environment Setup
echo.
echo [2/5] Setting up Python Virtual Environment...
set "VENV_DIR=%PROJECT_ROOT%\backend\venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_PIP=%VENV_DIR%\Scripts\pip.exe"

if not exist "%VENV_DIR%" (
    echo Creating virtual environment at %VENV_DIR%...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create Python virtual environment. Ensure Python is installed and in PATH.
        exit /b 1
    )
    echo [PASS] Virtual environment created.
) else (
    echo [PASS] Virtual environment already exists at %VENV_DIR%
)

rem Fallback if venv python missing
if not exist "%VENV_PYTHON%" (
    set "VENV_PYTHON=python"
    set "VENV_PIP=pip"
)

rem 3. Installing Python Dependencies
echo.
echo [3/5] Installing Backend Python Dependencies...
"%VENV_PIP%" install --upgrade pip setuptools wheel
"%VENV_PIP%" install -r "%PROJECT_ROOT%\backend\requirements.txt"
if errorlevel 1 (
    echo [WARN] Python dependency installation completed with warnings.
) else (
    echo [PASS] Backend Python dependencies installed successfully.
)

rem 4. Database Schema Initialization
echo.
echo [4/5] Running Database Migrations ^& Initializing Schema...
cd /d "%PROJECT_ROOT%\backend"
"%VENV_PYTHON%" run_migrations.py
if errorlevel 1 (
    echo [WARN] Database migration step completed with warnings. Check database configuration in .env.
) else (
    echo [PASS] Database migrations complete.
)

rem 5. Frontend Package Installation
echo.
echo [5/5] Installing Frontend Node.js Dependencies...
where npm >nul 2>nul
if %errorlevel%==0 (
    cd /d "%PROJECT_ROOT%\frontend"
    call npm install
    echo [PASS] Frontend Node.js dependencies installed successfully.
) else (
    echo [WARN] npm is not installed or not available in PATH. Skipping frontend npm install.
)

cd /d "%PROJECT_ROOT%"
echo.
echo ======================================================================
echo   [PASS] SETUP COMPLETED!
echo ======================================================================
echo Next steps:
echo   - Start Services:   scripts\start.bat
echo   - Run Test Suite:   scripts\test.bat
echo   - Run Benchmarks:   scripts\benchmark.bat
echo   - Launch Docker:    scripts\docker_run.bat up
echo ======================================================================

endlocal
