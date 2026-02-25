@echo off
REM ============================================================================
REM kubectl-ai - AI-Assisted Kubernetes Operations for Phase 4
REM ============================================================================
REM This script provides AI-assisted Kubernetes commands using kubectl-ai
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo kubectl-ai - AI-Assisted Kubernetes for Phase 4 Todo Chatbot
echo ============================================================================
echo.

REM Check if kubectl is installed
where kubectl >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] kubectl is not installed or not in PATH
    echo Please install kubectl from: https://kubernetes.io/docs/tasks/tools/
    exit /b 1
)

echo [INFO] kubectl found:
kubectl version --client
echo.

REM Check if kubectl-ai is installed
where kubectl-ai >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] kubectl-ai is not installed or not in PATH
    echo Download from: https://github.com/sozercan/kubectl-ai
    echo.
    echo Installing kubectl-ai...
    REM Download kubectl-ai (Windows)
    curl -L -o kubectl-ai.exe https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai_Windows_x86_64.zip
    if exist kubectl-ai.exe (
        move /y kubectl-ai.exe C:\Windows\System32\kubectl-ai.exe
        echo [OK] kubectl-ai installed
    ) else (
        echo [INFO] Please install manually or use the included kubectl-ai.exe
    )
    echo.
) else (
    echo [INFO] kubectl-ai found
    kubectl-ai version
    echo.
)

REM Display kubectl-ai capabilities
echo ============================================================================
echo kubectl-ai Capabilities
echo ============================================================================
echo.
echo kubectl-ai allows you to manage Kubernetes using natural language:
echo   - Deploy applications
echo   - Scale resources
echo   - Troubleshoot issues
echo   - Generate manifests
echo   - Optimize configurations
echo.

echo ============================================================================
echo kubectl-ai Commands for Phase 4
echo ============================================================================
echo.

REM Deployment Commands
echo [DEPLOYMENT COMMANDS]
echo.
echo # Deploy the todo frontend with 2 replicas
echo kubectl-ai "deploy the todo frontend with 2 replicas"
echo.
echo # Deploy the backend with 2 replicas
echo kubectl-ai "deploy the todo backend with 2 replicas"
echo.
echo # Deploy PostgreSQL database
echo kubectl-ai "deploy postgresql for todo app"
echo.
echo # Create namespace for phase 4
echo kubectl-ai "create namespace phase4"
echo.

REM Scaling Commands
echo [SCALING COMMANDS]
echo.
echo # Scale backend to handle more load
echo kubectl-ai "scale the backend to 5 replicas to handle more load"
echo.
echo # Scale frontend to 3 replicas
echo kubectl-ai "scale frontend to 3 replicas"
echo.
echo # Enable HPA for backend
echo kubectl-ai "enable horizontal pod autoscaling for backend"
echo.

REM Troubleshooting Commands
echo [TROUBLESHOOTING COMMANDS]
echo.
echo # Check why pods are failing
echo kubectl-ai "check why the pods are failing"
echo.
echo # Analyze backend issues
echo kubectl-ai "why is the backend pod crashing?"
echo.
echo # Check database connectivity
echo kubectl-ai "check database connection issues"
echo.
echo # Analyze cluster health
echo kubectl-ai "analyze cluster health"
echo.

REM Resource Optimization
echo [RESOURCE OPTIMIZATION COMMANDS]
echo.
echo # Optimize resource allocation
echo kubectl-ai "optimize resource allocation for the backend"
echo.
echo # Set resource limits
echo kubectl-ai "set CPU and memory limits for frontend pods"
echo.
echo # Add resource requests
echo kubectl-ai "add resource requests for all deployments"
echo.

REM Security Commands
echo [SECURITY COMMANDS]
echo.
echo # Add security context
echo kubectl-ai "add security context to backend deployment"
echo.
echo # Create network policy
echo kubectl-ai "create network policy to isolate backend"
echo.
echo # Add pod security standards
echo kubectl-ai "add pod security standards for phase4 namespace"
echo.

