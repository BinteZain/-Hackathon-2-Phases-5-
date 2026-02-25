@echo off
REM Phase V - Run Backend Locally (Windows)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Backend Server                            ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Navigate to backend directory
if exist backend (
    cd backend
) else (
    echo [ERROR] backend directory not found
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt -q
echo.

REM Set environment variables
set DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/todo_chatbot
set REDIS_URL=redis://localhost:6379
set LOG_LEVEL=INFO

echo Starting Backend Server...
echo.
echo ════════════════════════════════════════════════════════
echo   Backend will run at: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ════════════════════════════════════════════════════════
echo.

REM Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
