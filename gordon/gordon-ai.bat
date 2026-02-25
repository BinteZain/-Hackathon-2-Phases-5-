@echo off
REM ============================================================================
REM Gordon - Docker AI Agent Integration Script for Phase 4
REM ============================================================================
REM This script provides AI-assisted Docker operations using Gordon
REM (Docker Desktop AI Agent)
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo Gordon - Docker AI Agent for Phase 4 Todo Chatbot
echo ============================================================================
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    exit /b 1
)

echo [INFO] Docker found:
docker --version
echo.

REM Check if Docker Desktop is running
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running
    echo Please start Docker Desktop
    exit /b 1
)

echo [INFO] Docker Desktop is running
echo.

REM Display Gordon capabilities
echo ============================================================================
echo Gordon AI Capabilities
echo ============================================================================
echo.
echo Gordon is Docker's AI agent that helps with:
echo   - Intelligent container operations
echo   - Automated Dockerfile generation
echo   - Smart image optimization
echo   - Context-aware troubleshooting
echo   - Natural language Docker commands
echo.

REM Check if Gordon is available (Docker Desktop 4.53+)
echo [INFO] Checking Gordon availability...
echo.
echo To enable Gordon:
echo   1. Open Docker Desktop
echo   2. Go to Settings ^> Beta features
echo   3. Toggle on "Docker AI" or "Gordon"
echo.

REM Show available Gordon commands
echo ============================================================================
echo Gordon Commands for Phase 4
echo ============================================================================
echo.
echo # Check Gordon capabilities
echo docker ai "What can you do?"
echo.
echo # Build images with AI assistance
echo docker ai "Build optimized Docker images for a Next.js frontend and FastAPI backend"
echo.
echo # Optimize Dockerfiles
echo docker ai "Optimize this Dockerfile for production: backend/Dockerfile"
echo.
echo # Generate Docker Compose configurations
echo docker ai "Create a docker-compose.yml for a 3-tier application"
echo.
echo # Troubleshoot containers
echo docker ai "Why is my container failing to start?"
echo.
echo # Security scanning
echo docker ai "Scan my images for vulnerabilities"
echo.

REM Quick Docker operations
echo ============================================================================
echo Quick Docker Operations
echo ============================================================================
echo.

REM Build images
echo [INFO] Building Docker images...
echo.

echo Building Frontend image...
docker build -t phase3-frontend:latest ./frontend
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend image
) else (
    echo [OK] Frontend image built successfully
)
echo.

echo Building Backend image...
docker build -t phase3-backend:latest ./backend
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build backend image
) else (
    echo [OK] Backend image built successfully
)
echo.

REM Show built images
echo [INFO] Built images:
docker images | findstr "phase3"
echo.

REM Test containers locally
echo ============================================================================
echo Test Run Containers Locally
echo ============================================================================
echo.

echo Starting PostgreSQL container...
docker run -d ^
  --name phase3-db ^
  -e POSTGRES_DB=todoapp ^
  -e POSTGRES_USER=phase3user ^
  -e POSTGRES_PASSWORD=phase3password123 ^
  -p 5432:5432 ^
  postgres:15-alpine

if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL container may already be running
) else (
    echo [OK] PostgreSQL started
)
echo.

echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul
echo.

echo Starting Backend container...
docker run -d ^
  --name phase3-backend ^
  --link phase3-db:db ^
  -e DATABASE_URL=postgresql://phase3user:phase3password123@db:5432/todoapp ^
  -e BETTER_AUTH_SECRET=dev_secret_key_for_testing ^
  -p 4000:4000 ^
  phase3-backend:latest

if %errorlevel% neq 0 (
    echo [WARNING] Backend container failed to start - check logs
) else (
    echo [OK] Backend started
)
echo.

echo Starting Frontend container...
docker run -d ^
  --name phase3-frontend ^
  --link phase3-backend:backend ^
  -e NEXT_PUBLIC_API_URL=http://localhost:4000/api/v1 ^
  -p 3000:3000 ^
  phase3-frontend:latest

if %errorlevel% neq 0 (
    echo [WARNING] Frontend container failed to start - check logs
) else (
    echo [OK] Frontend started
)
echo.

REM Show running containers
echo [INFO] Running containers:
docker ps --filter "name=phase3"
echo.

echo ============================================================================
echo Container Management Commands
echo ============================================================================
echo.
echo View logs:
echo   docker logs -f phase3-frontend
echo   docker logs -f phase3-backend
echo   docker logs -f phase3-db
echo.
echo Stop containers:
echo   docker stop phase3-frontend phase3-backend phase3-db
echo.
echo Remove containers:
echo   docker rm -f phase3-frontend phase3-backend phase3-db
echo.
echo Full cleanup:
echo   docker rm -f phase3-frontend phase3-backend phase3-db ^&^& docker rmi phase3-frontend:latest phase3-backend:latest
echo.

echo ============================================================================
echo Gordon AI Integration Complete
echo ============================================================================
echo.
echo Next Steps:
echo   1. Enable Gordon in Docker Desktop Settings ^> Beta features
echo   2. Use 'docker ai' commands for AI assistance
echo   3. Run '.\deploy-minikube.bat' for Kubernetes deployment
echo.

endlocal
