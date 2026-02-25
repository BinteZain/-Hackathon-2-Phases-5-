@echo off
REM Phase V - Monitoring Stack Deployment Script (Windows)
REM Deploys Prometheus, Grafana, Loki, and Alertmanager

setlocal enabledelayedexpansion

REM Configuration
set NAMESPACE=monitoring
set RELEASE_NAME=monitoring
set GRAFANA_PASSWORD=admin

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Phase V - Monitoring Stack Deployment                ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check prerequisites
echo [1/8] Checking prerequisites...

where kubectl >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] kubectl is not installed
    exit /b 1
)
for /f "tokens=2" %%i in ('kubectl version --client --short 2^>nul ^| find "Client Version"') do set KUBECTL_VERSION=%%i
echo [OK] kubectl installed: %KUBECTL_VERSION%

where helm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Helm is not installed
    exit /b 1
)
for /f "tokens=3" %%i in ('helm version --short 2^>nul') do set HELM_VERSION=%%i
echo [OK] Helm installed: %HELM_VERSION%

kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot connect to Kubernetes cluster
    exit /b 1
)
echo [OK] Connected to cluster

REM Get node count
for /f "tokens=1" %%i in ('kubectl get nodes --no-headers 2^>nul ^| find /c /v ""') do set NODE_COUNT=%%i
if %NODE_COUNT% LSS 2 (
    echo [WARNING] Cluster has only %NODE_COUNT% node(s). Recommended: 4+ nodes
) else (
    echo [OK] Cluster has %NODE_COUNT% nodes
)

REM Create namespace
echo.
echo [2/8] Creating namespace...
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -
echo [OK] Namespace '%NAMESPACE%' created/verified

REM Add Helm repositories
echo.
echo [3/8] Adding Helm repositories...
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add loki https://grafana.github.io/helm-charts
helm repo update
echo [OK] Helm repositories added and updated

REM Install kube-prometheus-stack
echo.
echo [4/8] Installing kube-prometheus-stack...
echo    This may take 5-10 minutes...

helm upgrade --install %RELEASE_NAME% prometheus-community/kube-prometheus-stack ^
    --namespace %NAMESPACE% ^
    --create-namespace ^
    --values monitoring/values-production.yaml ^
    --set grafana.adminPassword=%GRAFANA_PASSWORD% ^
    --wait ^
    --timeout 15m ^
    --atomic

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install kube-prometheus-stack
    exit /b 1
)
echo [OK] kube-prometheus-stack installed

REM Install Loki stack
echo.
echo [5/8] Installing Loki stack...

helm upgrade --install loki loki/loki-stack ^
    --namespace %NAMESPACE% ^
    --create-namespace ^
    --values monitoring/loki-values.yaml ^
    --wait ^
    --timeout 10m ^
    --atomic

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Loki stack
    exit /b 1
)
echo [OK] Loki stack installed

REM Apply Prometheus rules
echo.
echo [6/8] Applying Prometheus rules...
kubectl apply -f monitoring/prometheus-rules.yaml
echo [OK] Prometheus rules applied

REM Apply Alertmanager configuration
echo.
echo [7/8] Applying Alertmanager configuration...
kubectl apply -f monitoring/alertmanager-config.yaml
echo [OK] Alertmanager configuration applied

REM Wait for pods
echo.
echo [8/8] Waiting for components to be ready...
timeout /t 30 /nobreak >nul

kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=%RELEASE_NAME% -n %NAMESPACE% --timeout=300s 2>nul || echo [WARNING] Some pods may still be starting
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=loki -n %NAMESPACE% --timeout=300s 2>nul || echo [WARNING] Loki may still be starting
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=promtail -n %NAMESPACE% --timeout=300s 2>nul || echo [WARNING] Promtail may still be starting

REM Print access information
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Monitoring Stack Deployment Complete!                ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Access Information:
echo.

REM Get Grafana info
for /f "tokens=1" %%i in ('kubectl get svc -n %NAMESPACE% -l app.kubernetes.io/name=grafana -o jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}" 2^>nul') do set GRAFANA_IP=%%i
if defined GRAFANA_IP (
    echo   [OK] Grafana: http://%GRAFANA_IP%
) else (
    echo   [INFO] Grafana: kubectl port-forward svc/%RELEASE_NAME%-grafana -n %NAMESPACE% 3000:80
)
echo      Username: admin
echo      Password: %GRAFANA_PASSWORD%
echo.

REM Get Prometheus info
for /f "tokens=1" %%i in ('kubectl get svc -n %NAMESPACE% -l app.kubernetes.io/name=prometheus -o jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}" 2^>nul') do set PROMETHEUS_IP=%%i
if defined PROMETHEUS_IP (
    echo   [OK] Prometheus: http://%PROMETHEUS_IP%
) else (
    echo   [INFO] Prometheus: kubectl port-forward svc/%RELEASE_NAME%-prometheus -n %NAMESPACE% 9090:9090
)
echo.

REM Get Alertmanager info
for /f "tokens=1" %%i in ('kubectl get svc -n %NAMESPACE% -l app.kubernetes.io/name=alertmanager -o jsonpath="{.items[0].status.loadBalancer.ingress[0].ip}" 2^>nul') do set ALERTMANAGER_IP=%%i
if defined ALERTMANAGER_IP (
    echo   [OK] Alertmanager: http://%ALERTMANAGER_IP%
) else (
    echo   [INFO] Alertmanager: kubectl port-forward svc/%RELEASE_NAME%-alertmanager -n %NAMESPACE% 9093:9093
)
echo.

REM Print pods
echo Resource Usage:
echo.
kubectl get pods -n %NAMESPACE% -o wide
echo.

REM Print PVCs
echo Persistent Volumes:
echo.
kubectl get pvc -n %NAMESPACE%
echo.

echo Next Steps:
echo.
echo   1. Access Grafana and configure datasources
echo   2. Import dashboards (IDs: 6417, 1860, 13817, 7589)
echo   3. Update Alertmanager Slack webhook URL
echo   4. Configure ServiceMonitors for your applications
echo   5. Set up alerting rules based on your SLOs
echo.
echo Documentation: MONITORING_SETUP.md
echo.

pause
