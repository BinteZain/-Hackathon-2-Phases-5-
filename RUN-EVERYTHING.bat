@echo off
REM Phase V - Complete Setup and Run Script
REM Yeh script sab kuch automatically karegi

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Complete Setup & Run                      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Running in normal mode...
)

echo [Step 1/4] Checking prerequisites...
echo.

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker Desktop is not running
    echo Please start Docker Desktop first
    echo.
    pause
) else (
    echo [OK] Docker is running
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo [OK] Node.js is installed
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    echo Please install Python from: https://python.org/
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
)

echo.
echo [Step 2/4] Opening Dashboard...
echo.

REM Open dashboard
start "" "START_HERE.html"
echo [OK] Dashboard opened in browser

echo.
echo [Step 3/4] Starting Services...
echo.

REM Start backend in new window
echo Starting Backend...
start "Backend (Port 8000)" cmd /k "cd backend && echo Starting backend server... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo [OK] Backend starting on http://localhost:8000

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend...
start "Frontend (Port 3000)" cmd /k "cd frontend && echo Starting frontend dev server... && npm run dev"
echo [OK] Frontend starting on http://localhost:3000

echo.
echo [Step 4/4] Waiting for services to start...
echo.

REM Wait for services
timeout /t 10 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════
echo   ✅ Application is now running!
echo ════════════════════════════════════════════════════════
echo.
echo   📱 Frontend:  http://localhost:3000
echo   ⚡ Backend:   http://localhost:8000
echo   📖 API Docs:  http://localhost:8000/docs
echo.
echo   The dashboard should be open in your browser.
echo   If not, open: START_HERE.html
echo.
echo ════════════════════════════════════════════════════════
echo.
echo   To stop all services:
echo   - Close the Backend and Frontend windows
echo   - Or press Ctrl+C in each window
echo.

REM Open frontend in browser after waiting
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo Press any key to exit this window...
pause >nul
