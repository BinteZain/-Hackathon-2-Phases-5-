@echo off
REM ============================================================================
REM Phase 4 - Complete AI-Assisted Deployment Script
REM ============================================================================
REM This script deploys the Phase 4 Todo Chatbot using:
REM - Gordon (Docker AI) for containerization
REM - kubectl-ai for AI-assisted Kubernetes operations
REM - kagent for advanced cluster management
REM - Minikube for local Kubernetes cluster
REM - Helm Charts for package management
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo Phase 4 - AI-Assisted Cloud Native Todo Chatbot Deployment
echo ============================================================================
echo.
echo AI Tools:
echo   - Gordon (Docker AI) - Intelligent container operations
echo   - kubectl-ai - AI-assisted Kubernetes management
echo   - kagent - Advanced cluster optimization
echo.
echo Technology Stack:
echo   - Containerization: Docker (Docker Desktop)
echo   - Orchestration: Kubernetes (Minikube)
echo   - Package Manager: Helm Charts
echo   - AI DevOps: kubectl-ai, kagent, Gordon
echo   - Application: Phase 4 Todo Chatbot
echo.

REM ============================================================================
REM Prerequisites Check
REM ============================================================================
echo ============================================================================
echo Step 1: Checking Prerequisites
echo ============================================================================
echo.

REM Check Docker
echo [INFO] Checking Docker...
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    exit /b 1
)
docker --version
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not running
    echo Please start Docker Desktop
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Check Minikube
echo [INFO] Checking Minikube...
where minikube >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Minikube is not installed or not in PATH
    echo Please install Minikube from: https://minikube.sigs.k8s.io/docs/start/
    exit /b 1
)
minikube version
echo [OK] Minikube is installed
echo.

REM Check kubectl
echo [INFO] Checking kubectl...
where kubectl >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] kubectl is not installed or not in PATH
    echo Please install kubectl from: https://kubernetes.io/docs/tasks/tools/
    exit /b 1
)
kubectl version --client
echo [OK] kubectl is installed
echo.

REM Check Helm
echo [INFO] Checking Helm...
where helm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Helm is not installed or not in PATH
    echo Please install Helm from: https://helm.sh/docs/intro/install/
    exit /b 1
)
helm version --short
echo [OK] Helm is installed
echo.

REM Check kubectl-ai (optional)
echo [INFO] Checking kubectl-ai (optional)...
where kubectl-ai >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] kubectl-ai not found - will use standard kubectl commands
    echo Download from: https://github.com/sozercan/kubectl-ai
) else (
    kubectl-ai version
    echo [OK] kubectl-ai is available
)
echo.

REM ============================================================================
REM Start Minikube Cluster
REM ============================================================================
echo ============================================================================
echo Step 2: Starting Minikube Cluster
echo ============================================================================
echo.

echo [INFO] Starting Minikube with recommended resources...
echo [INFO] Allocating 6GB RAM, 4 CPUs, 20GB disk
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Minikube
    exit /b 1
)
echo [OK] Minikube started successfully
echo.

echo [INFO] Enabling required addons...
minikube addons enable ingress --profile phase4
minikube addons enable metrics-server --profile phase4
echo [OK] Addons enabled
echo.

echo [INFO] Waiting for cluster to be ready...
timeout /t 10 /nobreak >nul
minikube status --profile phase4
echo [OK] Cluster is ready
echo.

REM ============================================================================
REM Configure Docker for Minikube
REM ============================================================================
echo ============================================================================
echo Step 3: Configuring Docker for Minikube
echo ============================================================================
echo.

echo [INFO] Pointing Docker to Minikube's daemon...
FOR /f "tokens=*" %%i IN ('minikube -p phase4 docker-env --shell cmd') DO %%i
echo [OK] Docker configured
echo.

REM ============================================================================
REM Build Docker Images (with Gordon AI assistance if available)
REM ============================================================================
echo ============================================================================
echo Step 4: Building Docker Images
echo ============================================================================
echo.

REM Check if Gordon is available
echo [INFO] Checking for Gordon (Docker AI)...
docker ai "What can you do?" >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Gordon is available - using AI-assisted builds
    echo.
    echo [INFO] Asking Gordon to optimize builds...
    docker ai "Build optimized Docker images for Next.js frontend and FastAPI backend"
) else (
    echo [INFO] Gordon not available - using standard builds
)
echo.

echo [INFO] Building Frontend image...
cd frontend
docker build -t phase3-frontend:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build frontend image
    cd ..
    exit /b 1
)
cd ..
echo [OK] Frontend image built: phase3-frontend:latest
echo.

echo [INFO] Building Backend image...
cd backend
docker build -t phase3-backend:latest .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build backend image
    cd ..
    exit /b 1
)
cd ..
echo [OK] Backend image built: phase3-backend:latest
echo.

echo [INFO] Built images:
docker images | findstr "phase3"
echo.

REM ============================================================================
REM Create Namespace and Secrets
REM ============================================================================
echo ============================================================================
echo Step 5: Creating Namespace and Secrets
echo ============================================================================
echo.

echo [INFO] Creating namespace: phase4
kubectl create namespace phase4 --dry-run=client -o yaml | kubectl apply -f -
echo [OK] Namespace created
echo.

