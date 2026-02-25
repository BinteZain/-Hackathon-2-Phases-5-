# Infrastructure Specification: Phase 3 Todo Chatbot on Kubernetes

**Document Type:** Infrastructure Specification  
**Version:** 1.0.0  
**Target Platform:** Local Kubernetes (Minikube)  
**Package Manager:** Helm v3.x  
**Date:** February 18, 2026  

---

## 1. Executive Summary

This specification defines the infrastructure requirements for deploying the Phase 3 Todo Chatbot application on a local Kubernetes cluster using Minikube and Helm. The application consists of three primary components: Next.js frontend, FastAPI backend, and PostgreSQL database.

---

## 2. System Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Ingress                           │   │
│  │              (nginx-ingress-controller)              │   │
│  │              Port: 80 (HTTP), 443 (HTTPS)            │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                     │
│         ┌─────────────┴─────────────┐                       │
│         │                           │                       │
│  ┌──────▼──────┐            ┌──────▼──────┐                │
│  │  Frontend   │            │   Backend   │                │
│  │  Service    │            │   Service   │                │
│  │  Port: 80   │            │  Port: 8080 │                │
│  └──────┬──────┘            └──────┬──────┘                │
│         │                           │                       │
│  ┌──────▼──────┐            ┌──────▼──────┐                │
│  │  Frontend   │            │   Backend   │                │
│  │ Deployment  │            │ Deployment  │                │
│  │ Replicas: 2 │            │ Replicas: 2 │                │
│  │ Port: 3000  │            │ Port: 4000  │                │
│  └─────────────┘            └──────┬──────┘                │
│                                    │                       │
│                           ┌────────▼────────┐              │
│                           │   PostgreSQL    │              │
│                           │   StatefulSet   │              │
│                           │   Replicas: 1   │              │
│                           │   Port: 5432    │              │
│                           └─────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Components Overview

| Component | Technology | Container Image | Port | Replicas |
|-----------|------------|-----------------|------|----------|
| Frontend | Next.js 13 | `phase3-frontend:latest` | 3000 | 2 |
| Backend | FastAPI | `phase3-backend:latest` | 4000 | 2 |
| Database | PostgreSQL 15 | `postgres:15-alpine` | 5432 | 1 |
| Ingress | NGINX | `registry.k8s.io/ingress-nginx/controller:v1.9.5` | 80/443 | 1 |

---

## 3. Container Images

### 3.1 Frontend Image

```dockerfile
Repository: phase3-frontend
Tag: latest (development), v1.0.0 (production)
Base Image: node:18-alpine
Registry: Local Minikube Registry / Docker Hub
Build Context: ./frontend
```

**Image Details:**
- **Size:** ~500MB
- **Exposed Port:** 3000
- **Health Check:** `curl -f http://localhost:3000/health || exit 1`
- **User:** node (non-root)

### 3.2 Backend Image

```dockerfile
Repository: phase3-backend
Tag: latest (development), v1.0.0 (production)
Base Image: python:3.11-slim
Registry: Local Minikube Registry / Docker Hub
Build Context: ./backend
```

**Image Details:**
- **Size:** ~400MB
- **Exposed Port:** 4000
- **Health Check:** `curl -f http://localhost:4000/health || exit 1`
- **User:** nobody (non-root)

### 3.3 Database Image

```dockerfile
Repository: postgres
Tag: 15-alpine
Registry: Docker Hub (public)
```

**Image Details:**
- **Size:** ~150MB
- **Exposed Port:** 5432
- **Persistent Volume:** 5Gi

---

## 4. Network Configuration

### 4.1 Ports Mapping

| Component | Container Port | Service Port | NodePort (Optional) | Protocol |
|-----------|---------------|--------------|---------------------|----------|
| Frontend | 3000 | 80 | 30080 | TCP |
| Backend | 4000 | 8080 | 30081 | TCP |
| PostgreSQL | 5432 | 5432 | - | TCP |
| Ingress | 80/443 | 80/443 | 80/443 | TCP |

