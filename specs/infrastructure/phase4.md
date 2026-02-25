# Phase IV Infrastructure Specification

**Document Type:** Infrastructure Specification  
**Version:** 1.0.0  
**Stage:** Deployment  
**Project:** Todo Chatbot - Phase IV  
**Date:** 2026-02-21  

---

## Executive Summary

This specification defines the complete cloud-native infrastructure for deploying the Phase III Todo Chatbot application using Docker, Minikube, Helm, and Kubernetes. All deployments are spec-driven with zero manual coding.

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOCAL DEVELOPMENT ENVIRONMENT                    │
│                        (Docker Desktop + Minikube)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           INGRESS LAYER                                  │
│                      NGINX Ingress Controller                            │
│                    Host: todo-app.local                                  │
│                    /api/* → Backend Service                              │
│                    /*     → Frontend Service                             │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
    ┌───────────────────────────┐       ┌───────────────────────────┐
    │   FRONTEND LAYER          │       │   BACKEND LAYER           │
    │   ┌───────────────────┐   │       │   ┌───────────────────┐   │
    │   │   Next.js App     │   │       │   │   FastAPI App     │   │
    │   │   Port: 3000      │   │       │   │   Port: 3001      │   │
    │   │   Replicas: 2-10  │   │       │   │   Replicas: 2-15  │   │
    │   │   [HPA Enabled]   │   │       │   │   [HPA Enabled]   │   │
    │   └───────────────────┘   │       │   └───────────────────┘   │
    │   Health: /               │       │   Health: /health         │
    │   Resources:              │       │   Resources:              │
    │     CPU: 100m-500m        │       │     CPU: 200m-1000m       │
    │     Memory: 128Mi-512Mi   │       │     Memory: 256Mi-1Gi     │
    └───────────────────────────┘       └───────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      PostgreSQL Database                         │   │
│   │                      Image: postgres:15-alpine                   │   │
│   │                      Port: 5432                                  │   │
│   │                      Storage: 5Gi PVC                            │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Specifications

| Component | Technology | Port | Replicas | HPA |
|-----------|------------|------|----------|-----|
| Frontend | Next.js 14+ | 3000 | 2-10 | ✅ |
| Backend | FastAPI/Express | 3001 | 2-15 | ✅ |
| Database | PostgreSQL 15 | 5432 | 1 | ❌ |
| Ingress | NGINX | 80/443 | - | - |

---

## 2. Docker Specification

### 2.1 Containerization Strategy

**Build Approach:** Multi-stage Docker builds for minimal image size and security.

### 2.2 Frontend Dockerfile Specification

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS dependencies
- Install all npm packages
- Cache node_modules

# Stage 2: Builder
FROM node:20-alpine AS builder
- Copy dependencies
- Build Next.js production bundle
- Output: .next directory

# Stage 3: Production
FROM node:20-alpine AS production
- Create non-root user (UID 1001)
- Install production dependencies only
- Copy built assets from builder
- Set environment: NODE_ENV=production
- Expose port: 3000
- Health check: HTTP GET /
- CMD: npm start
```

**Image Specifications:**
- Base Image: `node:20-alpine`
- Target Size: < 250MB
- User: non-root (UID 1001)
- Port: 3000
- Health Check: HTTP GET / every 30s

### 2.3 Backend Dockerfile Specification

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS dependencies
- Install production npm packages only
- Cache node_modules

# Stage 2: Builder
FROM node:20-alpine AS builder
- Install all dependencies (including devDependencies)
- Compile TypeScript to JavaScript
- Output: dist/ directory

# Stage 3: Production
FROM node:20-alpine AS production
- Create non-root user (UID 1001)
- Copy production dependencies
- Copy compiled code from builder
- Set environment: NODE_ENV=production
- Expose port: 3001
- Health check: HTTP GET /health
- CMD: node dist/server.js
```

**Image Specifications:**
- Base Image: `node:20-alpine`
- Target Size: < 200MB
- User: non-root (UID 1001)
- Port: 3001
- Health Check: HTTP GET /health every 30s

### 2.4 Docker Compose Specification

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=http://backend:3001
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000"]
      interval: 30s
      timeout: 5s
      retries: 3
  
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - PORT=3001
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3001/health"]
      interval: 30s
      timeout: 5s
      retries: 3
  
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=todoapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 3. Minikube Specification

### 3.1 Cluster Configuration

**Minimum Requirements:**
- CPUs: 4
- Memory: 8192MB (8GB)
- Disk: 20GB
- Kubernetes Version: Latest stable

**Start Command:**
```bash
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --kubernetes-version=stable
```

### 3.2 Required Addons

| Addon | Purpose | Command |
|-------|---------|---------|
| **ingress** | NGINX Ingress Controller | `minikube addons enable ingress` |
| **metrics-server** | HPA metrics collection | `minikube addons enable metrics-server` |
| **dashboard** (optional) | Kubernetes UI | `minikube addons enable dashboard` |

### 3.3 Verification Commands

```bash
# Verify cluster status
minikube status

# Verify addons
minikube addons list | findstr ingress
minikube addons list | findstr metrics-server

# Verify kubectl context
kubectl config current-context

# Verify cluster connectivity
kubectl cluster-info
```

---

## 4. Helm Specification

### 4.1 Chart Structure

```
todo-app/
├── Chart.yaml                 # Chart metadata (v2 API)
├── values.yaml                # Default values (350+ options)
├── values-minikube.yaml       # Minikube-optimized values
├── values-production.yaml     # Production-hardened values
├── .helmignore                # Build exclusions
└── templates/
    ├── _helpers.tpl           # Template helpers
    ├── NOTES.txt              # Post-install notes
    ├── namespace.yaml         # Namespace creation
    ├── deployment-frontend.yaml
    ├── deployment-backend.yaml
    ├── service-frontend.yaml
    ├── service-backend.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── ingress.yaml
    ├── hpa-frontend.yaml
    ├── hpa-backend.yaml
    ├── pdb.yaml
    ├── serviceaccount.yaml
    ├── rbac.yaml
    ├── networkpolicy.yaml
    ├── resourcequota.yaml
    └── limitrange.yaml
```

### 4.2 Chart Metadata (Chart.yaml)

```yaml
apiVersion: v2
name: todo-app
description: Production-ready Helm chart for Todo Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - nextjs
  - kubernetes
  - cloud-native
```

### 4.3 Installation Commands

**Minikube Deployment:**
```bash
cd helm-charts/todo-app
helm install todo-app . -f values-minikube.yaml --create-namespace
```

**Production Deployment:**
```bash
helm install todo-app . -f values-production.yaml --create-namespace
```

---

## 5. Kubernetes Specification

### 5.1 Namespace Configuration

**Namespace Name:** `todo-app`

**Purpose:** Logical isolation of application resources

**Specification:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    name: todo-app
    environment: production
```

### 5.2 Deployment Specifications

#### 5.2.1 Frontend Deployment

| Property | Value |
|----------|-------|
| **Name** | todo-app-frontend |
| **Image** | phase3-frontend:latest |
| **Replicas** | 2 (min) - 10 (max) |
| **Port** | 3000 |
| **Strategy** | RollingUpdate |
| **Max Surge** | 1 |
| **Max Unavailable** | 0 |

**Pod Specification:**
```yaml
containers:
  - name: frontend
    image: phase3-frontend:latest
    ports:
      - containerPort: 3000
    env:
      - name: NODE_ENV
        value: production
      - name: PORT
        value: "3000"
      - name: NEXT_PUBLIC_API_URL
        value: http://todo-app-backend:3001
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi
    livenessProbe:
      httpGet:
        path: /
        port: 3000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 3000
      initialDelaySeconds: 10
      periodSeconds: 5
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
          - ALL
```

#### 5.2.2 Backend Deployment

| Property | Value |
|----------|-------|
| **Name** | todo-app-backend |
| **Image** | phase3-backend:latest |
| **Replicas** | 2 (min) - 15 (max) |
| **Port** | 3001 |
| **Strategy** | RollingUpdate |
| **Max Surge** | 1 |
| **Max Unavailable** | 0 |

**Pod Specification:**
```yaml
containers:
  - name: backend
    image: phase3-backend:latest
    ports:
      - containerPort: 3001
    env:
      - name: NODE_ENV
        value: production
      - name: PORT
        value: "3001"
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 1Gi
    livenessProbe:
      httpGet:
        path: /health
        port: 3001
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health
        port: 3001
      initialDelaySeconds: 10
      periodSeconds: 5
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
          - ALL
```

### 5.3 Service Specifications

#### 5.3.1 Frontend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-app-frontend
  namespace: todo-app
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/component: frontend
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
      name: http
```

#### 5.3.2 Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-app-backend
  namespace: todo-app
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/component: backend
  ports:
    - port: 8080
      targetPort: 3001
      protocol: TCP
      name: http
```

---

## 6. Horizontal Pod Autoscaler (HPA) Specification

### 6.1 Frontend HPA

| Property | Value |
|----------|-------|
| **Min Replicas** | 2 |
| **Max Replicas** | 10 |
| **Target CPU** | 70% |
| **Target Memory** | 80% |
| **Scale Down Stabilization** | 300s |
| **Scale Up Stabilization** | 0s |

**Specification:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-app-frontend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-app-frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

### 6.2 Backend HPA

| Property | Value |
|----------|-------|
| **Min Replicas** | 2 |
| **Max Replicas** | 15 |
| **Target CPU** | 60% |
| **Target Memory** | 75% |
| **Scale Down Stabilization** | 300s |
| **Scale Up Stabilization** | 0s |

**Specification:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: todo-app-backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: todo-app-backend
  minReplicas: 2
  maxReplicas: 15
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 75
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
    scaleUp:
      stabilizationWindowSeconds: 0
```

---

## 7. Ingress Specification

### 7.1 Ingress Controller

**Type:** NGINX Ingress Controller  
**Installation:** Minikube addon  
**Class Name:** `nginx`

### 7.2 Ingress Rules

| Host | Path | Backend Service | Backend Port |
|------|------|-----------------|--------------|
| todo-app.local | /api(/|$)(.*) | todo-app-backend | 8080 |
| todo-app.local | /()(.*) | todo-app-frontend | 80 |

**Specification:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: todo-app
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
spec:
  rules:
    - host: todo-app.local
      http:
        paths:
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: todo-app-backend
                port:
                  number: 8080
          - path: /()(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: todo-app-frontend
                port:
                  number: 80
```

### 7.3 Host Configuration

**Local Development:**
Add to hosts file:
- Windows: `C:\Windows\System32\drivers\etc\hosts`
- Linux/Mac: `/etc/hosts`

**Entry:**
```
<minikube-ip> todo-app.local
```

**Get Minikube IP:**
```bash
minikube ip
```

---

## 8. Resource Limits Specification

### 8.1 Resource Quota (Namespace Level)

**Purpose:** Limit total resource consumption in namespace

**Specification:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: todo-app-quota
  namespace: todo-app
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "5"
    pods: "20"
    services: "10"
    secrets: "10"
    configmaps: "10"
```

### 8.2 Limit Range (Container Level)

**Purpose:** Set default and min/max limits for containers

**Specification:**
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: todo-app-limits
  namespace: todo-app
spec:
  limits:
    - type: Container
      default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      max:
        cpu: "2"
        memory: 4Gi
      min:
        cpu: 50m
        memory: 64Mi
```

### 8.3 Container Resource Summary

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 128Mi | 512Mi |
| Backend | 200m | 1000m | 256Mi | 1Gi |
| PostgreSQL | 250m | 2000m | 256Mi | 2Gi |

---

## 9. Deployment Workflow

### 9.1 Pre-Deployment Checklist

```bash
# Verify Docker Desktop running
docker info

# Verify Minikube installed
minikube version

# Verify kubectl installed
kubectl version --client

# Verify Helm installed
helm version
```

### 9.2 Cluster Setup

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress
minikube addons enable ingress

# Enable metrics-server
minikube addons enable metrics-server

# Verify cluster
kubectl cluster-info
```

### 9.3 Image Build

```bash
# Set Minikube Docker daemon
eval $(minikube docker-env)  # Linux/Mac
# OR
minikube docker-env | Invoke-Expression  # PowerShell

# Build frontend image
docker build -t phase3-frontend:latest ./frontend

# Build backend image
docker build -t phase3-backend:latest ./backend

# Verify images
docker images | findstr phase3
```

### 9.4 Helm Installation

```bash
# Navigate to chart
cd helm-charts/todo-app

# Install with Minikube values
helm install todo-app . -f values-minikube.yaml --create-namespace

# Verify installation
helm list -n todo-app

# Check deployment status
kubectl get all -n todo-app
```

### 9.5 Post-Deployment Configuration

```bash
# Get Minikube IP
$IP = minikube ip

# Add to hosts file (PowerShell as Administrator)
Add-Content C:\Windows\System32\drivers\etc\hosts "$IP todo-app.local"

# Verify hosts entry
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "todo-app.local"
```

### 9.6 Verification

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Check HPA
kubectl get hpa -n todo-app

# Test frontend
curl http://todo-app.local

# Test backend health
curl http://todo-app.local/api/health
```

---

## 10. Acceptance Criteria

### 10.1 Docker

- [ ] Frontend image builds successfully
- [ ] Backend image builds successfully
- [ ] Image sizes within targets (< 250MB frontend, < 200MB backend)
- [ ] Health checks defined in Dockerfiles
- [ ] Non-root users configured

### 10.2 Minikube

- [ ] Cluster starts with 4 CPUs and 8GB RAM
- [ ] Ingress addon enabled
- [ ] Metrics-server addon enabled
- [ ] kubectl context configured correctly

### 10.3 Helm

- [ ] Chart passes `helm lint`
- [ ] Templates render with `helm template`
- [ ] Installation succeeds
- [ ] All resources created in correct namespace

### 10.4 Kubernetes

- [ ] All pods reach Running state
- [ ] All deployments show AVAILABLE
- [ ] Services have endpoints
- [ ] Namespace created and labeled

### 10.5 HPA

- [ ] Frontend HPA created with correct min/max
- [ ] Backend HPA created with correct min/max
- [ ] Metrics available via `kubectl top pods`
- [ ] Auto-scaling functional

### 10.6 Ingress

- [ ] Ingress resource created
- [ ] NGINX controller running
- [ ] Host routing functional
- [ ] /api/* routes to backend
- [ ] /* routes to frontend

### 10.7 Namespace

- [ ] todo-app namespace exists
- [ ] All resources in correct namespace
- [ ] Namespace properly labeled

### 10.8 Resource Limits

- [ ] ResourceQuota applied to namespace
- [ ] LimitRange applied to namespace
- [ ] Container requests/limits configured
- [ ] No resource quota violations

---

## 11. Troubleshooting Reference

### 11.1 Common Issues

| Issue | Command | Fix |
|-------|---------|-----|
| Pods not starting | `kubectl describe pod -n todo-app <pod>` | Check events |
| Image pull errors | `kubectl describe pod -n todo-app <pod>` | Verify image exists |
| HPA not working | `kubectl top pods -n todo-app` | Check metrics-server |
| Ingress 404 | `kubectl describe ingress -n todo-app` | Check ingress controller |
| Service not accessible | `kubectl get endpoints -n todo-app` | Check pod selectors |

### 11.2 Debug Commands

```bash
# View all resources
kubectl get all -n todo-app

# Describe problematic resource
kubectl describe pod -n todo-app <pod-name>

# View logs
kubectl logs -n todo-app <pod-name> -f

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n todo-app
kubectl top nodes
```

---

## 12. Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-21 | Hackathon Team | Initial specification |

---

**Document Status:** Complete  
**Next Steps:** Execute deployment per Section 9  
**PHR Location:** `history/prompts/infrastructure/`
