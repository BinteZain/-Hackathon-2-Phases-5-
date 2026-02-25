# Phase 4 - Local Kubernetes Deployment with AI Agents

## 🎯 Overview

Phase 4 deploys the Todo Chatbot on a local Kubernetes cluster using **AI-assisted operations**:

| Component | Technology | AI Agent |
|-----------|------------|----------|
| **Containerization** | Docker Desktop | Gordon (Docker AI) |
| **Orchestration** | Kubernetes (Minikube) | kubectl-ai |
| **Package Management** | Helm Charts | - |
| **Cluster Optimization** | - | kagent |
| **Spec-Driven Dev** | Claude Code + SpecKit | - |

## ✅ Quick Start

### Option 1: Fully Automated (Recommended)

```powershell
# One command to deploy everything
.\deploy-all.bat
```

### Option 2: Step-by-Step with AI

```powershell
# Step 1: Docker operations with Gordon
.\gordon\gordon-ai.bat

# Step 2: Kubernetes with kubectl-ai
.\kubectl-ai\kubectl-ai-commands.bat

# Step 3: Cluster optimization with kagent
.\kagent\kagent-commands.bat

# Step 4: Complete deployment
.\deploy-all.bat
```

## 📁 Project Structure

```
E:\All Phases\4 phir se\
├── deploy-all.bat                  # Complete automated deployment
├── deploy-minikube.bat             # Minikube deployment script
├── docker-compose.yml              # Docker Compose configuration
├── PHASE4_AI_WORKFLOWS.md          # AI workflows documentation
├── SPEC_DRIVEN_BLUEPRINTS.md       # Spec-driven deployment blueprints
│
├── gordon/                         # Gordon (Docker AI) Integration
│   ├── gordon-ai.bat               # Gordon AI script
│   └── README.md                   # Gordon documentation
│
├── kubectl-ai/                     # kubectl-ai Integration
│   ├── kubectl-ai-commands.bat     # kubectl-ai commands script
│   └── README.md                   # kubectl-ai documentation
│
├── kagent/                         # kagent Integration
│   ├── kagent-commands.bat         # kagent commands script
│   └── README.md                   # kagent documentation
│
├── docker-compose/                 # Docker Compose AI Guide
│   └── DOCKER_COMPOSE_AI.md        # Docker Compose with AI
│
├── helm-charts/
│   └── phase3-todo-chatbot/        # Helm Chart for deployment
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-minikube.yaml
│       └── templates/
│
├── k8s/
│   └── local/                      # Kubernetes manifests
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── secrets.yaml
│       ├── *.yaml
│       └── kustomization.yaml
│
├── frontend/                       # Next.js Frontend
│   └── Dockerfile
│
└── backend/                        # FastAPI Backend
    └── Dockerfile
```

