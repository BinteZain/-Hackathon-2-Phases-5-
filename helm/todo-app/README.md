# Todo App - Production Helm Chart

[![ Helm Chart Version ]( https://img.shields.io/badge/version-2.0.0-blue.svg )]( https://helm.sh/ )
[![ App Version ]( https://img.shields.io/badge/app-2.0.0-green.svg )]( https://github.com/BinteZain/-Hackathon_2_Phase_3- )
[![ Kubernetes ]( https://img.shields.io/badge/k8s-1.23+-purple.svg )]( https://kubernetes.io/ )

Production-ready Helm chart for deploying a full-stack Todo application with:
- **Frontend**: Next.js (Node.js 18)
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15

## 📁 Folder Structure

```
helm/todo-app/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Configuration values
├── .helmignore                # Files to ignore when packaging
├── README.md                  # This file
└── templates/
    ├── _helpers.tpl           # Template helper functions
    ├── NOTES.txt              # Post-install notes
    ├── namespace.yaml         # Namespace creation
    ├── configmap.yaml         # Application configuration
    ├── secrets.yaml           # Sensitive data
    ├── serviceaccount.yaml    # Service accounts for pods
    ├── rbac.yaml              # RBAC roles and bindings
    ├── frontend-deployment.yaml    # Frontend deployment
    ├── frontend-service.yaml       # Frontend service
    ├── frontend-hpa.yaml           # Frontend autoscaler
    ├── frontend-pdb.yaml           # Frontend disruption budget
    ├── backend-deployment.yaml     # Backend deployment
    ├── backend-service.yaml        # Backend service
    ├── backend-hpa.yaml            # Backend autoscaler
    ├── backend-pdb.yaml            # Backend disruption budget
    ├── postgresql-statefulset.yaml # PostgreSQL StatefulSet
    ├── postgresql-service.yaml     # PostgreSQL service
    ├── ingress.yaml                # Ingress routing
    └── networkpolicy.yaml          # Network policies
```

## ✨ Features

- ✅ **Multi-component deployment**: Frontend + Backend + PostgreSQL
- ✅ **Horizontal Pod Autoscaling (HPA)**: Auto-scale based on CPU/Memory
- ✅ **Pod Disruption Budgets (PDB)**: High availability during updates
- ✅ **Resource limits**: CPU and memory requests/limits
- ✅ **Health probes**: Liveness, readiness, and startup probes
- ✅ **Security contexts**: Non-root users, read-only filesystems
- ✅ **Network policies**: Service isolation and access control
- ✅ **Ingress support**: NGINX ingress with path-based routing
- ✅ **Secrets management**: Kubernetes secrets for sensitive data
- ✅ **ConfigMap support**: Externalized configuration
- ✅ **Service accounts**: Dedicated service accounts per component
- ✅ **RBAC support**: Role-based access control
- ✅ **Persistent storage**: StatefulSet with PVC for PostgreSQL
- ✅ **Init containers**: Database readiness checks
- ✅ **Topology spread**: Pod distribution across nodes
- ✅ **Monitoring ready**: ServiceMonitor/PodMonitor support

## 🚀 Quick Start

### Prerequisites

- Kubernetes 1.23+
- Helm 3.10+
- NGINX Ingress Controller (optional, for ingress support)

### Installation

1. **Add the chart repository** (if published):
```bash
helm repo add todo-app https://your-repo.com/helm
helm repo update
```

2. **Install the chart**:
```bash
# Install with default values
helm install todo-app ./helm/todo-app -n todo-app --create-namespace

# Install with custom values
helm install todo-app ./helm/todo-app \
  -n todo-app \
  --create-namespace \
  -f values-custom.yaml
```

3. **Verify installation**:
```bash
kubectl get all -n todo-app
kubectl get hpa -n todo-app
kubectl get ingress -n todo-app
```

### Access the Application

#### Via Ingress (Recommended)

If ingress is enabled (default):
```
Host: todo-app.local
Frontend: http://todo-app.local/
Backend API: http://todo-app.local/api/
```

#### Via Port Forwarding

```bash
# Frontend
kubectl port-forward svc/todo-app-frontend 3000:80 -n todo-app

# Backend
kubectl port-forward svc/todo-app-backend 4000:8080 -n todo-app

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:4000
```

## ⚙️ Configuration

### Key Parameters

#### Global Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `todo-app` |
| `global.createNamespace` | Create namespace automatically | `true` |
| `global.imageRegistry` | Container image registry | `""` |

#### Frontend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.image.repository` | Frontend image repository | `todo-frontend` |
| `frontend.image.tag` | Frontend image tag | `v1` |
| `frontend.replicaCount` | Number of replicas | `2` |
| `frontend.hpa.enabled` | Enable HPA | `true` |
| `frontend.hpa.minReplicas` | Minimum replicas | `2` |
| `frontend.hpa.maxReplicas` | Maximum replicas | `10` |
| `frontend.resources.requests.memory` | Memory request | `256Mi` |
| `frontend.resources.requests.cpu` | CPU request | `100m` |
| `frontend.resources.limits.memory` | Memory limit | `512Mi` |
| `frontend.resources.limits.cpu` | CPU limit | `500m` |

#### Backend Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.image.repository` | Backend image repository | `todo-backend` |
| `backend.image.tag` | Backend image tag | `v1` |
| `backend.replicaCount` | Number of replicas | `2` |
| `backend.hpa.enabled` | Enable HPA | `true` |
| `backend.hpa.minReplicas` | Minimum replicas | `2` |
| `backend.hpa.maxReplicas` | Maximum replicas | `10` |
| `backend.resources.requests.memory` | Memory request | `512Mi` |
| `backend.resources.requests.cpu` | CPU request | `200m` |
| `backend.resources.limits.memory` | Memory limit | `1Gi` |
| `backend.resources.limits.cpu` | CPU limit | `1000m` |

#### PostgreSQL Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Enable PostgreSQL | `true` |
| `postgresql.image.repository` | PostgreSQL image | `postgres` |
| `postgresql.image.tag` | PostgreSQL tag | `15-alpine` |
| `postgresql.persistence.enabled` | Enable persistent storage | `true` |
| `postgresql.persistence.size` | PVC size | `10Gi` |
| `postgresql.env.POSTGRES_DB` | Database name | `todoapp` |
| `postgresql.env.POSTGRES_USER` | Database user | `todouser` |

#### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.hosts[0].host` | Ingress host | `todo-app.local` |
| `ingress.tls` | TLS configuration | `[]` |

### Example Custom Values

```yaml
# values-custom.yaml

global:
  namespace: my-todo-app
  imageRegistry: ghcr.io/myorg

frontend:
  image:
    tag: v2.0.0
  hpa:
    minReplicas: 3
    maxReplicas: 20

backend:
  image:
    tag: v2.0.0
  env:
    LOG_LEVEL: DEBUG

ingress:
  hosts:
    - host: todo.example.com
      paths:
        - path: /api(/|$)(.*)
          backend:
            service:
              name: backend
              port: 8080
        - path: /()(.*)
          backend:
            service:
              name: frontend
              port: 80
  tls:
    - secretName: todo-app-tls
      hosts:
        - todo.example.com

secrets:
  stringData:
    POSTGRES_PASSWORD: "super-secure-password"
    BETTER_AUTH_SECRET: "auth-secret-key"
    OPENAI_API_KEY: "sk-..."
```

## 🔒 Security

### Secrets Management

Update secrets before deploying to production:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=POSTGRES_PASSWORD='secure-password' \
  --from-literal=BETTER_AUTH_SECRET='auth-secret' \
  --from-literal=OPENAI_API_KEY='api-key' \
  -n todo-app
```

### Network Policies

The chart includes network policies for:
- Default deny all ingress traffic
- Allow frontend → backend communication
- Allow backend → postgresql communication
- Allow ingress controller → frontend/backend

### Pod Security

- Non-root users (UID 1000 for app, 999 for postgres)
- Read-only root filesystem (frontend)
- Dropped capabilities
- Seccomp profile: RuntimeDefault

## 📊 Monitoring

### Enable ServiceMonitor (Prometheus Operator)

```yaml
monitoring:
  serviceMonitor:
    enabled: true
    namespace: monitoring
    interval: 30s
```

### Health Endpoints

- **Frontend**: `GET /` (HTTP 200)
- **Backend**: `GET /health` (HTTP 200)
- **PostgreSQL**: `pg_isready` command

## 🔄 Upgrading

```bash
# Upgrade an existing release
helm upgrade todo-app ./helm/todo-app \
  -n todo-app \
  -f values-custom.yaml

# Upgrade with new image tag
helm upgrade todo-app ./helm/todo-app \
  -n todo-app \
  --set frontend.image.tag=v2.0.0 \
  --set backend.image.tag=v2.0.0
```

## 🗑️ Uninstallation

```bash
# Uninstall the chart
helm uninstall todo-app -n todo-app

# Delete namespace (removes everything)
kubectl delete namespace todo-app
```

## 🐛 Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n todo-app
kubectl describe pod <pod-name> -n todo-app
```

### View Logs

```bash
kubectl logs -f deployment/todo-app-frontend -n todo-app
kubectl logs -f deployment/todo-app-backend -n todo-app
kubectl logs -f statefulset/todo-app-postgres -n todo-app
```

### Test Database Connection

```bash
kubectl exec deployment/todo-app-backend -n todo-app -- \
  python -c "import psycopg2; print('DB Connected!')"
```

### Check HPA Status

```bash
kubectl get hpa -n todo-app
kubectl describe hpa todo-app-frontend-hpa -n todo-app
```

## 📝 License

This Helm chart is part of the Todo App project. See the main repository for license information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `helm lint` and `helm template`
5. Submit a pull request

## 📞 Support

- GitHub Issues: https://github.com/BinteZain/-Hackathon_2_Phase_3-/issues
- Documentation: https://github.com/BinteZain/-Hackathon_2_Phase_3-/wiki

---

**Built with ❤️ using Helm 3**