### 4.2 Service Types

| Service | Type | Cluster IP | External Access |
|---------|------|------------|-----------------|
| frontend-service | ClusterIP | Auto-assigned | Via Ingress |
| backend-service | ClusterIP | Auto-assigned | Internal only |
| postgres-service | ClusterIP | Auto-assigned | Internal only |

### 4.3 Ingress Rules

```yaml
Host: todo-app.local
Paths:
  - /api/* → backend-service:8080 (strip prefix: /api)
  - /*     → frontend-service:80
```

---

## 5. Environment Variables

### 5.1 Frontend Environment Variables

| Variable | Required | Default | Description | Source |
|----------|----------|---------|-------------|--------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | `http://backend-service:8080/api/v1` | Backend API URL | ConfigMap |
| `NEXT_PUBLIC_BETTER_AUTH_SECRET` | ✅ Yes | - | Auth secret key | Secret |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | ❌ No | `""` | OpenAI API key | Secret |
| `NODE_ENV` | ❌ No | `production` | Node environment | ConfigMap |

### 5.2 Backend Environment Variables

| Variable | Required | Default | Description | Source |
|----------|----------|---------|-------------|--------|
| `DATABASE_URL` | ✅ Yes | - | PostgreSQL connection string | Secret |
| `BETTER_AUTH_SECRET` | ✅ Yes | - | JWT signing secret | Secret |
| `OPENAI_API_KEY` | ❌ No | `""` | OpenAI API key | Secret |
| `PYTHON_ENV` | ❌ No | `production` | Python environment | ConfigMap |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level | ConfigMap |

### 5.3 Database Environment Variables

| Variable | Required | Default | Description | Source |
|----------|----------|---------|-------------|--------|
| `POSTGRES_DB` | ✅ Yes | `todoapp` | Database name | ConfigMap |
| `POSTGRES_USER` | ✅ Yes | - | Database user | Secret |
| `POSTGRES_PASSWORD` | ✅ Yes | - | Database password | Secret |
| `PGDATA` | ❌ No | `/var/lib/postgresql/data/pgdata` | Data directory | ConfigMap |

---

## 6. Secrets Management

### 6.1 Kubernetes Secrets

**Secret Name:** `phase3-secrets`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: phase3-secrets
  namespace: phase3
type: Opaque
stringData:
  # Database Credentials
  POSTGRES_USER: "phase3user"
  POSTGRES_PASSWORD: "<generated-secure-password>"
  
  # Database Connection String (computed)
  DATABASE_URL: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres-service:5432/$(POSTGRES_DB)"
  
  # Authentication
  BETTER_AUTH_SECRET: "<generated-secure-secret>"
  
  # OpenAI API Key (optional)
  OPENAI_API_KEY: "<user-provided-key>"
```

### 6.2 Secret Generation

```bash
# Generate secure passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
BETTER_AUTH_SECRET=$(openssl rand -base64 32)
```

### 6.3 Secret Rotation Strategy

- **Frequency:** Every 90 days (production)
- **Method:** Helm upgrade with new secret values
- **Downtime:** Zero (rolling update)

---

## 7. Replica Count and Scaling

### 7.1 Default Replica Count

| Component | Minikube (Local) | Production-Ready | Notes |
|-----------|------------------|------------------|-------|
| Frontend | 2 | 3 | High availability |
| Backend | 2 | 3 | High availability |
| PostgreSQL | 1 | 1 (with replication) | StatefulSet |
| Ingress | 1 | 2 | DaemonSet or Deployment |

### 7.2 Scaling Strategy

#### Horizontal Pod Autoscaler (HPA)

**Frontend HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
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
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
```

**Backend HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
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
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
```

#### Vertical Pod Autoscaler (VPA) - Optional

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
```

#### Scaling Triggers

