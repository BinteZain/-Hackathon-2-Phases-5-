# Execution Plan: Phase 3 Todo Chatbot Kubernetes Deployment

**Document Type:** Execution Plan  
**Version:** 1.0.0  
**Based On:** [K8S_INFRASTRUCTURE_SPEC.md](./K8S_INFRASTRUCTURE_SPEC.md)  
**Date:** February 18, 2026  

---

## Overview

This execution plan breaks down the infrastructure specification into three actionable phases with specific tasks, acceptance criteria, and validation steps.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Timeline                           │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: Containerization     │  2-3 hours    │  Foundation   │
│  Phase 2: Helm Chart           │  3-4 hours    │  Packaging    │
│  Phase 3: Kubernetes Deploy    │  1-2 hours    │  Deployment   │
├─────────────────────────────────────────────────────────────────┤
│  Total Estimated Time: 6-9 hours                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Containerization

**Objective:** Build production-ready Docker images for Frontend and Backend components.

**Duration:** 2-3 hours  
**Dependencies:** None  
**Owner:** DevOps Engineer

---

### Task 1.1: Analyze Existing Dockerfiles

**Path:** `./frontend/Dockerfile`, `./backend/Dockerfile`

**Steps:**
1. Read existing Dockerfiles
2. Verify base images match spec (node:18-alpine, python:3.11-slim)
3. Check exposed ports (3000, 4000)
4. Verify health check endpoints exist

**Acceptance Criteria:**
- [ ] Frontend uses `node:18-alpine` base image
- [ ] Backend uses `python:3.11-slim` base image
- [ ] Frontend exposes port 3000
- [ ] Backend exposes port 4000
- [ ] Backend `/health` endpoint exists and returns 200

**Validation:**
```bash
# Check Dockerfiles exist
ls -la frontend/Dockerfile backend/Dockerfile

# Verify health endpoint
curl http://localhost:4000/health
```

---

### Task 1.2: Optimize Frontend Dockerfile

**Path:** `./frontend/Dockerfile`

**Steps:**
1. Implement multi-stage build (build + runtime)
2. Add non-root user for security
3. Add health check instruction
4. Optimize layer caching

**Target Dockerfile:**
```dockerfile
# Build Stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Runtime Stage
FROM node:18-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1000 -S nodejs && \
    adduser -S nextjs -u 1000 -G nodejs

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["npm", "start"]
```

**Acceptance Criteria:**
- [ ] Multi-stage build implemented
- [ ] Non-root user configured (UID 1000)
- [ ] Health check instruction added
- [ ] Image size < 500MB
- [ ] Build completes without errors

**Validation:**
```bash
cd frontend
docker build -t phase3-frontend:test .
docker images phase3-frontend:test
docker run --rm phase3-frontend:test ls -la /app
```

---

### Task 1.3: Optimize Backend Dockerfile

**Path:** `./backend/Dockerfile`

**Steps:**
1. Implement multi-stage build (dependencies + runtime)
2. Add non-root user for security
3. Add health check instruction
4. Include alembic migration support

**Target Dockerfile:**
```dockerfile
# Build Stage
FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime Stage
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash appuser

# Copy installed packages
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy application code
COPY --chown=appuser:appuser . .

ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health')" || exit 1

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 4000"]
```

**Acceptance Criteria:**
- [ ] Multi-stage build implemented
- [ ] Non-root user configured (UID 1000)
- [ ] Health check instruction added
- [ ] Alembic migrations run on startup
- [ ] Image size < 500MB

**Validation:**
```bash
cd backend
docker build -t phase3-backend:test .
docker images phase3-backend:test
docker run --rm phase3-backend:test whoami
```

---

### Task 1.4: Build and Test Images Locally

**Steps:**
1. Build both images
2. Run containers locally
3. Test inter-container communication
4. Verify health endpoints

