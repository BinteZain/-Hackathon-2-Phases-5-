# Kubernetes Deployment Guide - Phase 3 Todo Chatbot

**Last Updated:** February 18, 2026  
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Installation Methods](#installation-methods)
6. [Configuration](#configuration)
7. [Operations](#operations)
8. [Troubleshooting](#troubleshooting)
9. [Uninstall](#uninstall)

---

## Overview

This guide provides step-by-step instructions for deploying the Phase 3 Todo Chatbot application on a local Kubernetes cluster using Minikube and Helm.

### Components

| Component | Technology | Replicas | Port |
|-----------|------------|----------|------|
| Frontend | Next.js 13 | 2 | 3000 |
| Backend | FastAPI | 2 | 4000 |
| Database | PostgreSQL 15 | 1 | 5432 |
| Ingress | NGINX | 1 | 80/443 |

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Installation Link |
|------|-----------------|-------------------|
| Minikube | v1.32.0 | [Download](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | v1.28.0 | [Download](https://kubernetes.io/docs/tasks/tools/) |
| Helm | v3.13.0 | [Download](https://helm.sh/docs/intro/install/) |
| Docker | v24.0.0 | [Download](https://docs.docker.com/get-docker/) |

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 6 cores |
| Memory | 6 GB | 8 GB |
| Disk | 20 GB | 30 GB |
| OS | Windows 10 / macOS 10.15+ / Linux | - |

### Verify Installation

```bash
# Windows (PowerShell)
minikube version
kubectl version --client
helm version
docker --version

# Linux/Mac
minikube version
kubectl version --client
helm version
docker --version
```

---

## Quick Start

### Windows

```powershell
# Run the deployment script
.\deploy-minikube.bat
```

### Linux/Mac

```bash
# Make script executable
chmod +x deploy-minikube.sh

# Run the deployment script
./deploy-minikube.sh
```

### Manual Deployment

See [Installation Methods](#installation-methods) for detailed steps.

---

## Architecture

### Cluster Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Minikube Cluster                   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │              Ingress (NGINX)                │   │
│  │              todo-app.local:80              │   │
│  └────────────────────┬────────────────────────┘   │
│                       │                             │
│         ┌─────────────┴─────────────┐               │
│         │                           │               │
│  ┌──────▼──────┐            ┌──────▼──────┐        │
│  │  Frontend   │            │   Backend   │        │
│  │  (x2)       │            │   (x2)      │        │
│  │  :3000      │            │   :4000     │        │
│  └─────────────┘            └──────┬──────┘        │
│                                    │               │
│                           ┌────────▼────────┐      │
│                           │   PostgreSQL    │      │
│                           │   StatefulSet   │      │
│                           │   :5432         │      │
│                           └─────────────────┘      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Network Flow

```
User → Ingress → Frontend → Backend → PostgreSQL
                      ↘         ↗
                    (API calls)
```

---

## Installation Methods

### Method 1: Automated Script (Recommended)

#### Windows

```powershell
.\deploy-minikube.bat
```

#### Linux/Mac

```bash
chmod +x deploy-minikube.sh
./deploy-minikube.sh
```

### Method 2: Helm Chart

```bash
# 1. Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

# 2. Enable addons
minikube addons enable ingress --profile phase3
minikube addons enable metrics-server --profile phase3

# 3. Configure Docker
eval $(minikube -p phase3 docker-env)

# 4. Build images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# 5. Create namespace
kubectl create namespace phase3

# 6. Create secrets
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=phase3password123 \
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp \
  --from-literal=BETTER_AUTH_SECRET=dev_secret_key \
  -n phase3

# 7. Deploy with Helm
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3
```

### Method 3: Kustomize

```bash
# 1. Start Minikube and build images (same as Method 2)

# 2. Apply Kustomize configuration
kubectl apply -k k8s/local/
```

### Method 4: Raw Manifests

```bash
# 1. Start Minikube and build images (same as Method 2)

# 2. Apply manifests in order
kubectl apply -f k8s/local/namespace.yaml
kubectl apply -f k8s/local/configmap.yaml
kubectl apply -f k8s/local/secrets.yaml
kubectl apply -f k8s/local/rbac.yaml
kubectl apply -f k8s/local/postgres-statefulset.yaml
kubectl apply -f k8s/local/postgres-service.yaml
kubectl apply -f k8s/local/backend-deployment.yaml
kubectl apply -f k8s/local/backend-service.yaml
kubectl apply -f k8s/local/frontend-deployment.yaml
kubectl apply -f k8s/local/frontend-service.yaml
kubectl apply -f k8s/local/ingress.yaml
kubectl apply -f k8s/local/networkpolicy.yaml
```

---

## Configuration

### Environment Variables

#### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node environment |
| `NEXT_PUBLIC_API_URL` | `http://backend-service:8080/api/v1` | Backend API URL |
| `NEXT_PUBLIC_BETTER_AUTH_SECRET` | From secret | Auth secret |

#### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON_ENV` | `production` | Python environment |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DATABASE_URL` | From secret | PostgreSQL connection |
| `BETTER_AUTH_SECRET` | From secret | JWT secret |
| `OPENAI_API_KEY` | From secret (optional) | OpenAI API key |

#### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `todoapp` | Database name |
| `POSTGRES_USER` | `phase3user` | Database user |
| `POSTGRES_PASSWORD` | From secret | Database password |
| `PGDATA` | `/var/lib/postgresql/data/pgdata` | Data directory |

### Resource Configuration

#### Frontend Resources

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Backend Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### PostgreSQL Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Scaling Configuration

#### Horizontal Pod Autoscaler

| Component | Min Replicas | Max Replicas | CPU Target | Memory Target |
|-----------|--------------|--------------|------------|---------------|
| Frontend | 2 | 5 | 70% | 80% |
| Backend | 2 | 8 | 60% | 75% |

---

## Operations

### Access the Application

#### Option 1: Minikube Service

```bash
minikube service frontend-service -n phase3 --profile phase3
```

#### Option 2: Port Forward

```bash
kubectl port-forward svc/frontend-service 3000:80 -n phase3
# Visit http://localhost:3000
```

#### Option 3: Ingress

```bash
# Get Minikube IP
minikube ip -p phase3

# Add to hosts file
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts
<MINIKUBE_IP> todo-app.local

# Visit http://todo-app.local
```

### View Logs

```bash
# Frontend logs
kubectl logs -f deployment/frontend -n phase3

# Backend logs
kubectl logs -f deployment/backend -n phase3

# PostgreSQL logs
kubectl logs -f postgres-phase3-todo-chatbot-0 -n phase3
```

### Access Database

```bash
# Connect to PostgreSQL
kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase3 -- psql -U phase3user todoapp

# Run queries
\dt                    # List tables
SELECT * FROM users;   # Query users
\q                     # Quit
```

### Scale Application

```bash
# Scale frontend
kubectl scale deployment/frontend --replicas=3 -n phase3

# Scale backend
kubectl scale deployment/backend --replicas=5 -n phase3
```

### Update Deployment

```bash
# Rebuild images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Restart deployments
kubectl rollout restart deployment/frontend -n phase3
kubectl rollout restart deployment/backend -n phase3

# Or upgrade with Helm
helm upgrade phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3
```

### Rollback

```bash
# Rollback Helm release
helm rollback phase3 -n phase3

# Rollback Kubernetes deployment
kubectl rollout undo deployment/frontend -n phase3
kubectl rollout undo deployment/backend -n phase3
```

### Health Checks

```bash
# Check deployment status
kubectl get deployments -n phase3

# Check pod status
kubectl get pods -n phase3

# Check service status
kubectl get services -n phase3

# Check HPA status
kubectl get hpa -n phase3
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n phase3

# Check events
kubectl get events -n phase3 --sort-by='.lastTimestamp'
```

#### Image Pull Errors

```bash
# Ensure Docker is pointing to Minikube
eval $(minikube -p phase3 docker-env)

# Rebuild images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Verify images exist
docker images | grep phase3
```

#### Database Connection Issues

```bash
# Check database is running
kubectl get pods -n phase3 | grep postgres

# Check service
kubectl get svc postgres-service -n phase3

# Test connection from backend pod
kubectl exec -it deployment/backend -n phase3 -- \
  python -c "import psycopg2; psycopg2.connect('postgresql://phase3user:phase3password123@postgres-service:5432/todoapp')"
```

#### Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress phase3-ingress -n phase3

# Test ingress directly
curl -H "Host: todo-app.local" http://<MINIKUBE_IP>/
```

#### HPA Not Scaling

```bash
# Check metrics-server
kubectl get pods -n kube-system | grep metrics-server

# Check HPA status
kubectl describe hpa frontend-hpa -n phase3

# Check metrics
kubectl top pods -n phase3
```

### Debug Mode

```bash
# Enable debug logging
kubectl edit configmap phase3-config -n phase3
# Change BACKEND_LOG_LEVEL to DEBUG

# Restart backend
kubectl rollout restart deployment/backend -n phase3

# View debug logs
kubectl logs -f deployment/backend -n phase3
```

---

## Uninstall

### Uninstall Helm Chart

```bash
helm uninstall phase3 -n phase3
```

### Delete Namespace

```bash
kubectl delete namespace phase3
```

### Stop Minikube

```bash
minikube stop -p phase3
```

### Delete Minikube Profile

```bash
minikube delete -p phase3
```

### Clean Up Docker Images

```bash
docker rmi phase3-frontend:latest
docker rmi phase3-backend:latest
```

---

## Appendix

### File Structure

```
Phase_3/
├── helm-charts/
│   └── phase3-todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-minikube.yaml
│       ├── values-production.yaml
│       └── templates/
├── k8s/
│   └── local/
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── secrets.yaml
│       ├── *.yaml
│       └── kustomization.yaml
├── deploy-minikube.bat
├── deploy-minikube.sh
└── KUBERNETES_DEPLOYMENT.md
```

### Quick Reference

```bash
# Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

# Deploy
helm install phase3 ./helm-charts/phase3-todo-chatbot -f helm-charts/phase3-todo-chatbot/values-minikube.yaml -n phase3 --create-namespace

# Access
minikube service frontend-service -n phase3 --profile phase3

# Monitor
kubectl get all -n phase3

# Logs
kubectl logs -f deployment/frontend -n phase3

# Uninstall
helm uninstall phase3 -n phase3
```

### Support

For issues or questions:
- Check [Infrastructure Spec](specs/infrastructure/K8S_INFRASTRUCTURE_SPEC.md)
- Review Kubernetes logs
- Contact: afnan@example.com
