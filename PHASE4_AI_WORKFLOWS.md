# Phase 4 - AI-Assisted Deployment Workflows

## Overview

Phase 4 introduces AI-assisted deployment workflows for the Todo Chatbot application using:
- **Gordon** (Docker AI) for intelligent container operations
- **kubectl-ai** for AI-assisted Kubernetes management
- **kagent** for advanced cluster optimization
- **Spec-Driven Development** for infrastructure automation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 4 AI-Assisted Stack                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Gordon     │  │  kubectl-ai  │  │    kagent    │          │
│  │  (Docker AI) │  │   (K8s AI)   │  │  (Cluster AI)│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  Minikube K8s   │                            │
│                  │    Cluster      │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐             │
│  │  Frontend   │  │   Backend   │  │  PostgreSQL │             │
│  │  Next.js    │  │   FastAPI   │  │   Stateful  │             │
│  │  (x2)       │  │   (x2)      │  │   Set       │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Spec-Driven Development Workflow

### Phase 4 Blueprint

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Write     │ -> │   Generate  │ -> │   Break     │ -> │  Implement  │
│   Spec      │    │   Plan      │    │   Tasks     │    │  via AI     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼
 Define K8s         Create K8s        Create AI          Execute AI
 Requirements       Architecture      Tasks              Commands
```

## Quick Start

### Option 1: Fully Automated (Recommended)

```powershell
# Run the complete deployment script
.\deploy-all.bat
```

### Option 2: Step-by-Step with AI Assistance

```powershell
# Step 1: Use Gordon for Docker operations
.\gordon\gordon-ai.bat

# Step 2: Use kubectl-ai for Kubernetes operations
.\kubectl-ai\kubectl-ai-commands.bat

# Step 3: Use kagent for cluster optimization
.\kagent\kagent-commands.bat
```

### Option 3: Manual with AI Commands

```powershell
# Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4

# Build images with Gordon assistance
docker ai "Build optimized images for Next.js and FastAPI"

# Deploy with kubectl-ai
kubectl-ai "create namespace phase4"
kubectl-ai "deploy postgresql with 5Gi storage"
kubectl-ai "deploy backend with 2 replicas"
kubectl-ai "deploy frontend with 2 replicas"

# Optimize with kagent
kagent "optimize resource allocation"
kagent "analyze cluster health"
```

## AI Tool Integration

### Gordon (Docker AI) Commands

```bash
# Check Gordon capabilities
docker ai "What can you do?"

# Build optimized images
docker ai "Build production Docker images for 3-tier application"

# Optimize Dockerfiles
docker ai "Optimize backend/Dockerfile for production"

# Security scanning
docker ai "Scan phase3-backend:latest for vulnerabilities"

# Troubleshooting
docker ai "Why is my container failing to start?"
```

### kubectl-ai Commands

```bash
# Deployment
kubectl-ai "deploy the todo frontend with 2 replicas"
kubectl-ai "deploy postgresql for todo app"

# Scaling
kubectl-ai "scale the backend to handle more load"
kubectl-ai "enable HPA for frontend and backend"

# Troubleshooting
kubectl-ai "check why the pods are failing"
kubectl-ai "analyze backend connection issues"

# Optimization
kubectl-ai "optimize resource allocation"
kubectl-ai "set resource limits for all pods"
```

### kagent Commands

```bash
# Cluster health
kagent "analyze the cluster health"
kagent "generate health report for phase4"

# Resource optimization
kagent "optimize resource allocation"
kagent "right-size pod resources"

# Security
kagent "perform security audit"
kagent "check pod security compliance"

# Performance
kagent "analyze performance bottlenecks"
kagent "recommend scaling strategies"
```

## Complete Deployment Workflow

### Step 1: Infrastructure Setup

```bash
# Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4

# Enable addons
minikube addons enable ingress --profile phase4
minikube addons enable metrics-server --profile phase4

# Verify cluster
kubectl get nodes
```

### Step 2: Containerization with Gordon

```bash
# Configure Docker for Minikube
eval $(minikube -p phase4 docker-env)

# Ask Gordon for build optimization
docker ai "What are best practices for building production images?"

# Build images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Scan for vulnerabilities
docker ai "Scan images for security issues"
```

### Step 3: Deploy with kubectl-ai

```bash
# Create namespace
kubectl-ai "create namespace phase4"

# Create secrets
kubectl-ai "create secret phase3-secrets with database credentials"

# Deploy database
kubectl-ai "deploy postgresql:15-alpine with 5Gi storage in phase4"

# Deploy backend
kubectl-ai "deploy phase3-backend:latest with 2 replicas"

# Deploy frontend
kubectl-ai "deploy phase3-frontend:latest with 2 replicas"