| Metric | Scale Up Threshold | Scale Down Threshold | Cooldown |
|--------|-------------------|---------------------|----------|
| CPU Utilization | > 70% | < 30% | 5 minutes |
| Memory Utilization | > 80% | < 40% | 5 minutes |
| Request Latency (p95) | > 500ms | < 200ms | 3 minutes |
| Request Queue Depth | > 100 | < 20 | 2 minutes |

---

## 8. Resource Limits and Requests

### 8.1 Frontend Resources

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

| Environment | Replicas | Total Memory | Total CPU |
|-------------|----------|--------------|-----------|
| Minikube | 2 | 256Mi - 1Gi | 200m - 1000m |
| Production | 3 | 384Mi - 1.5Gi | 300m - 1500m |

### 8.2 Backend Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

| Environment | Replicas | Total Memory | Total CPU |
|-------------|----------|--------------|-----------|
| Minikube | 2 | 512Mi - 2Gi | 400m - 2000m |
| Production | 3 | 768Mi - 3Gi | 600m - 3000m |

### 8.3 PostgreSQL Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

| Environment | Replicas | Total Memory | Total CPU |
|-------------|----------|--------------|-----------|
| Minikube | 1 | 256Mi - 2Gi | 250m - 2000m |
| Production | 1 | 512Mi - 4Gi | 500m - 4000m |

### 8.4 Resource Summary (Minikube)

| Component | Requests (Memory/CPU) | Limits (Memory/CPU) |
|-----------|----------------------|---------------------|
| Frontend (x2) | 256Mi / 200m | 1Gi / 1000m |
| Backend (x2) | 512Mi / 400m | 2Gi / 2000m |
| PostgreSQL (x1) | 256Mi / 250m | 2Gi / 2000m |
| **Total** | **1024Mi / 850m** | **5Gi / 5000m** |

**Recommended Minikube Profile:**
```bash
minikube start --memory=6144 --cpus=4 --disk-size=20g
```

---

## 9. Storage Configuration

### 9.1 Persistent Volumes

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: phase3
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
```

### 9.2 Storage Class

**Minikube Default:** `standard` (hostpath provisioner)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: k8s.io/minikube-hostpath
reclaimPolicy: Retain
volumeBindingMode: Immediate
```

### 9.3 Data Retention

| Data Type | Retention Policy | Backup Strategy |
|-----------|-----------------|-----------------|
| PostgreSQL Data | Persistent (PVC) | Manual export via `pg_dump` |
| Application Logs | Ephemeral | stdout/stderr (kubectl logs) |
| Secrets | Persistent (etcd) | External secret management |

---

## 10. Health Checks and Probes

### 10.1 Frontend Probes

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1

startupProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
```

### 10.2 Backend Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1

readinessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1

startupProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
```

### 10.3 PostgreSQL Probes

```yaml
livenessProbe:
  exec:
    command:
      - pg_isready
      - -U
      - $(POSTGRES_USER)
  initialDelaySeconds: 60
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

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

---

## 11. Security Configuration

### 11.1 Pod Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
```

### 11.2 Container Security Context

```yaml
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

### 11.3 Network Policies

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
    # Allow ingress to frontend from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 3000
    # Allow ingress to backend from frontend
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 4000
    # Allow ingress to postgres from backend
    - from:
        - podSelector:
            matchLabels:
              app: backend
      ports:
        - protocol: TCP
          port: 5432
  egress:
    # Allow DNS resolution
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
    # Allow backend to access database
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

### 11.4 RBAC Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: phase3-role
  namespace: phase3
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: phase3-rolebinding
  namespace: phase3
subjects:
  - kind: ServiceAccount
    name: phase3-sa
    namespace: phase3
roleRef:
  kind: Role
  name: phase3-role
  apiGroup: rbac.authorization.k8s.io
```

---

## 12. Helm Chart Structure

