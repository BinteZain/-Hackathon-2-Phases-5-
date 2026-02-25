# Atomic Deployment Tasks - Phase 3 Todo Chatbot Kubernetes

**Execution Mode:** Fully Automated (No Manual Steps)  
**Target:** Minikube Local Kubernetes  
**Total Tasks:** 15 atomic executable tasks  

---

## Task List

### Task 1: Create Optimized Backend Dockerfile
**File:** `backend/Dockerfile`  
**Action:** Write/Update  
**Duration:** 2 min  

**Requirements:**
- Multi-stage build (builder + runtime)
- Base image: `python:3.11-slim`
- Non-root user: `appuser` (UID 1000)
- Health check: `/health` endpoint
- Alembic migrations on startup
- Expose port: 4000

**Validation:**
```bash
test -f backend/Dockerfile && echo "PASS" || echo "FAIL"
grep -q "python:3.11-slim" backend/Dockerfile && echo "PASS" || echo "FAIL"
grep -q "HEALTHCHECK" backend/Dockerfile && echo "PASS" || echo "FAIL"
```

---

### Task 2: Create Optimized Frontend Dockerfile
**File:** `frontend/Dockerfile`  
**Action:** Write/Update  
**Duration:** 2 min  

**Requirements:**
- Multi-stage build (builder + runtime)
- Base image: `node:18-alpine`
- Non-root user: `nextjs` (UID 1000)
- Health check: `/` endpoint
- Build Next.js production bundle
- Expose port: 3000

**Validation:**
```bash
test -f frontend/Dockerfile && echo "PASS" || echo "FAIL"
grep -q "node:18-alpine" frontend/Dockerfile && echo "PASS" || echo "FAIL"
grep -q "HEALTHCHECK" frontend/Dockerfile && echo "PASS" || echo "FAIL"
```

---

### Task 3: Build Backend Docker Image
**Command:** `docker build -t phase3-backend:latest ./backend`  
**Action:** Execute  
**Duration:** 3 min  

**Requirements:**
- Working directory: project root
- Context: `./backend`
- Tag: `phase3-backend:latest`
- Exit code: 0

**Validation:**
```bash
docker images phase3-backend:latest --format "{{.Repository}}" | grep -q "phase3-backend" && echo "PASS" || echo "FAIL"
```

---

### Task 4: Build Frontend Docker Image
**Command:** `docker build -t phase3-frontend:latest ./frontend`  
**Action:** Execute  
**Duration:** 3 min  

**Requirements:**
- Working directory: project root
- Context: `./frontend`
- Tag: `phase3-frontend:latest`
- Exit code: 0

**Validation:**
```bash
docker images phase3-frontend:latest --format "{{.Repository}}" | grep -q "phase3-frontend" && echo "PASS" || echo "FAIL"
```

---

### Task 5: Start Minikube Cluster
**Command:** `minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3`  
**Action:** Execute  
**Duration:** 2 min  

**Requirements:**
- Memory: 6144 MB
- CPUs: 4
- Disk: 20 GB
- Profile: `phase3`
- Exit code: 0

**Validation:**
```bash
minikube status -p phase3 | grep -q "Running" && echo "PASS" || echo "FAIL"
```

---

### Task 6: Enable Minikube Addons
**Commands:**
- `minikube addons enable ingress --profile phase3`
- `minikube addons enable metrics-server --profile phase3`  
**Action:** Execute  
**Duration:** 1 min  

**Requirements:**
- Ingress addon: enabled
- Metrics-server addon: enabled
- Exit code: 0

**Validation:**
```bash
minikube addons list --profile phase3 | grep -E "ingress|metrics-server" | grep -q "enabled" && echo "PASS" || echo "FAIL"
```

---

### Task 7: Configure Docker for Minikube
**Command:** `eval $(minikube -p phase3 docker-env)`  
**Action:** Execute  
**Duration:** 30 sec  

**Requirements:**
- Docker daemon points to Minikube
- Images buildable in Minikube context
- Exit code: 0

**Validation:**
```bash
docker info 2>&1 | grep -q "minikube" && echo "PASS" || echo "FAIL"
```

---

### Task 8: Rebuild Images in Minikube Context
**Commands:**
- `docker build -t phase3-backend:latest ./backend`
- `docker build -t phase3-frontend:latest ./frontend`  
**Action:** Execute  
**Duration:** 5 min  

**Requirements:**
- Images built in Minikube registry
- Both images available locally
- Exit code: 0

**Validation:**
```bash
docker images | grep -q "phase3-backend" && docker images | grep -q "phase3-frontend" && echo "PASS" || echo "FAIL"
```

