# Automated Deployment Script for Windows PowerShell
# Run this script to deploy the entire application

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Cloud-Native Todo App Deployer  " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_PATH = Join-Path $PROJECT_ROOT "backend"
$FRONTEND_PATH = Join-Path $PROJECT_ROOT "frontend"
$CHARTS_PATH = Join-Path $PROJECT_ROOT "charts\todo-app"
$K8S_PATH = Join-Path $PROJECT_ROOT "k8s"

# Colors
function Write-Success {
    param([string]$Message)
    Write-Host "✓ " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

# Check prerequisites
Write-Info "Checking prerequisites..."

$minikubeInstalled = Get-Command minikube -ErrorAction SilentlyContinue
$kubectlInstalled = Get-Command kubectl -ErrorAction SilentlyContinue
$helmInstalled = Get-Command helm -ErrorAction SilentlyContinue
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if (-not $minikubeInstalled) {
    Write-Error-Custom "Minikube is not installed. Please install minikube first."
    exit 1
}
Write-Success "Minikube found"

if (-not $kubectlInstalled) {
    Write-Error-Custom "kubectl is not installed. Please install kubectl first."
    exit 1
}
Write-Success "kubectl found"

if (-not $helmInstalled) {
    Write-Error-Custom "Helm is not installed. Please install helm first."
    exit 1
}
Write-Success "Helm found"

if (-not $dockerInstalled) {
    Write-Error-Custom "Docker is not installed. Please install docker first."
    exit 1
}
Write-Success "Docker found"

Write-Host ""

# Start Minikube
Write-Info "Starting Minikube..."
minikube start --memory=4096 --cpus=2
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to start Minikube"
    exit 1
}
Write-Success "Minikube started"

Write-Host ""

# Build Docker images
Write-Info "Building Docker images..."

Write-Info "Building backend image..."
Set-Location $BACKEND_PATH
docker build -t todo-backend:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to build backend image"
    exit 1
}
Write-Success "Backend image built"

Write-Info "Building frontend image..."
Set-Location $FRONTEND_PATH
docker build -t todo-frontend:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to build frontend image"
    exit 1
}
Write-Success "Frontend image built"

# Load images into Minikube
Write-Info "Loading images into Minikube..."
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
Write-Success "Images loaded"

Write-Host ""

# Deploy using Helm
Write-Info "Deploying application with Helm..."

# Check if release exists
$releaseExists = helm list | Select-String "todo-app"

if ($releaseExists) {
    Write-Info "Release exists, upgrading..."
    helm upgrade todo-app $CHARTS_PATH
} else {
    Write-Info "Installing new release..."
    helm install todo-app $CHARTS_PATH
}

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to deploy with Helm"
    exit 1
}
Write-Success "Application deployed"

Write-Host ""

# Wait for pods to be ready
Write-Info "Waiting for pods to be ready..."
Start-Sleep -Seconds 10

# Check deployment status
Write-Host ""
Write-Info "Deployment Status:"
Write-Host ""

kubectl get pods
Write-Host ""
kubectl get services
Write-Host ""
kubectl get deployments
Write-Host ""
kubectl get hpa

Write-Host ""
Write-Success "Deployment complete!"

# Get access URL
Write-Host ""
Write-Info "Access the application:"
$minikubeIp = minikube ip
Write-Host "  Frontend: http://$($minikubeIp):30080" -ForegroundColor Cyan
Write-Host "  Backend Health: http://$($minikubeIp):3001/health" -ForegroundColor Cyan

Write-Host ""
Write-Info "Useful commands:"
Write-Host "  kubectl get pods                    - View all pods"
Write-Host "  kubectl get services                - View all services"
Write-Host "  kubectl logs -l app=backend         - View backend logs"
Write-Host "  kubectl scale deployment backend-deployment --replicas=5  - Scale backend"
Write-Host "  minikube stop                       - Stop Minikube"

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete! 🚀           " -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan

Set-Location $PROJECT_ROOT
