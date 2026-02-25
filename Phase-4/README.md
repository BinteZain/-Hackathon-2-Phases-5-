# Phase IV - Cloud Native Todo Chatbot

**Complete Kubernetes-Native Deployment with AI-Assisted DevOps**

---

## 📁 Directory Structure

```
Phase-4/
├── specs/                      # Infrastructure specifications
│   ├── phase4-deployment.md    # Complete K8s architecture
│   ├── phase4-execution-plan.md # Step-by-step deployment tasks
│   └── infrastructure/         # Additional specs
│
├── backend/                    # Backend containerization
│   ├── Dockerfile              # Multi-stage production build
│   ├── .dockerignore           # Build context exclusions
│   └── (source from hackathon-todo/backend/)
│
├── frontend/                   # Frontend containerization
│   ├── Dockerfile              # Multi-stage production build
│   ├── .dockerignore           # Build context exclusions
│   └── (source from hackathon-todo/frontend/)
│
├── docker/                     # Docker configurations
│   ├── docker-compose.yml      # Local development stack
│   └── (additional Docker configs)
│
├── helm/                       # Kubernetes Helm chart
│   ├── todo-app/
│   │   ├── Chart.yaml          # Chart metadata
│   │   ├── values.yaml         # Default values (350+ options)
│   │   ├── values-minikube.yaml # Local dev optimized
│   │   ├── values-production.yaml # Production hardened
│   │   ├── templates/          # 27 Kubernetes manifests
│   │   │   ├── deployment-*.yaml
│   │   │   ├── service-*.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── secrets.yaml
│   │   │   ├── ingress.yaml
│   │   │   ├── hpa-*.yaml
│   │   │   ├── pdb.yaml
│   │   │   ├── rbac-*.yaml
│   │   │   ├── networkpolicy-*.yaml
│   │   │   ├── servicemonitor.yaml
│   │   │   ├── prometheusrule.yaml
│   │   │   ├── grafana-dashboard.yaml
│   │   │   └── NOTES.txt
│   │   └── .helmignore
│   └── ENHANCED_INFRASTRUCTURE.md
│
└── demo-script.md              # Hackathon presentation script
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Docker Desktop
https://www.docker.com/products/docker-desktop

# Install Minikube
choco install minikube  # Windows

# Install Helm
choco install kubernetes-helm

# Install kubectl
choco install kubernetes-cli
```

### 2. Local Development (Docker Compose)

```bash
cd docker

# Start all services
docker-compose up -d

# Access application
start http://localhost:3000

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Kubernetes Deployment (Minikube)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Deploy with Helm
cd helm/todo-app
helm install todo-app . -f values-minikube.yaml --create-namespace

# Configure hosts
$IP = minikube ip
Add-Content C:\Windows\System32\drivers\etc\hosts "$IP todo-app.local"

# Access application
start http://todo-app.local
```

---

## 📋 Specifications

### Infrastructure Spec (`specs/phase4-deployment.md`)

Complete Kubernetes architecture documentation:

- Architecture diagram
- Component breakdown (Frontend, Backend, Database)
- Containerization strategy
- Kubernetes objects (20+ resource types)
- Namespace strategy
- Resource limits
- Service exposure
- Ingress configuration
- Health probes
- Horizontal Pod Autoscaling
- Helm chart structure
- Environment variables mapping
- Deployment workflow

### Execution Plan (`specs/phase4-execution-plan.md`)

74 testable tasks across 5 phases:

| Phase | Tasks | Duration |
|-------|-------|----------|
| A – Dockerization | 8 | 2-3 hours |
| B – Helm Chart Creation | 20 | 3-4 hours |
| C – Kubernetes Deployment | 16 | 2-3 hours |
| D – Scaling & Optimization | 15 | 2-3 hours |
| E – Observability & Debugging | 15 | 2-3 hours |

---

## 🐳 Docker Features

### Backend Dockerfile

```dockerfile
# 3-stage build
Stage 1: Dependencies (production npm packages)
Stage 2: Builder (TypeScript compilation)
Stage 3: Production (minimal runtime)

# Results:
- Image size: 204MB
- Non-root user (UID 1001)
- Health check on /health
- Read-only filesystem where possible
```

### Frontend Dockerfile

```dockerfile
# 3-stage build
Stage 1: Dependencies (all packages)
Stage 2: Builder (Next.js production build)
Stage 3: Runner (production runtime)

# Results:
- Image size: ~250MB
- Non-root user (UID 1001)
- Health check on /
- Optimized static assets
```

### Docker Compose

```yaml
services:
  frontend:  # Next.js on port 3000
  backend:   # Express on port 3001
  # Network: phase3-network
  # Health checks: Both services
  # Resource limits: Configured
```

---

## ☸️ Helm Chart Features

### Deployment Strategies

| Strategy | Command | Use Case |
|----------|---------|----------|
| **Rolling** (default) | `helm install todo-app .` | Regular updates |
| **Blue-Green** | `--set global.deploymentStrategy=blue-green` | Zero-downtime, instant rollback |
| **Canary** | `--set global.canaryPercentage=10` | Gradual rollout |

### Enhanced Security

```yaml
# RBAC
- ServiceAccount per component
- Role with minimal permissions
- Optional cluster-wide access

# NetworkPolicies
- Default deny all
- Allow ingress from NGINX
- Allow frontend → backend
- Allow DNS egress
- Allow HTTPS outbound
```

### Monitoring Stack

```yaml
# Prometheus Integration
- ServiceMonitors for auto-discovery
- 8 alerting rules (CPU, Memory, Crashes, etc.)
- 30s scrape interval

# Grafana Dashboards
- 8 panels (pods, CPU, memory, HPA, deployments)
- Auto-imported via ConfigMap
- Real-time metrics
```

