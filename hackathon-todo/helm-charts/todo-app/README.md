# Todo Chatbot Helm Chart

A production-ready Helm chart for deploying the Todo Chatbot application on Kubernetes.

## Features

- ✅ **Multi-component deployment**: Frontend (Next.js) and Backend (FastAPI/Express)
- ✅ **Auto-scaling**: Horizontal Pod Autoscaler (HPA) for both components
- ✅ **High availability**: Pod Disruption Budgets and anti-affinity rules
- ✅ **Security**: Network policies, RBAC, non-root containers, read-only filesystems
- ✅ **Resource management**: Resource quotas, limit ranges, and configurable limits
- ✅ **Ingress**: NGINX ingress with path-based routing
- ✅ **Health checks**: Liveness and readiness probes
- ✅ **ConfigMaps & Secrets**: Centralized configuration management
- ✅ **Namespace isolation**: Automatic namespace creation
- ✅ **Monitoring ready**: Service monitor support (optional)

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- NGINX Ingress Controller (optional, for ingress)
- Metrics Server (required for HPA)

## Installation

### Quick Start (Minikube)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable ingress and metrics-server
minikube addons enable ingress
minikube addons enable metrics-server

# Navigate to chart directory
cd helm-charts/todo-app

# Install with Minikube values
helm install todo-app . -f values-minikube.yaml

# Check deployment
kubectl get all -n todo-app
```

### Production Deployment

```bash
# Create namespace
kubectl create namespace todo-app

# Create image pull secret (if using private registry)
kubectl create secret docker-registry registry-credentials \
  --docker-server=ghcr.io \
  --docker-username=your-username \
  --docker-password=your-token \
  -n todo-app

# Install with production values
helm install todo-app . \
  -f values-production.yaml \
  --namespace todo-app \
  --create-namespace

# Monitor rollout
kubectl rollout status deployment/todo-app-frontend -n todo-app
kubectl rollout status deployment/todo-app-backend -n todo-app
```

### Custom Configuration

```bash
# Install with custom values
helm install todo-app . \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3 \
  --set ingress.hosts[0].host=todo.example.com \
  --namespace todo-app \
  --create-namespace
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Kubernetes namespace | `todo-app` |
| `frontend.replicaCount` | Frontend replicas | `2` |
| `frontend.autoscaling.enabled` | Enable HPA for frontend | `true` |
| `backend.replicaCount` | Backend replicas | `2` |
| `backend.autoscaling.enabled` | Enable HPA for backend | `true` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.hosts` | Ingress hosts | `todo-app.local` |
| `resourceQuota.enabled` | Enable resource quota | `true` |
| `networkPolicy.enabled` | Enable network policy | `true` |

### Values Files

- `values.yaml` - Default values
- `values-minikube.yaml` - Minikube-optimized values
- `values-production.yaml` - Production-hardened values

## Accessing the Application

### Via Ingress

```bash
# Get ingress IP
minikube ip

# Add to hosts file
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Access application
open http://todo-app.local
```

### Via Port Forwarding

```bash
# Frontend
kubectl port-forward svc/todo-app-frontend -n todo-app 3000:80

# Backend
kubectl port-forward svc/todo-app-backend -n todo-app 3001:8080

# Access
# Frontend: http://localhost:3000
# Backend Health: http://localhost:3001/health
```

## Monitoring

### Check Deployment Status

```bash
# View all resources
kubectl get all -n todo-app

# View pods
kubectl get pods -n todo-app

# View HPA
kubectl get hpa -n todo-app

# View ingress
kubectl get ingress -n todo-app
```

### View Logs

```bash
# Frontend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=frontend -f

# Backend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f
```

### Scaling

```bash
# Manual scale
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Check HPA
kubectl get hpa -n todo-app
kubectl describe hpa todo-app-frontend-hpa -n todo-app
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-app . -f values.yaml

# Upgrade with new image tag
helm upgrade todo-app . \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0

# Rollback
helm rollback todo-app -n todo-app

# View history
helm history todo-app -n todo-app
```

## Uninstall

```bash
# Uninstall chart
helm uninstall todo-app -n todo-app

# Delete namespace (removes all resources)
kubectl delete namespace todo-app
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod -n todo-app -l app.kubernetes.io/name=todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n todo-app <pod-name>
```

### HPA Not Scaling

```bash
# Check metrics-server
kubectl top pods -n todo-app

# Describe HPA
kubectl describe hpa -n todo-app

# Check resource requests
kubectl get deployment -n todo-app -o yaml | grep -A 5 resources
```

### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Describe ingress
kubectl describe ingress todo-app-ingress -n todo-app

# Test backend directly
kubectl port-forward svc/todo-app-backend -n todo-app 3001:8080
curl http://localhost:3001/health
```

## Security Considerations

- Non-root containers (UID 1001)
- Read-only root filesystem (frontend)
- Dropped capabilities
- Network policies restrict pod-to-pod communication
- RBAC with minimal permissions
- Secrets managed separately (consider sealed-secrets or external-secrets)

## Resource Requirements

### Minimum (Minikube)

- CPU: 2 cores
- Memory: 4Gi
- Storage: 10Gi

### Recommended (Production)

- CPU: 4+ cores
- Memory: 8Gi+
- Storage: 20Gi+

## Chart Structure

```
todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-minikube.yaml    # Minikube overrides
├── values-production.yaml  # Production overrides
├── .helmignore             # Files to exclude
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── NOTES.txt           # Post-install notes
    ├── namespace.yaml      # Namespace creation
    ├── serviceaccount.yaml # Service account
    ├── configmap.yaml      # ConfigMap
    ├── secrets.yaml        # Secrets
    ├── deployment-frontend.yaml
    ├── deployment-backend.yaml
    ├── service-frontend.yaml
    ├── service-backend.yaml
    ├── ingress.yaml
    ├── hpa-frontend.yaml
    ├── hpa-backend.yaml
    ├── rbac.yaml
    ├── networkpolicy.yaml
    ├── pdb.yaml
    ├── resourcequota.yaml
    └── limitrange.yaml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test with `helm lint` and `helm template`
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please create an issue in the repository.
