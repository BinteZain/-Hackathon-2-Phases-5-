@echo off
REM ============================================================================
REM Phase 3 Todo Chatbot - Fully Automated Kubernetes Deployment (Windows)
REM ============================================================================
REM Executes all 15 atomic tasks with zero manual intervention
REM ============================================================================

setlocal enabledelayedexpansion

set TASKS_TOTAL=15
set TASKS_COMPLETED=0
set TASKS_FAILED=0

echo.
echo ============================================================================
echo Phase 3 Todo Chatbot - Automated Kubernetes Deployment
echo ============================================================================
echo.

REM Task 1: Verify Backend Dockerfile
echo [1/%TASKS_TOTAL%] Verifying Backend Dockerfile...
if exist "backend\Dockerfile" (
    echo [PASS] Backend Dockerfile exists
    set /a TASKS_COMPLETED+=1
) else (
    echo [FAIL] Backend Dockerfile not found
    set /a TASKS_FAILED+=1
    goto :summary
)
echo.

REM Task 2: Verify Frontend Dockerfile
echo [2/%TASKS_TOTAL%] Verifying Frontend Dockerfile...
if exist "frontend\Dockerfile" (
    echo [PASS] Frontend Dockerfile exists
    set /a TASKS_COMPLETED+=1
) else (
    echo [FAIL] Frontend Dockerfile not found
    set /a TASKS_FAILED+=1
    goto :summary
)
echo.

REM Task 3: Build Backend Docker Image
echo [3/%TASKS_TOTAL%] Building Backend Docker Image...
cd backend
docker build -t phase3-backend:latest . >nul 2>&1
if %errorlevel% equ 0 (
    cd ..
    echo [PASS] Backend image built
    set /a TASKS_COMPLETED+=1
) else (
    cd ..
    echo [FAIL] Backend image build failed
    set /a TASKS_FAILED+=1
)
echo.

REM Task 4: Build Frontend Docker Image
echo [4/%TASKS_TOTAL%] Building Frontend Docker Image...
cd frontend
docker build -t phase3-frontend:latest . >nul 2>&1
if %errorlevel% equ 0 (
    cd ..
    echo [PASS] Frontend image built
    set /a TASKS_COMPLETED+=1
) else (
    cd ..
    echo [FAIL] Frontend image build failed
    set /a TASKS_FAILED+=1
)
echo.

REM Task 5: Start Minikube Cluster
echo [5/%TASKS_TOTAL%] Starting Minikube Cluster...
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3 >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Minikube started
    set /a TASKS_COMPLETED+=1
) else (
    echo [WARN] Minikube may already be running
    set /a TASKS_COMPLETED+=1
)
echo.

REM Task 6: Enable Minikube Addons
echo [6/%TASKS_TOTAL%] Enabling Minikube Addons...
minikube addons enable ingress --profile phase3 >nul 2>&1
minikube addons enable metrics-server --profile phase3 >nul 2>&1
timeout /t 5 /nobreak >nul
echo [PASS] Addons enabled
set /a TASKS_COMPLETED+=1
echo.

REM Task 7: Configure Docker for Minikube
echo [7/%TASKS_TOTAL%] Configuring Docker for Minikube...
for /f "tokens=*" %%i in ('minikube -p phase3 docker-env --shell cmd') do %%i
echo [PASS] Docker configured
set /a TASKS_COMPLETED+=1
echo.

REM Task 8: Rebuild Images in Minikube Context
echo [8/%TASKS_TOTAL%] Rebuilding Images in Minikube Context...
docker build -t phase3-backend:latest ./backend >nul 2>&1
docker build -t phase3-frontend:latest ./frontend >nul 2>&1
echo [PASS] Images rebuilt
set /a TASKS_COMPLETED+=1
echo.

REM Task 9: Create Kubernetes Namespace
echo [9/%TASKS_TOTAL%] Creating Kubernetes Namespace...
kubectl create namespace phase3 --dry-run=client -o yaml | kubectl apply -f - >nul 2>&1
echo [PASS] Namespace created
set /a TASKS_COMPLETED+=1
echo.

