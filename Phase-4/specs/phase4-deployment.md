# Phase IV: Cloud Native Deployment Specification

**Document Type:** Infrastructure Specification  
**Version:** 1.0.0  
**Stage:** Deployment  
**Hackathon:** Todo Chatbot - Phase IV  
**Date:** 2026-02-21  

---

## Executive Summary

This specification defines the complete cloud-native deployment architecture for the Phase III Todo Chatbot application using Kubernetes, Helm, Minikube, and modern GitOps practices. The deployment targets local development environments using Docker Desktop and Minikube while maintaining production parity.

---

## 1. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOCAL DEVELOPMENT ENVIRONMENT                      │
│                              (Docker Desktop + Minikube)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INGRESS LAYER                                   │
│                         (NGINX Ingress Controller)                           │
│                    Host: todo-app.local                                      │
│                    /api/* → Backend Service                                  │
│                    /*     → Frontend Service                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌──────────────────────────────┐      ┌──────────────────────────────┐
│    FRONTEND LAYER            │      │     BACKEND LAYER            │
│  ┌────────────────────────┐  │      │  ┌────────────────────────┐  │
│  │  Next.js Application   │  │      │  │  FastAPI Application   │  │
│  │  Port: 3000            │  │      │  │  Port: 4000            │  │
│  │  Replicas: 2-10 (HPA)  │  │      │  │  Replicas: 2-15 (HPA)  │  │
│  │  Resource Limits:      │  │      │  │  Resource Limits:      │  │
│  │    CPU: 500m           │  │      │  │    CPU: 1000m          │  │
│  │    Memory: 512Mi       │  │      │  │    Memory: 1Gi         │  │
│  └────────────────────────┘  │      │  └────────────────────────┘  │
│  Health Probes:              │      │  Health Probes:              │
│    Liveness: / (30s)         │      │    Liveness: /health (30s)   │
│    Readiness: / (10s)        │      │    Readiness: /health (10s)  │
└──────────────────────────────┘      └──────────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL Database                               │   │
│  │                    Image: postgres:15-alpine                         │   │
│  │                    Port: 5432                                        │   │
│  │                    Storage: 5Gi PVC (ReadWriteOnce)                  │   │
│  │                    Resource Limits:                                  │   │
│  │                      CPU: 2000m                                      │   │
│  │                      Memory: 2Gi                                     │   │
│  │                    Health Probes:                                    │   │
│  │                      Liveness: tcpSocket:5432 (60s)                  │   │
│  │                      Readiness: tcpSocket:5432 (30s)                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SUPPORTING SERVICES                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │  ConfigMaps      │  │     Secrets      │  │  ServiceAccount (RBAC)   │  │
│  │  - App Config    │  │  - DB Creds      │  │  - API Access Control    │  │
│  │  - Env Vars      │  │  - Auth Keys     │  │  - Namespace Isolation   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### 2.1 Frontend (Next.js)

| Attribute | Value |
|-----------|-------|
| **Framework** | Next.js 14+ |
| **Node Version** | 18-alpine |
| **Port** | 3000 |
| **Build Command** | `npm run build` |
| **Start Command** | `npm start` |
| **Base Image** | `node:18-alpine` |
| **Build Strategy** | Multi-stage Docker build |
| **Security Context** | Non-root user (UID 1000) |

**Environment Variables:**
```yaml
NODE_ENV: production
NEXT_PUBLIC_API_URL: http://backend:4000/api/v1
PORT: 3000
HOSTNAME: 0.0.0.0
```

### 2.2 Backend (FastAPI)

| Attribute | Value |
|-----------|-------|
| **Framework** | FastAPI |
| **Python Version** | 3.11-slim |
| **Port** | 4000 |
| **ASGI Server** | Uvicorn |
| **Base Image** | `python:3.11-slim` |
| **Build Strategy** | Multi-stage Docker build |
| **Security Context** | Non-root user (UID 1000) |
| **Migrations** | Alembic (auto-run on startup) |

**Environment Variables:**
```yaml
DATABASE_URL: postgresql://user:password@postgres:5432/todoapp
BETTER_AUTH_SECRET: <generated-secret>
PYTHON_ENV: production
LOG_LEVEL: INFO
PORT: 4000
```

### 2.3 Database (PostgreSQL)

| Attribute | Value |
|-----------|-------|
| **Image** | `postgres:15-alpine` |
| **Port** | 5432 |
| **Default Database** | todoapp |
| **Data Directory** | `/var/lib/postgresql/data/pgdata` |
| **Persistence** | 5Gi PVC |
| **Security Context** | Non-root user (UID 999) |

---

## 3. Containerization Strategy

### 3.1 Multi-Stage Build Pattern

All components use multi-stage Docker builds to minimize image size and attack surface:

```dockerfile
# Stage 1: Builder
FROM <base-image>:<version> AS builder
WORKDIR /app
COPY dependencies
RUN install dependencies
COPY source
RUN build

# Stage 2: Runtime
FROM <base-image>:<version>-slim AS runtime
WORKDIR /app
RUN create non-root user
COPY --from=builder /app /app
COPY --from=builder dependencies
USER appuser
EXPOSE <port>
HEALTHCHECK ...
CMD [...]
```

### 3.2 Image Registry Strategy

| Environment | Registry | Image Tag Strategy |
|-------------|----------|-------------------|
| **Local/Minikube** | Docker Desktop | `latest`, `dev-{date}` |
| **Production** | Docker Hub / GHCR | Semantic versioning `v1.0.0` |

### 3.3 Image Optimization

- Use Alpine-based images where possible
- Multi-stage builds to exclude build tools
- Layer caching optimization (dependencies first)
- No secrets baked into images

---

## 4. Kubernetes Objects Required

### 4.1 Core Objects

| Object Kind | Count | Purpose |
|-------------|-------|---------|
| `Namespace` | 1 | Isolation: `phase3` |
| `Deployment` | 3 | Frontend, Backend, PostgreSQL |
| `Service` | 3 | ClusterIP services for each component |
| `ConfigMap` | 2 | Application configuration |
| `Secret` | 1 | Sensitive data (DB creds, auth keys) |
| `PersistentVolumeClaim` | 1 | Database storage |
| `ServiceAccount` | 1 | RBAC identity |
| `Role` | 1 | Namespace-scoped permissions |
| `RoleBinding` | 1 | Bind SA to Role |

### 4.2 Advanced Objects

| Object Kind | Count | Purpose |
|-------------|-------|---------|
| `Ingress` | 1 | External access routing |
| `HorizontalPodAutoscaler` | 2 | Auto-scaling (Frontend, Backend) |
| `PodDisruptionBudget` | 2 | High availability |
| `NetworkPolicy` | 1 | Pod-to-pod traffic control |
| `ResourceQuota` | 1 | Namespace resource limits |
| `LimitRange` | 1 | Default container limits |

---

## 5. Namespace Strategy

### 5.1 Namespace Definition

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: phase3
  labels:
    name: phase3
    environment: local
    managed-by: helm
```

### 5.2 Resource Quota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: phase3-quota
  namespace: phase3
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

### 5.3 Limit Range

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: phase3-limits
  namespace: phase3
spec:
  limits:
  - default:
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
    type: Container
```

---

## 6. Resource Limits

### 6.1 Frontend Resources

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 6.2 Backend Resources

```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

### 6.3 PostgreSQL Resources

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### 6.4 Resource Justification

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit | Rationale |
|-----------|-------------|-----------|----------------|--------------|-----------|
| Frontend | 100m | 500m | 128Mi | 512Mi | Next.js SSR requires moderate resources |
| Backend | 200m | 1000m | 256Mi | 1Gi | FastAPI + DB connections + AI processing |
| PostgreSQL | 250m | 2000m | 256Mi | 2Gi | Database needs memory for caching |

---

## 7. Service Exposure Strategy

### 7.1 Service Types

| Service | Type | Port | Target Port | Selector |
|---------|------|------|-------------|----------|
| `frontend` | ClusterIP | 80 | 3000 | `app: frontend` |
| `backend` | ClusterIP | 8080 | 4000 | `app: backend` |
| `postgres` | ClusterIP | 5432 | 5432 | `app: postgres` |

### 7.2 Service Definitions

```yaml
# Frontend Service
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: phase3
  labels:
    app: frontend
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
      name: http
  selector:
    app: frontend

# Backend Service
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: phase3
  labels:
    app: backend
spec:
  type: ClusterIP
  ports:
    - port: 8080
      targetPort: 4000
      protocol: TCP
      name: http
  selector:
    app: backend

# PostgreSQL Service
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: phase3
  labels:
    app: postgres
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
      protocol: TCP
      name: postgres
  selector:
    app: postgres
```

### 7.3 Internal DNS Resolution

Services are accessible within the namespace via:
- `frontend.phase3.svc.cluster.local`
- `backend.phase3.svc.cluster.local`
- `postgres.phase3.svc.cluster.local`

Or short form within same namespace:
- `frontend`
- `backend`
- `postgres`

---

## 8. Ingress Configuration

### 8.1 Ingress Controller

- **Type:** NGINX Ingress Controller
- **Installation:** Via Minikube addon or Helm
- **Class:** `nginx`

### 8.2 Ingress Rules

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phase3-ingress
  namespace: phase3
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
          # Backend API routes
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: backend
                port:
                  number: 8080
          # Frontend routes (catch-all)
          - path: /()(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

### 8.3 Host Resolution (Local Development)

Add to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1 todo-app.local
```

For Minikube:
```bash
minikube ip
# Add output IP to hosts file
```

---

## 9. Health Probes

### 9.1 Frontend Probes

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

### 9.2 Backend Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
```

### 9.3 PostgreSQL Probes

```yaml
livenessProbe:
  tcpSocket:
    port: 5432
  initialDelaySeconds: 60
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 6

readinessProbe:
  exec:
    command:
      - pg_isready
      - -U
      - $(POSTGRES_USER)
  initialDelaySeconds: 30
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

### 9.4 Probe Configuration Rationale

| Probe Type | Initial Delay | Period | Timeout | Failure Threshold | Purpose |
|------------|---------------|--------|---------|-------------------|---------|
| Liveness (Frontend) | 30s | 10s | 5s | 3 | Restart if frozen |
| Readiness (Frontend) | 10s | 5s | 3s | 3 | Remove from service if not ready |
| Liveness (Backend) | 30s | 10s | 5s | 3 | Restart if frozen |
| Readiness (Backend) | 10s | 5s | 3s | 3 | Remove from service if not ready |
| Liveness (DB) | 60s | 10s | 5s | 6 | Longer tolerance for DB |
| Readiness (DB) | 30s | 5s | 3s | 3 | Ensure DB accepts connections |

---

## 10. Horizontal Pod Autoscaling

### 10.1 Frontend HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: phase3
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
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
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### 10.2 Backend HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: phase3
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
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
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
```

### 10.3 HPA Configuration Rationale

| Component | Min Replicas | Max Replicas | CPU Target | Memory Target | Scale Up | Scale Down |
|-----------|--------------|--------------|------------|---------------|----------|------------|
| Frontend | 2 | 10 | 70% | 80% | Aggressive | Conservative |
| Backend | 2 | 15 | 60% | 75% | Aggressive | Conservative |

**Notes:**
- Minimum 2 replicas ensures high availability
- Backend has higher max replicas due to AI processing load
- Scale down stabilization (300s) prevents flapping
- Scale up is immediate for traffic spikes

---

## 11. Helm Chart Folder Structure

```
helm-charts/
└── phase3-todo-chatbot/
    ├── Chart.yaml                 # Chart metadata
    ├── values.yaml                # Default values
    ├── values-minikube.yaml       # Minikube-specific overrides
    ├── values-production.yaml     # Production overrides
    ├── .helmignore                # Files to exclude from package
    ├── charts/                    # Subcharts (if any)
    ├── templates/                 # Kubernetes manifests templates
    │   ├── _helpers.tpl           # Template helpers
    │   ├── NOTES.txt              # Installation notes
    │   ├── namespace.yaml         # Namespace definition
    │   ├── configmap-frontend.yaml
    │   ├── configmap-backend.yaml
    │   ├── secrets.yaml
    │   ├── serviceaccount.yaml
    │   ├── role.yaml
    │   ├── rolebinding.yaml
    │   ├── deployment-frontend.yaml
    │   ├── deployment-backend.yaml
    │   ├── deployment-postgres.yaml
    │   ├── service-frontend.yaml
    │   ├── service-backend.yaml
    │   ├── service-postgres.yaml
    │   ├── pvc-postgres.yaml
    │   ├── ingress.yaml
    │   ├── hpa-frontend.yaml
    │   ├── hpa-backend.yaml
    │   ├── pdb-frontend.yaml
    │   ├── pdb-backend.yaml
    │   ├── networkpolicy.yaml
    │   ├── resourcequota.yaml
    │   └── limitrange.yaml
    └── tests/                     # Helm chart tests
        ├── test-frontend.yaml
        └── test-backend.yaml
```

---

## 12. Values.yaml Structure

```yaml
# =============================================================================
# Phase 3 Todo Chatbot - Helm Chart Values
# =============================================================================

# Global configuration applied across all components
global:
  namespace: phase3
  imageRegistry: ""  # Use Docker Hub by default
  storageClass: "standard"
  imagePullSecrets: []
  extraLabels: {}

# Frontend configuration
frontend:
  enabled: true
  name: frontend
  
  image:
    repository: phase3-frontend
    tag: latest
    pullPolicy: IfNotPresent
  
  replicaCount: 2
  
  service:
    type: ClusterIP
    port: 80
    targetPort: 3000
    annotations: {}
  
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  probes:
    liveness:
      path: /
      port: 3000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readiness:
      path: /
      port: 3000
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
  
  env:
    NODE_ENV: production
    # NEXT_PUBLIC_API_URL is set dynamically
  
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  
  containerSecurityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
    capabilities:
      drop:
        - ALL
  
  nodeSelector: {}
  tolerations: []
  affinity: {}

# Backend configuration
backend:
  enabled: true
  name: backend
  
  image:
    repository: phase3-backend
    tag: latest
    pullPolicy: IfNotPresent
  
  replicaCount: 2
  
  service:
    type: ClusterIP
    port: 8080
    targetPort: 4000
    annotations: {}
  
  resources:
    requests:
      memory: "256Mi"
      cpu: "200m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 15
    targetCPUUtilizationPercentage: 60
    targetMemoryUtilizationPercentage: 75
  
  probes:
    liveness:
      path: /health
      port: 4000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readiness:
      path: /health
      port: 4000
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
  
  env:
    PYTHON_ENV: production
    LOG_LEVEL: INFO
  
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  
  containerSecurityContext:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: false
    capabilities:
      drop:
        - ALL
  
  nodeSelector: {}
  tolerations: []
  affinity: {}

# PostgreSQL configuration
postgresql:
  enabled: true
  name: postgres
  
  image:
    repository: postgres
    tag: 15-alpine
    pullPolicy: IfNotPresent
  
  replicaCount: 1
  
  service:
    type: ClusterIP
    port: 5432
    targetPort: 5432
  
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "2Gi"
      cpu: "2000m"
  
  persistence:
    enabled: true
    size: 5Gi
    storageClass: ""
    accessModes:
      - ReadWriteOnce
  
  env:
    POSTGRES_DB: todoapp
    PGDATA: /var/lib/postgresql/data/pgdata
  
  probes:
    liveness:
      initialDelaySeconds: 60
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 6
    readiness:
      initialDelaySeconds: 30
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
  
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 999
    runAsGroup: 999
    fsGroup: 999
  
  containerSecurityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
  
  hosts:
    - host: todo-app.local
      paths:
        - path: /api(/|$)(.*)
          pathType: ImplementationSpecific
          backend:
            service:
              name: backend
              port:
                number: 8080
        - path: /()(.*)
          pathType: ImplementationSpecific
          backend:
            service:
              name: frontend
              port:
                number: 80
  
  tls: []

# Secrets configuration
secrets:
  enabled: true
  name: phase3-secrets
  postgresUser: "phase3user"
  postgresPassword: ""  # Auto-generate if empty
  postgresDB: "todoapp"
  betterAuthSecret: ""  # Auto-generate if empty
  openaiApiKey: ""

# Network Policy configuration
networkPolicy:
  enabled: true
  name: phase3-network-policy
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
  egress:
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53

# RBAC configuration
rbac:
  enabled: true
  serviceAccount:
    create: true
    name: phase3-sa
    annotations: {}
  
  role:
    rules:
      - apiGroups: [""]
        resources: ["configmaps", "secrets"]
        verbs: ["get", "list"]

# Pod Disruption Budget configuration
podDisruptionBudget:
  frontend:
    enabled: true
    minAvailable: 1
  backend:
    enabled: true
    minAvailable: 1

# Resource Quota configuration
resourceQuota:
  enabled: true
  name: phase3-quota
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    persistentvolumeclaims: "5"
    pods: "20"
    services: "10"

# Limit Range configuration
limitRange:
  enabled: true
  name: phase3-limits
  limits:
    - default:
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
      type: Container
```

---

## 13. Environment Variables Mapping

### 13.1 Frontend Environment Variables

| Variable | Source | Default | Description |
|----------|--------|---------|-------------|
| `NODE_ENV` | ConfigMap | `production` | Node environment |
| `NEXT_PUBLIC_API_URL` | ConfigMap | `http://backend:4000/api/v1` | Backend API URL |
| `PORT` | Deployment | `3000` | Application port |
| `HOSTNAME` | Deployment | `0.0.0.0` | Bind address |

### 13.2 Backend Environment Variables

| Variable | Source | Default | Description |
|----------|--------|---------|-------------|
| `DATABASE_URL` | Secret | Computed | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Secret | Auto-generated | Authentication secret |
| `PYTHON_ENV` | ConfigMap | `production` | Python environment |
| `LOG_LEVEL` | ConfigMap | `INFO` | Logging level |
| `PORT` | Deployment | `4000` | Application port |

### 13.3 PostgreSQL Environment Variables

| Variable | Source | Default | Description |
|----------|--------|---------|-------------|
| `POSTGRES_DB` | Secret | `todoapp` | Database name |
| `POSTGRES_USER` | Secret | `phase3user` | Database user |
| `POSTGRES_PASSWORD` | Secret | Auto-generated | Database password |
| `PGDATA` | ConfigMap | `/var/lib/postgresql/data/pgdata` | Data directory |

### 13.4 Secret Generation

```bash
# Generate secure random passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
BETTER_AUTH_SECRET=$(openssl rand -base64 32)

# Create Kubernetes secret
kubectl create secret generic phase3-secrets \
  --from-literal=postgres-password="$POSTGRES_PASSWORD" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --namespace=phase3
```

---

## 14. Deployment Workflow

### 14.1 Prerequisites

```bash
# Verify Docker Desktop is running
docker info

# Verify Minikube is installed
minikube version

# Verify kubectl is installed
kubectl version --client

# Verify Helm is installed
helm version
```

### 14.2 Minikube Cluster Setup

```bash
# Start Minikube with sufficient resources
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=20g \
  --kubernetes-version=stable

# Enable NGINX Ingress Controller
minikube addons enable ingress

# Enable Metrics Server (for HPA)
minikube addons enable metrics-server

# Verify cluster is running
kubectl cluster-info
```

### 14.3 Build Docker Images

```bash
# Set Minikube's Docker daemon
eval $(minikube docker-env)

# Build Frontend image
docker build -t phase3-frontend:latest ./frontend

# Build Backend image
docker build -t phase3-backend:latest ./backend

# Verify images
docker images | grep phase3
```

### 14.4 Install Helm Chart

```bash
# Navigate to chart directory
cd helm-charts/phase3-todo-chatbot

# Install with Minikube values
helm install phase3-todo . \
  --namespace phase3 \
  --create-namespace \
  --values values-minikube.yaml \
  --set secrets.postgresPassword=$(openssl rand -base64 32) \
  --set secrets.betterAuthSecret=$(openssl rand -base64 32)

# Verify installation
helm list -n phase3
kubectl get all -n phase3
```

### 14.5 Configure DNS

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Add to hosts file (requires admin)
# Windows (Run as Administrator):
echo "$MINIKUBE_IP todo-app.local" >> C:\Windows\System32\drivers\etc\hosts

# Linux/Mac:
echo "$MINIKUBE_IP todo-app.local" | sudo tee -a /etc/hosts
```

### 14.6 Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n phase3

# Check services
kubectl get svc -n phase3

# Check ingress
kubectl get ingress -n phase3

# Check HPA
kubectl get hpa -n phase3

# Test frontend
curl http://todo-app.local

# Test backend health
curl http://todo-app.local/api/health

# View logs
kubectl logs -n phase3 -l app=frontend
kubectl logs -n phase3 -l app=backend
```

### 14.7 Upgrade Deployment

```bash
# Update images
docker build -t phase3-frontend:v1.1.0 ./frontend
docker build -t phase3-backend:v1.1.0 ./backend

# Upgrade Helm release
helm upgrade phase3-todo . \
  --namespace phase3 \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0

# Monitor rollout
kubectl rollout status deployment/frontend -n phase3
kubectl rollout status deployment/backend -n phase3
```

### 14.8 Rollback

```bash
# Rollback to previous revision
helm rollback phase3-todo -n phase3

# Or rollback to specific revision
helm rollback phase3-todo 1 -n phase3

# View rollout history
helm history phase3-todo -n phase3
```

### 14.9 Uninstall

```bash
# Uninstall Helm chart
helm uninstall phase3-todo -n phase3

# Delete namespace
kubectl delete namespace phase3

# Clean up Docker images
docker rmi phase3-frontend:latest
docker rmi phase3-backend:latest

# Stop Minikube (optional)
minikube stop
```

### 14.10 CI/CD Integration (Future)

```yaml
# GitHub Actions workflow example
name: Deploy to Minikube

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Minikube
        uses: manusa/actions-setup-minikube@v2
        with:
          minikube version: 'latest'
          kubernetes version: 'stable'
          driver: docker
      
      - name: Build images
        run: |
          eval $(minikube docker-env)
          docker build -t phase3-frontend:${{ github.sha }} ./frontend
          docker build -t phase3-backend:${{ github.sha }} ./backend
      
      - name: Deploy with Helm
        run: |
          helm upgrade phase3-todo ./helm-charts/phase3-todo-chatbot \
            --namespace phase3 \
            --create-namespace \
            --install \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.tag=${{ github.sha }}
```

---

## 15. Monitoring and Observability

### 15.1 Metrics Collection

```bash
# Install Prometheus Stack (optional)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Access Grafana
minikube service monitoring-grafana -n monitoring
```

### 15.2 Log Aggregation

```bash
# View logs
kubectl logs -n phase3 -l app=frontend --follow
kubectl logs -n phase3 -l app=backend --follow

# Export logs
kubectl logs -n phase3 -l app=backend > backend-logs.txt
```

### 15.3 Health Dashboard

Access the following endpoints:
- Frontend: `http://todo-app.local/`
- Backend Health: `http://todo-app.local/api/health`
- Kubernetes Dashboard: `minikube dashboard`

---

## 16. Security Considerations

### 16.1 Pod Security Standards

All pods run with:
- Non-root user
- Read-only root filesystem (where applicable)
- Dropped capabilities
- No privilege escalation

### 16.2 Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: phase3-network-policy
  namespace: phase3
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow from Ingress Controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
        - protocol: TCP
          port: 4000
    # Allow internal communication
    - from:
        - podSelector: {}
  egress:
    # Allow DNS resolution
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53
    # Allow database connections
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

### 16.3 Secret Management

- Secrets stored in Kubernetes Secrets (base64 encoded)
- Consider external secret management (Vault, AWS Secrets Manager) for production
- Rotate secrets regularly
- Never commit secrets to version control

---

## 17. Troubleshooting Guide

### 17.1 Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| ImagePullBackOff | Pods can't pull images | Verify image exists, check `imagePullSecrets` |
| CrashLoopBackOff | Pods restarting | Check logs: `kubectl logs <pod> -n phase3` |
| Pending PVC | Storage not provisioned | Verify `StorageClass`: `kubectl get sc` |
| Ingress not working | 404 errors | Check Ingress Controller: `kubectl get pods -n ingress-nginx` |
| HPA not scaling | Metrics unavailable | Verify Metrics Server: `kubectl top pods` |

### 17.2 Debug Commands

```bash
# Describe problematic resource
kubectl describe pod <pod-name> -n phase3
kubectl describe deployment <deployment-name> -n phase3

# Execute into container
kubectl exec -it <pod-name> -n phase3 -- /bin/sh

# Port forward for debugging
kubectl port-forward svc/frontend 3000:80 -n phase3
kubectl port-forward svc/backend 4000:8080 -n phase3

# Check events
kubectl get events -n phase3 --sort-by='.lastTimestamp'
```

---

## 18. Acceptance Criteria

- [ ] Minikube cluster running with 4 CPUs and 8GB RAM
- [ ] NGINX Ingress Controller enabled and functional
- [ ] All three deployments (frontend, backend, postgres) running
- [ ] All pods passing health checks
- [ ] HPA configured and monitoring metrics
- [ ] Ingress routing `/api/*` to backend, `/*` to frontend
- [ ] Database persistence configured with 5Gi PVC
- [ ] Network policies restricting pod-to-pod communication
- [ ] Resource quotas and limit ranges applied
- [ ] Pod Disruption Budgets configured
- [ ] Secrets properly managed
- [ ] Application accessible at `http://todo-app.local`
- [ ] Backend health endpoint responding
- [ ] Horizontal scaling triggered under load
- [ ] Rollback procedure tested and documented

---

## 19. Appendix

### 19.1 Quick Reference Commands

```bash
# Cluster management
minikube start --driver=docker --cpus=4 --memory=8192
minikube stop
minikube delete
minikube status

# Docker image management
eval $(minikube docker-env)
docker build -t phase3-frontend:latest ./frontend
docker images

# Helm operations
helm install phase3-todo ./helm-charts/phase3-todo-chatbot -n phase3 --create-namespace
helm upgrade phase3-todo ./helm-charts/phase3-todo-chatbot -n phase3
helm rollback phase3-todo -n phase3
helm uninstall phase3-todo -n phase3
helm history phase3-todo -n phase3

# Kubernetes operations
kubectl get all -n phase3
kubectl describe pod <pod-name> -n phase3
kubectl logs -n phase3 -l app=backend
kubectl exec -it <pod-name> -n phase3 -- /bin/bash
kubectl port-forward svc/frontend 3000:80 -n phase3
```

### 19.2 File References

- `docker-compose.yml` - Local Docker Compose configuration
- `helm-charts/phase3-todo-chatbot/` - Helm chart directory
- `frontend/Dockerfile` - Frontend container definition
- `backend/Dockerfile` - Backend container definition
- `values-minikube.yaml` - Minikube-specific Helm values
- `values-production.yaml` - Production-specific Helm values

### 19.3 Related Documentation

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

**Document Status:** Complete  
**Next Steps:** Execute deployment using `/sp.tasks` workflow  
**PHR Location:** `history/prompts/infrastructure/`  
**ADR Required:** No (standard deployment pattern)
