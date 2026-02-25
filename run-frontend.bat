@echo off
REM Phase V - Run Frontend Locally (Windows)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Frontend (Modern UI)                      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js is installed
echo.

REM Navigate to frontend directory
if exist frontend (
    cd frontend
) else (
    echo [ERROR] frontend directory not found
    pause
    exit /b 1
)

REM Install dependencies
echo Installing npm dependencies (this may take a few minutes)...
call npm install
echo.

echo Starting Frontend Development Server...
echo.
echo ════════════════════════════════════════════════════════
echo   Frontend will run at: http://localhost:3000
echo   Hot reload is enabled
echo ════════════════════════════════════════════════════════
echo.

REM Start the dev server
call npm run dev

pause
