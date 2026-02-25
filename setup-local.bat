@echo off
REM Phase V - Complete Local Setup Script (Windows)
REM This script sets up and runs the entire Phase V stack locally

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Local Setup and Run                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Docker Desktop
echo [1/6] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is not installed or not running
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker Desktop is running
echo.

REM Step 2: Start Minikube
echo [2/6] Starting Minikube...
minikube start --memory=8192 --cpus=4 --disk-size=40gb
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Minikube
    echo Make sure Docker Desktop is running and virtualization is enabled
    pause
    exit /b 1
)
echo [OK] Minikube started
echo.

REM Step 3: Install Dapr
echo [3/6] Installing Dapr...
dapr status -k >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Dapr on Kubernetes...
    dapr init -k
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Dapr
        pause
        exit /b 1
    )
) else (
    echo [OK] Dapr is already installed
)
dapr status -k
echo.

REM Step 4: Install Kafka (Strimzi)
echo [4/6] Installing Kafka (Strimzi Operator)...
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.38.0/strimzi-cluster-operator-0.38.0.yaml -n kafka
echo Waiting for Strimzi Operator to be ready (this may take 2-3 minutes)...
timeout /t 30 /nobreak >nul
kubectl wait --for=condition=Available deployment/strimzi-cluster-operator -n kafka --timeout=300s 2>nul || echo [WARNING] Operator may still be starting
echo.

REM Step 5: Deploy Kafka Cluster
echo [5/6] Deploying Kafka Cluster...
if exist kafka-cluster.yaml (
    kubectl apply -f kafka-cluster.yaml -n kafka
    echo Waiting for Kafka brokers to be ready (this may take 3-5 minutes)...
    timeout /t 60 /nobreak >nul
    kubectl get pods -n kafka
) else (
    echo [WARNING] kafka-cluster.yaml not found
    echo Please create the Kafka cluster configuration first
)
echo.

REM Step 6: Install Redis and PostgreSQL
echo [6/6] Installing Redis and PostgreSQL...
kubectl create namespace redis --dry-run=client -o yaml | kubectl apply -f -
helm repo add bitnami https://charts.bitnami.com/bitnami >nul 2>&1
helm repo update >nul 2>&1

echo Installing Redis...
helm install redis bitnami/redis --namespace redis --set auth.password=redis123 --wait --timeout 5m 2>nul || echo [WARNING] Redis installation may still be in progress

echo Installing PostgreSQL...
helm install postgresql bitnami/postgresql --namespace postgres --set auth.password=postgres123 --set auth.username=postgres --wait --timeout 5m 2>nul || echo [WARNING] PostgreSQL installation may still be in progress

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Infrastructure Setup Complete!                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Access Information:
echo.
echo   Minikube Dashboard: minikube dashboard
echo   Grafana: kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
echo   Prometheus: kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
echo.
echo Next Steps:
echo   1. Run 'run-backend.bat' to start the backend
echo   2. Run 'run-frontend.bat' to start the frontend
echo   3. Access the application at http://localhost:3000
echo.

pause
