# Cloud-Native Todo App - Deployment Scripts

## Prerequisites

Install these tools first:

1. **Docker Desktop** - For containerization
2. **Minikube** - For local Kubernetes cluster
3. **kubectl** - Kubernetes CLI
4. **Helm** - Package manager for Kubernetes
5. **kubectl-ai** (optional) - AI-driven kubectl commands

### Installation Commands (Windows)

```powershell
# Install Minikube
choco install minikube

# Install kubectl
choco install kubernetes-cli

# Install Helm
choco install helm

# Install kubectl-ai (kubectl plugin)
# Download from: https://github.com/sozercan/kubectl-ai/releases
```

---

## Quick Start

### 1. Start Minikube

```powershell
minikube start --memory=4096 --cpus=2
```

### 2. Build Docker Images

```powershell
# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image
docker build -t todo-frontend:latest ./frontend

# Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### 3. Deploy using Helm

```powershell
# Install the application
helm install todo-app ./charts/todo-app

# Check status
helm status todo-app

# List releases
helm list
```

### 4. Deploy using kubectl (Alternative)

```powershell
# Apply all manifests
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/hpa/

# Or apply all at once
kubectl apply -f k8s/
```

### 5. Verify Deployment

```powershell
# Check pods
kubectl get pods

# Check services
kubectl get services

# Check deployments
kubectl get deployments

# Check HPA
kubectl get hpa
```

### 6. Access the Application

```powershell
# Get Minikube IP
minikube ip

# Access via NodePort (default: 30080)
# Open in browser: http://<minikube-ip>:30080

# Or use minikube service
minikube service frontend-service --url
```

---

## AI-Driven Commands (kubectl-ai)

### Install kubectl-ai

```powershell
# Download latest release from GitHub
# https://github.com/sozercan/kubectl-ai

# Or install via krew (if installed)
kubectl krew install ai
```

### Example AI Commands

```bash
# Scale backend
kubectl-ai "scale backend to 5 replicas"

# Show all pods
kubectl-ai "show me all pods"

# Get deployment status
kubectl-ai "what is the status of backend deployment"

# Create HPA
kubectl-ai "create horizontal pod autoscaler for backend with min 2 max 10 replicas"

# Show logs
kubectl-ai "show me the logs of backend pod"

# Debug pod
kubectl-ai "why is backend pod crashing"
```

---

## Scaling Demo

### Manual Scaling

```powershell
# Scale backend to 5 replicas
kubectl scale deployment backend-deployment --replicas=5

# Verify
kubectl get pods

# Scale back to 2
kubectl scale deployment backend-deployment --replicas=2
```

### Auto Scaling (HPA)

```powershell
# Watch HPA
kubectl get hpa -w

# Generate load (in another terminal)
while true; do curl http://<minikube-ip>:30080; done

# HPA will automatically scale based on CPU/Memory usage
```

---

## Monitoring

```powershell
# View logs
kubectl logs -l app=backend
kubectl logs -l app=frontend

# Follow logs in real-time
kubectl logs -l app=backend -f

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh

# Top pods (requires metrics-server)
kubectl top pods

# Top nodes
kubectl top nodes
```

---

## Cleanup

```powershell
# Uninstall Helm release
helm uninstall todo-app

# Or delete all resources
kubectl delete -f k8s/

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

---

## Troubleshooting

### Pod not starting

```powershell
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Service not accessible

```powershell
# Check service endpoints
kubectl get endpoints

# Check service details
kubectl describe service <service-name>
```

### Image pull errors

```powershell
# Make sure images are loaded in Minikube
minikube image list

# Rebuild and reload images
docker build -t todo-backend:latest ./backend
minikube image load todo-backend:latest
```
