# Enhanced Infrastructure Guide

**Todo Chatbot - Advanced Deployment Strategies & Monitoring**

**Version:** 2.0.0  
**Last Updated:** 2026-02-21

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Strategies](#deployment-strategies)
3. [RBAC Configuration](#rbac-configuration)
4. [Network Policies](#network-policies)
5. [Pod Disruption Budgets](#pod-disruption-budgets)
6. [Prometheus Monitoring](#prometheus-monitoring)
7. [Grafana Dashboards](#grafana-dashboards)
8. [Local Cluster Compatibility](#local-cluster-compatibility)

---

## Overview

This guide covers the enhanced infrastructure features added to the Todo Chatbot Helm chart:

| Feature | Description | Production Ready |
|---------|-------------|------------------|
| **Blue-Green Deployment** | Zero-downtime deployments with instant rollback | ✅ |
| **Canary Deployment** | Gradual rollout with percentage-based traffic | ✅ |
| **Enhanced RBAC** | Fine-grained access control | ✅ |
| **Network Policies** | Pod-to-pod traffic isolation | ✅ |
| **Pod Disruption Budgets** | High availability during maintenance | ✅ |
| **Prometheus Monitoring** | Metrics collection and alerting | ✅ |
| **Grafana Dashboards** | Visual monitoring | ✅ |

---

## Deployment Strategies

### Rolling Deployment (Default)

Standard Kubernetes rolling update with zero downtime.

```bash
# Install with rolling deployment (default)
helm install todo-app . -f values.yaml

# Upgrade with new version
helm upgrade todo-app . \
  --set frontend.image.tag=v1.1.0 \
  --set backend.image.tag=v1.1.0

# Monitor rollout
kubectl rollout status deployment/todo-app-frontend -n todo-app
```

### Blue-Green Deployment

Deploy two identical environments (blue and green) and switch traffic between them.

```bash
# Install with blue-green strategy
helm install todo-app . \
  --set global.deploymentStrategy=blue-green \
  --set global.activeEnvironment=blue

# Deploy new version to green environment
helm upgrade todo-app . \
  --set global.deploymentStrategy=blue-green \
  --set global.activeEnvironment=blue \
  --set frontend.image.tag=v1.1.0

# Test green environment directly
kubectl port-forward svc/todo-app-frontend-green -n todo-app 3001:3000

# Switch traffic to green
helm upgrade todo-app . \
  --set global.deploymentStrategy=blue-green \
  --set global.activeEnvironment=green

# Rollback to blue (instant)
helm upgrade todo-app . \
  --set global.deploymentStrategy=blue-green \
  --set global.activeEnvironment=blue
```

**Architecture:**
```
                    ┌─────────────┐
                    │   Ingress   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │   Blue Service  │       │  Green Service  │
    │   (Active)      │       │  (Standby)      │
    └────────┬────────┘       └────────┬────────┘
             │                         │
    ┌────────┴────────┐       ┌────────┴────────┐
    │  Blue Pods (2)  │       │ Green Pods (2)  │
    └─────────────────┘       └─────────────────┘
```

### Canary Deployment

Gradually shift traffic from stable to canary deployment.

```bash
# Install with canary deployment (10% traffic to canary)
helm install todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=10

# Increase canary traffic to 25%
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=25

# Increase to 50%
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=50

# Full rollout (100% to new version)
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=100

# Rollback (set canary to 0%)
helm upgrade todo-app . \
  --set global.deploymentStrategy=canary \
  --set global.canaryPercentage=0
```

**Architecture:**
```
                    ┌─────────────┐
                    │   Ingress   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │  Stable (90%)   │       │  Canary (10%)   │
    └────────┬────────┘       └────────┬────────┘
             │                         │
    ┌────────┴────────┐       ┌────────┴────────┐
    │ Stable Pods (9) │       │ Canary Pod (1)  │
    └─────────────────┘       └─────────────────┘
```

### Strategy Comparison

| Feature | Rolling | Blue-Green | Canary |
|---------|---------|------------|--------|
| **Downtime** | Zero | Zero | Zero |
| **Rollback Speed** | Slow | Instant | Fast |
| **Resource Cost** | 1x | 2x | 1.x |
| **Risk** | Low | Lowest | Lowest |
| **Complexity** | Low | Medium | Medium |
| **Best For** | Regular updates | Critical apps | Gradual testing |

---

## RBAC Configuration

### Service Account

Each deployment uses a dedicated service account with minimal permissions.

```yaml
# values.yaml
serviceAccount:
  create: true
  name: todo-app-sa
  annotations: {}
  automountServiceAccountToken: true
```

### Role (Namespace-Scoped)

```yaml
# Permissions granted:
- Pods: get, list, watch
- ConfigMaps: get, list, watch
- Secrets: get (read-only)
- Services: get, list
- Events: get, list
- Deployments: get, list
- HPAs: get, list
```

### Enable Cluster-Wide RBAC (Optional)

```bash
# Enable cluster-wide permissions
helm upgrade todo-app . \
  --set rbac.create=true \
  --set rbac.clusterWide=true
```

### Verify RBAC

```bash
# Check service account
kubectl get sa -n todo-app

# Check role
kubectl get role -n todo-app

# Check role binding
kubectl get rolebinding -n todo-app

# Verify permissions
kubectl auth can-i get pods --as=system:serviceaccount:todo-app:todo-app-sa -n todo-app
```

---

## Network Policies

### Default Deny Policy

All ingress and egress traffic is denied by default.

```bash
# Enable network policies
helm upgrade todo-app . \
  --set networkPolicy.enabled=true
```

### Allowed Traffic Flows

```
┌─────────────────────────────────────────────────────────────┐
│                      Namespace: todo-app                     │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │◄────────│    Backend   │                 │
│  │   (3000)     │         │    (3001)    │                 │
│  └──────┬───────┘         └──────┬───────┘                 │
│         │                        │                          │
│         │    ┌──────────────┐   │                          │
│         └────│   Ingress    │   │                          │
│              │   Controller │   │                          │
│              └──────────────┘   │                          │
│                                 │                          │
│         ┌───────────────────────┴──────────────┐           │
│         │           Egress Rules               │           │
│         │  - DNS (53)                          │           │
│         │  - HTTPS (443, 80)                   │           │
│         │  - Internal (3000, 3001, 5432)       │           │
│         └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Verify Network Policies

```bash
# List network policies
kubectl get networkpolicy -n todo-app

# Describe policy
kubectl describe networkpolicy todo-app-default-deny -n todo-app

# Test connectivity (from test pod)
kubectl run test --rm -it --image=busybox --restart=Never -n todo-app -- \
  wget -qO- http://todo-app-frontend.todo-app.svc.cluster.local
```

---

## Pod Disruption Budgets

PDBs ensure minimum availability during voluntary disruptions.

```yaml
# values.yaml
podDisruptionBudget:
  frontend:
    enabled: true
    minAvailable: 1
  backend:
    enabled: true
    minAvailable: 1
```

### Verify PDBs

```bash
# List PDBs
kubectl get pdb -n todo-app

# Describe PDB
kubectl describe pdb todo-app-frontend-pdb -n todo-app

# Check allowed disruptions
kubectl get pdb -n todo-app -o wide
```

### Test PDB

```bash
# Try to drain node (should respect PDB)
kubectl drain minikube --ignore-daemonsets --delete-emptydir-data

# PDB will block if it would violate minAvailable
```

---

## Prometheus Monitoring

### Installation

```bash
# Install Prometheus Stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Enable monitoring in todo-app
helm upgrade todo-app . \
  --set monitoring.enabled=true \
  --set monitoring.serviceMonitor.enabled=true \
  --set monitoring.prometheusRules.enabled=true
```

### ServiceMonitors

Automatically discovers and scrapes metrics from todo-app services.

```yaml
# Scraping configuration
monitoring:
  enabled: true
  scrapeInterval: 30s
  serviceMonitor:
    enabled: true
```

### Alerting Rules

Pre-configured alerts for common issues:

| Alert | Threshold | Severity |
|-------|-----------|----------|
| PodCrashLooping | >0 restarts in 5m | Critical |
| HighMemoryUsage | >85% | Warning |
| HighCPUUsage | >80% | Warning |
| ServiceDown | 2m uptime == 0 | Critical |
| PodNotReady | 5m not ready | Warning |
| DeploymentReplicasMismatch | 10m mismatch | Warning |
| IngressHighErrorRate | >5% errors | Critical |
| HPAMaxReplicasReached | At max replicas | Warning |

### Verify Monitoring

```bash
# Check ServiceMonitors
kubectl get servicemonitor -n monitoring

# Check PrometheusRules
kubectl get prometheusrule -n monitoring

# Access Prometheus
kubectl port-forward svc/prometheus-operated -n monitoring 9090:80

# Query metrics
curl http://localhost:9090/api/v1/query?query=up{namespace="todo-app"}
```

---

## Grafana Dashboards

### Dashboard Features

The included Grafana dashboard provides:

1. **Running Pods** - Current pod count
2. **Average CPU Usage** - Cluster-wide CPU utilization
3. **Average Memory Usage** - Cluster-wide memory utilization
4. **Pod Restarts** - Crash loop detection
5. **CPU by Container** - Per-container breakdown
6. **Memory by Container** - Per-container breakdown
7. **HPA Replicas** - Auto-scaling visualization
8. **Deployment Replicas** - Desired vs Available

### Access Grafana

```bash
# Get Grafana password
kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d

# Port forward
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Access dashboard
# URL: http://localhost:3000
# Username: admin
# Password: <from command above>
```

### Import Dashboard

The dashboard is automatically imported via ConfigMap when monitoring is enabled.

```bash
# Verify dashboard ConfigMap
kubectl get configmap todo-app-grafana-dashboard -n monitoring

# List Grafana dashboards (via API)
curl -u admin:$(kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d) \
  http://localhost:3000/api/search
```

---

## Local Cluster Compatibility

### Minikube Configuration

The `values-minikube.yaml` file is optimized for local development:

```bash
# Install for Minikube
helm install todo-app . -f values-minikube.yaml

# Key differences from production:
# - Lower resource requests/limits
# - Reduced replica counts
# - Monitoring disabled by default
# - Simplified RBAC
# - Basic network policies
```

### Kind Configuration

```bash
# Create Kind cluster
kind create cluster --name todo-app --config=- <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install
helm install todo-app . -f values-kind.yaml
```

### Resource Requirements

| Environment | CPU | Memory | Storage |
|-------------|-----|--------|---------|
| **Minikube** | 2 cores | 4Gi | 20Gi |
| **Kind** | 2 cores | 4Gi | 20Gi |
| **Production** | 4+ cores | 8Gi+ | 50Gi+ |

### Enable Monitoring on Minikube (Optional)

```bash
# Install Prometheus Stack on Minikube
minikube addons enable prometheus
minikube addons enable grafana

# Enable monitoring in todo-app
helm upgrade todo-app . \
  -f values-minikube.yaml \
  --set monitoring.enabled=true
```

---

## Quick Reference Commands

### Deployment Strategies

```bash
# Rolling (default)
helm install todo-app .

# Blue-Green
helm install todo-app . --set global.deploymentStrategy=blue-green

# Canary (10%)
helm install todo-app . --set global.deploymentStrategy=canary --set global.canaryPercentage=10
```

### Monitoring

```bash
# Enable monitoring
helm upgrade todo-app . --set monitoring.enabled=true

# Access Prometheus
kubectl port-forward svc/prometheus-operated -n monitoring 9090

# Access Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000
```

### Security

```bash
# Verify RBAC
kubectl auth can-i get pods --as=system:serviceaccount:todo-app:todo-app-sa

# Verify NetworkPolicy
kubectl get networkpolicy -n todo-app

# Check PDB
kubectl get pdb -n todo-app
```

---

## Troubleshooting

### Blue-Green Switch Fails

```bash
# Check service selector
kubectl get svc todo-app-frontend -n todo-app -o yaml

# Verify active environment
kubectl get svc todo-app-frontend -n todo-app -o jsonpath='{.metadata.labels.active-environment}'
```

### Canary Not Working

```bash
# Check canary deployment
kubectl get deployment todo-app-frontend-canary -n todo-app

# Verify service endpoints
kubectl get endpoints -n todo-app
```

### Monitoring Not Scraping

```bash
# Check ServiceMonitor
kubectl get servicemonitor -n monitoring

# Verify Prometheus targets
kubectl port-forward svc/prometheus-operated -n monitoring 9090
# Visit: http://localhost:9090/targets
```

### Network Policy Blocking

```bash
# Temporarily disable for testing
helm upgrade todo-app . --set networkPolicy.enabled=false

# Test connectivity
kubectl run test --rm -it --image=busybox --restart=Never -n todo-app -- wget http://todo-app-frontend
```

---

**Document Version:** 2.0.0  
**Compatible With:** Helm 3+, Kubernetes 1.25+, Minikube 1.32+  
**PHR Location:** `history/prompts/infrastructure/`