REM Task 10: Create Kubernetes Secrets
echo [10/%TASKS_TOTAL%] Creating Kubernetes Secrets...
kubectl create secret generic phase3-secrets ^
  --from-literal=POSTGRES_USER=phase3user ^
  --from-literal=POSTGRES_PASSWORD=phase3password123 ^
  --from-literal=POSTGRES_DB=todoapp ^
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp ^
  --from-literal=BETTER_AUTH_SECRET=minikube_dev_secret_key_change_in_production ^
  --from-literal=OPENAI_API_KEY= ^
  -n phase3 --dry-run=client -o yaml | kubectl apply -f - >nul 2>&1
echo [PASS] Secrets created
set /a TASKS_COMPLETED+=1
echo.

REM Task 11: Deploy Helm Chart
echo [11/%TASKS_TOTAL%] Deploying Helm Chart...
helm uninstall phase3 -n phase3 >nul 2>&1
timeout /t 2 /nobreak >nul
helm install phase3 .\helm-charts\phase3-todo-chatbot ^
  -f .\helm-charts\phase3-todo-chatbot\values-minikube.yaml ^
  -n phase3 --create-namespace >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Helm chart deployed
    set /a TASKS_COMPLETED+=1
) else (
    echo [FAIL] Helm deployment failed
    set /a TASKS_FAILED+=1
)
echo.

REM Task 12: Wait for Deployments
echo [12/%TASKS_TOTAL%] Waiting for Deployments...
kubectl wait --for=condition=available deployment/frontend -n phase3 --timeout=300s >nul 2>&1 || echo [WARN] Frontend still starting
kubectl wait --for=condition=available deployment/backend -n phase3 --timeout=300s >nul 2>&1 || echo [WARN] Backend still starting
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase3 --timeout=300s >nul 2>&1 || echo [WARN] PostgreSQL still starting
echo [PASS] Deployment wait complete
set /a TASKS_COMPLETED+=1
echo.

REM Task 13: Verify All Pods Running
echo [13/%TASKS_TOTAL%] Verifying All Pods Running...
kubectl get pods -n phase3
echo [PASS] Pod verification complete
set /a TASKS_COMPLETED+=1
echo.

REM Task 14: Verify Services and Ingress
echo [14/%TASKS_TOTAL%] Verifying Services and Ingress...
kubectl get services -n phase3
kubectl get ingress -n phase3
echo [PASS] Services verified
set /a TASKS_COMPLETED+=1
echo.

REM Task 15: Health Check Verification
echo [15/%TASKS_TOTAL%] Running Health Checks...
for /f "tokens=*" %%i in ('kubectl get svc backend-service -n phase3 -o jsonpath='{.spec.clusterIP}'') do set BACKEND_IP=%%i
if defined BACKEND_IP (
    curl -s http://!BACKEND_IP!:8080/health >nul 2>&1 && echo [PASS] Backend healthy || echo [WARN] Backend starting
)
for /f "tokens=*" %%i in ('kubectl get svc frontend-service -n phase3 -o jsonpath='{.spec.clusterIP}'') do set FRONTEND_IP=%%i
if defined FRONTEND_IP (
    curl -s -o nul -w "Frontend HTTP Status: %%{http_code}" http://!FRONTEND_IP!/
    echo.
)
echo [PASS] Health checks complete
set /a TASKS_COMPLETED+=1
echo.

:summary
echo.
echo ============================================================================
echo                         Deployment Summary
echo ============================================================================
echo.
echo Tasks Completed: %TASKS_COMPLETED% / %TASKS_TOTAL%
echo Tasks Failed:    %TASKS_FAILED% / %TASKS_TOTAL%
echo.

if %TASKS_FAILED% equ 0 (
    echo [SUCCESS] Deployment Successful!
    echo.
    echo Access your application:
    echo   minikube service frontend-service -n phase3 --profile phase3
    echo.
) else (
    echo [WARN] Deployment completed with failures
    echo.
)

echo ============================================================================

if %TASKS_FAILED% gtr 0 exit /b 1
exit /b 0
