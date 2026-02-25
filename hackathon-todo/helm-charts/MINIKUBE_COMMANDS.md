# Minikube + Helm Deployment Commands
**Todo Chatbot - Quick Reference**

---

## 1. Enable Ingress in Minikube

```bash
# Start Minikube (if not already running)
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable NGINX Ingress Controller
minikube addons enable ingress

# Verify ingress addon is enabled
minikube addons list | findstr ingress

# Wait for ingress controller pods to be ready
kubectl wait --namespace ingress-nginx ^
  --for=condition=ready pod ^
  --selector=app.kubernetes.io/component=controller ^
  --timeout=90s

# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Expected output:
# NAME                                        READY   STATUS      RESTARTS   AGE
# ingress-nginx-admission-create-xxxxx        0/1     Completed   0          2m
# ingress-nginx-admission-patch-xxxxx         0/1     Completed   0          2m
# ingress-nginx-controller-xxxxxxxxxx-xxxxx   1/1     Running     0          2m
```

---

## 2. Create Namespace

```bash
# Create namespace manually (optional - Helm can create it)
kubectl create namespace todo-app

# Verify namespace was created
kubectl get namespace todo-app

# Label namespace for identification
kubectl label namespace todo-app environment=production

# Verify label
kubectl get namespace todo-app --show-labels

# Alternative: Let Helm create namespace during install
# (No manual step needed - use --create-namespace flag)
```

---

## 3. Install Helm Chart

```bash
# Navigate to chart directory
cd helm-charts/todo-app

# Dry run first (validate templates)
helm install todo-app . --dry-run --debug

# Install with Minikube values
helm install todo-app . -f values-minikube.yaml --create-namespace

# Install with custom namespace
helm install todo-app . -f values-minikube.yaml --namespace todo-app --create-namespace

# Install with inline overrides
helm install todo-app . ^
  --set frontend.replicaCount=3 ^
  --set backend.replicaCount=3 ^
  --set ingress.enabled=true ^
  --namespace todo-app ^
  --create-namespace

# Verify installation
helm list -n todo-app

# Check release status
helm status todo-app -n todo-app

# Expected output:
# NAME: todo-app
# NAMESPACE: todo-app
# STATUS: deployed
# REVISION: 1
```

---

## 4. Verify Pods

```bash
# List all pods in namespace
kubectl get pods -n todo-app

# List pods with wider output
kubectl get pods -n todo-app -o wide

# Watch pods until ready
kubectl get pods -n todo-app --watch

# Check pod details
kubectl describe pod -n todo-app -l app.kubernetes.io/name=todo-app

# Check specific pod logs
kubectl logs -n todo-app <pod-name>

# Check frontend pod logs
kubectl logs -n todo-app -l app.kubernetes.io/component=frontend -f

# Check backend pod logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend -f

# Verify pod health
kubectl get pods -n todo-app --field-selector=status.phase=Running

# Check for pending pods
kubectl get pods -n todo-app --field-selector=status.phase=Pending

# Check for crashed pods
kubectl get pods -n todo-app --field-selector=status.phase=Failed

# Expected output:
# NAME                                 READY   STATUS    RESTARTS   AGE
# todo-app-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# todo-app-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# todo-app-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
# todo-app-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
```

---

## 5. Verify Services

```bash
# List all services
kubectl get svc -n todo-app

# List services with wider output
kubectl get svc -n todo-app -o wide

# Get service details
kubectl describe svc -n todo-app

# Check frontend service
kubectl describe svc todo-app-frontend -n todo-app

# Check backend service
kubectl describe svc todo-app-backend -n todo-app

# Verify service endpoints
kubectl get endpoints -n todo-app

# Describe endpoints
kubectl describe endpoints todo-app-frontend -n todo-app
kubectl describe endpoints todo-app-backend -n todo-app

# Test service connectivity
kubectl run test-pod --rm -it --image=busybox --restart=Never -- ^
  wget -qO- http://todo-app-frontend.todo-app.svc.cluster.local

# Expected output:
# NAME              TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)   AGE
# todo-app-frontend ClusterIP   10.96.xxx.xxx    <none>        80/TCP    5m
# todo-app-backend  ClusterIP   10.96.yyy.yyy    <none>        8080/TCP  5m
```