**Commands:**
```bash
# Create network
docker network create phase3-test

# Start PostgreSQL
docker run -d --name postgres-test \
  -e POSTGRES_USER=phase3user \
  -e POSTGRES_PASSWORD=phase3password123 \
  -e POSTGRES_DB=todoapp \
  --network phase3-test \
  postgres:15-alpine

# Start Backend
docker run -d --name backend-test \
  -e DATABASE_URL=postgresql://phase3user:phase3password123@postgres-test:5432/todoapp \
  -e BETTER_AUTH_SECRET=test_secret \
  --network phase3-test \
  phase3-backend:test

# Start Frontend
docker run -d --name frontend-test \
  -e NEXT_PUBLIC_API_URL=http://backend-test:4000/api/v1 \
  --network phase3-test \
  -p 3000:3000 \
  phase3-frontend:test
```

**Acceptance Criteria:**
- [ ] All containers start successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend health returns 200 at http://localhost:4000/health
- [ ] No permission errors in logs
- [ ] Containers restart automatically on failure

**Validation:**
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test endpoints
curl http://localhost:4000/health
curl http://localhost:3000

# Check logs
docker logs backend-test --tail 50
docker logs frontend-test --tail 50
```

---

### Task 1.5: Tag and Push Images

**Steps:**
1. Tag images with version
2. Push to local Minikube registry
3. Document image tags

**Commands:**
```bash
# Tag images
docker tag phase3-frontend:test phase3-frontend:latest
docker tag phase3-frontend:test phase3-frontend:v1.0.0
docker tag phase3-backend:test phase3-backend:latest
docker tag phase3-backend:test phase3-backend:v1.0.0

# Push to Minikube registry
eval $(minikube -p phase3 docker-env)
docker push phase3-frontend:latest
docker push phase3-backend:latest
```

**Acceptance Criteria:**
- [ ] Images tagged with `latest` and `v1.0.0`
- [ ] Images available in Minikube registry
- [ ] Image digests recorded

**Deliverables:**
- `frontend/Dockerfile` (optimized)
- `backend/Dockerfile` (optimized)
- `phase3-frontend:latest` image
- `phase3-backend:latest` image

---

## Phase 2: Helm Chart

**Objective:** Create a production-ready Helm chart for packaging and deploying the application.

**Duration:** 3-4 hours  
**Dependencies:** Phase 1 Complete  
**Owner:** DevOps Engineer

---

### Task 2.1: Initialize Helm Chart Structure

**Path:** `./helm-charts/phase3-todo-chatbot/`

**Steps:**
1. Create chart directory structure
2. Initialize Chart.yaml
3. Create values files (default, minikube, production)
4. Create .helmignore

**Commands:**
```bash
mkdir -p helm-charts/phase3-todo-chatbot/templates/{frontend,backend,postgres,ingress,network,rbac}
```

**Acceptance Criteria:**
- [ ] Directory structure matches spec
- [ ] Chart.yaml contains valid metadata
- [ ] Three values files created
- [ ] .helmignore configured

**Validation:**
```bash
helm lint helm-charts/phase3-todo-chatbot/
helm template phase3 helm-charts/phase3-todo-chatbot/
```

---

### Task 2.2: Create Helper Templates

**Path:** `./helm-charts/phase3-todo-chatbot/templates/_helpers.tpl`

**Steps:**
1. Define name helpers
2. Define label helpers
3. Define selector helpers
4. Define utility functions (database URL, secrets)

**Acceptance Criteria:**
- [ ] `phase3.name` helper defined
- [ ] `phase3.fullname` helper defined
- [ ] `phase3.chart` helper defined
- [ ] Component-specific labels defined
- [ ] Database URL generation works

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ | grep -A 5 "labels:"
```

---

### Task 2.3: Create Namespace and ConfigMap Templates

**Paths:**
- `./helm-charts/phase3-todo-chatbot/templates/namespace.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/configmap.yaml`