REM Configuration Commands
echo [CONFIGURATION COMMANDS]
echo.
echo # Create configmap
echo kubectl-ai "create configmap for backend configuration"
echo.
echo # Create secret
echo kubectl-ai "create secret for database credentials"
echo.
echo # Update environment variables
echo kubectl-ai "update DATABASE_URL environment variable"
echo.

REM Monitoring Commands
echo [MONITORING COMMANDS]
echo.
echo # Check pod status
echo kubectl-ai "show me the status of all pods"
echo.
echo # View deployment status
echo kubectl-ai "show deployment status"
echo.
echo # Check service endpoints
echo kubectl-ai "show service endpoints"
echo.
echo # View resource usage
echo kubectl-ai "show resource usage for all pods"
echo.

REM Cleanup Commands
echo [CLEANUP COMMANDS]
echo.
echo # Delete frontend deployment
echo kubectl-ai "delete frontend deployment"
echo.
echo # Remove all phase4 resources
echo kubectl-ai "delete all resources in phase4 namespace"
echo.
echo # Rollback deployment
echo kubectl-ai "rollback the backend deployment"
echo.

echo ============================================================================
echo Interactive kubectl-ai Session
echo ============================================================================
echo.
echo To start an interactive session:
echo   kubectl-ai
echo.
echo Then type your commands naturally:
echo   ^> deploy the todo app with 2 replicas each
echo   ^> scale backend to 5 replicas
echo   ^> show me the logs of the backend
echo   ^> why is the frontend pod failing?
echo   ^> exit
echo.

echo ============================================================================
echo Example: Complete Deployment with kubectl-ai
echo ============================================================================
echo.
echo # Step 1: Create namespace
echo kubectl-ai "create a namespace called phase4"
echo.
echo # Step 2: Deploy PostgreSQL
echo kubectl-ai "deploy postgresql with 5Gi storage in phase4 namespace"
echo.
echo # Step 3: Deploy backend
echo kubectl-ai "deploy phase3-backend image with 2 replicas, connect to postgres"
echo.
echo # Step 4: Deploy frontend
echo kubectl-ai "deploy phase3-frontend image with 2 replicas, connect to backend"
echo.
echo # Step 5: Create services
echo kubectl-ai "create services for frontend and backend"
echo.
echo # Step 6: Set up ingress
echo kubectl-ai "create ingress for todo-app.local"
echo.
echo # Step 7: Enable autoscaling
echo kubectl-ai "enable HPA for frontend and backend"
echo.
echo # Step 8: Verify deployment
echo kubectl-ai "show me all resources in phase4 namespace"
echo.

echo ============================================================================
echo kubectl-ai + Helm Integration
echo ============================================================================
echo.
echo # Deploy with Helm, then use kubectl-ai for management
echo helm install phase3 .\helm-charts\phase3-todo-chatbot -f .\helm-charts\phase3-todo-chatbot\values-minikube.yaml -n phase4 --create-namespace
echo.
echo # Then use kubectl-ai for operations
echo kubectl-ai "scale the phase3 deployment to 3 replicas"
echo kubectl-ai "check the health of phase3 release"
echo kubectl-ai "show me the helm release status"
echo.

echo ============================================================================
echo kubectl-ai Best Practices
echo ============================================================================
echo.
echo 1. Be specific in your commands
echo 2. Review generated manifests before applying
echo 3. Use dry-run for complex operations
echo 4. Combine with kubectl for fine-tuning
echo 5. Keep security in mind
echo.

echo ============================================================================
echo Next Steps
echo ============================================================================
echo.
echo 1. Ensure Minikube is running: minikube start --profile phase4
echo 2. Build Docker images: docker build -t phase3-frontend:latest ./frontend
echo 3. Use kubectl-ai commands to deploy
echo 4. Or run the automated script: .\deploy-all.bat
echo.

endlocal