# Create services
kubectl-ai "create services for frontend and backend"

# Setup ingress
kubectl-ai "create ingress for todo-app.local"
```

### Step 4: Optimize with kagent

```bash
# Analyze deployment
kagent "analyze the deployment health"

# Get optimization recommendations
kagent "recommend optimizations for phase4"

# Apply recommendations
kagent "apply resource optimizations"

# Set up monitoring
kagent "configure monitoring for phase4"
```

### Step 5: Verify and Access

```bash
# Check status
kubectl get all -n phase4

# AI verification
kubectl-ai "verify deployment is healthy"

# Access application
minikube service frontend-service -n phase4 --profile phase4
```

## Spec-Driven Infrastructure

### Infrastructure Spec Template

```yaml
# specs/phase4/infrastructure-spec.yaml
apiVersion: v1
kind: Spec
metadata:
  name: phase4-infrastructure
  version: 1.0.0

spec:
  cluster:
    type: minikube
    profile: phase4
    resources:
      memory: 6144
      cpus: 4
      disk: 20g
  
  applications:
    frontend:
      image: phase3-frontend:latest
      replicas: 2
      port: 3000
      autoscaling:
        enabled: true
        min: 2
        max: 10
        targetCPU: 70
    
    backend:
      image: phase3-backend:latest
      replicas: 2
      port: 4000
      autoscaling:
        enabled: true
        min: 2
        max: 15
        targetCPU: 60
    
    database:
      image: postgres:15-alpine
      storage: 5Gi
      port: 5432

  security:
    networkPolicies: enabled
    podSecurityStandards: restricted
    secretsEncryption: enabled

  monitoring:
    metricsServer: enabled
    hpa: enabled
    healthChecks: enabled
```

### Generate Plan from Spec

```bash
# Use AI to generate deployment plan from spec
kubectl-ai "generate deployment plan from specs/phase4/infrastructure-spec.yaml"

# Review and apply
kubectl apply -f generated-manifests/
```

## Troubleshooting with AI

### Common Issues and AI Commands

| Issue | AI Command |
|-------|------------|
| Pods not starting | `kubectl-ai "check why pods are failing"` |
| Database connection | `kubectl-ai "debug database connectivity"` |
| High latency | `kagent "analyze performance bottlenecks"` |
| Resource issues | `kubectl-ai "optimize resource allocation"` |
| Image pull errors | `docker ai "fix image pull issues"` |
| Service not accessible | `kubectl-ai "debug service endpoint"` |

### AI Troubleshooting Workflow

```bash
# 1. Identify the issue
kubectl-ai "what's wrong with my deployment?"

# 2. Get detailed analysis
kagent "perform root cause analysis"

# 3. Get recommendations
kubectl-ai "how do I fix this?"

# 4. Apply fix
kubectl-ai "apply the recommended fix"

# 5. Verify
kubectl-ai "verify the fix worked"
```

## Best Practices

### 1. AI-Assisted Operations

- Always review AI-generated manifests before applying
- Use AI for complex operations and troubleshooting
- Combine AI commands with standard kubectl for precision
- Keep AI tools updated

### 2. Security

```bash
# Ask AI for security recommendations
docker ai "What security best practices should I follow?"
kubectl-ai "add security context to all deployments"
kagent "perform security audit"
```

### 3. Resource Optimization

```bash
# Right-size resources
kagent "recommend resource requests and limits"
kubectl-ai "apply resource optimization"
```

### 4. Monitoring

```bash
# Set up monitoring
kubectl-ai "enable comprehensive monitoring"
kagent "configure alerts for critical issues"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Phase 4 AI-Assisted Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Minikube
        uses: manusa/actions-setup-minikube@v2
        with:
          memory: '6144'
          cpus: '4'
      
      - name: Build Images
        run: |
          eval $(minikube docker-env)
          docker build -t phase3-frontend:latest ./frontend
          docker build -t phase3-backend:latest ./backend
      
      - name: Deploy with kubectl-ai
        run: |
          kubectl-ai "deploy the todo app with 2 replicas each"
      
      - name: Verify with kagent
        run: |
          kagent "verify deployment health"
```

## Resources

- [Gordon Documentation](./gordon/README.md)
- [kubectl-ai Documentation](./kubectl-ai/README.md)
- [kagent Documentation](./kagent/README.md)
- [Kubernetes Deployment Guide](./KUBERNETES_DEPLOYMENT.md)
- [Helm Chart Documentation](./helm-charts/phase3-todo-chatbot/README.md)

---

**Phase 4 Complete!** 🎉

Your Todo Chatbot is now deployed with AI-assisted operations using Gordon, kubectl-ai, and kagent.
