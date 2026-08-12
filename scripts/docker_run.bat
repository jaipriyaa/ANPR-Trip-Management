@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Docker Stack Manager (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "ACTION=%~1"
if "%ACTION%"=="" set "ACTION=up"

cd /d "%PROJECT_ROOT%"

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - DOCKER ORCHESTRATION (WINDOWS)
echo   Action: %ACTION%
echo ======================================================================

where docker >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH! Please install Docker Desktop.
    exit /b 1
)

if /i "%ACTION%"=="up" (
    docker compose up --build
    goto :end
)

if /i "%ACTION%"=="daemon" (
    docker compose up --build -d
    echo [PASS] Stack launched in background. View logs with: scripts\docker_run.bat logs
    goto :end
)

if /i "%ACTION%"=="down" (
    docker compose down
    echo [PASS] Docker containers stopped.
    goto :end
)

if /i "%ACTION%"=="build" (
    docker compose build
    echo [PASS] Docker images built.
    goto :end
)

if /i "%ACTION%"=="logs" (
    docker compose logs -f
    goto :end
)

if /i "%ACTION%"=="ps" (
    docker compose ps
    goto :end
)

if /i "%ACTION%"=="status" (
    docker compose ps
    goto :end
)

if /i "%ACTION%"=="restart" (
    docker compose restart
    goto :end
)

echo Usage: scripts\docker_run.bat [up^|daemon^|down^|build^|logs^|status^|restart]

:end
endlocal
