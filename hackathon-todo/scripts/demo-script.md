# 🎯 Hackathon Demo Script - Cloud-Native Todo App

## Demo Duration: 5-7 minutes

---

## 📋 Pre-Demo Checklist (Before Judges Arrive)

```powershell
# Ensure everything is ready
minikube status
kubectl get pods
helm list

# If not running, deploy:
.\scripts\deploy.ps1
```

---

## 🎬 Demo Flow

### 1️⃣ Introduction (30 seconds)

**Say:**
> "Welcome! Today I'll demonstrate a Cloud-Native Todo Application built with AI-Driven DevOps practices. This application follows Spec-First workflow and runs on Kubernetes."

**Show:**
- Project folder structure
- `specs/cloud-native-todo/spec.md` (Specification document)

---

### 2️⃣ Application Overview (30 seconds)

**Say:**
> "The application consists of two microservices: a Next.js frontend and a Node.js backend API, both containerized with Docker and orchestrated by Kubernetes."

**Show:**
```powershell
# Show folder structure
tree /F

# Show Dockerfiles
code backend/Dockerfile
code frontend/Dockerfile
```

---

### 3️⃣ Spec-First Workflow (1 minute)

**Say:**
> "We start with a specification document that defines all requirements, APIs, and infrastructure. This ensures consistency and enables AI-assisted code generation."

**Show:**
```powershell
# Open spec document
code specs\cloud-native-todo\spec.md

# Highlight key sections:
# - API endpoints
# - Kubernetes resources
# - Acceptance criteria
```

**Key Points:**
- ✅ Spec-driven development
- ✅ Clear API contracts
- ✅ Infrastructure as Code

---

### 4️⃣ Helm Deployment (1 minute)

**Say:**
> "We use Helm charts for packaging and deployment. This enables one-command deployment and environment consistency."

**Show:**
```powershell
# Show Helm chart structure
tree charts\todo-app

# Show values.yaml
code charts\todo-app\values.yaml

# Deploy/Upgrade
helm upgrade --install todo-app ./charts/todo-app

# Check status
helm status todo-app
helm list
```

**Key Points:**
- ✅ Single command deployment
- ✅ Environment configuration via values.yaml
- ✅ Version control and rollback capability

---

### 5️⃣ Kubernetes Resources (1 minute)

**Say:**
> "The application runs on Kubernetes with proper health checks, resource limits, and auto-scaling capabilities."

**Show:**
```powershell
# View all resources
kubectl get all

# Show deployments
kubectl get deployments

# Show pods with details
kubectl get pods -o wide

# Show services
kubectl get services

# Show HPA (Horizontal Pod Autoscaler)
kubectl get hpa
```

**Key Points:**
- ✅ Multiple replicas for high availability
- ✅ Health probes (liveness/readiness)
- ✅ Resource limits and requests
- ✅ Auto-scaling with HPA

---

### 6️⃣ AI-Driven DevOps with kubectl-ai (1.5 minutes) ⭐

**Say:**
> "Now for the exciting part - AI-Driven DevOps! Instead of memorizing complex kubectl commands, I can use natural language with kubectl-ai."

**Show:**

```powershell
# Command 1: Check pod status
kubectl-ai "show me all pods"

# Command 2: Scale backend (THE KEY DEMO!)
kubectl-ai "scale backend to 5 replicas"

# Wait a moment, then show:
kubectl get pods

# You should see 5 backend pods!

# Command 3: Check deployment status
kubectl-ai "what is the status of backend deployment"

# Command 4: View logs
kubectl-ai "show me the logs of backend pod"
```

**Key Points:**
- ✅ Natural language to Kubernetes
- ✅ No manual YAML editing
- ✅ AI understands context
- ✅ Faster operations

---

### 7️⃣ Scaling Demo (1 minute) ⭐

**Say:**
> "Let me demonstrate the scaling capability. I'll scale the backend from 2 to 5 replicas using AI commands."

**Show:**

