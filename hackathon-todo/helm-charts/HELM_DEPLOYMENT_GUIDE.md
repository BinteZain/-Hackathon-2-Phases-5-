# Helm Chart Deployment Guide

**Chart:** Todo Chatbot  
**Version:** 1.0.0  
**Location:** `helm-charts/todo-app/`

---

## Quick Start

### 1. Prerequisites Check

```bash
# Verify Kubernetes cluster
kubectl cluster-info

# Verify Helm
helm version

# Verify metrics-server (required for HPA)
kubectl top nodes
```

### 2. Deploy to Minikube

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Navigate to chart
cd helm-charts/todo-app

# Install with Minikube values
helm install todo-app . -f values-minikube.yaml

# Check status
kubectl get all -n todo-app
```

### 3. Access Application

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (Windows - run as Administrator)
echo "$(minikube ip) todo-app.local" >> C:\Windows\System32\drivers\etc\hosts

# Access in browser
start http://todo-app.local
```

---

## Chart Structure

```
todo-app/
├── Chart.yaml                 # Chart metadata
├── values.yaml                # Default values (350+ options)
├── values-minikube.yaml       # Minikube-optimized
├── values-production.yaml     # Production-hardened
├── .helmignore                # Exclude patterns
├── README.md                  # Documentation
└── templates/
    ├── _helpers.tpl           # Template helpers
    ├── NOTES.txt              # Post-install notes
    ├── namespace.yaml         # Namespace creation
    ├── serviceaccount.yaml    # Service account
    ├── configmap.yaml         # ConfigMap
    ├── secrets.yaml           # Secrets
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

---

## Configuration Options

### Frontend Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frontend.enabled` | `true` | Enable frontend |
| `frontend.replicaCount` | `2` | Number of replicas |
| `frontend.image.repository` | `phase3-frontend` | Image repo |
| `frontend.image.tag` | `latest` | Image tag |
| `frontend.autoscaling.enabled` | `true` | Enable HPA |
| `frontend.autoscaling.minReplicas` | `2` | Min replicas |
| `frontend.autoscaling.maxReplicas` | `10` | Max replicas |
| `frontend.resources.requests.cpu` | `100m` | CPU request |
| `frontend.resources.requests.memory` | `128Mi` | Memory request |
| `frontend.resources.limits.cpu` | `500m` | CPU limit |
| `frontend.resources.limits.memory` | `512Mi` | Memory limit |

### Backend Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `backend.enabled` | `true` | Enable backend |
| `backend.replicaCount` | `2` | Number of replicas |
| `backend.image.repository` | `phase3-backend` | Image repo |
| `backend.image.tag` | `latest` | Image tag |
| `backend.autoscaling.enabled` | `true` | Enable HPA |
| `backend.autoscaling.minReplicas` | `2` | Min replicas |
| `backend.autoscaling.maxReplicas` | `15` | Max replicas |
| `backend.resources.requests.cpu` | `200m` | CPU request |
| `backend.resources.requests.memory` | `256Mi` | Memory request |
| `backend.resources.limits.cpu` | `1000m` | CPU limit |
| `backend.resources.limits.memory` | `1Gi` | Memory limit |

### Ingress Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ingress.enabled` | `true` | Enable ingress |
| `ingress.className` | `nginx` | Ingress class |
| `ingress.hosts[0].host` | `todo-app.local` | Host name |
| `ingress.tls` | `[]` | TLS configuration |

---

## Deployment Commands

### Install

```bash
# Basic install
helm install todo-app . -n todo-app --create-namespace

# With custom values
helm install todo-app . \
  -f values.yaml \
  -n todo-app \
  --create-namespace

# With inline overrides
helm install todo-app . \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3 \
  --set ingress.hosts[0].host=todo.example.com \
  -n todo-app \
  --create-namespace

# Dry run
helm install todo-app . --dry-run --debug
```

### Upgrade

```bash
# Upgrade with new values
helm upgrade todo-app . -f values.yaml

# Upgrade image tags
helm upgrade todo-app . \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0

# Force upgrade
helm upgrade todo-app . --force --recreate-pods

# View rollout history
helm history todo-app -n todo-app
```

### Rollback

```bash
# Rollback to previous revision
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 1 -n todo-app

# View revisions
helm history todo-app -n todo-app
```

### Uninstall

