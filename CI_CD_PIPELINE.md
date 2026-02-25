# Phase V: CI/CD Pipeline Documentation

**Cloud-Native AI Todo Chatbot - Continuous Integration & Deployment**

---

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Workflow Files](#workflow-files)
4. [Pipeline Stages](#pipeline-stages)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Monitoring & Debugging](#monitoring--debugging)
8. [Best Practices](#best-practices)

---

## Overview

### Pipeline Goals

- **Automated Builds**: Build and test on every commit
- **Container Images**: Build and push multi-arch Docker images
- **Security Scanning**: Automated vulnerability scanning with Trivy
- **Kubernetes Deployment**: Deploy to AKS with Helm
- **Environment Promotion**: Staging → Production flow
- **Rollback Support**: Atomic deployments with automatic rollback

### Technologies

| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD orchestration |
| Docker Buildx | Multi-architecture builds |
| GHCR | Container registry |
| Helm | Kubernetes package management |
| AKS | Kubernetes cluster |
| Dapr | Distributed application runtime |
| Trivy | Security scanning |

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                             │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                  │
│  │  Push    │    │   PR     │    │   Tag    │                  │
│  │  main    │    │  develop │    │   v*     │                  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                  │
│       │               │               │                         │
│       ▼               ▼               ▼                         │
│  ┌─────────────────────────────────────────────────┐           │
│  │        deploy.yml (Production Pipeline)         │           │
│  └─────────────────────────────────────────────────┘           │
│       │               │               │                         │
│       ▼               ▼               ▼                         │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐                     │
│  │  Build  │ → │ Security │ → │  Deploy  │                     │
│  │  & Test │   │   Scan   │   │   AKS    │                     │
│  └─────────┘   └──────────┘   └──────────┘                     │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Kubernetes Service                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │              Helm Release (todo-app)               │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │         │
│  │  │   Chat API   │  │   Recurring  │  │  Notify  │ │         │
│  │  │  Deployment  │  │  Deployment  │  │  Deploy  │ │         │
│  │  └──────────────┘  └──────────────┘  └──────────┘ │         │
│  │                                                    │         │
│  │  ┌──────────────────────────────────────────────┐ │         │
│  │  │           Dapr Sidecars (Injected)           │ │         │
│  │  └──────────────────────────────────────────────┘ │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow Files

### 1. deploy.yml (Production)

**Location:** `.github/workflows/deploy.yml`

**Triggers:**
- Push to `main` branch
- Git tags (`v*`)
- Pull requests to `main`

**Jobs:**
1. `build` - Build and test frontend/backend
2. `build-images` - Build and push Docker images
3. `security-scan` - Trivy vulnerability scanning
4. `deploy` - Deploy to AKS
5. `deploy-frontend` - Deploy frontend to Vercel
6. `notify` - Send Slack/email notifications

---

### 2. deploy-staging.yml

**Location:** `.github/workflows/deploy-staging.yml`

**Triggers:**
- Push to `develop` branch
- Pull requests to `develop`

**Jobs:**
1. `build` - Build and test
2. `build-images` - Build images with `staging` tag
3. `deploy-staging` - Deploy to staging AKS cluster

---

### 3. cleanup.yml

**Location:** `.github/workflows/cleanup.yml`

**Triggers:**
- Manual trigger (workflow_dispatch)

**Inputs:**
- `environment` - staging/production
- `delete-namespace` - Boolean

**Actions:**
- Uninstall Helm release
- Delete Kubernetes secrets
- Delete Kafka topics
- Clean up Dapr components

---

## Pipeline Stages

### Stage 1: Build and Test

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci && npm run build
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt && pytest
```

**Duration:** ~5 minutes

**Outputs:**
- Build artifacts
- Test coverage reports
- Version tag

---

### Stage 2: Build Docker Images

```yaml
jobs:
  build-images:
    runs-on: ubuntu-latest
    steps:
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
      - uses: docker/build-push-action@v5
        with:
          platforms: linux/amd64,linux/arm64
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Duration:** ~10 minutes

**Images Built:**
- `ghcr.io/todo-chatbot/chat-api`
- `ghcr.io/todo-chatbot/recurring-service`
- `ghcr.io/todo-chatbot/notification-service`

---

### Stage 3: Security Scan

```yaml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          severity: 'CRITICAL,HIGH'
      - uses: github/codeql-action/upload-sarif@v3
```

**Duration:** ~3 minutes

**Scans For:**
- CVE vulnerabilities
- Misconfigurations
- Secrets in code

---

### Stage 4: Deploy to AKS

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: azure/login@v1
      - uses: Azure/aks-set-context@v3
      - run: helm upgrade --install todo-app ./helm
```

**Duration:** ~8 minutes

**Deployment Strategy:**
- Rolling update
- Max surge: 1
- Max unavailable: 0
- Timeout: 10 minutes
- Atomic: true (auto-rollback on failure)

---

### Stage 5: Verify & Notify

```yaml
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - run: kubectl rollout status deployment/todo-app-chat-api
      - run: curl http://<endpoint>/health
```

**Notifications:**
- Slack webhook
- Email (optional)
- GitHub status check

---

## Configuration

### Required Secrets

| Secret | Scope | Description |
|--------|-------|-------------|
| `AZURE_CREDENTIALS` | Repo | Azure service principal |
| `DB_PASSWORD` | Repo/Env | Database password |
| `REDIS_PASSWORD` | Repo/Env | Redis password |
| `FIREBASE_API_KEY` | Repo/Env | Firebase API key |
| `SLACK_WEBHOOK_URL` | Repo | Slack notification |
| `VERCEL_TOKEN` | Repo | Vercel deployment |

**Setup Guide:** See [`.github/SECRETS_SETUP.md`](./.github/SECRETS_SETUP.md)

---

### Environment Variables

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  AKS_CLUSTER_NAME: todo-aks
  AKS_RESOURCE_GROUP: todo-rg
  HELM_RELEASE_NAME: todo-app
```

---

### Helm Values Override

Production values (`helm/values-aks.yaml`):

```yaml
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

monitoring:
  enabled: true
```

---

## Usage

### Trigger Production Deployment

```bash
# Push to main
git checkout main
git push origin main

# Or create a release tag
git tag v1.0.0
git push origin v1.0.0
```

### Trigger Staging Deployment

```bash
# Push to develop
git checkout develop
git push origin develop
```

### Manual Cleanup

1. Go to **Actions** tab
2. Select "Phase V - Cleanup Resources"
3. Click "Run workflow"
4. Select environment and options
5. Click "Run workflow"

---

### Monitor Deployment

**GitHub Actions:**
```
Repository → Actions → Select workflow → View run
```

**Kubernetes:**
```bash
kubectl get pods -l app.kubernetes.io/instance=todo-app
kubectl rollout status deployment/todo-app-chat-api
kubectl logs -l app.kubernetes.io/name=chat-api
```

**Dapr:**
```bash
dapr status -k
dapr logs -a chat-api -k
```

**Helm:**
```bash
helm list
helm history todo-app
helm status todo-app
```

---

## Monitoring & Debugging

### Pipeline Logs

**View logs:**
```
Actions → Workflow run → Click job → View logs
```

**Download logs:**
```bash
gh run download <run-id> --dir ./logs
```

---

### Common Issues

#### Issue 1: Build Fails

**Symptoms:**
- npm install fails
- pytest errors

**Solution:**
```bash
# Test locally
cd frontend && npm ci && npm run build
cd backend && pip install -r requirements.txt && pytest
```

---

#### Issue 2: Docker Build Fails

**Symptoms:**
- Base image not found
- Dependencies fail

**Solution:**
```bash
# Test build locally
docker build -f backend/Dockerfile -t test:latest .
docker buildx build --platform linux/amd64,linux/arm64 .
```

---

#### Issue 3: AKS Deployment Fails

**Symptoms:**
- Helm install fails
- Pods not starting

**Solution:**
```bash
# Check cluster
az aks get-credentials --resource-group todo-rg --name todo-aks
kubectl get nodes
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Test Helm locally
helm upgrade --install todo-app ./helm --dry-run --debug
```

---

#### Issue 4: Dapr Sidecar Not Injecting

**Symptoms:**
- Pods start without Dapr sidecar
- Service invocation fails

**Solution:**
```bash
# Check Dapr installation
dapr status -k
kubectl get pods -n dapr-system

# Check annotations
kubectl get deployment chat-api -o yaml | grep dapr.io

# Reinstall Dapr
dapr init -k --wait
```

---

## Best Practices

### 1. Branch Strategy

```
main (production)
  ↑
  │ PR + Review
  │
develop (staging)
  ↑
  │ Feature branches
  │
feature/*
```

---

### 2. Versioning

**Semantic Versioning:**
```
vMAJOR.MINOR.PATCH
v1.2.3

Pre-release:
v1.2.3-alpha.1
v1.2.3-beta.2
v1.2.3-rc.1
```

---

### 3. Image Tagging

```yaml
tags: |
  type=ref,event=branch     # main, develop
  type=ref,event=pr         # PR number
  type=semver,pattern={{version}}  # v1.2.3
  type=sha,prefix=,format=short    # abc1234
```

---

### 4. Deployment Strategy

**Blue-Green (Recommended for Production):**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

**Canary (Advanced):**
```yaml
# Use Flagger or Argo Rollouts
# Gradually shift traffic from old to new version
```

---

### 5. Security

- **Use OIDC** instead of long-lived credentials
- **Scan images** with Trivy before deployment
- **Use secrets** for sensitive data (never commit)
- **Enable branch protection** on main
- **Require PR reviews** before merge
- **Use environment protection rules** for production

---

### 6. Cost Optimization

```yaml
# Staging: 1 replica
replicaCount: 1

# Production: 3 replicas with autoscaling
replicaCount: 3
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
```

---

### 7. Rollback Strategy

**Automatic (Helm atomic):**
```yaml
helm upgrade --install --atomic --timeout 10m
```

**Manual:**
```bash
# Rollback to previous revision
helm rollback todo-app 1

# Or redeploy previous image
helm upgrade todo-app ./helm \
  --set image.tag=previous-sha
```

---

## Metrics & KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Build Time | < 10 min | GitHub Actions logs |
| Deployment Time | < 15 min | Workflow duration |
| Success Rate | > 95% | Workflow runs / total |
| Rollback Rate | < 5% | Rollbacks / deployments |
| MTTR | < 30 min | Time to restore service |

---

## Pipeline Optimization

### Caching

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      ~/.cache/pip
    key: ${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

### Parallel Jobs

```yaml
jobs:
  build-frontend:
    runs-on: ubuntu-latest
    steps: [...]
  
  build-backend:
    runs-on: ubuntu-latest
    steps: [...]
  
  build-images:
    needs: [build-frontend, build-backend]
    steps: [...]
```

---

## Support Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Azure AKS CI/CD](https://docs.microsoft.com/en-us/azure/aks/kubernetes-action)
- [Helm Charts](https://helm.sh/docs/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Author:** Phase V Development Team