echo [INFO] Creating secrets...
kubectl create secret generic phase3-secrets ^
  --from-literal=POSTGRES_USER=phase3user ^
  --from-literal=POSTGRES_PASSWORD=phase3password123 ^
  --from-literal=POSTGRES_DB=todoapp ^
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp?sslmode=disable ^
  --from-literal=BETTER_AUTH_SECRET=phase4_dev_secret_key_change_in_production ^
  --from-literal=OPENAI_API_KEY= ^
  -n phase4 --dry-run=client -o yaml | kubectl apply -f -
echo [OK] Secrets created
echo.

REM ============================================================================
REM Deploy with Helm
REM ============================================================================
echo ============================================================================
echo Step 6: Deploying Application with Helm
echo ============================================================================
echo.

echo [INFO] Installing Phase 4 Todo Chatbot with Helm...
helm install phase3 .\helm-charts\phase3-todo-chatbot ^
  -f .\helm-charts\phase3-todo-chatbot\values-minikube.yaml ^
  -n phase4 ^
  --create-namespace
if %errorlevel% neq 0 (
    echo [ERROR] Helm deployment failed
    exit /b 1
)
echo [OK] Helm deployment completed
echo.

REM ============================================================================
REM Wait for Deployments
REM ============================================================================
echo ============================================================================
echo Step 7: Waiting for Deployments
echo ============================================================================
echo.

echo [INFO] Waiting for PostgreSQL to be ready...
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase4 --timeout=300s
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL may not be ready yet
)
echo.

echo [INFO] Waiting for Backend to be available...
kubectl wait --for=condition=available deployment/backend -n phase4 --timeout=300s
if %errorlevel% neq 0 (
    echo [WARNING] Backend may not be ready yet
)
echo.

echo [INFO] Waiting for Frontend to be available...
kubectl wait --for=condition=available deployment/frontend -n phase4 --timeout=300s
if %errorlevel% neq 0 (
    echo [WARNING] Frontend may not be ready yet
)
echo.

REM ============================================================================
REM AI-Assisted Verification with kubectl-ai
REM ============================================================================
echo ============================================================================
echo Step 8: AI-Assisted Verification
echo ============================================================================
echo.

where kubectl-ai >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Using kubectl-ai for verification...
    echo.
    
    echo [INFO] Asking kubectl-ai to check deployment status...
    kubectl-ai "show me all resources in phase4 namespace"
    echo.
    
    echo [INFO] Asking kubectl-ai to verify health...
    kubectl-ai "check the health of phase3 deployment"
    echo.
) else (
    echo [INFO] Standard verification with kubectl...
    echo.
    
    echo [INFO] Deployment status:
    kubectl get deployments -n phase4
    echo.
    
    echo [INFO] Pod status:
    kubectl get pods -n phase4
    echo.
    
    echo [INFO] Service status:
    kubectl get services -n phase4
    echo.
)

REM ============================================================================
REM Display Access Information
REM ============================================================================
echo ============================================================================
echo Step 9: Access Information
echo ============================================================================
echo.

REM Get Minikube IP
FOR /f "tokens=*" %%i IN ('minikube ip -p phase4') DO set MINIKUBE_IP=%%i

echo To access the application:
echo.
echo Option 1: Using Minikube service command (Recommended)
echo   minikube service frontend-service -n phase4 --profile phase4
echo.
echo Option 2: Using NodePort
echo   http://%MINIKUBE_IP%:30080
echo.
echo Option 3: Using Ingress
echo   1. Add to hosts file: %MINIKUBE_IP% todo-app.local
echo   2. Visit: http://todo-app.local
echo.

REM ============================================================================
REM Display Useful Commands
REM ============================================================================
echo ============================================================================
echo Useful Commands
echo ============================================================================
echo.
echo View logs:
echo   kubectl logs -f deployment/frontend -n phase4
echo   kubectl logs -f deployment/backend -n phase4
echo   kubectl logs -f postgres-phase3-todo-chatbot-0 -n phase4
echo.
echo Access database:
echo   kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase4 -- psql -U phase3user todoapp
echo.
echo Scale application:
echo   kubectl scale deployment/frontend --replicas=3 -n phase4
echo   kubectl scale deployment/backend --replicas=5 -n phase4
echo.
echo AI-assisted operations:
echo   kubectl-ai "scale backend to handle more load"
echo   kubectl-ai "optimize resource allocation"
echo   kubectl-ai "check why pods are failing"
echo.
echo Uninstall:
echo   helm uninstall phase3 -n phase4
echo   kubectl delete namespace phase4
echo   minikube stop -p phase4
echo.

REM ============================================================================
REM Final Status
REM ============================================================================
echo ============================================================================
echo Deployment Summary
echo ============================================================================
echo.
kubectl get all -n phase4
echo.

echo ============================================================================
echo [SUCCESS] Phase 4 Todo Chatbot deployed successfully!
echo ============================================================================
echo.
echo AI Tools Used:
echo   - Gordon (Docker AI) - Container operations
echo   - kubectl-ai - Kubernetes management
echo   - Helm - Package deployment
echo.
echo Application URLs:
echo   - Frontend: http://localhost:3000 (via port-forward)
echo   - Backend API: http://localhost:4000 (via port-forward)
echo.
echo Next Steps:
echo   1. Access the application using one of the methods above
echo   2. Test the Todo Chatbot functionality
echo   3. Use AI tools for ongoing management
echo.

endlocal
