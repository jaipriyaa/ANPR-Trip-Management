@echo off
rem ==============================================================================
rem Edge ANPR & Vehicle Trip Management Platform - Cleanup Script (Batch)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo ======================================================================
echo   ANPR ^& TRIP MANAGEMENT PLATFORM - REPOSITORY CLEANUP (WINDOWS)
echo   Project Root: %PROJECT_ROOT%
echo ======================================================================

cd /d "%PROJECT_ROOT%"

echo.
echo [1/4] Removing Python Bytecode Cache (__pycache__, *.pyc)...
for /d /r "%PROJECT_ROOT%" %%d in (__pycache__) do (
    echo %%d | findstr /i /c:"\venv\" /c:"\.venv\" /c:"\node_modules\" >nul
    if errorlevel 1 (
        if exist "%%d" rd /s /q "%%d" 2>nul
    )
)
for /r "%PROJECT_ROOT%" %%f in (*.pyc *.pyo) do (
    echo %%f | findstr /i /c:"\venv\" /c:"\.venv\" /c:"\node_modules\" >nul
    if errorlevel 1 (
        if exist "%%f" del /f /q "%%f" 2>nul
    )
)
echo [PASS] Python bytecode cache cleaned.

echo.
echo [2/4] Removing Pytest ^& Coverage Caches (.pytest_cache, .coverage)...
if exist "%PROJECT_ROOT%\.pytest_cache" rd /s /q "%PROJECT_ROOT%\.pytest_cache"
if exist "%PROJECT_ROOT%\backend\.pytest_cache" rd /s /q "%PROJECT_ROOT%\backend\.pytest_cache"
if exist "%PROJECT_ROOT%\.coverage" del /f /q "%PROJECT_ROOT%\.coverage"
if exist "%PROJECT_ROOT%\htmlcov" rd /s /q "%PROJECT_ROOT%\htmlcov"
if exist "%PROJECT_ROOT%\coverage.xml" del /f /q "%PROJECT_ROOT%\coverage.xml"
echo [PASS] Test caches cleaned.

echo.
echo [3/4] Cleaning Frontend Build ^& Log Files...
if exist "%PROJECT_ROOT%\frontend\dist" rd /s /q "%PROJECT_ROOT%\frontend\dist"
if exist "%PROJECT_ROOT%\frontend\node_modules\.vite" rd /s /q "%PROJECT_ROOT%\frontend\node_modules\.vite"
if exist "%PROJECT_ROOT%\frontend\vite_stderr.log" del /f /q "%PROJECT_ROOT%\frontend\vite_stderr.log"
if exist "%PROJECT_ROOT%\frontend\vite_stdout.log" del /f /q "%PROJECT_ROOT%\frontend\vite_stdout.log"
echo [PASS] Frontend build ^& log files cleaned.

echo.
echo [4/4] Cleaning OS Temporary Files (Thumbs.db, .DS_Store)...
del /s /q /f Thumbs.db .DS_Store 2>nul
echo [PASS] OS temporary files cleaned.

echo.
echo ======================================================================
echo   [PASS] REPOSITORY CLEANUP COMPLETED!
echo ======================================================================

endlocal
