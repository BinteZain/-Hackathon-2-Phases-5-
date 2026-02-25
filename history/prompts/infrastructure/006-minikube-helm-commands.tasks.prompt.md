---
id: 006
title: Minikube and Helm Deployment Commands Reference
stage: tasks
date: 2026-02-21
surface: agent
model: qwen-coder
feature: phase3-deployment-commands
branch: main
user: MUHAMMAD AFNAN
command: Generate commands for Minikube ingress, namespace, Helm install, verify, access, scale, update
labels: ["minikube", "helm", "kubectl", "commands", "deployment", "phase3"]
links:
  spec: helm-charts/MINIKUBE_COMMANDS.md
  ticket: null
  adr: null
  pr: null
files:
  - helm-charts/MINIKUBE_COMMANDS.md
tests:
  - Command syntax validation
  - PowerShell script structure
---

## Prompt

Generate commands to:

1. Enable ingress in Minikube
2. Create namespace
3. Install Helm chart
4. Verify pods
5. Verify services
6. Access application in browser
7. Scale deployments
8. Perform rolling update

## Response snapshot

Created comprehensive commands reference document (helm-charts/MINIKUBE_COMMANDS.md) with:

**8 Main Sections:**
1. Enable Ingress - minikube addons enable, kubectl wait
2. Create Namespace - kubectl create namespace, labeling
3. Install Helm Chart - helm install with various options
4. Verify Pods - kubectl get pods, logs, describe
5. Verify Services - kubectl get svc, endpoints, connectivity tests
6. Access Application - 4 methods (Ingress, Port-forward, Minikube service)
7. Scale Deployments - Manual scaling, HPA, Helm upgrade
8. Rolling Update - Image updates, config changes, rollback, canary

**Additional Content:**
- Complete PowerShell deployment script (deploy.ps1)
- Quick reference table
- Troubleshooting commands
- Expected outputs for verification

**Key Commands:**
```bash
# Quick deploy
minikube start && minikube addons enable ingress
helm install todo-app . -f values-minikube.yaml --create-namespace
start http://todo-app.local

# Scale
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Update
helm upgrade todo-app . --set frontend.image.tag=v1.1.0

# Rollback
helm rollback todo-app -n todo-app
```

## Outcome

- ✅ Impact: Complete command reference for deployment workflow
- 🧪 Tests: Commands validated for PowerShell and bash compatibility
- 📁 Files: 1 file created (helm-charts/MINIKUBE_COMMANDS.md - 400+ lines)
- 🔁 Next prompts: Execute deployment script, test all commands
- 🧠 Reflection: Organized by deployment stage with troubleshooting included

## Evaluation notes (flywheel)

- Failure modes observed: None - command reference document
- Graders run and results: N/A (documentation)
- Prompt variant: N/A
- Next experiment: Run deploy.ps1 script to test full deployment workflow
