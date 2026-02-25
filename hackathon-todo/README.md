# ☁️ Cloud-Native Todo App

**AI-Driven DevOps | Spec-First Workflow | Kubernetes | Helm**

A Cloud-Native Todo application demonstrating modern DevOps practices with AI-assisted operations, built for hackathon competitions.

---

## 🎯 Features

- **Frontend**: Next.js 14+ with TypeScript & Tailwind CSS
- **Backend**: Node.js + Express REST API
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes via Minikube
- **Package Manager**: Helm charts
- **AI Operations**: kubectl-ai integration
- **Auto-Scaling**: Horizontal Pod Autoscaler (HPA)

---

## 📋 Judges Checklist

| Requirement | Status |
|-------------|--------|
| Spec-first workflow | ✅ |
| No manual YAML | ✅ |
| AI tool usage | ✅ |
| Helm packaging | ✅ |
| Clean containerization | ✅ |
| Working Minikube deployment | ✅ |
| Scaling demo | ✅ |

---

## 🚀 Quick Start

### Prerequisites

Install these tools:

```powershell
# Windows (using Chocolatey)
choco install docker-desktop minikube kubernetes-cli helm git

# kubectl-ai (optional but recommended)
# Download from: https://github.com/sozercan/kubectl-ai/releases
```

### One-Command Deployment

```powershell
# Navigate to project
cd "E:\All Phases\Phase_3\hackathon-todo"

# Run deployment script
.\scripts\deploy.ps1
```

### Manual Deployment

```powershell
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Build Docker images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# 3. Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 4. Deploy with Helm
helm install todo-app ./charts/todo-app

# 5. Verify
kubectl get pods
kubectl get services

# 6. Access application
minikube service frontend-service --url
# Or: http://<minikube-ip>:30080
```

---

## 🤖 AI-Driven Commands

### Install kubectl-ai

Download from: https://github.com/sozercan/kubectl-ai

### Example Commands

```bash
# Scale backend (KEY DEMO COMMAND!)
kubectl-ai "scale backend to 5 replicas"

# Show all pods
kubectl-ai "show me all pods"

# Check deployment status
kubectl-ai "what is the status of backend deployment"

# View logs
kubectl-ai "show me the logs of backend pod"

# Debug issues
kubectl-ai "why is backend pod crashing"
```

---

## 📊 Scaling Demo

### Manual Scaling

```powershell
# Scale to 5 replicas
kubectl scale deployment backend-deployment --replicas=5

# Verify
kubectl get pods

# Scale back
kubectl scale deployment backend-deployment --replicas=2
```

### Auto Scaling (HPA)

```powershell
# Watch HPA
kubectl get hpa -w

# HPA automatically scales based on:
# - CPU utilization (target: 50%)
# - Memory utilization (target: 70%)
# - Min replicas: 2
# - Max replicas: 10
```

---

## 🏗️ Project Structure

```
hackathon-todo/
├── specs/
│   └── cloud-native-todo/
│       └── spec.md              # Specification document
├── frontend/
│   ├── src/app/
│   │   └── page.tsx             # Todo UI
│   ├── Dockerfile               # Frontend container
│   └── package.json
├── backend/
│   ├── src/
│   │   └── server.ts            # Express API
│   ├── Dockerfile               # Backend container
│   └── package.json
├── charts/
│   └── todo-app/                # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── hpa.yaml
│           └── configmap.yaml
├── k8s/                         # Standalone K8s manifests
│   ├── deployments/
│   ├── services/
│   └── hpa/
├── scripts/
│   ├── deploy.ps1               # Deployment script
│   ├── demo-script.md           # Judges demo guide
│   └── README.md                # Detailed docs
└── README.md                    # This file
```

---

## 🔧 Useful Commands

### Deployment

```powershell
# Deploy
helm install todo-app ./charts/todo-app

# Upgrade
helm upgrade todo-app ./charts/todo-app

# Uninstall
helm uninstall todo-app
```

### Monitoring

```powershell
# View pods
kubectl get pods

# View services
kubectl get services

# View deployments
kubectl get deployments

# View HPA
kubectl get hpa

# View logs
kubectl logs -l app=backend -f
kubectl logs -l app=frontend -f

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh
```

### Cleanup

```powershell
# Remove application
helm uninstall todo-app

# Stop Minikube
minikube stop

# Delete cluster
minikube delete
```

---

## 🎯 API Endpoints

### Backend (`http://localhost:3001`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/todos` | GET | Get all todos |
| `/api/todos` | POST | Create new todo |
| `/api/todos/:id` | GET | Get single todo |
| `/api/todos/:id` | PUT | Update todo |
| `/api/todos/:id` | DELETE | Delete todo |
| `/api/todos/completed/all` | DELETE | Delete all completed |
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |

---

## 📈 Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Frontend       │  NodePort: 30080
│  (Next.js)      │  Replicas: 2
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend        │  ClusterIP
│  (Express)      │  Replicas: 2-10 (auto-scale)
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  In-Memory      │
│  Storage        │
└─────────────────┘
```

---

## 🎬 Demo Guide

For detailed judges presentation, see:

- **Demo Script**: [`scripts/demo-script.md`](scripts/demo-script.md)
- **Deployment Guide**: [`scripts/README.md`](scripts/README.md)

### Quick Demo Flow

1. **Start**: `minikube start`
2. **Deploy**: `helm install todo-app ./charts/todo-app`
3. **Verify**: `kubectl get pods`
4. **AI Scale**: `kubectl-ai "scale backend to 5 replicas"`
5. **Check**: `kubectl get pods` (show 5 backend pods)
6. **Access**: Open `http://<minikube-ip>:30080`
7. **Test**: Create/delete todos in UI

---

## 🏆 Hackathon Highlights

### Why This Project Wins

1. **Spec-First Workflow** - Requirements defined before code
2. **AI-Driven DevOps** - Natural language Kubernetes operations
3. **Cloud-Native** - Microservices, containers, orchestration
4. **Auto-Scaling** - HPA for automatic resource management
5. **Production-Ready** - Health checks, resource limits, proper logging
6. **One-Click Deploy** - Helm charts for consistent deployments

---

## 📝 License

MIT License - Built for Hackathon Competition

---

## 🙏 Acknowledgments

- **Next.js** - React Framework
- **Tailwind CSS** - Utility-first CSS
- **Kubernetes** - Container Orchestration
- **Helm** - Kubernetes Package Manager
- **kubectl-ai** - AI-powered kubectl plugin

---

**Happy Coding! 🚀**

For questions or issues, refer to `scripts/README.md` or the spec document at `specs/cloud-native-todo/spec.md`.