---

## 6. Access Application in Browser

### Method 1: Via Ingress (Recommended)

```bash
# Get Minikube IP
minikube ip

# Add to hosts file (Windows - Run PowerShell as Administrator)
$MINIKUBE_IP = minikube ip
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "$MINIKUBE_IP todo-app.local"

# Verify hosts entry
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String "todo-app.local"

# Access in browser
start http://todo-app.local

# Or test with curl
curl http://todo-app.local
curl http://todo-app.local/api/health
```

### Method 2: Via Port Forwarding (Frontend)

```bash
# Start port forwarding for frontend
kubectl port-forward svc/todo-app-frontend -n todo-app 3000:80

# Access in browser
start http://localhost:3000

# Test with curl
curl http://localhost:3000
```

### Method 3: Via Port Forwarding (Backend)

```bash
# Start port forwarding for backend
kubectl port-forward svc/todo-app-backend -n todo-app 3001:8080

# Test health endpoint
curl http://localhost:3001/health

# Access in browser
start http://localhost:3001/health
```

### Method 4: Via Minikube Service Command

```bash
# Open frontend in browser
minikube service todo-app-frontend -n todo-app --url

# Open backend in browser
minikube service todo-app-backend -n todo-app --url

# Get URLs without opening browser
minikube service todo-app-frontend -n todo-app --url
minikube service todo-app-backend -n todo-app --url
```

---

## 7. Scale Deployments

### Manual Scaling

```bash
# Scale frontend to 5 replicas
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Scale backend to 10 replicas
kubectl scale deployment todo-app-backend -n todo-app --replicas=10

# Verify scaling
kubectl get pods -n todo-app

# Watch scaling in real-time
kubectl get pods -n todo-app --watch

# Wait for rollout to complete
kubectl rollout status deployment/todo-app-frontend -n todo-app
kubectl rollout status deployment/todo-app-backend -n todo-app
```

### Autoscaling (HPA)

```bash
# Check HPA status
kubectl get hpa -n todo-app

# Describe HPA
kubectl describe hpa todo-app-frontend-hpa -n todo-app
kubectl describe hpa todo-app-backend-hpa -n todo-app

# Watch HPA metrics
kubectl get hpa -n todo-app --watch

# Trigger scaling with load test (Apache Bench)
ab -n 10000 -c 100 http://todo-app.local/

# Watch pods scale up
watch kubectl get pods -n todo-app

# Check scaling events
kubectl get events -n todo-app --field-selector reason=SuccessfulRescale
```

### Scale via Helm Upgrade

```bash
# Upgrade with new replica counts
helm upgrade todo-app . -n todo-app ^
  --set frontend.replicaCount=5 ^
  --set backend.replicaCount=8

# Verify
kubectl get pods -n todo-app
```

---

## 8. Perform Rolling Update

### Update Image Tag

```bash
# Upgrade with new image tag
helm upgrade todo-app . -n todo-app ^
  --set frontend.image.tag=v1.1.0 ^
  --set backend.image.tag=v1.1.0

# Monitor rollout
kubectl rollout status deployment/todo-app-frontend -n todo-app
kubectl rollout status deployment/todo-app-backend -n todo-app

# Watch pods update
kubectl get pods -n todo-app --watch
```

### Update Configuration

```bash
# Update environment variables
helm upgrade todo-app . -n todo-app ^
  --set frontend.env.LOG_LEVEL=debug ^
  --set backend.env.LOG_LEVEL=debug

# Update resource limits
helm upgrade todo-app . -n todo-app ^
  --set frontend.resources.limits.cpu=750m ^
  --set frontend.resources.limits.memory=768Mi
```

### Rollback

```bash
# View rollout history
helm history todo-app -n todo-app

# Rollback to previous revision
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 1 -n todo-app

# Verify rollback
kubectl get pods -n todo-app
```