### Resource Management

```yaml
# Pod Disruption Budgets
- minAvailable: 1 (frontend & backend)
- Ensures HA during maintenance

# Resource Quotas
- Namespace-level limits
- Prevents resource exhaustion

# Limit Ranges
- Default container limits
- Min/max constraints
```

---

## 🎯 Key Commands

### Scaling

```bash
# Manual scale
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Auto-scale (HPA)
kubectl get hpa -n todo-app --watch
```

### Rolling Update

```bash
# Upgrade image
helm upgrade todo-app . --set frontend.image.tag=v1.1.0

# Monitor rollout
kubectl rollout status deployment/todo-app-frontend -n todo-app

# Rollback
helm rollback todo-app -n todo-app
```

### Blue-Green Switch

```bash
# Deploy to green
helm upgrade todo-app . --set global.deploymentStrategy=blue-green

# Switch traffic to green
helm upgrade todo-app . \
  --set global.deploymentStrategy=blue-green \
  --set global.activeEnvironment=green
```

### Canary Rollout

```bash
# Start with 10% traffic
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=10

# Increase to 50%
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=50

# Full rollout
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=100
```

### Monitoring Access

```bash
# Prometheus
kubectl port-forward svc/prometheus-operated -n monitoring 9090

# Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000
# Username: admin
# Password: $(kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d)
```

---

## 🎨 UI Features

The frontend includes:

- ✨ Glassmorphism design
- 🌈 Animated gradient background
- 💫 Floating particle bubbles
- 🔵 Neon glow effects
- 🎭 Smooth Framer Motion animations
- 🌓 Dark/light toggle
- 📱 Fully responsive layout
- ⚡ Real-time backend status

---

## 🤖 AI-Assisted DevOps

### kubectl-ai Commands

```bash
# Natural language K8s operations
kubectl-ai "Show me the deployment status"
kubectl-ai "How do I scale frontend to 5 replicas?"
kubectl-ai "Check if all pods are healthy"
kubectl-ai "Why is my pod crashing?"
```

### Kagent Health Analysis

```bash
# Analyze cluster health
kagent analyze --namespace todo-app

# Get recommendations
kagent recommend --namespace todo-app

# Health summary
kagent health --namespace todo-app
```

---

## 📊 Monitoring & Alerts

### Pre-configured Alerts

| Alert | Threshold | Severity |
|-------|-----------|----------|
| PodCrashLooping | >0 restarts/5m | Critical |
| HighMemoryUsage | >85% | Warning |
| HighCPUUsage | >80% | Warning |
| ServiceDown | 2m downtime | Critical |
| IngressHighErrorRate | >5% errors | Critical |
| HPAMaxReplicasReached | At max replicas | Warning |

### Dashboard Panels

1. Running Pods
2. Average CPU Usage
3. Average Memory Usage
4. Pod Restarts
5. CPU by Container
6. Memory by Container
7. HPA Replicas
8. Deployment Replicas

---

## 🔧 Troubleshooting

### Common Issues

```bash
# Pod not starting
kubectl describe pod -n todo-app <pod-name>
kubectl logs -n todo-app <pod-name> --previous

# Image pull failure
kubectl describe pod -n todo-app <pod-name> | grep -A 5 Events

# OOMKilled (exit 137)
kubectl top pods -n todo-app
helm upgrade todo-app . --set frontend.resources.limits.memory=1Gi

# Probe failures
helm upgrade todo-app . --set frontend.probes.liveness.initialDelaySeconds=60

# Network issues
kubectl exec -it -n todo-app <pod-name> -- wget http://backend:3001/health
```

### Debug Script

```powershell
# Save as debug-pods.ps1
param([string]$Namespace = "todo-app", [string]$PodName = "")

kubectl get pods -n $Namespace
kubectl describe pod -n $Namespace $PodName
kubectl logs -n $Namespace $PodName --previous
kubectl get events -n $Namespace --sort-by='.lastTimestamp'
kubectl top pods -n $Namespace $PodName
```

---

## 📚 Documentation

| Document | Location |
|----------|----------|
| Infrastructure Spec | `specs/phase4-deployment.md` |
| Execution Plan | `specs/phase4-execution-plan.md` |
| Enhanced Features | `helm/ENHANCED_INFRASTRUCTURE.md` |
| Docker Guide | `hackathon-todo/DOCKER_DEPLOYMENT.md` |
| Helm Guide | `hackathon-todo/helm-charts/HELM_DEPLOYMENT_GUIDE.md` |
| Minikube Commands | `hackathon-todo/helm-charts/MINIKUBE_COMMANDS.md` |
| Pod Debugging | `hackathon-todo/helm-charts/POD_CRASH_DEBUGGING.md` |
| Demo Script | `demo-script.md` |

---

## 🎤 Demo Presentation

See `demo-script.md` for the complete 10-12 minute hackathon presentation including:

- Architecture explanation
- Live scaling demo
- kubectl-ai demonstration
- Kagent health analysis
- UI walkthrough
- Closing impact statement

---

## ✅ Acceptance Criteria

- [ ] Docker images build successfully
- [ ] Docker Compose starts all services
- [ ] Helm chart passes linting
- [ ] All pods reach Running state
- [ ] HPA configured and functional
- [ ] Ingress routing works correctly
- [ ] Health probes passing
- [ ] Network policies enforced
- [ ] RBAC configured properly
- [ ] Monitoring stack operational
- [ ] Grafana dashboard accessible
- [ ] Blue-Green switching works
- [ ] Canary deployment functional
- [ ] UI visually impressive

---

**Version:** 2.0.0  
**Last Updated:** 2026-02-21  
**Compatible:** Kubernetes 1.25+, Helm 3+, Minikube 1.32+
