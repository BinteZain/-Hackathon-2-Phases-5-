# Kubernetes Pod Crash Debugging Guide

**Todo Chatbot - Troubleshooting Reference**

---

## Table of Contents

1. [Possible Causes](#possible-causes)
2. [Inspect Logs](#inspect-logs)
3. [Describe Pods](#describe-pods)
4. [Resource Debugging](#resource-debugging)
5. [Network Debugging](#network-debugging)
6. [Suggested Fixes](#suggested-fixes)
7. [Quick Reference](#quick-reference)

---

## Possible Causes

### 1. Image Pull Issues

| Exit Code | Status | Cause |
|-----------|--------|-------|
| N/A | `ImagePullBackOff` | Invalid image name/tag |
| N/A | `ErrImagePull` | Registry authentication failed |
| N/A | `ErrImageNeverPull` | Image not present with `IfNotPresent` policy |

**Common Issues:**
- Image doesn't exist in registry
- Typo in image name or tag
- Private registry without credentials
- Network connectivity to registry

### 2. Container Startup Failures

| Exit Code | Status | Cause |
|-----------|--------|-------|
| 1 | `CrashLoopBackOff` | Application error |
| 126 | `CrashLoopBackOff` | Command not executable |
| 127 | `CrashLoopBackOff` | Command not found |
| 137 | `CrashLoopBackOff` | OOMKilled (memory limit) |
| 143 | `CrashLoopBackOff` | SIGTERM (graceful shutdown) |

### 3. Configuration Issues

| Status | Cause |
|--------|-------|
| `CreateContainerConfigError` | Missing secret/configmap |
| `InvalidImageName` | Malformed image reference |
| `RunContainerError` | Container runtime error |

### 4. Resource Issues

| Status | Cause |
|--------|-------|
| `OOMKilled` | Memory limit exceeded |
| `Evicted` | Node resource pressure |
| `Pending` | Insufficient cluster resources |

### 5. Probe Failures

| Status | Cause |
|--------|-------|
| `Unhealthy` (Liveness) | Container restarted due to failed liveness probe |
| `Unhealthy` (Readiness) | Container not receiving traffic |

### 6. Network Issues

| Status | Cause |
|--------|-------|
| `ContainerCreating` | CNI plugin issues |
| `Pending` | Network policy blocking |

---

## Inspect Logs

### View Current Logs

```bash
# View logs for all pods with label
kubectl logs -n todo-app -l app.kubernetes.io/name=todo-app

# View logs for specific pod
kubectl logs -n todo-app <pod-name>

# View logs for specific container (multi-container pods)
kubectl logs -n todo-app <pod-name> -c <container-name>

# Follow logs in real-time
kubectl logs -n todo-app <pod-name> -f

# Show timestamps
kubectl logs -n todo-app <pod-name> --timestamps

# Show last N lines
kubectl logs -n todo-app <pod-name> --tail=100

# Show logs from previous instance (after crash)
kubectl logs -n todo-app <pod-name> --previous
```

### View Logs for Crashed Pods

```bash
# Get crashed pods
kubectl get pods -n todo-app --field-selector=status.phase=Failed

# View logs from crashed pod
kubectl logs -n todo-app <crashed-pod-name> --previous

# Save logs to file for analysis
kubectl logs -n todo-app <pod-name> --previous > crash-logs.txt
```

### Filter Logs

```bash
# Search for errors
kubectl logs -n todo-app <pod-name> | grep -i error

# Search for specific patterns
kubectl logs -n todo-app <pod-name> | grep -E "ERROR|FATAL|Exception"

# View logs from last minute
kubectl logs -n todo-app <pod-name> --since=1m

# View logs from specific time
kubectl logs -n todo-app <pod-name> --since-time=2026-02-21T10:00:00Z
```

### All Pods at Once

```bash
# View logs for all pods in namespace
kubectl logs -n todo-app --all-containers=true

# View logs with pod names
kubectl logs -n todo-app --all-containers=true --prefix=true
```

---

## Describe Pods

### Basic Pod Description

```bash
# Describe specific pod
kubectl describe pod -n todo-app <pod-name>

# Describe all pods in namespace
kubectl describe pods -n todo-app

# Describe pods by label
kubectl describe pods -n todo-app -l app.kubernetes.io/component=frontend
```

### Key Sections to Check

When running `kubectl describe pod`, focus on these sections:

#### 1. Status Section
```
Name:         todo-app-frontend-xxxxxxxxxx-xxxxx
Namespace:    todo-app
Priority:     0
Node:         minikube/192.168.49.2
Start Time:   Sat, 21 Feb 2026 10:00:00 +0500
Labels:       app.kubernetes.io/name=todo-app
Status:       Running  # ← Check this
IP:           172.17.0.5
Containers:
  frontend:
    State:    Running  # ← Or Waiting/CrashLoopBackOff
      Started:      Sat, 21 Feb 2026 10:00:05 +0500
    Ready:    True   # ← Should be True
    Restart Count: 3  # ← High number indicates crashes
```

#### 2. Events Section (Most Important!)
```
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  5m                 default-scheduler  Successfully assigned todo-app/todo-app-frontend-xxx to minikube
  Normal   Pulling    5m                 kubelet            Pulling image "phase3-frontend:latest"
  Normal   Pulled     5m                 kubelet            Successfully pulled image
  Normal   Created    5m                 kubelet            Created container frontend
  Normal   Started    5m                 kubelet            Started container frontend
  Warning  Unhealthy  2m (x5 over 4m)    kubelet            Liveness probe failed: HTTP probe failed with statuscode: 503
  Normal   Killing    2m (x5 over 4m)    kubelet            Container frontend failed liveness probe, will be restarted
```

#### 3. Check Exit Codes
```
    State:          Terminated
      Reason:       Error
      Exit Code:    137  # ← OOMKilled
      Started:      Sat, 21 Feb 2026 10:00:05 +0500
      Finished:     Sat, 21 Feb 2026 10:05:00 +0500
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1    # ← Application error
```

### Common Exit Codes

| Exit Code | Meaning | Fix |
|-----------|---------|-----|
| 0 | Success (normal exit) | No action needed |
| 1 | Application error | Check application logs |
| 126 | Command not executable | Check command/args in deployment |
| 127 | Command not found | Check command/args, missing binary |
| 137 | OOMKilled (128+9) | Increase memory limits |
| 143 | SIGTERM (128+15) | Graceful shutdown issue |
| 134 | SIGABRT (128+6) | Application abort |

### Describe Related Resources

```bash
# Describe deployment
kubectl describe deployment -n todo-app todo-app-frontend

# Describe replica set
kubectl describe replicaset -n todo-app todo-app-frontend-xxxxxxxxxx

# Describe service account
kubectl describe serviceaccount -n todo-app todo-app-sa

# Describe secrets
kubectl describe secret -n todo-app todo-app-secrets

# Describe configmap
kubectl describe configmap -n todo-app todo-app-config
```

---

## Resource Debugging

### Check Resource Usage

```bash
# View resource usage for all pods
kubectl top pods -n todo-app

# View resource usage for nodes
kubectl top nodes

# View resource usage for specific pod
kubectl top pod -n todo-app <pod-name>
```

### Check Resource Limits

```bash
# View resource requests/limits
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources}{"\n"}{end}'

# Describe to see resources
kubectl describe pod -n todo-app <pod-name> | grep -A 5 "Limits:"
kubectl describe pod -n todo-app <pod-name> | grep -A 5 "Requests:"
```

### Check for OOMKilled

```bash
# Find OOMKilled pods
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}: {.status.containerStatuses[*].lastState.terminated.reason}{"\n"}{end}' | grep OOMKilled

# Check dmesg for OOM events (on node)
kubectl debug node/minikube -it --image=ubuntu -- dmesg | grep -i "killed process"
```

### Check Node Resources

```bash
# Check node capacity
kubectl describe node minikube | grep -A 10 "Allocated resources"

# Check node conditions
kubectl describe node minikube | grep -A 5 "Conditions:"

# Check if node is ready
kubectl get nodes
```

### Resource Quota Issues

```bash
# Check resource quotas
kubectl describe resourcequota -n todo-app

# Check limit range
kubectl describe limitrange -n todo-app

# Check if quota is exceeded
kubectl get resourcequota -n todo-app -o wide
```

### Fix Resource Issues

```bash
# Increase memory limits (Helm)
helm upgrade todo-app . -n todo-app \
  --set frontend.resources.limits.memory=1Gi \
  --set backend.resources.limits.memory=2Gi

# Increase CPU limits
helm upgrade todo-app . -n todo-app \
  --set frontend.resources.limits.cpu=1000m \
  --set backend.resources.limits.cpu=1500m

# Adjust via kubectl (temporary)
kubectl set resources deployment todo-app-frontend -n todo-app \
  --limits=memory=1Gi,cpu=1000m
```

---

## Network Debugging

### Check Pod Network

```bash
# Get pod IP
kubectl get pod -n todo-app <pod-name> -o jsonpath='{.status.podIP}'

# Get pod IP and node IP
kubectl get pod -n todo-app <pod-name> -o wide

# Check pod network status
kubectl describe pod -n todo-app <pod-name> | grep -A 5 "Network"
```

### Test Pod Connectivity

```bash
# Exec into pod and test connectivity
kubectl exec -it -n todo-app <pod-name> -- sh

# Inside pod, test:
# wget http://todo-app-backend:8080/health
# curl http://todo-app-backend:8080/health
# nslookup todo-app-backend.todo-app.svc.cluster.local
```

### Test Service Connectivity

```bash
# Run test pod
kubectl run test-pod --rm -it --image=busybox --restart=Never -n todo-app -- sh

# Inside test pod:
# wget -qO- http://todo-app-frontend.todo-app.svc.cluster.local
# wget -qO- http://todo-app-backend.todo-app.svc.cluster.local:8080/health
# nslookup todo-app-frontend
```

### Check DNS Resolution

```bash
# Test DNS from within cluster
kubectl run dns-test --rm -it --image=busybox --restart=Never -n todo-app -- nslookup todo-app-frontend.todo-app.svc.cluster.local

# Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Check CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns
```

### Check Network Policies

```bash
# List network policies
kubectl get networkpolicy -n todo-app

# Describe network policy
kubectl describe networkpolicy todo-app-network-policy -n todo-app

# Check if network policy is blocking
kubectl get networkpolicy -n todo-app -o yaml
```

### Check Ingress

```bash
# Get ingress
kubectl get ingress -n todo-app

# Describe ingress
kubectl describe ingress todo-app-ingress -n todo-app

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Check Service Endpoints

```bash
# Get endpoints
kubectl get endpoints -n todo-app

# Describe endpoints
kubectl describe endpoints todo-app-frontend -n todo-app
kubectl describe endpoints todo-app-backend -n todo-app

# Check if endpoints have addresses
kubectl get endpoints todo-app-frontend -n todo-app -o jsonpath='{.subsets[*].addresses}'
```

---

## Suggested Fixes

### Fix 1: Image Pull Issues

```bash
# Verify image exists
docker pull phase3-frontend:latest

# Check image name in deployment
kubectl get deployment -n todo-app todo-app-frontend -o jsonpath='{.spec.template.spec.containers[*].image}'

# Fix image reference
helm upgrade todo-app . -n todo-app \
  --set frontend.image.repository=correct-repo/phase3-frontend \
  --set frontend.image.tag=v1.0.0

# Add image pull secret
kubectl create secret docker-registry registry-credentials \
  --docker-server=docker.io \
  --docker-username=your-username \
  --docker-password=your-password \
  -n todo-app

helm upgrade todo-app . -n todo-app \
  --set global.imagePullSecrets[0].name=registry-credentials
```

### Fix 2: CrashLoopBackOff

```bash
# Check logs for error
kubectl logs -n todo-app <pod-name> --previous

# Check if command is correct
kubectl get deployment -n todo-app todo-app-frontend -o jsonpath='{.spec.template.spec.containers[*].command}'
kubectl get deployment -n todo-app todo-app-frontend -o jsonpath='{.spec.template.spec.containers[*].args}'

# Fix command/args in values.yaml and upgrade
helm upgrade todo-app . -n todo-app \
  --set frontend.command[0]=npm \
  --set frontend.command[1]=start
```

### Fix 3: OOMKilled (Exit Code 137)

```bash
# Check current memory usage
kubectl top pods -n todo-app

# Increase memory limits
helm upgrade todo-app . -n todo-app \
  --set frontend.resources.limits.memory=1Gi \
  --set frontend.resources.requests.memory=256Mi \
  --set backend.resources.limits.memory=2Gi \
  --set backend.resources.requests.memory=512Mi

# Or edit deployment directly
kubectl edit deployment -n todo-app todo-app-frontend
```

### Fix 4: Probe Failures

```bash
# Check current probe configuration
kubectl get deployment -n todo-app todo-app-frontend -o jsonpath='{.spec.template.spec.containers[*].livenessProbe}'
kubectl get deployment -n todo-app todo-app-frontend -o jsonpath='{.spec.template.spec.containers[*].readinessProbe}'

# Increase initial delay
helm upgrade todo-app . -n todo-app \
  --set frontend.probes.liveness.initialDelaySeconds=60 \
  --set frontend.probes.readiness.initialDelaySeconds=30

# Or disable probes temporarily
helm upgrade todo-app . -n todo-app \
  --set frontend.probes.liveness.enabled=false \
  --set frontend.probes.readiness.enabled=false
```

### Fix 5: Missing ConfigMap/Secret

```bash
# Check if configmap exists
kubectl get configmap -n todo-app

# Check if secret exists
kubectl get secret -n todo-app

# Create missing configmap
kubectl create configmap todo-app-config \
  --from-literal=KEY=value \
  -n todo-app

# Create missing secret
kubectl create secret generic todo-app-secrets \
  --from-literal=API_KEY=secret-key \
  -n todo-app

# Restart pods to pick up changes
kubectl rollout restart deployment -n todo-app
```

### Fix 6: Pending Pods (Insufficient Resources)

```bash
# Check node resources
kubectl describe node minikube | grep -A 10 "Allocated resources"

# Reduce resource requests
helm upgrade todo-app . -n todo-app \
  --set frontend.resources.requests.cpu=50m \
  --set frontend.resources.requests.memory=64Mi \
  --set backend.resources.requests.cpu=100m \
  --set backend.resources.requests.memory=128Mi

# Or add more nodes (for production clusters)
# minikube node list
```

### Fix 7: Network Policy Blocking

```bash
# Check current network policy
kubectl get networkpolicy -n todo-app -o yaml

# Temporarily remove network policy
kubectl delete networkpolicy -n todo-app todo-app-network-policy

# Or modify to allow traffic
kubectl edit networkpolicy -n todo-app todo-app-network-policy
```

### Fix 8: DNS Issues

```bash
# Restart CoreDNS
kubectl rollout restart deployment -n kube-system coredns

# Check DNS configuration
kubectl exec -it -n todo-app <pod-name> -- cat /etc/resolv.conf

# Use hostNetwork temporarily (debug only)
kubectl edit deployment -n todo-app todo-app-frontend
# Add: hostNetwork: true
```

---

## Quick Reference

### Debugging Workflow

```bash
# 1. Check pod status
kubectl get pods -n todo-app

# 2. Describe problematic pod
kubectl describe pod -n todo-app <pod-name>

# 3. Check logs
kubectl logs -n todo-app <pod-name> --previous

# 4. Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# 5. Check resources
kubectl top pods -n todo-app

# 6. Test connectivity
kubectl exec -it -n todo-app <pod-name> -- wget -qO- http://backend:8080/health

# 7. Fix and restart
helm upgrade todo-app . -n todo-app --set <fix>
kubectl rollout restart deployment -n todo-app
```

### Common Commands

| Issue | Command |
|-------|---------|
| Pod crashing | `kubectl logs <pod> --previous` |
| Pod pending | `kubectl describe pod <pod>` |
| Image pull fail | `kubectl describe pod <pod>` |
| OOMKilled | `kubectl top pods` + increase limits |
| Probe fail | `kubectl describe pod <pod>` + adjust probes |
| Network issue | `kubectl exec <pod> -- wget <service>` |
| DNS issue | `kubectl exec <pod> -- nslookup <service>` |

### Exit Code Quick Reference

| Code | Command | Fix |
|------|---------|-----|
| 1 | `logs --previous` | Fix application error |
| 126 | `describe pod` | Fix command permissions |
| 127 | `describe pod` | Fix command path |
| 137 | `top pods` | Increase memory |
| 143 | `logs --previous` | Handle SIGTERM |

---

## Debugging Script

```powershell
# Save as debug-pods.ps1

param(
    [string]$Namespace = "todo-app",
    [string]$PodName = ""
)

Write-Host "=== Kubernetes Pod Debugging ===" -ForegroundColor Green
Write-Host "Namespace: $Namespace" -ForegroundColor Yellow

# Get pod status
Write-Host "`n[1/7] Pod Status" -ForegroundColor Yellow
kubectl get pods -n $Namespace

if ($PodName) {
    # Describe pod
    Write-Host "`n[2/7] Pod Description" -ForegroundColor Yellow
    kubectl describe pod -n $Namespace $PodName

    # Get logs
    Write-Host "`n[3/7] Current Logs" -ForegroundColor Yellow
    kubectl logs -n $Namespace $PodName --tail=50

    Write-Host "`n[4/7] Previous Logs (if crashed)" -ForegroundColor Yellow
    kubectl logs -n $Namespace $PodName --previous --tail=50

    # Check events
    Write-Host "`n[5/7] Recent Events" -ForegroundColor Yellow
    kubectl get events -n $Namespace --sort-by='.lastTimestamp' | Select-Object -Last 20

    # Check resources
    Write-Host "`n[6/7] Resource Usage" -ForegroundColor Yellow
    kubectl top pods -n $Namespace $PodName --print-metrics=true

    # Test connectivity
    Write-Host "`n[7/7] Network Test" -ForegroundColor Yellow
    kubectl exec -n $Namespace $PodName -- wget -qO- http://localhost:3000 2>&1
} else {
    Write-Host "`nSpecify -PodName for detailed debugging" -ForegroundColor Yellow
}

Write-Host "`n=== Debug Complete ===" -ForegroundColor Green
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-21  
**Compatible With:** Kubernetes v1.25+
