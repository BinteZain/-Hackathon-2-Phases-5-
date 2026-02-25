@echo off
REM Phase V - Quick Start (Simple Local Run)
REM This runs the application WITHOUT Kubernetes for quick testing

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Quick Start (Local Mode)                  ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo This will run the application WITHOUT Kafka/Dapr
echo For full setup, run: setup-local.bat
echo.
pause

echo.
echo [1/3] Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm run dev"
echo [OK] Frontend starting at http://localhost:3000
echo.

echo [2/3] Starting Backend...
start "Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo [OK] Backend starting at http://localhost:8000
echo.

echo [3/3] Opening Application in Browser...
timeout /t 5 /nobreak >nul
start http://localhost:3000
echo.

echo ════════════════════════════════════════════════════════
echo   Application is running!
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ════════════════════════════════════════════════════════
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WindowTitle eq Frontend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Backend*" /T /F >nul 2>&1

echo All services stopped.
pause
