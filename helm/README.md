# Helm Chart - Phase 3 Todo Chatbot

**Chart Version:** 1.0.0  
**App Version:** 1.0.0  
**Status:** ✅ Validated (`helm lint` passed)

---

## Chart Structure

```
helm/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Configuration values
├── .helmignore                # Files to ignore
└── templates/
    ├── _helpers.tpl           # Template helpers
    ├── namespace.yaml         # Namespace definition
    ├── secrets.yaml           # Kubernetes secrets
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── postgres-statefulset.yaml
    ├── postgres-service.yaml
    └── ingress.yaml           # Ingress routing
```

---

## Components

| Component | Type | Replicas | Port | Image |
|-----------|------|----------|------|-------|
| Frontend | Deployment | 2 | 3000 | `phase3-frontend:latest` |
| Backend | Deployment | 2 | 4000 | `phase3-backend:latest` |
| PostgreSQL | StatefulSet | 1 | 5432 | `postgres:15-alpine` |
| Ingress | Ingress | - | 80/443 | NGINX |

---

## Benefits

### ✅ Versioned Infrastructure
- Chart version: `1.0.0`
- App version: `1.0.0`
- Track changes with Helm revisions
- Rollback to previous versions

### ✅ Easy Scaling
```bash
# Scale frontend
helm upgrade phase3 helm/ --set frontend.replicaCount=5

# Scale backend
helm upgrade phase3 helm/ --set backend.replicaCount=10

# Scale both
helm upgrade phase3 helm/ \
  --set frontend.replicaCount=5 \
  --set backend.replicaCount=10
```

### ✅ Configurable Resources
```bash
# Increase backend resources
helm upgrade phase3 helm/ \
  --set backend.resources.limits.memory=2Gi \
  --set backend.resources.limits.cpu=2000m
```

### ✅ Environment Separation
```bash
# Development
helm install phase3-dev helm/ -f values-dev.yaml

# Staging
helm install phase3-staging helm/ -f values-staging.yaml

# Production
helm install phase3-prod helm/ -f values-prod.yaml
```

---

## Installation

### Prerequisites
- Kubernetes cluster (Minikube, kind, EKS, GKE, AKS)
- Helm v3.x
- Docker images built (`phase3-frontend:latest`, `phase3-backend:latest`)

### Quick Install

```bash
# 1. Validate chart
helm lint helm/

# 2. Dry run (verify templates)
helm template phase3 helm/ --debug

# 3. Install
helm install phase3 helm/ -n phase3 --create-namespace

# 4. Verify
helm list -n phase3
kubectl get all -n phase3
```

### Upgrade

```bash
# Upgrade with new values
helm upgrade phase3 helm/ -n phase3 \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3

# Upgrade with new image tag
helm upgrade phase3 helm/ -n phase3 \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0
```

### Rollback

```bash
# View release history
helm history phase3 -n phase3

# Rollback to previous revision
helm rollback phase3 -n phase3

# Rollback to specific revision
helm rollback phase3 1 -n phase3
```

### Uninstall

```bash
helm uninstall phase3 -n phase3
kubectl delete namespace phase3
```

---

## Configuration (values.yaml)

