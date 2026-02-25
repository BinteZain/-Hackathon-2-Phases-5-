#!/bin/bash
# ============================================================================
# Phase 3 Todo Chatbot - Minikube Deployment Script (Linux/Mac)
# ============================================================================
# This script deploys the Phase 3 Todo Chatbot application to Minikube
# ============================================================================

set -e

echo ""
echo "============================================================================"
echo "Phase 3 Todo Chatbot - Minikube Deployment"
echo "============================================================================"
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "[ERROR] Minikube is not installed or not in PATH"
    echo "Please install Minikube from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

echo "[INFO] Minikube found:"
minikube version
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "[ERROR] kubectl is not installed or not in PATH"
    echo "Please install kubectl from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo "[INFO] kubectl found:"
kubectl version --client --short 2>/dev/null || kubectl version --client
echo ""

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "[ERROR] Helm is not installed or not in PATH"
    echo "Please install Helm from: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo "[INFO] Helm found:"
helm version --short
echo ""

# Start Minikube
echo "[INFO] Starting Minikube with recommended resources..."
echo "[INFO] Allocating 6GB RAM, 4 CPUs, 20GB disk"
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3
echo "[OK] Minikube started successfully"
echo ""

# Enable ingress addon
echo "[INFO] Enabling NGINX Ingress addon..."
minikube addons enable ingress --profile phase3
echo "[OK] Ingress addon enabled"
echo ""

# Enable metrics-server addon (for HPA)
echo "[INFO] Enabling metrics-server addon..."
minikube addons enable metrics-server --profile phase3
echo "[OK] metrics-server addon enabled"
echo ""

# Wait for Minikube to be ready
echo "[INFO] Waiting for Minikube to be ready..."
sleep 10
echo ""

# Point Docker to Minikube's Docker daemon
echo "[INFO] Configuring Docker to use Minikube's daemon..."
eval $(minikube -p phase3 docker-env)
echo "[OK] Docker configured"
echo ""

# Build Docker images
echo "[INFO] Building Frontend Docker image..."
cd frontend
docker build -t phase3-frontend:latest .
cd ..
echo "[OK] Frontend image built"
echo ""

echo "[INFO] Building Backend Docker image..."
cd backend
docker build -t phase3-backend:latest .
cd ..
echo "[OK] Backend image built"
echo ""

# Create namespace
echo "[INFO] Creating namespace: phase3"
kubectl create namespace phase3 --dry-run=client -o yaml | kubectl apply -f -
echo "[OK] Namespace created"
echo ""

# Create secrets
echo "[INFO] Creating secrets..."
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=phase3password123 \
  --from-literal=POSTGRES_DB=todoapp \
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp?sslmode=disable \
  --from-literal=BETTER_AUTH_SECRET=minikube_dev_secret_key_change_in_production \
  --from-literal=OPENAI_API_KEY= \
  -n phase3 --dry-run=client -o yaml | kubectl apply -f -
echo "[OK] Secrets created"
echo ""

# Deploy using Helm
echo "[INFO] Deploying application using Helm..."
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3 \
  --create-namespace
echo "[OK] Helm deployment completed"
echo ""

# Wait for deployments
echo "[INFO] Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/frontend -n phase3 --timeout=300s
kubectl wait --for=condition=available deployment/backend -n phase3 --timeout=300s
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase3 --timeout=300s
echo "[OK] Deployments are ready"
echo ""

# Show status
echo ""
echo "============================================================================"
echo "Deployment Status"
echo "============================================================================"
echo ""
kubectl get all -n phase3
echo ""

# Get application URL
echo ""
echo "============================================================================"
echo "Access Information"
echo "============================================================================"
echo ""
echo "To access the application:"
echo ""

# Get Minikube IP
MINIKUBE_IP=$(minikube ip -p phase3)

echo "Option 1: Using Minikube service command"
echo "  minikube service frontend-service -n phase3 --profile phase3"
echo ""

echo "Option 2: Using NodePort (if configured)"
echo "  http://${MINIKUBE_IP}:30080"
echo ""

echo "Option 3: Using Ingress (add to hosts file first)"
echo "  1. Add to /etc/hosts:"
echo "     ${MINIKUBE_IP} todo-app.local"
echo "  2. Visit: http://todo-app.local"
echo ""

echo "============================================================================"
echo "Useful Commands"
echo "============================================================================"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/frontend -n phase3"
echo "  kubectl logs -f deployment/backend -n phase3"
echo ""
echo "Access database:"
echo "  kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase3 -- psql -U phase3user todoapp"
echo ""
echo "Scale application:"
echo "  kubectl scale deployment/frontend --replicas=3 -n phase3"
echo ""
echo "Uninstall:"
echo "  helm uninstall phase3 -n phase3"
echo "  minikube stop -p phase3"
echo ""
echo "============================================================================"
echo "[SUCCESS] Phase 3 Todo Chatbot deployed successfully!"
echo "============================================================================"
echo ""
