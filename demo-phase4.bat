@echo off
REM ============================================================================
REM Phase 4 - Final Judge Demonstration Script
REM ============================================================================

echo.
echo ============================================================================
echo         PHASE 4 - JUDGE DEMONSTRATION
echo ============================================================================
echo.

echo [1/7] Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

echo [2/7] Checking Minikube...
minikube version
echo.

echo [3/7] Starting Minikube Cluster...
echo         This may take 3-5 minutes...
minikube delete -p phase3 >nul 2>&1
timeout /t 2 /nobreak >nul
minikube start --memory=3500 --cpus=2 --profile phase3
if %errorlevel% neq 0 (
    echo [ERROR] Minikube start failed
    pause
    exit /b 1
)
echo [OK] Minikube started
echo.

echo [4/7] Enabling Addons...
minikube addons enable ingress --profile phase3
minikube addons enable metrics-server --profile phase3
echo [OK] Addons enabled
echo.

echo [5/7] Configuring Docker for Minikube...
for /f "tokens=*" %%i in ('minikube -p phase3 docker-env --shell cmd') do %%i
echo [OK] Docker configured
echo.

echo [6/7] Building Docker Images...
echo         Building frontend...
docker build -t phase3-frontend:latest ./frontend
echo         Building backend...
docker build -t phase3-backend:latest ./backend
echo [OK] Images built
echo.

echo [7/7] Deploying with Helm...
helm uninstall todo -n phase3 >nul 2>&1
timeout /t 2 /nobreak >nul
helm install todo ./helm -n phase3 --create-namespace
if %errorlevel% neq 0 (
    echo [ERROR] Helm install failed
    pause
    exit /b 1
)
echo [OK] Helm deployed
echo.

timeout /t 15 /nobreak >nul

echo ============================================================================
echo                      VERIFICATION
echo ============================================================================
echo.
echo Pod Status:
kubectl get pods -n phase3
echo.
echo Service Status:
kubectl get svc -n phase3
echo.
echo Deployment Status:
kubectl get deployment -n phase3
echo.

echo ============================================================================
echo                      SCALING DEMO
echo ============================================================================
echo.
echo Scaling backend from 2 to 5 replicas...
kubectl scale deployment/todo-backend --replicas=5 -n phase3
echo.
timeout /t 10 /nobreak >nul
echo New Pod Status:
kubectl get pods -n phase3
echo.

echo ============================================================================
echo                      ACCESS APPLICATION
echo ============================================================================
echo.
echo Opening application in browser...
echo.
start cmd /k "minikube service todo-frontend -n phase3 --profile phase3"
echo.
echo Or visit: http://localhost:3000 (after port-forward)
echo.

echo ============================================================================
echo                 PHASE 4 DEMO COMPLETE!
echo ============================================================================
echo.
echo Summary:
echo   - Infrastructure Spec: specs/infrastructure/K8S_INFRASTRUCTURE_SPEC.md
echo   - Helm Chart: helm/Chart.yaml
echo   - Dockerfiles: frontend/Dockerfile, backend/Dockerfile
echo   - Deployment: phase3 namespace
echo   - Replicas: Frontend x2, Backend x5, PostgreSQL x1
echo.
pause