---

### Task 9: Create Kubernetes Namespace
**Command:** `kubectl create namespace phase3`  
**Action:** Execute  
**Duration:** 30 sec  

**Requirements:**
- Namespace: `phase3`
- Exit code: 0

**Validation:**
```bash
kubectl get namespace phase3 && echo "PASS" || echo "FAIL"
```

---

### Task 10: Create Kubernetes Secrets
**Command:**
```bash
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=phase3password123 \
  --from-literal=POSTGRES_DB=todoapp \
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp \
  --from-literal=BETTER_AUTH_SECRET=minikube_dev_secret_key_change_in_production \
  --from-literal=OPENAI_API_KEY= \
  -n phase3
```
**Action:** Execute  
**Duration:** 30 sec  

**Requirements:**
- Secret name: `phase3-secrets`
- All 6 keys present
- Namespace: `phase3`
- Exit code: 0

**Validation:**
```bash
kubectl get secret phase3-secrets -n phase3 && echo "PASS" || echo "FAIL"
```

---

### Task 11: Deploy Helm Chart
**Command:**
```bash
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3
```
**Action:** Execute  
**Duration:** 2 min  

**Requirements:**
- Release name: `phase3`
- Values file: `values-minikube.yaml`
- Namespace: `phase3`
- Exit code: 0

**Validation:**
```bash
helm list -n phase3 | grep -q "phase3" && echo "PASS" || echo "FAIL"
```

---

### Task 12: Wait for Deployments
**Commands:**
```bash
kubectl wait --for=condition=available deployment/frontend -n phase3 --timeout=300s
kubectl wait --for=condition=available deployment/backend -n phase3 --timeout=300s
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase3 --timeout=300s
```
**Action:** Execute  
**Duration:** 5 min  

**Requirements:**
- Frontend deployment: Available
- Backend deployment: Available
- PostgreSQL pod: Ready
- Timeout: 300s per deployment
- Exit code: 0

**Validation:**
```bash
kubectl get deployments -n phase3 | grep -E "frontend|backend" | grep -q "1/1" && echo "PASS" || echo "FAIL"
```

---

### Task 13: Verify All Pods Running
**Command:** `kubectl get pods -n phase3`  
**Action:** Execute + Validate  
**Duration:** 1 min  

**Requirements:**
- All pods in `Running` state
- All containers in `READY` state
- Minimum 5 pods (2 frontend, 2 backend, 1 postgres)

**Validation:**
```bash
RUNNING=$(kubectl get pods -n phase3 --no-headers | grep -c "Running")
test "$RUNNING" -ge 5 && echo "PASS ($RUNNING pods)" || echo "FAIL ($RUNNING pods)"
```

---

### Task 14: Verify Services and Ingress
**Commands:**
```bash
kubectl get services -n phase3
kubectl get ingress -n phase3
```
**Action:** Execute + Validate  
**Duration:** 1 min  

**Requirements:**
- frontend-service: ClusterIP, port 80
- backend-service: ClusterIP, port 8080
- postgres-service: ClusterIP, port 5432
- Ingress: configured with host `todo-app.local`

**Validation:**
```bash
kubectl get svc frontend-service backend-service postgres-service -n phase3 && echo "PASS" || echo "FAIL"
kubectl get ingress phase3-ingress -n phase3 && echo "PASS" || echo "FAIL"
```

---

### Task 15: Health Check Verification
**Commands:**
```bash
# Backend health
BACKEND_IP=$(kubectl get svc backend-service -n phase3 -o jsonpath='{.spec.clusterIP}')
curl -s http://${BACKEND_IP}:8080/health | grep -q "healthy"

# Frontend health
FRONTEND_IP=$(kubectl get svc frontend-service -n phase3 -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" http://${FRONTEND_IP}/

# Database health
kubectl exec postgres-phase3-todo-chatbot-0 -n phase3 -- pg_isready -U phase3user
```
**Action:** Execute + Validate  
**Duration:** 2 min  

**Requirements:**
- Backend returns `{"status": "healthy"}`
- Frontend returns HTTP 200
- PostgreSQL returns `accepting connections`

**Validation:**
```bash
# All three checks must pass
curl -s http://${BACKEND_IP}:8080/health | grep -q "healthy" && \
test "$(curl -s -o /dev/null -w "%{http_code}" http://${FRONTEND_IP}/)" = "200" && \
kubectl exec postgres-phase3-todo-chatbot-0 -n phase3 -- pg_isready -U phase3user && \
echo "PASS" || echo "FAIL"
```

---

## Execution Summary