## 🛠️ Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 24.0+ | [Download](https://docs.docker.com/get-docker/) |
| Minikube | 1.32+ | [Download](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | [Download](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.13+ | [Download](https://helm.sh/docs/intro/install/) |
| kubectl-ai | Latest | [Download](https://github.com/sozercan/kubectl-ai) |

### Optional AI Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Gordon (Docker AI) | Docker operations | Docker Desktop 4.53+ Beta |
| kagent | Cluster optimization | `pip install kagent` |

## 🚀 Deployment Steps

### Step 1: Verify Prerequisites

```powershell
# Check all tools
docker --version
minikube version
kubectl version --client
helm version
kubectl-ai version  # Optional
```

### Step 2: Start Minikube

```powershell
# Start cluster with recommended resources
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4

# Enable addons
minikube addons enable ingress --profile phase4
minikube addons enable metrics-server --profile phase4
```

### Step 3: Build Docker Images

```powershell
# Configure Docker for Minikube
eval $(minikube -p phase4 docker-env)

# Build images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Or use Gordon AI
docker ai "Build optimized images for Next.js and FastAPI"
```

### Step 4: Deploy with Helm

```powershell
# Create namespace
kubectl create namespace phase4

# Create secrets
kubectl create secret generic phase3-secrets ^
  --from-literal=POSTGRES_USER=phase3user ^
  --from-literal=POSTGRES_PASSWORD=phase3password123 ^
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp ^
  --from-literal=BETTER_AUTH_SECRET=phase4_dev_secret ^
  -n phase4

# Deploy with Helm
helm install phase3 ./helm-charts/phase3-todo-chatbot ^
  -f ./helm-charts/phase3-todo-chatbot/values-minikube.yaml ^
  -n phase4 ^
  --create-namespace
```

### Step 5: Verify Deployment

```powershell
# Check all resources
kubectl get all -n phase4

# Or use AI
kubectl-ai "show me all resources in phase4 namespace"
kubectl-ai "check the health of phase3 deployment"
```

### Step 6: Access Application

```powershell
# Get Minikube IP
minikube ip -p phase4

# Access via service
minikube service frontend-service -n phase4 --profile phase4

# Or port-forward
kubectl port-forward svc/frontend-service 3000:80 -n phase4
```

## 🤖 AI Agent Commands

### Gordon (Docker AI)

```bash
# Check capabilities
docker ai "What can you do?"

# Build optimization
docker ai "Build optimized Docker images for production"

# Security scanning
docker ai "Scan phase3-backend:latest for vulnerabilities"

# Troubleshooting
docker ai "Why is my container failing?"
```

### kubectl-ai

```bash
# Deployment
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "deploy postgresql with 5Gi storage"

# Scaling
kubectl-ai "scale backend to 5 replicas"
kubectl-ai "enable HPA for frontend and backend"

# Troubleshooting
kubectl-ai "check why pods are failing"
kubectl-ai "analyze database connection issues"

# Optimization
kubectl-ai "optimize resource allocation"
```

### kagent

```bash
# Cluster health
kagent "analyze the cluster health"

# Resource optimization
kagent "optimize resource allocation"

# Security audit
kagent "perform security audit"

# Performance
kagent "analyze performance bottlenecks"
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Minikube Cluster                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │              Ingress (NGINX)                    │     │
│  │              todo-app.local:80                  │     │
│  └─────────────────────┬──────────────────────────┘     │
│                        │                                 │
│          ┌─────────────┴─────────────┐                   │
│          │                           │                   │
│   ┌──────▼──────┐            ┌──────▼──────┐            │
│   │  Frontend   │            │   Backend   │            │
│   │  Next.js    │            │   FastAPI   │            │
│   │  (x2)       │            │   (x2)      │            │
│   │  :3000      │            │   :4000     │            │
│   └─────────────┘            └──────┬──────┘            │
│                                     │                   │
│                            ┌────────▼────────┐          │
│                            │   PostgreSQL    │          │
│                            │   StatefulSet   │          │
│                            │   :5432         │          │
│                            └─────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Operations

### View Logs

```powershell
# Frontend logs
kubectl logs -f deployment/frontend -n phase4

# Backend logs
kubectl logs -f deployment/backend -n phase4

# Database logs
kubectl logs -f postgres-phase3-todo-chatbot-0 -n phase4
```

### Scale Application

```powershell
# Scale frontend
kubectl scale deployment/frontend --replicas=3 -n phase4

# Scale backend
kubectl scale deployment/backend --replicas=5 -n phase4

# Or use AI
kubectl-ai "scale backend to handle more load"
```

### Access Database

```powershell
# Connect to PostgreSQL
kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase4 -- psql -U phase3user todoapp

# Run queries
\dt                    # List tables
SELECT * FROM users;   # Query users
\q                     # Quit
```

### Update Deployment

```powershell
# Rebuild images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Restart deployments
kubectl rollout restart deployment/frontend -n phase4
kubectl rollout restart deployment/backend -n phase4

# Or upgrade with Helm
helm upgrade phase3 ./helm-charts/phase3-todo-chatbot -n phase4
```

### Rollback

```powershell
# Rollback Helm release
helm rollback phase3 -n phase4

# Rollback Kubernetes deployment
kubectl rollout undo deployment/frontend -n phase4
```

## 🧹 Cleanup

```powershell
# Uninstall Helm release
helm uninstall phase3 -n phase4

# Delete namespace
kubectl delete namespace phase4

# Stop Minikube
minikube stop -p phase4

# Delete profile (optional)
minikube delete -p phase4
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [PHASE4_AI_WORKFLOWS.md](./PHASE4_AI_WORKFLOWS.md) | AI-assisted deployment workflows |
| [SPEC_DRIVEN_BLUEPRINTS.md](./SPEC_DRIVEN_BLUEPRINTS.md) | Spec-driven deployment blueprints |
| [KUBERNETES_DEPLOYMENT.md](./KUBERNETES_DEPLOYMENT.md) | Detailed Kubernetes guide |
| [gordon/README.md](./gordon/README.md) | Gordon (Docker AI) documentation |
| [kubectl-ai/README.md](./kubectl-ai/README.md) | kubectl-ai documentation |
| [kagent/README.md](./kagent/README.md) | kagent documentation |
| [docker-compose/DOCKER_COMPOSE_AI.md](./docker-compose/DOCKER_COMPOSE_AI.md) | Docker Compose AI guide |

## 🐛 Troubleshooting

### Pods Not Starting

```powershell
# Check pod status
kubectl describe pod <pod-name> -n phase4

# Check events
kubectl get events -n phase4 --sort-by='.lastTimestamp'

# Or use AI
kubectl-ai "check why pods are failing"
```

### Image Pull Errors

```powershell
# Ensure Docker points to Minikube
eval $(minikube -p phase4 docker-env)

# Rebuild images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Verify images
docker images | grep phase3
```

### Database Connection Issues

```powershell
# Check database status
kubectl get pods -n phase4 | grep postgres

# Test connection
kubectl exec -it deployment/backend -n phase4 -- python -c "import psycopg2; psycopg2.connect('...')"

# Or use AI
kubectl-ai "check database connection issues"
```

## 📖 Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Docker AI Documentation](https://docs.docker.com/ai/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

## ✅ Checklist

- [ ] Prerequisites installed
- [ ] Minikube cluster running
- [ ] Docker images built
- [ ] Namespace created
- [ ] Secrets configured
- [ ] Helm chart deployed
- [ ] All pods healthy
- [ ] Application accessible
- [ ] AI tools configured (optional)

---

**Phase 4 Complete!** 🎉

Your Cloud Native Todo Chatbot is deployed with AI-assisted operations!