```
helm-charts/
└── phase3-todo-chatbot/
    ├── Chart.yaml              # Chart metadata
    ├── values.yaml             # Default configuration values
    ├── values-minikube.yaml    # Minikube-specific overrides
    ├── values-production.yaml  # Production-specific overrides
    ├── .helmignore             # Files to ignore when packaging
    ├── templates/
    │   ├── _helpers.tpl        # Template helpers
    │   ├── namespace.yaml      # Namespace definition
    │   ├── configmap.yaml      # ConfigMaps
    │   ├── secrets.yaml        # Secrets (template)
    │   ├── frontend/
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   ├── hpa.yaml
    │   │   ├── pdb.yaml
    │   │   └── serviceaccount.yaml
    │   ├── backend/
    │   │   ├── deployment.yaml
    │   │   ├── service.yaml
    │   │   ├── hpa.yaml
    │   │   ├── pdb.yaml
    │   │   └── serviceaccount.yaml
    │   ├── postgres/
    │   │   ├── statefulset.yaml
    │   │   ├── service.yaml
    │   │   ├── pvc.yaml
    │   │   └── serviceaccount.yaml
    │   ├── ingress/
    │   │   ├── ingress.yaml
    │   │   └── ingress-class.yaml
    │   ├── network/
    │   │   └── networkpolicy.yaml
    │   └── rbac/
    │       ├── role.yaml
    │       ├── rolebinding.yaml
    │       └── serviceaccount.yaml
    ├── charts/                 # Subcharts (if any)
    └── tests/
        └── frontend-deployment_test.yaml
```

---

## 13. Deployment Workflow

### 13.1 Prerequisites

```bash
# Required tools
minikube version >= 1.32.0
kubectl version >= 1.28.0
helm version >= 3.13.0
docker version >= 24.0.0

# Minimum system requirements
CPU: 4 cores
Memory: 6 GB
Disk: 20 GB
```

### 13.2 Installation Steps

```bash
# 1. Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

# 2. Enable ingress addon
minikube addons enable ingress --profile phase3

# 3. Build and load images
eval $(minikube docker-env --profile phase3)
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# 4. Create namespace
kubectl create namespace phase3

# 5. Create secrets
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=$(openssl rand -base64 32) \
  --from-literal=BETTER_AUTH_SECRET=$(openssl rand -base64 32) \
  --from-literal=OPENAI_API_KEY="" \
  -n phase3

# 6. Install Helm chart
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3

# 7. Verify deployment
kubectl get all -n phase3

# 8. Get application URL
minikube service frontend-service -n phase3 --url --profile phase3
```

### 13.3 Upgrade Workflow

```bash
# Update values
vim helm-charts/phase3-todo-chatbot/values-minikube.yaml

# Upgrade release
helm upgrade phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3

# Rollback if needed
helm rollback phase3 -n phase3
```

### 13.4 Uninstall Workflow

```bash
# Uninstall Helm chart
helm uninstall phase3 -n phase3

# Delete namespace
kubectl delete namespace phase3

# Stop Minikube
minikube stop --profile phase3
```

---

## 14. Monitoring and Observability

### 14.1 Metrics Collection

| Component | Metrics Endpoint | Metrics |
|-----------|-----------------|---------|
| Frontend | `/metrics` (via sidecar) | Request count, latency, errors |
| Backend | `/metrics` | Request count, latency, DB connections |
| PostgreSQL | `pg_stat_statements` | Queries, connections, locks |

### 14.2 Logging Strategy

```yaml
# Log aggregation via stdout/stderr
# Access logs via kubectl
kubectl logs -f deployment/frontend -n phase3
kubectl logs -f deployment/backend -n phase3

# Log levels
DEBUG - Development only
INFO  - Default production level
WARN  - Warnings and errors
ERROR - Errors only
```

### 14.3 Alerting Rules (Prometheus)

```yaml
groups:
  - name: phase3-alerts
    rules:
      - alert: FrontendHighErrorRate
        expr: rate(http_requests_total{job="frontend",status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "Frontend error rate is high"
      
      - alert: BackendHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m])) > 1
        for: 5m
        annotations:
          summary: "Backend p95 latency > 1s"
      
      - alert: PostgresHighConnections
        expr: pg_stat_activity_count > 80
        for: 5m
        annotations:
          summary: "PostgreSQL connections > 80%"
```

