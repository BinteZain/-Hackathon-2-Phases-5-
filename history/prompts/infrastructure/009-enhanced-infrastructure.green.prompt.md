---
id: 009
title: Enhanced Infrastructure with Blue-Green, Canary, Monitoring
stage: green
date: 2026-02-21
surface: agent
model: qwen-coder
feature: phase3-infrastructure-enhancement
branch: main
user: MUHAMMAD AFNAN
command: Enhance infrastructure with Blue-Green deployment, Canary strategy, PDB, RBAC, NetworkPolicies, Prometheus, Grafana - keep local cluster compatible
labels: ["kubernetes", "helm", "blue-green", "canary", "monitoring", "prometheus", "grafana", "rbac", "networkpolicy", "phase3"]
links:
  spec: helm-charts/ENHANCED_INFRASTRUCTURE.md
  ticket: null
  adr: null
  pr: null
files:
  - helm-charts/todo-app/values.yaml (enhanced)
  - helm-charts/todo-app/values-minikube.yaml (enhanced)
  - helm-charts/todo-app/templates/deployment-canary.yaml
  - helm-charts/todo-app/templates/deployment-blue-green.yaml
  - helm-charts/todo-app/templates/service-blue-green.yaml
  - helm-charts/todo-app/templates/rbac-enhanced.yaml
  - helm-charts/todo-app/templates/networkpolicy-enhanced.yaml
  - helm-charts/todo-app/templates/servicemonitor.yaml
  - helm-charts/todo-app/templates/prometheusrule.yaml
  - helm-charts/todo-app/templates/grafana-dashboard.yaml
  - helm-charts/ENHANCED_INFRASTRUCTURE.md
tests:
  - helm lint (structure validation)
  - helm template (template rendering)
  - values-minikube compatibility check
---

## Prompt

Enhance infrastructure with:

- Blue-Green deployment
- Canary deployment strategy
- PodDisruptionBudget
- RBAC
- NetworkPolicies
- Prometheus monitoring
- Grafana dashboard

Keep local cluster compatible.

## Response snapshot

Enhanced Helm chart with advanced deployment strategies and monitoring:

**Deployment Strategies Added:**
1. Blue-Green Deployment
   - deployment-blue-green.yaml (blue + green environments)
   - service-blue-green.yaml (traffic switching)
   - Switch via: --set global.activeEnvironment=blue|green

2. Canary Deployment
   - deployment-canary.yaml (stable + canary tracks)
   - Configurable percentage: --set global.canaryPercentage=10

3. Rolling Deployment (default)
   - Standard Kubernetes rolling update

**Security Enhancements:**
1. Enhanced RBAC (rbac-enhanced.yaml)
   - Fine-grained permissions
   - Optional cluster-wide access
   - Service account per component

2. Enhanced NetworkPolicies (networkpolicy-enhanced.yaml)
   - Default deny all
   - Allow ingress from NGINX
   - Allow frontend→backend
   - Allow DNS egress
   - Allow HTTPS outbound

**Monitoring Stack:**
1. ServiceMonitor (servicemonitor.yaml)
   - Auto-discovers frontend/backend services
   - 30s scrape interval
   - Prometheus integration

2. PrometheusRule (prometheusrule.yaml)
   - 8 alerting rules:
     - PodCrashLooping
     - HighMemoryUsage (>85%)
     - HighCPUUsage (>80%)
     - ServiceDown
     - PodNotReady
     - DeploymentReplicasMismatch
     - IngressHighErrorRate (>5%)
     - HPAMaxReplicasReached

3. Grafana Dashboard (grafana-dashboard.yaml)
   - 8 panels:
     - Running Pods stat
     - Average CPU Usage stat
     - Average Memory Usage stat
     - Pod Restarts stat
     - CPU by Container (timeseries)
     - Memory by Container (timeseries)
     - HPA Replicas (timeseries)
     - Deployment Replicas (timeseries)

**Local Cluster Compatibility:**
- values-minikube.yaml updated:
  - deploymentStrategy: rolling (simplified)
  - monitoring.enabled: false (optional)
  - Lower resource limits
  - Simplified RBAC (clusterWide: false)
  - Basic network policies

**Documentation:**
- ENHANCED_INFRASTRUCTURE.md (400+ lines)
  - Strategy comparison table
  - Architecture diagrams
  - Command reference
  - Troubleshooting guide

**Template Count:** 27 files (was 20, now 27)

## Outcome

- ✅ Impact: Production-grade deployment strategies with monitoring
- 🧪 Tests: Templates validated, Minikube compatibility maintained
- 📁 Files: 10 files created/modified
- 🔁 Next prompts: Test blue-green switch, canary rollout, verify alerts
- 🧠 Reflection: Balanced enterprise features with local dev simplicity

## Evaluation notes (flywheel)

- Failure modes observed: None - templates validated
- Graders run and results: N/A (infrastructure enhancement)
- Prompt variant: N/A
- Next experiment: Deploy with --set global.deploymentStrategy=blue-green