### Canary Deployment (Advanced)

```bash
# Update with canary deployment
helm upgrade todo-app . -n todo-app ^
  --set frontend.image.tag=v1.1.0 ^
  --set frontend.replicaCount=1 ^
  --wait --timeout=5m

# Test canary
curl http://todo-app.local

# If successful, scale up
kubectl scale deployment todo-app-frontend -n todo-app --replicas=3

# If failed, rollback
helm rollback todo-app -n todo-app
```

---

## Complete Deployment Script

```powershell
# Save as deploy.ps1 and run in PowerShell

Write-Host "=== Starting Todo Chatbot Deployment ===" -ForegroundColor Green

# 1. Start Minikube
Write-Host "`n[1/8] Starting Minikube..." -ForegroundColor Yellow
minikube start --cpus=4 --memory=8192

# 2. Enable Ingress
Write-Host "`n[2/8] Enabling Ingress..." -ForegroundColor Yellow
minikube addons enable ingress

# 3. Enable Metrics Server
Write-Host "`n[3/8] Enabling Metrics Server..." -ForegroundColor Yellow
minikube addons enable metrics-server

# 4. Navigate to chart
Write-Host "`n[4/8] Installing Helm Chart..." -ForegroundColor Yellow
Set-Location "helm-charts/todo-app"
helm install todo-app . -f values-minikube.yaml --create-namespace

# 5. Wait for deployment
Write-Host "`n[5/8] Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --namespace todo-app --for=condition=ready pod --selector=app.kubernetes.io/name=todo-app --timeout=120s

# 6. Configure hosts
Write-Host "`n[6/8] Configuring hosts file..." -ForegroundColor Yellow
$MINIKUBE_IP = minikube ip
$HOSTS_PATH = "C:\Windows\System32\drivers\etc\hosts"
if (!(Get-Content $HOSTS_PATH | Select-String "todo-app.local")) {
    Add-Content -Path $HOSTS_PATH -Value "$MINIKUBE_IP todo-app.local"
    Write-Host "Added hosts entry: $MINIKUBE_IP todo-app.local" -ForegroundColor Green
}

# 7. Verify deployment
Write-Host "`n[7/8] Verifying deployment..." -ForegroundColor Yellow
kubectl get all -n todo-app

# 8. Open application
Write-Host "`n[8/8] Opening application..." -ForegroundColor Yellow
start http://todo-app.local

Write-Host "`n=== Deployment Complete! ===" -ForegroundColor Green
Write-Host "Access application at: http://todo-app.local" -ForegroundColor Cyan
```

---

## Quick Reference Table

| Command | Description |
|---------|-------------|
| `minikube start` | Start Minikube cluster |
| `minikube addons enable ingress` | Enable NGINX Ingress |
| `helm install todo-app .` | Install Helm chart |
| `kubectl get pods -n todo-app` | List pods |
| `kubectl get svc -n todo-app` | List services |
| `kubectl scale deployment` | Scale manually |
| `helm upgrade todo-app .` | Upgrade release |
| `helm rollback todo-app` | Rollback release |
| `kubectl rollout status` | Monitor rollout |
| `kubectl logs -n todo-app` | View logs |

---

## Troubleshooting Commands

```bash
# Check cluster status
minikube status

# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n todo-app

# Describe problematic pod
kubectl describe pod -n todo-app <pod-name>

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Restart deployment
kubectl rollout restart deployment/todo-app-frontend -n todo-app

# Delete pod (auto-recreate)
kubectl delete pod -n todo-app <pod-name>

# Check ingress
kubectl get ingress -n todo-app
kubectl describe ingress todo-app-ingress -n todo-app

# Test connectivity
kubectl run test --rm -it --image=busybox --restart=Never -- wget -qO- http://todo-app-backend.todo-app.svc.cluster.local:8080/health
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-21  
**Compatible With:** Minikube v1.32+, Helm v3+, Kubernetes v1.25+