**Steps:**
1. Create namespace template
2. Create ConfigMap with all environment variables
3. Add proper labels and annotations

**Acceptance Criteria:**
- [ ] Namespace template creates `phase3` namespace
- [ ] ConfigMap contains all 10+ environment variables
- [ ] Labels use helper templates
- [ ] Values are properly templated

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/namespace.yaml
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/configmap.yaml
```

---

### Task 2.4: Create Secrets Template

**Path:** `./helm-charts/phase3-todo-chatbot/templates/secrets.yaml`

**Steps:**
1. Create Secret template with conditional creation
2. Include all required secrets (DB credentials, auth secret)
3. Support auto-generation of secure values
4. Add DATABASE_URL computation

**Acceptance Criteria:**
- [ ] Secret template creates `phase3-secrets`
- [ ] All 5 required secrets included
- [ ] Auto-generation for missing passwords
- [ ] DATABASE_URL computed from components

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/secrets.yaml
```

---

### Task 2.5: Create Frontend Deployment Templates

**Paths:**
- `./helm-charts/phase3-todo-chatbot/templates/frontend/deployment.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/frontend/service.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/frontend/hpa.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/frontend/pdb.yaml`

**Steps:**
1. Create Deployment with all spec requirements
2. Create ClusterIP Service
3. Create HPA with CPU/memory metrics
4. Create PodDisruptionBudget

**Acceptance Criteria:**
- [ ] Deployment uses values for replicas, images, resources
- [ ] Security contexts applied (non-root, capabilities dropped)
- [ ] Probes configured from values
- [ ] Service exposes port 80 → 3000
- [ ] HPA minReplicas=2, maxReplicas=10
- [ ] PDB minAvailable=1

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/frontend/deployment.yaml
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/frontend/hpa.yaml
```

---

### Task 2.6: Create Backend Deployment Templates

**Paths:**
- `./helm-charts/phase3-todo-chatbot/templates/backend/deployment.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/backend/service.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/backend/hpa.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/backend/pdb.yaml`

**Steps:**
1. Create Deployment with all spec requirements
2. Create ClusterIP Service
3. Create HPA with CPU/memory metrics
4. Create PodDisruptionBudget

**Acceptance Criteria:**
- [ ] Deployment uses values for replicas, images, resources
- [ ] Security contexts applied
- [ ] All environment variables from secrets/configmap
- [ ] Service exposes port 8080 → 4000
- [ ] HPA minReplicas=2, maxReplicas=15
- [ ] PDB minAvailable=1

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/backend/deployment.yaml
```

---

### Task 2.7: Create PostgreSQL StatefulSet Templates

**Paths:**
- `./helm-charts/phase3-todo-chatbot/templates/postgres/statefulset.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/postgres/service.yaml`

**Steps:**
1. Create StatefulSet for PostgreSQL
2. Configure PersistentVolumeClaim
3. Create headless Service
4. Add pg_isready probes

