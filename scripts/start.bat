@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Service Startup Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

set "MODE=%~1"
if "%MODE%"=="" set "MODE=all"

set "VENV_PYTHON=%PROJECT_ROOT%\backend\venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" set "VENV_PYTHON=python"

if /i "%MODE%"=="backend" goto :start_backend
if /i "%MODE%"=="--backend" goto :start_backend
if /i "%MODE%"=="-b" goto :start_backend

if /i "%MODE%"=="frontend" goto :start_frontend
if /i "%MODE%"=="--frontend" goto :start_frontend
if /i "%MODE%"=="-f" goto :start_frontend

if /i "%MODE%"=="docker" goto :start_docker
if /i "%MODE%"=="--docker" goto :start_docker
if /i "%MODE%"=="-d" goto :start_docker

if /i "%MODE%"=="all" goto :start_all
if /i "%MODE%"=="--all" goto :start_all

:start_all
echo ======================================================================
echo   LAUNCHING ALL SERVICES (FastAPI Backend + React Frontend)
echo ======================================================================
echo Starting FastAPI Backend server in separate Command Window...
start "ANPR Backend Service (Port 8000)" cmd /k "cd /d "%PROJECT_ROOT%\backend" && "%VENV_PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting React Frontend Dev Server in current window...
cd /d "%PROJECT_ROOT%\frontend"
call npm run dev
goto :end

:start_backend
echo ======================================================================
echo   STARTING BACKEND API SERVICE (FastAPI)
echo ======================================================================
cd /d "%PROJECT_ROOT%\backend"
"%VENV_PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
goto :end

:start_frontend
echo ======================================================================
echo   STARTING FRONTEND DASHBOARD SERVICE (React / Vite)
echo ======================================================================
cd /d "%PROJECT_ROOT%\frontend"
call npm run dev
goto :end

:start_docker
echo ======================================================================
echo   STARTING DOCKER CONTAINER STACK
echo ======================================================================
cd /d "%PROJECT_ROOT%"
docker compose up --build
goto :end

:end
endlocal