---

## 15. Disaster Recovery

### 15.1 Backup Strategy

| Component | Backup Type | Frequency | Retention |
|-----------|-------------|-----------|-----------|
| PostgreSQL | pg_dump | Daily | 7 days |
| Secrets | kubectl get secret | On change | Indefinite |
| ConfigMaps | kubectl get configmap | On change | Indefinite |
| PVCs | Volume snapshot | Weekly | 4 weeks |

### 15.2 Recovery Procedures

**Database Recovery:**
```bash
# Backup
kubectl exec -it postgres-0 -n phase3 -- pg_dump -U phase3user todoapp > backup.sql

# Restore
kubectl exec -i postgres-0 -n phase3 -- psql -U phase3user todoapp < backup.sql
```

**Application Recovery:**
```bash
# Rollback to previous Helm release
helm rollback phase3 -n phase3

# Force recreate pods
kubectl rollout restart deployment/frontend -n phase3
kubectl rollout restart deployment/backend -n phase3
```

---

## 16. Acceptance Criteria

### 16.1 Functional Requirements

- [ ] Frontend accessible via Ingress at `todo-app.local`
- [ ] Backend API accessible at `todo-app.local/api/v1`
- [ ] PostgreSQL database persistent across pod restarts
- [ ] All components healthy (readiness probes passing)
- [ ] Horizontal Pod Autoscaler configured and functional
- [ ] Network policies restrict unauthorized access

### 16.2 Non-Functional Requirements

- [ ] Frontend p95 latency < 500ms
- [ ] Backend p95 latency < 300ms
- [ ] Database connection time < 100ms
- [ ] Application available 99.9% (local)
- [ ] Zero-downtime deployments
- [ ] Resource limits enforced

### 16.3 Security Requirements

- [ ] All pods run as non-root
- [ ] Secrets stored in Kubernetes Secrets
- [ ] Network policies enforce least privilege
- [ ] RBAC configured for service accounts
- [ ] No hardcoded credentials in code/config

### 16.4 Operational Requirements

- [ ] Health endpoints responding
- [ ] Logs accessible via kubectl
- [ ] Metrics exposed for monitoring
- [ ] Helm chart passes `helm lint`
- [ ] Helm chart passes `helm template`
- [ ] Rollback tested and functional

---

## 17. Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Minikube resource exhaustion | High | Medium | Set resource limits, use adequate profile |
| Database data loss | High | Low | PVC with Retain policy, regular backups |
| Secret exposure | High | Low | Use Kubernetes Secrets, avoid env files |
| Network misconfiguration | Medium | Medium | Test network policies thoroughly |
| Image pull failures | Medium | Low | Use local registry, preload images |
| Ingress routing issues | Medium | Medium | Test ingress rules with curl |

---

## 18. Cost Estimation (Minikube Local)

| Resource | Allocation | Local Cost |
|----------|------------|------------|
| CPU | 4 cores | $0 (local) |
| Memory | 6 GB | $0 (local) |
| Storage | 20 GB | $0 (local) |
| Network | Local | $0 (local) |
| **Total** | | **$0/month** |

---

## 19. Future Enhancements

1. **Service Mesh:** Istio/Linkerd for advanced traffic management
2. **GitOps:** ArgoCD for declarative deployments
3. **CI/CD:** GitHub Actions for automated deployments
4. **Multi-cluster:** Federation for high availability
5. **Database HA:** PostgreSQL operator with replication
6. **Observability:** Full Prometheus/Grafana stack
7. **Security:** OPA/Gatekeeper for policy enforcement

---

## 20. References

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [PostgreSQL Helm Chart](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

**Document Status:** ✅ Complete  
**Review Status:** ⏳ Pending Judge Review  
**Next Steps:** Create Helm chart implementation