**Acceptance Criteria:**
- [ ] StatefulSet with serviceName reference
- [ ] PVC with 5Gi storage
- [ ] Security context (UID 999)
- [ ] Probes use pg_isready
- [ ] Environment from secrets

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/postgres/statefulset.yaml
```

---

### Task 2.8: Create Ingress and Network Policy Templates

**Paths:**
- `./helm-charts/phase3-todo-chatbot/templates/ingress/ingress.yaml`
- `./helm-charts/phase3-todo-chatbot/templates/network/networkpolicy.yaml`

**Steps:**
1. Create Ingress with path-based routing
2. Create NetworkPolicy with least-privilege rules
3. Support TLS configuration

**Acceptance Criteria:**
- [ ] Ingress routes `/api/*` to backend
- [ ] Ingress routes `/*` to frontend
- [ ] NetworkPolicy restricts pod-to-pod communication
- [ ] DNS egress allowed
- [ ] TLS configuration optional

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/ingress/ingress.yaml
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/network/networkpolicy.yaml
```

---

### Task 2.9: Create RBAC Templates

**Path:** `./helm-charts/phase3-todo-chatbot/templates/rbac/rolebinding.yaml`

**Steps:**
1. Create ServiceAccount
2. Create Role with minimal permissions
3. Create RoleBinding

**Acceptance Criteria:**
- [ ] ServiceAccount created
- [ ] Role allows get/list on configmaps, secrets, pods
- [ ] RoleBinding links SA to Role
- [ ] automountServiceAccountToken=false

**Validation:**
```bash
helm template phase3 helm-charts/phase3-todo-chatbot/ -s templates/rbac/rolebinding.yaml
```

---

### Task 2.10: Validate Complete Helm Chart

**Steps:**
1. Run helm lint
2. Run helm template with all values files
3. Validate rendered manifests
4. Test dry-run install

**Commands:**
```bash
# Lint chart
helm lint helm-charts/phase3-todo-chatbot/

# Template with minikube values
helm template phase3 helm-charts/phase3-todo-chatbot/ \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  --debug

# Dry run install
helm install phase3 helm-charts/phase3-todo-chatbot/ \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3 --dry-run
```

**Acceptance Criteria:**
- [ ] `helm lint` passes with no errors
- [ ] `helm template` renders all manifests
- [ ] All YAML is valid
- [ ] No undefined template variables
- [ ] Dry-run install succeeds

**Deliverables:**
- Complete Helm chart in `helm-charts/phase3-todo-chatbot/`
- Three values files (default, minikube, production)
- Validated and linted chart

---

## Phase 3: Kubernetes Deployment

**Objective:** Deploy the application to Minikube and validate all components.

**Duration:** 1-2 hours  
**Dependencies:** Phase 1 & 2 Complete  
**Owner:** DevOps Engineer

---

### Task 3.1: Setup Minikube Cluster

**Steps:**
1. Start Minikube with required resources
2. Enable required addons
3. Configure kubectl context
4. Verify cluster health

**Commands:**
```bash
# Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

# Enable addons
minikube addons enable ingress --profile phase3
minikube addons enable metrics-server --profile phase3

# Verify
kubectl cluster-info
kubectl get nodes
```

**Acceptance Criteria:**
- [ ] Minikube running with 6GB RAM, 4 CPUs
- [ ] Ingress addon enabled
- [ ] Metrics-server addon enabled
- [ ] kubectl connected to cluster
- [ ] Node status Ready

**Validation:**
```bash
minikube status -p phase3
kubectl get nodes
kubectl get pods -n ingress-nginx
```

---

### Task 3.2: Build and Load Images

**Steps:**
1. Configure Docker for Minikube
2. Build frontend image
3. Build backend image
4. Verify images in Minikube

**Commands:**
```bash
# Configure Docker
eval $(minikube -p phase3 docker-env)

# Build images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# Verify
docker images | grep phase3
```

**Acceptance Criteria:**
- [ ] Docker daemon connected to Minikube
- [ ] Frontend image built successfully
- [ ] Backend image built successfully
- [ ] Images visible in Minikube

**Validation:**
```bash
docker images phase3-frontend
docker images phase3-backend
```

---

### Task 3.3: Create Namespace and Secrets

**Steps:**
1. Create phase3 namespace
2. Create secrets manually (or via Helm)
3. Verify resources

**Commands:**
```bash
# Create namespace
kubectl create namespace phase3

# Create secrets
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=phase3password123 \
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp \
  --from-literal=BETTER_AUTH_SECRET=minikube_dev_secret_key \
  --from-literal=OPENAI_API_KEY= \
  -n phase3
```

**Acceptance Criteria:**
- [ ] Namespace `phase3` created
- [ ] Secret `phase3-secrets` created
- [ ] All required keys present in secret

**Validation:**
```bash
kubectl get namespace phase3
kubectl get secret phase3-secrets -n phase3 -o yaml
```

---

### Task 3.4: Deploy with Helm

**Steps:**
1. Install Helm chart
2. Wait for rollout
3. Verify all resources created

**Commands:**
```bash
# Install
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3

# Wait for rollout
kubectl wait --for=condition=available deployment/frontend -n phase3 --timeout=300s
kubectl wait --for=condition=available deployment/backend -n phase3 --timeout=300s
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase3 --timeout=300s
```

**Acceptance Criteria:**
- [ ] Helm release `phase3` deployed
- [ ] Frontend deployment available
- [ ] Backend deployment available
- [ ] PostgreSQL StatefulSet ready
- [ ] All pods Running

**Validation:**
```bash
helm list -n phase3
kubectl get all -n phase3
kubectl get pods -n phase3
```

---

### Task 3.5: Verify Services and Ingress

**Steps:**
1. Check services are created
2. Verify ingress configuration
3. Test external access

**Commands:**
```bash
# Check services
kubectl get services -n phase3

# Check ingress
kubectl get ingress -n phase3
kubectl describe ingress phase3-ingress -n phase3

# Get Minikube IP
minikube ip -p phase3
```

**Acceptance Criteria:**
- [ ] frontend-service exists (ClusterIP, port 80)
- [ ] backend-service exists (ClusterIP, port 8080)
- [ ] postgres-service exists (ClusterIP, port 5432)
- [ ] Ingress configured with correct paths
- [ ] Ingress rules point to correct services

**Validation:**
```bash
kubectl get svc -n phase3
kubectl get ingress -n phase3
curl -H "Host: todo-app.local" http://$(minikube ip)/
```

---

### Task 3.6: Test Application Functionality

**Steps:**
1. Access frontend via Minikube service
2. Test backend health endpoint
3. Test database connectivity
4. Verify end-to-end flow

**Commands:**
```bash
# Access frontend
minikube service frontend-service -n phase3 --profile phase3

# Test backend health
BACKEND_URL=$(kubectl get svc backend-service -n phase3 -o jsonpath='{.spec.clusterIP}')
curl http://${BACKEND_URL}:8080/health

# Test database
kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase3 -- psql -U phase3user -c "\dt"
```

**Acceptance Criteria:**
- [ ] Frontend loads successfully (HTTP 200)
- [ ] Backend health returns `{"status": "healthy"}`
- [ ] Database tables created
- [ ] No errors in application logs

**Validation:**
```bash
# Frontend
curl -I http://$(minikube ip)/

# Backend logs
kubectl logs deployment/backend -n phase3 --tail=50

# Frontend logs
kubectl logs deployment/frontend -n phase3 --tail=50
```

---

### Task 3.7: Verify Autoscaling

**Steps:**
1. Check HPA configuration
2. Verify metrics-server working
3. Test manual scaling

**Commands:**
```bash
# Check HPA
kubectl get hpa -n phase3

# Check metrics
kubectl top pods -n phase3

# Test scaling
kubectl scale deployment/frontend --replicas=3 -n phase3
kubectl get pods -n phase3 -l app.kubernetes.io/component=frontend
```

**Acceptance Criteria:**
- [ ] Frontend HPA shows CURRENT/TARGET metrics
- [ ] Backend HPA shows CURRENT/TARGET metrics
- [ ] kubectl top shows resource usage
- [ ] Manual scaling creates additional pods

**Validation:**
```bash
kubectl get hpa -n phase3
kubectl top pods -n phase3
kubectl get pods -n phase3
```

---

### Task 3.8: Verify Security Configuration

**Steps:**
1. Check pod security contexts
2. Verify network policies
3. Test RBAC configuration

**Commands:**
```bash
# Check security context
kubectl get pod frontend-pod -n phase3 -o jsonpath='{.spec.securityContext}'
kubectl get pod backend-pod -n phase3 -o jsonpath='{.spec.containers[0].securityContext}'

# Check network policy
kubectl get networkpolicy -n phase3
kubectl describe networkpolicy phase3-network-policy -n phase3

# Check service account
kubectl get serviceaccount phase3-sa -n phase3
kubectl get rolebinding -n phase3
```

**Acceptance Criteria:**
- [ ] Pods run as non-root (runAsUser: 1000/999)
- [ ] Capabilities dropped
- [ ] NetworkPolicy exists and configured
- [ ] ServiceAccount created
- [ ] RoleBinding links SA to Role

**Validation:**
```bash
kubectl get pods -n phase3 -o json | jq '.items[].spec.securityContext'
kubectl get networkpolicy -n phase3
kubectl get role,rolebinding -n phase3
```

---

### Task 3.9: Create Deployment Report

**Steps:**
1. Capture final state
2. Document access URLs
3. Record resource usage
4. Create runbook

**Commands:**
```bash
# Capture state
kubectl get all -n phase3 > deployment-state.txt
kubectl get ingress -n phase3 -o yaml >> deployment-state.txt
kubectl top pods -n phase3 >> deployment-state.txt
```

**Acceptance Criteria:**
- [ ] Deployment state documented
- [ ] Access URLs recorded
- [ ] Resource usage captured
- [ ] Runbook created

**Deliverables:**
- `deployment-state.txt`
- Updated README with access instructions

---

### Task 3.10: Cleanup and Uninstall (Optional)

**Steps:**
1. Uninstall Helm chart
2. Delete namespace
3. Stop Minikube

**Commands:**
```bash
# Uninstall
helm uninstall phase3 -n phase3

# Delete namespace
kubectl delete namespace phase3

# Stop Minikube
minikube stop -p phase3
```

**Acceptance Criteria:**
- [ ] Helm release removed
- [ ] Namespace deleted
- [ ] All resources cleaned up

---

## Summary

### Phase Deliverables

| Phase | Deliverables | Success Criteria |
|-------|--------------|------------------|
| **1. Containerization** | Optimized Dockerfiles, Tested images | Images build, run, pass health checks |
| **2. Helm Chart** | Complete chart with templates | helm lint passes, template renders |
| **3. Kubernetes Deploy** | Running application on Minikube | All pods healthy, app accessible |

### Acceptance Criteria Summary

#### Phase 1: Containerization
- [ ] Frontend Dockerfile optimized (multi-stage, non-root, healthcheck)
- [ ] Backend Dockerfile optimized (multi-stage, non-root, healthcheck)
- [ ] Both images build without errors
- [ ] Images run locally and communicate
- [ ] Health endpoints respond correctly

#### Phase 2: Helm Chart
- [ ] Chart.yaml valid
- [ ] All templates render correctly
- [ ] values-minikube.yaml configured
- [ ] values-production.yaml configured
- [ ] helm lint passes
- [ ] helm template renders all manifests

#### Phase 3: Kubernetes Deployment
- [ ] Minikube cluster running
- [ ] All pods Running and Ready
- [ ] Services accessible
- [ ] Ingress routing works
- [ ] HPA configured and receiving metrics
- [ ] Security contexts applied
- [ ] Network policies enforced
- [ ] Application end-to-end test passes

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Image build failures | Test locally first, use multi-stage |
| Helm template errors | Run helm lint frequently |
| Pod scheduling failures | Verify resource requests fit cluster |
| Database persistence | Check PVC bound status |
| Network isolation breaks app | Test with NetworkPolicy disabled first |

### Rollback Plan

```bash
# Helm rollback
helm rollback phase3 -n phase3

# Kubernetes rollback
kubectl rollout undo deployment/frontend -n phase3
kubectl rollout undo deployment/backend -n phase3

# Full uninstall
helm uninstall phase3 -n phase3
kubectl delete namespace phase3
```

---

**Next Steps:** Execute Phase 1, Task 1.1