```powershell
# Before scaling
Write-Host "Before: $(kubectl get pods -l app=backend --no-headers | Measure-Object | Select-Object -ExpandProperty Count) pods"

# AI Command
kubectl-ai "scale backend to 5 replicas"

# Watch scaling happen
kubectl get pods -w

# After scaling (in new terminal)
Write-Host "After: $(kubectl get pods -l app=backend --no-headers | Measure-Object | Select-Object -ExpandProperty Count) pods"

# Show HPA
kubectl get hpa -w
```

**Key Points:**
- ✅ Zero-downtime scaling
- ✅ Automatic load distribution
- ✅ HPA for auto-scaling

---

### 8️⃣ Live Application Demo (1 minute)

**Say:**
> "Let's see the application in action!"

**Show:**

```powershell
# Get application URL
minikube service frontend-service --url

# Or open manually
Start-Process "http://$(minikube ip):30080"
```

**Demonstrate:**
- ✅ Create a new todo
- ✅ Mark as complete
- ✅ Delete todo
- ✅ Filter (All/Active/Completed)
- ✅ Backend status indicator

---

### 9️⃣ Judges Checklist Verification (30 seconds)

**Say:**
> "Let me verify all the requirements are met."

**Show:**

```powershell
Write-Host "✓ Spec-first workflow" -ForegroundColor Green
code specs\cloud-native-todo\spec.md

Write-Host "✓ No manual YAML" -ForegroundColor Green
Write-Host "  (Helm templates auto-generated)"

Write-Host "✓ AI tool usage" -ForegroundColor Green
kubectl-ai "show me all pods"

Write-Host "✓ Helm packaging" -ForegroundColor Green
helm list

Write-Host "✓ Clean containerization" -ForegroundColor Green
docker images | Select-String "todo-"

Write-Host "✓ Working Minikube deployment" -ForegroundColor Green
kubectl get pods

Write-Host "✓ Scaling demo" -ForegroundColor Green
kubectl get pods -l app=backend
```

---

### 🔟 Conclusion (30 seconds)

**Say:**
> "To summarize, we've demonstrated:
> - Spec-First development workflow
> - Cloud-Native architecture with microservices
> - Containerization with Docker
> - Kubernetes orchestration with Helm
> - AI-Driven DevOps with kubectl-ai
> - Auto-scaling capabilities
> 
> All requirements are complete. Thank you!"

**Show:**
```powershell
# Final status
kubectl get all
helm list
```

---

## 🎯 Key Commands Quick Reference

```powershell
# Deploy
helm install todo-app ./charts/todo-app

# Scale with AI
kubectl-ai "scale backend to 5 replicas"

# Scale manually
kubectl scale deployment backend-deployment --replicas=5

# View pods
kubectl get pods

# View logs
kubectl logs -l app=backend -f

# Access app
minikube service frontend-service --url

# Cleanup
helm uninstall todo-app
```

---

## 🚨 Troubleshooting During Demo

If something goes wrong:

```powershell
# Pods not ready?
kubectl describe pod <pod-name>

# Service not accessible?
kubectl get endpoints

# Need to redeploy?
helm upgrade --install todo-app ./charts/todo-app

# Minikube issues?
minikube restart
```

---

## 📊 Success Metrics to Show

```powershell
# Deployment time
Measure-Command { helm install todo-app ./charts/todo-app }

# Scaling time
Measure-Command { kubectl scale deployment backend-deployment --replicas=5 }

# Pod count
kubectl get pods --no-headers | Measure-Object | Select-Object -ExpandProperty Count

# Backend health
curl http://$(minikube ip):3001/health
```

---

## ✨ Demo Tips

1. **Practice the flow** - Rehearse 2-3 times
2. **Have backup screenshots** - In case of live issues
3. **Keep terminals ready** - Pre-open command windows
4. **Show enthusiasm** - Especially during AI commands
5. **Emphasize key points** - Spec-first, AI-driven, Cloud-native

---

**Good Luck! 🚀**