```bash
# Uninstall chart
helm uninstall todo-app -n todo-app

# Uninstall and delete namespace
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```

---

## Monitoring

### Check Deployment Status

```bash
# All resources
kubectl get all -n todo-app

# Deployments
kubectl get deployments -n todo-app

# Pods
kubectl get pods -n todo-app -o wide

# Services
kubectl get svc -n todo-app

# Ingress
kubectl get ingress -n todo-app

# HPA
kubectl get hpa -n todo-app
```

### View Logs

```bash
# Frontend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=frontend -f

# Backend logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f

# Specific pod
kubectl logs -n todo-app <pod-name> -f
```

### Check Health

```bash
# Frontend health
curl http://todo-app.local/

# Backend health
curl http://todo-app.local/api/health

# Via port-forward
kubectl port-forward svc/todo-app-backend -n todo-app 3001:8080
curl http://localhost:3001/health
```

---

## Scaling

### Manual Scaling

```bash
# Scale frontend
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Scale backend
kubectl scale deployment todo-app-backend -n todo-app --replicas=10

# Verify
kubectl get pods -n todo-app
```

### Autoscaling (HPA)

```bash
# Check HPA status
kubectl get hpa -n todo-app

# Describe HPA
kubectl describe hpa todo-app-frontend-hpa -n todo-app

# Watch scaling events
kubectl get events -n todo-app --field-selector reason=SuccessfulRescale
```

### Load Testing

```bash
# Install k6 or use Apache Bench
ab -n 10000 -c 100 http://todo-app.local/

# Watch HPA during load
watch kubectl get hpa -n todo-app
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod -n todo-app -l app.kubernetes.io/name=todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n todo-app <pod-name> --previous
```

### HPA Not Working

```bash
# Check metrics-server
kubectl top pods -n todo-app

# If metrics unavailable, restart metrics-server
kubectl rollout restart deployment metrics-server -n kube-system

# Check HPA
kubectl describe hpa -n todo-app
```

### Ingress Issues

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Describe ingress
kubectl describe ingress todo-app-ingress -n todo-app

# Test backend directly
kubectl port-forward svc/todo-app-backend -n todo-app 3001:8080
curl http://localhost:3001/health
```

### Resource Quota Issues

```bash
# Check quota
kubectl describe resourcequota -n todo-app

# Check limit range
kubectl describe limitrange -n todo-app

# Adjust in values.yaml and upgrade
```

---

## Security

### Service Account

```bash
# View service account
kubectl get sa -n todo-app

# View role
kubectl get role -n todo-app

# View role binding
kubectl get rolebinding -n todo-app
```

### Network Policy

```bash
# View network policy
kubectl get networkpolicy -n todo-app

# Describe policy
kubectl describe networkpolicy todo-app-network-policy -n todo-app
```

### Pod Security

```bash
# Verify non-root
kubectl exec -n todo-app <pod-name> -- id

# Verify capabilities
kubectl exec -n todo-app <pod-name> -- cat /proc/1/status | grep Cap
```

---

## Production Checklist

- [ ] Update image tags to specific versions (not `latest`)
- [ ] Configure TLS for ingress
- [ ] Set up external secrets management
- [ ] Configure resource quotas appropriately
- [ ] Enable pod anti-affinity for HA
- [ ] Set up monitoring and alerting
- [ ] Configure backup for persistent data
- [ ] Test disaster recovery
- [ ] Document runbooks
- [ ] Set up CI/CD pipeline

---

## Useful Helm Commands

```bash
# List releases
helm list -n todo-app

# Get release status
helm status todo-app -n todo-app

# Get values
helm get values todo-app -n todo-app

# Get manifest
helm get manifest todo-app -n todo-app

# Get hooks
helm get hooks todo-app -n todo-app

# Template rendering
helm template todo-app . --debug

# Lint chart
helm lint .

# Package chart
helm package .

# Verify chart
helm lint && helm template test .
```

---

## Next Steps

1. **Deploy to Minikube:** `helm install todo-app . -f values-minikube.yaml`
2. **Test Application:** Access at http://todo-app.local
3. **Validate HPA:** Run load test and watch scaling
4. **Test Failover:** Delete pods and verify recovery
5. **Production Deploy:** Use `values-production.yaml` with modifications

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-21  
**PHR Location:** `history/prompts/infrastructure/005-helm-chart-production.green.prompt.md`