| Phase | Tasks | Total Duration |
|-------|-------|----------------|
| **Containerization** | 1-4 | 10 min |
| **Cluster Setup** | 5-8 | 8.5 min |
| **Kubernetes Deploy** | 9-12 | 9.5 min |
| **Verification** | 13-15 | 4 min |
| **TOTAL** | **15 tasks** | **32 min** |

---

## Automated Execution Script

```bash
#!/bin/bash
set -e

echo "=== Phase 3 Todo Chatbot - Automated Kubernetes Deployment ==="

# Task 1-2: Dockerfiles exist (already created)
echo "[1/15] Checking Backend Dockerfile..."
test -f backend/Dockerfile && echo "✓ Backend Dockerfile exists"

echo "[2/15] Checking Frontend Dockerfile..."
test -f frontend/Dockerfile && echo "✓ Frontend Dockerfile exists"

# Task 3-4: Build images
echo "[3/15] Building Backend image..."
docker build -t phase3-backend:latest ./backend

echo "[4/15] Building Frontend image..."
docker build -t phase3-frontend:latest ./frontend

# Task 5-6: Start Minikube
echo "[5/15] Starting Minikube..."
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

echo "[6/15] Enabling addons..."
minikube addons enable ingress --profile phase3
minikube addons enable metrics-server --profile phase3

# Task 7-8: Configure Docker for Minikube
echo "[7/15] Configuring Docker for Minikube..."
eval $(minikube -p phase3 docker-env)

echo "[8/15] Rebuilding images in Minikube context..."
docker build -t phase3-backend:latest ./backend
docker build -t phase3-frontend:latest ./frontend

# Task 9-10: Create namespace and secrets
echo "[9/15] Creating namespace..."
kubectl create namespace phase3 --dry-run=client -o yaml | kubectl apply -f -

echo "[10/15] Creating secrets..."
kubectl create secret generic phase3-secrets \
  --from-literal=POSTGRES_USER=phase3user \
  --from-literal=POSTGRES_PASSWORD=phase3password123 \
  --from-literal=POSTGRES_DB=todoapp \
  --from-literal=DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp \
  --from-literal=BETTER_AUTH_SECRET=minikube_dev_secret_key_change_in_production \
  --from-literal=OPENAI_API_KEY= \
  -n phase3 --dry-run=client -o yaml | kubectl apply -f -

# Task 11-12: Deploy Helm chart
echo "[11/15] Deploying Helm chart..."
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3 --create-namespace

echo "[12/15] Waiting for deployments..."
kubectl wait --for=condition=available deployment/frontend -n phase3 --timeout=300s
kubectl wait --for=condition=available deployment/backend -n phase3 --timeout=300s
kubectl wait --for=condition=ready pod/postgres-phase3-todo-chatbot-0 -n phase3 --timeout=300s

# Task 13-15: Verification
echo "[13/15] Verifying pods..."
kubectl get pods -n phase3

echo "[14/15] Verifying services and ingress..."
kubectl get services -n phase3
kubectl get ingress -n phase3

echo "[15/15] Running health checks..."
BACKEND_IP=$(kubectl get svc backend-service -n phase3 -o jsonpath='{.spec.clusterIP}')
FRONTEND_IP=$(kubectl get svc frontend-service -n phase3 -o jsonpath='{.spec.clusterIP}')

curl -s http://${BACKEND_IP}:8080/health
curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://${FRONTEND_IP}/
kubectl exec postgres-phase3-todo-chatbot-0 -n phase3 -- pg_isready -U phase3user

echo ""
echo "=== Deployment Complete ==="
echo "Access: minikube service frontend-service -n phase3 --profile phase3"
```

---

## Rollback Commands

```bash
# Task: Rollback Helm release
helm rollback phase3 -n phase3

# Task: Rollback frontend deployment
kubectl rollout undo deployment/frontend -n phase3

# Task: Rollback backend deployment
kubectl rollout undo deployment/backend -n phase3

# Task: Full uninstall
helm uninstall phase3 -n phase3
kubectl delete namespace phase3 --ignore-not-found

# Task: Stop Minikube
minikube stop -p phase3
```

---

## Task Dependencies

```
Task 1 ─┬─> Task 3 ─> Task 8 ─┐
        │                     │
Task 2 ─┴─> Task 4 ─> Task 8 ─┤
                              │
Task 5 ─> Task 6 ─> Task 7 ───┤
                              │
Task 9 ─> Task 10 ────────────┼─> Task 11 ─> Task 12 ─> Task 13 ─> Task 14 ─> Task 15
                              │
                              │
```

---

**Execution Status:** Ready for automated execution  
**Manual Intervention Required:** None