### Frontend

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frontend.enabled` | `true` | Enable/disable frontend |
| `frontend.replicaCount` | `2` | Number of replicas |
| `frontend.image.repository` | `phase3-frontend` | Image name |
| `frontend.image.tag` | `latest` | Image tag |
| `frontend.service.port` | `80` | Service port |
| `frontend.service.targetPort` | `3000` | Container port |
| `frontend.resources.requests.memory` | `128Mi` | Memory request |
| `frontend.resources.requests.cpu` | `100m` | CPU request |
| `frontend.resources.limits.memory` | `512Mi` | Memory limit |
| `frontend.resources.limits.cpu` | `500m` | CPU limit |

### Backend

| Parameter | Default | Description |
|-----------|---------|-------------|
| `backend.enabled` | `true` | Enable/disable backend |
| `backend.replicaCount` | `2` | Number of replicas |
| `backend.image.repository` | `phase3-backend` | Image name |
| `backend.image.tag` | `latest` | Image tag |
| `backend.service.port` | `8080` | Service port |
| `backend.service.targetPort` | `4000` | Container port |
| `backend.resources.requests.memory` | `256Mi` | Memory request |
| `backend.resources.requests.cpu` | `200m` | CPU request |
| `backend.resources.limits.memory` | `1Gi` | Memory limit |
| `backend.resources.limits.cpu` | `1000m` | CPU limit |

### PostgreSQL

| Parameter | Default | Description |
|-----------|---------|-------------|
| `postgresql.enabled` | `true` | Enable/disable database |
| `postgresql.replicaCount` | `1` | Number of replicas |
| `postgresql.image.repository` | `postgres` | Image name |
| `postgresql.image.tag` | `15-alpine` | Image tag |
| `postgresql.persistence.size` | `5Gi` | PVC size |
| `postgresql.env.POSTGRES_DB` | `todoapp` | Database name |
| `postgresql.env.POSTGRES_USER` | `phase3user` | Database user |

### Ingress

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ingress.enabled` | `true` | Enable/disable ingress |
| `ingress.className` | `nginx` | Ingress class |
| `ingress.hosts[0].host` | `todo-app.local` | Hostname |
| `ingress.annotations` | (see values) | NGINX annotations |

---

## Ingress Routing

```
User Request → Ingress (todo-app.local)
                    │
        ┌───────────┴───────────┐
        │                       │
   /api/*                   /*
        │                       │
        ▼                       ▼
  backend:8080          frontend:80
  (port 4000)           (port 3000)
```

---

## Security Features

### Pod Security Context
```yaml
securityContext:
  runAsNonRoot: true        # Cannot run as root
  runAsUser: 1000           # UID 1000
  runAsGroup: 1000          # GID 1000
  fsGroup: 1000             # File system group
```

### Container Security Context
```yaml
securityContext:
  allowPrivilegeEscalation: false  # No privilege escalation
  readOnlyRootFilesystem: true     # Read-only FS (frontend)
  capabilities:
    drop:
      - ALL                        # Drop all capabilities
```

### Secrets Management
- All sensitive data in Kubernetes Secrets
- DATABASE_URL computed from components
- BETTER_AUTH_SECRET from values
- OPENAI_API_KEY optional

---

## Health Checks

### Frontend Probes
```yaml
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
```

### Backend Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 4000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### PostgreSQL Probes
```yaml
livenessProbe:
  exec:
    command:
      - pg_isready
      - -U
      - phase3user
  initialDelaySeconds: 60
  periodSeconds: 10

readinessProbe:
  exec:
    command:
      - pg_isready
      - -U
      - phase3user
  initialDelaySeconds: 30
  periodSeconds: 5
```

---

## Resource Summary

| Component | Requests | Limits |
|-----------|----------|--------|
| Frontend (x2) | 256Mi / 200m | 1Gi / 1000m |
| Backend (x2) | 512Mi / 400m | 2Gi / 2000m |
| PostgreSQL (x1) | 256Mi / 250m | 2Gi / 2000m |
| **Total** | **1024Mi / 850m** | **5Gi / 5000m** |

**Minimum Cluster:** 2 CPU, 2GB RAM  
**Recommended:** 4 CPU, 6GB RAM

---

## Validation Commands

```bash
# Lint chart
helm lint helm/

# Template render
helm template phase3 helm/

# Dry run install
helm install phase3 helm/ --dry-run --debug

# Validate against cluster
helm install phase3 helm/ --dry-run --debug -n phase3
```

---

## Troubleshooting

### Chart Validation Failed
```bash
helm lint helm/ --debug
```

### Template Render Error
```bash
helm template phase3 helm/ --debug
```

### Pod Not Starting
```bash
kubectl describe deployment/frontend -n phase3
kubectl logs deployment/frontend -n phase3
```

### Service Not Accessible
```bash
kubectl get svc -n phase3
kubectl get endpoints -n phase3
```

---

## Next Steps

1. **Build Images:** `docker build -t phase3-frontend:latest ./frontend`
2. **Start Minikube:** `minikube start --profile phase3`
3. **Install Chart:** `helm install phase3 helm/ -n phase3 --create-namespace`
4. **Access App:** `minikube service frontend-service -n phase3`

---

**Chart Status:** ✅ Ready for Deployment
