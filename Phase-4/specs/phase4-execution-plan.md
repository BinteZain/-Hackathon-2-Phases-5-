# Phase IV: Step-by-Step Execution Plan

**Document Type:** Execution Plan  
**Version:** 1.0.0  
**Based On:** `specs/infrastructure/phase4-deployment.md`  
**Date:** 2026-02-21  

---

## Overview

This execution plan breaks down the Phase IV cloud-native deployment into 5 sequential phases with testable milestones. Each phase must complete successfully before proceeding to the next.

---

## Phase A – Dockerization

**Objective:** Build production-ready Docker images for all components  
**Duration:** 2-3 hours  
**Success Criteria:** All images build successfully and run locally  

### Task A.1: Verify Prerequisites

- [ ] A.1.1 Verify Docker Desktop is running (`docker info`)
- [ ] A.1.2 Verify Docker version >= 20.10 (`docker --version`)
- [ ] A.1.3 Verify sufficient disk space (minimum 10GB free)
- [ ] A.1.4 Verify existing Dockerfiles exist:
  - [ ] `frontend/Dockerfile`
  - [ ] `backend/Dockerfile`

### Task A.2: Validate Frontend Dockerfile

- [ ] A.2.1 Review `frontend/Dockerfile` for multi-stage build
- [ ] A.2.2 Verify Node.js version (18-alpine)
- [ ] A.2.3 Verify non-root user configuration (UID 1000)
- [ ] A.2.4 Verify health check configuration
- [ ] A.2.5 Verify build arguments and environment variables
- [ ] A.2.6 Document any required updates

### Task A.3: Validate Backend Dockerfile

- [ ] A.3.1 Review `backend/Dockerfile` for multi-stage build
- [ ] A.3.2 Verify Python version (3.11-slim)
- [ ] A.3.3 Verify non-root user configuration (UID 1000)
- [ ] A.3.4 Verify health check configuration (`/health` endpoint)
- [ ] A.3.5 Verify Alembic migration integration
- [ ] A.3.6 Verify PostgreSQL client installation
- [ ] A.3.7 Document any required updates

### Task A.4: Build Frontend Image

- [ ] A.4.1 Build image: `docker build -t phase3-frontend:latest ./frontend`
- [ ] A.4.2 Verify image created (`docker images | grep phase3-frontend`)
- [ ] A.4.3 Check image size (should be < 200MB)
- [ ] A.4.4 Test image locally:
  - [ ] Run container: `docker run -p 3000:3000 phase3-frontend:latest`
  - [ ] Verify health endpoint: `curl http://localhost:3000/`
  - [ ] Check logs: `docker logs <container-id>`
- [ ] A.4.5 Tag image for Minikube: `docker tag phase3-frontend:latest phase3-frontend:v1.0.0`

### Task A.5: Build Backend Image

- [ ] A.5.1 Build image: `docker build -t phase3-backend:latest ./backend`
- [ ] A.5.2 Verify image created (`docker images | grep phase3-backend`)
- [ ] A.5.3 Check image size (should be < 300MB)
- [ ] A.5.4 Test image locally:
  - [ ] Run container with env vars
  - [ ] Verify health endpoint: `curl http://localhost:4000/health`
  - [ ] Check logs: `docker logs <container-id>`
- [ ] A.5.5 Tag image for Minikube: `docker tag phase3-backend:latest phase3-backend:v1.0.0`

### Task A.6: Create .dockerignore Files

- [ ] A.6.1 Create `frontend/.dockerignore`:
  - [ ] Exclude `node_modules`
  - [ ] Exclude `.next` (built inside container)
  - [ ] Exclude `.env*` files
  - [ ] Exclude `.git`
- [ ] A.6.2 Create `backend/.dockerignore`:
  - [ ] Exclude `__pycache__`
  - [ ] Exclude `*.pyc`
  - [ ] Exclude `.env*` files
  - [ ] Exclude `venv/`
  - [ ] Exclude `.git`

### Task A.7: Docker Compose Validation

- [ ] A.7.1 Test existing `docker-compose.yml`
- [ ] A.7.2 Run: `docker-compose up --build`
- [ ] A.7.3 Verify all services start:
  - [ ] Frontend accessible at `http://localhost:3000`
  - [ ] Backend accessible at `http://localhost:4000`
  - [ ] Database running and accepting connections
- [ ] A.7.4 Run: `docker-compose down`

### Task A.8: Image Optimization (If Needed)

- [ ] A.8.1 Analyze image layers: `docker history phase3-frontend:latest`
- [ ] A.8.2 Identify optimization opportunities
- [ ] A.8.3 Rebuild with optimizations if size > target
- [ ] A.8.4 Document final image sizes

### Phase A Deliverables

- [ ] `frontend/Dockerfile` - Validated and tested
- [ ] `backend/Dockerfile` - Validated and tested
- [ ] `frontend/.dockerignore` - Created
- [ ] `backend/.dockerignore` - Created
- [ ] `phase3-frontend:v1.0.0` - Built and tested
- [ ] `phase3-backend:v1.0.0` - Built and tested
- [ ] Docker Compose validation report

### Phase A Acceptance Criteria

- [ ] Both images build without errors
- [ ] Both images pass health checks
- [ ] Image sizes within acceptable limits (< 500MB combined)
- [ ] Docker Compose stack runs successfully
- [ ] All containers use non-root users

---

## Phase B – Helm Chart Creation

**Objective:** Create complete Helm chart for Phase III application  
**Duration:** 3-4 hours  
**Success Criteria:** Helm chart passes linting and template validation  

### Task B.1: Review Existing Helm Chart

- [ ] B.1.1 Examine `helm-charts/phase3-todo-chatbot/` structure
- [ ] B.1.2 Review `Chart.yaml` metadata
- [ ] B.1.3 Review `values.yaml` configuration
- [ ] B.1.4 Review `values-minikube.yaml` overrides
- [ ] B.1.5 Review `values-production.yaml` overrides
- [ ] B.1.6 List existing templates in `templates/` directory
- [ ] B.1.7 Identify gaps vs. `phase4-deployment.md` specification

### Task B.2: Update Chart Metadata

- [ ] B.2.1 Update `Chart.yaml`:
  - [ ] Set version to `1.0.0`
  - [ ] Set appVersion to `1.0.0`
  - [ ] Update description
  - [ ] Add keywords: `todo`, `chatbot`, `fastapi`, `nextjs`, `postgresql`
  - [ ] Add maintainer information
  - [ ] Add source repository URL

### Task B.3: Create/Update Values Files

- [ ] B.3.1 Update `values.yaml` with complete configuration:
  - [ ] Global settings (namespace, registry, storageClass)
  - [ ] Frontend configuration (image, replicas, resources, probes, HPA)
  - [ ] Backend configuration (image, replicas, resources, probes, HPA)
  - [ ] PostgreSQL configuration (image, persistence, resources)
  - [ ] Ingress configuration (hosts, paths, annotations)
  - [ ] Secrets configuration
  - [ ] NetworkPolicy configuration
  - [ ] RBAC configuration
  - [ ] PDB configuration
  - [ ] ResourceQuota configuration
  - [ ] LimitRange configuration
- [ ] B.3.2 Create/update `values-minikube.yaml`:
  - [ ] Adjust resource limits for local environment
  - [ ] Set replica counts to minimum (2 for HA)
  - [ ] Configure storageClass for Minikube
  - [ ] Disable non-essential features
- [ ] B.3.3 Create/update `values-production.yaml`:
  - [ ] Increase resource limits
  - [ ] Configure production replicas
  - [ ] Enable all security features
  - [ ] Configure production storage

### Task B.4: Create Template Helpers

- [ ] B.4.1 Create/update `templates/_helpers.tpl`:
  - [ ] Define `phase3.name` helper
  - [ ] Define `phase3.fullname` helper
  - [ ] Define `phase3.chart` helper
  - [ ] Define `phase3.labels` helper
  - [ ] Define `phase3.selectorLabels` helper
  - [ ] Define `phase3.serviceAccountName` helper
  - [ ] Define `phase3.frontend.fullname` helper
  - [ ] Define `phase3.backend.fullname` helper
  - [ ] Define `phase3.postgres.fullname` helper

### Task B.5: Create Namespace Template

- [ ] B.5.1 Create `templates/namespace.yaml`:
  - [ ] Define namespace `phase3`
  - [ ] Add labels for identification
  - [ ] Conditionally create based on `.Values.global.createNamespace`

### Task B.6: Create ConfigMap Templates

- [ ] B.6.1 Create `templates/configmap-frontend.yaml`:
  - [ ] Define `NODE_ENV`
  - [ ] Define `NEXT_PUBLIC_API_URL`
  - [ ] Add frontend-specific configs
- [ ] B.6.2 Create `templates/configmap-backend.yaml`:
  - [ ] Define `PYTHON_ENV`
  - [ ] Define `LOG_LEVEL`
  - [ ] Add backend-specific configs

### Task B.7: Create Secret Templates

- [ ] B.7.1 Create `templates/secrets.yaml`:
  - [ ] Generate `postgres-password` (random if not provided)
  - [ ] Generate `better-auth-secret` (random if not provided)
  - [ ] Define `postgres-user`
  - [ ] Define `postgres-db`
  - [ ] Add template logic for auto-generation

### Task B.8: Create RBAC Templates

- [ ] B.8.1 Create `templates/serviceaccount.yaml`:
  - [ ] Define service account `phase3-sa`
  - [ ] Add annotations
  - [ ] Conditionally create based on `.Values.rbac.serviceAccount.create`
- [ ] B.8.2 Create `templates/role.yaml`:
  - [ ] Define role with minimal permissions
  - [ ] Allow configmap/secret read access
- [ ] B.8.3 Create `templates/rolebinding.yaml`:
  - [ ] Bind service account to role

### Task B.9: Create Deployment Templates

- [ ] B.9.1 Create `templates/deployment-frontend.yaml`:
  - [ ] Define metadata (name, labels, annotations)
  - [ ] Configure pod spec with security context
  - [ ] Set container image from values
  - [ ] Configure environment variables from ConfigMap
  - [ ] Configure resource limits
  - [ ] Configure liveness/readiness probes
  - [ ] Add pod anti-affinity for HA
- [ ] B.9.2 Create `templates/deployment-backend.yaml`:
  - [ ] Define metadata (name, labels, annotations)
  - [ ] Configure pod spec with security context
  - [ ] Set container image from values
  - [ ] Configure environment variables from Secret/ConfigMap
  - [ ] Configure resource limits
  - [ ] Configure liveness/readiness probes
  - [ ] Add database connection logic
  - [ ] Add pod anti-affinity for HA
- [ ] B.9.3 Create `templates/deployment-postgres.yaml`:
  - [ ] Define metadata (name, labels, annotations)
  - [ ] Configure pod spec with security context
  - [ ] Set container image from values
  - [ ] Configure environment variables from Secret
  - [ ] Configure resource limits
  - [ ] Configure liveness/readiness probes
  - [ ] Configure volume mounts for persistence

### Task B.10: Create Service Templates

- [ ] B.10.1 Create `templates/service-frontend.yaml`:
  - [ ] Define ClusterIP service
  - [ ] Configure port 80 → 3000
  - [ ] Add selector labels
- [ ] B.10.2 Create `templates/service-backend.yaml`:
  - [ ] Define ClusterIP service
  - [ ] Configure port 8080 → 4000
  - [ ] Add selector labels
- [ ] B.10.3 Create `templates/service-postgres.yaml`:
  - [ ] Define ClusterIP service
  - [ ] Configure port 5432 → 5432
  - [ ] Add selector labels

### Task B.11: Create Persistence Templates

- [ ] B.11.1 Create `templates/pvc-postgres.yaml`:
  - [ ] Define PersistentVolumeClaim
  - [ ] Set access mode `ReadWriteOnce`
  - [ ] Configure storage size from values
  - [ ] Set storageClass from values

### Task B.12: Create Ingress Template

- [ ] B.12.1 Create `templates/ingress.yaml`:
  - [ ] Define Ingress with NGINX class
  - [ ] Configure annotations (rewrite-target, ssl-redirect)
  - [ ] Define host `todo-app.local`
  - [ ] Configure path `/api/*` → backend
  - [ ] Configure path `/*` → frontend
  - [ ] Add TLS configuration (optional)

### Task B.13: Create HPA Templates

- [ ] B.13.1 Create `templates/hpa-frontend.yaml`:
  - [ ] Define HPA targeting frontend deployment
  - [ ] Set min/max replicas
  - [ ] Configure CPU/memory metrics
  - [ ] Configure scale up/down behavior
- [ ] B.13.2 Create `templates/hpa-backend.yaml`:
  - [ ] Define HPA targeting backend deployment
  - [ ] Set min/max replicas
  - [ ] Configure CPU/memory metrics
  - [ ] Configure scale up/down behavior

### Task B.14: Create PDB Templates

- [ ] B.14.1 Create `templates/pdb-frontend.yaml`:
  - [ ] Define PodDisruptionBudget
  - [ ] Set `minAvailable: 1`
  - [ ] Add selector labels
- [ ] B.14.2 Create `templates/pdb-backend.yaml`:
  - [ ] Define PodDisruptionBudget
  - [ ] Set `minAvailable: 1`
  - [ ] Add selector labels

### Task B.15: Create NetworkPolicy Template

- [ ] B.15.1 Create `templates/networkpolicy.yaml`:
  - [ ] Define NetworkPolicy for namespace
  - [ ] Configure ingress rules (allow from ingress-nginx)
  - [ ] Configure egress rules (allow DNS, database)
  - [ ] Apply to all pods in namespace

### Task B.16: Create ResourceQuota Template

- [ ] B.16.1 Create `templates/resourcequota.yaml`:
  - [ ] Define ResourceQuota for namespace
  - [ ] Set CPU/memory limits
  - [ ] Set pod/service/secret/configmap limits
  - [ ] Set PVC count limit

### Task B.17: Create LimitRange Template

- [ ] B.17.1 Create `templates/limitrange.yaml`:
  - [ ] Define LimitRange for containers
  - [ ] Set default requests/limits
  - [ ] Set min/max constraints

### Task B.18: Create NOTES.txt

- [ ] B.18.1 Create `templates/NOTES.txt`:
  - [ ] Display installation success message
  - [ ] Show access URLs
  - [ ] Provide troubleshooting commands
  - [ ] Display next steps

### Task B.19: Create Helm Tests

- [ ] B.19.1 Create `tests/test-frontend.yaml`:
  - [ ] Define test pod
  - [ ] Test frontend service connectivity
  - [ ] Verify health endpoint
- [ ] B.19.2 Create `tests/test-backend.yaml`:
  - [ ] Define test pod
  - [ ] Test backend service connectivity
  - [ ] Verify health endpoint

### Task B.20: Validate Helm Chart

- [ ] B.20.1 Run `helm lint ./helm-charts/phase3-todo-chatbot`
- [ ] B.20.2 Fix any linting errors
- [ ] B.20.3 Run `helm template phase3-todo ./helm-charts/phase3-todo-chatbot`
- [ ] B.20.4 Review rendered templates
- [ ] B.20.5 Run `helm template` with Minikube values
- [ ] B.20.6 Validate YAML syntax
- [ ] B.20.7 Dry-run install: `helm install --dry-run --debug`

### Phase B Deliverables

- [ ] `helm-charts/phase3-todo-chatbot/Chart.yaml` - Updated
- [ ] `helm-charts/phase3-todo-chatbot/values.yaml` - Complete
- [ ] `helm-charts/phase3-todo-chatbot/values-minikube.yaml` - Configured
- [ ] `helm-charts/phase3-todo-chatbot/values-production.yaml` - Configured
- [ ] `helm-charts/phase3-todo-chatbot/templates/` - All 20+ templates
- [ ] `helm-charts/phase3-todo-chatbot/tests/` - Test templates
- [ ] Helm lint validation report

### Phase B Acceptance Criteria

- [ ] `helm lint` passes with no errors
- [ ] `helm template` renders all templates successfully
- [ ] All templates produce valid Kubernetes YAML
- [ ] Values files override correctly
- [ ] Conditional logic works (enabled/disabled components)
- [ ] Secrets auto-generate when empty
- [ ] NOTES.txt displays helpful information

---

## Phase C – Kubernetes Deployment

**Objective:** Deploy application to Minikube cluster  
**Duration:** 2-3 hours  
**Success Criteria:** All pods running, services accessible, ingress functional  

### Task C.1: Prepare Minikube Environment

- [ ] C.1.1 Verify Minikube installation: `minikube version`
- [ ] C.1.2 Verify kubectl installation: `kubectl version --client`
- [ ] C.1.3 Verify Helm installation: `helm version`
- [ ] C.1.4 Check system resources (minimum 8GB RAM, 4 CPUs)
- [ ] C.1.5 Stop existing Minikube: `minikube stop` (if running)
- [ ] C.1.6 Delete existing cluster: `minikube delete` (if needed)

### Task C.2: Create Minikube Cluster

- [ ] C.2.1 Start Minikube with resources:
  ```
  minikube start \
    --driver=docker \
    --cpus=4 \
    --memory=8192 \
    --disk-size=20g \
    --kubernetes-version=stable
  ```
- [ ] C.2.2 Verify cluster status: `minikube status`
- [ ] C.2.3 Verify kubectl context: `kubectl config current-context`
- [ ] C.2.4 Test cluster connectivity: `kubectl cluster-info`

### Task C.3: Enable Minikube Addons

- [ ] C.3.1 Enable NGINX Ingress: `minikube addons enable ingress`
- [ ] C.3.2 Verify Ingress Controller: `kubectl get pods -n ingress-nginx`
- [ ] C.3.3 Enable Metrics Server: `minikube addons enable metrics-server`
- [ ] C.3.4 Verify Metrics Server: `kubectl top nodes`
- [ ] C.3.5 (Optional) Enable Dashboard: `minikube addons enable dashboard`

### Task C.4: Configure Docker Environment

- [ ] C.4.1 Point to Minikube Docker daemon: `eval $(minikube docker-env)`
- [ ] C.4.2 Verify Docker context: `docker context ls`
- [ ] C.4.3 Build frontend image in Minikube: `docker build -t phase3-frontend:v1.0.0 ./frontend`
- [ ] C.4.4 Build backend image in Minikube: `docker build -t phase3-backend:v1.0.0 ./backend`
- [ ] C.4.5 Verify images: `docker images | grep phase3`

### Task C.5: Generate Secrets

- [ ] C.5.1 Generate PostgreSQL password: `openssl rand -base64 32`
- [ ] C.5.2 Generate Better Auth secret: `openssl rand -base64 32`
- [ ] C.5.3 Store secrets securely for Helm installation

### Task C.6: Install Helm Chart

- [ ] C.6.1 Navigate to chart: `cd helm-charts/phase3-todo-chatbot`
- [ ] C.6.2 Install with Minikube values:
  ```
  helm install phase3-todo . \
    --namespace phase3 \
    --create-namespace \
    --values values-minikube.yaml \
    --set secrets.postgresPassword=<generated-password> \
    --set secrets.betterAuthSecret=<generated-secret>
  ```
- [ ] C.6.3 Verify installation: `helm list -n phase3`
- [ ] C.6.4 Check release status: `helm status phase3-todo -n phase3`

### Task C.7: Monitor Deployment Rollout

- [ ] C.7.1 Watch pods: `kubectl get pods -n phase3 --watch`
- [ ] C.7.2 Verify all pods reach `Running` state
- [ ] C.7.3 Check for pending pods: `kubectl get pods -n phase3 | grep Pending`
- [ ] C.7.4 Check for crash loops: `kubectl get pods -n phase3 | grep CrashLoopBackOff`
- [ ] C.7.5 Describe problematic pods: `kubectl describe pod <pod-name> -n phase3`

### Task C.8: Verify Deployments

- [ ] C.8.1 Check deployment status: `kubectl get deployments -n phase3`
- [ ] C.8.2 Verify replica counts match expected
- [ ] C.8.3 Check rollout status: `kubectl rollout status deployment/frontend -n phase3`
- [ ] C.8.4 Check rollout status: `kubectl rollout status deployment/backend -n phase3`
- [ ] C.8.5 Check rollout status: `kubectl rollout status deployment/postgres -n phase3`

### Task C.9: Verify Services

- [ ] C.9.1 List services: `kubectl get svc -n phase3`
- [ ] C.9.2 Verify frontend service endpoint
- [ ] C.9.3 Verify backend service endpoint
- [ ] C.9.4 Verify postgres service endpoint
- [ ] C.9.5 Test service connectivity from within cluster

### Task C.10: Configure Ingress

- [ ] C.10.1 Get Minikube IP: `minikube ip`
- [ ] C.10.2 Add to hosts file:
  - Windows: Add to `C:\Windows\System32\drivers\etc\hosts`
  - Linux/Mac: Add to `/etc/hosts`
- [ ] C.10.3 Verify ingress: `kubectl get ingress -n phase3`
- [ ] C.10.4 Describe ingress: `kubectl describe ingress phase3-ingress -n phase3`

### Task C.11: Test Application Access

- [ ] C.11.1 Test frontend: `curl http://todo-app.local`
- [ ] C.11.2 Test backend health: `curl http://todo-app.local/api/health`
- [ ] C.11.3 Test API endpoint: `curl http://todo-app.local/api/v1/todos`
- [ ] C.11.4 Open in browser: `http://todo-app.local`
- [ ] C.11.5 Verify frontend-backend communication

### Task C.12: Verify Database Connectivity

- [ ] C.12.1 Check postgres pod logs: `kubectl logs -n phase3 -l app=postgres`
- [ ] C.12.2 Exec into postgres pod: `kubectl exec -it -n phase3 <postgres-pod> -- psql -U phase3user -d todoapp`
- [ ] C.12.3 Run test query: `SELECT version();`
- [ ] C.12.4 Verify tables created: `\dt`
- [ ] C.12.5 Check backend can connect: Review backend logs for DB connection success

### Task C.13: Verify ConfigMaps and Secrets

- [ ] C.13.1 List configmaps: `kubectl get configmaps -n phase3`
- [ ] C.13.2 List secrets: `kubectl get secrets -n phase3`
- [ ] C.13.3 Verify configmap contents: `kubectl describe configmap frontend-config -n phase3`
- [ ] C.13.4 Verify secret contents (decoded): `kubectl get secret phase3-secrets -n phase3 -o jsonpath='{.data}'`

### Task C.14: Verify RBAC

- [ ] C.14.1 List service accounts: `kubectl get sa -n phase3`
- [ ] C.14.2 List roles: `kubectl get roles -n phase3`
- [ ] C.14.3 List role bindings: `kubectl get rolebindings -n phase3`
- [ ] C.14.4 Verify service account used by pods

### Task C.15: Verify Network Policies

- [ ] C.15.1 List network policies: `kubectl get networkpolicies -n phase3`
- [ ] C.15.2 Describe network policy: `kubectl describe networkpolicy phase3-network-policy -n phase3`
- [ ] C.15.3 Test pod-to-pod communication
- [ ] C.15.4 Test external access restrictions

### Task C.16: Create Deployment Report

- [ ] C.16.1 Document deployment timestamp
- [ ] C.16.2 Record image versions deployed
- [ ] C.16.3 Record Helm chart version
- [ ] C.16.4 Record any deviations from plan
- [ ] C.16.5 Save kubectl output for reference

### Phase C Deliverables

- [ ] Running Minikube cluster with proper resources
- [ ] NGINX Ingress Controller enabled
- [ ] Metrics Server enabled
- [ ] Helm release `phase3-todo` installed
- [ ] All deployments running (frontend, backend, postgres)
- [ ] All services accessible
- [ ] Ingress configured and functional
- [ ] Application accessible at `http://todo-app.local`
- [ ] Deployment report document

### Phase C Acceptance Criteria

- [ ] `kubectl get all -n phase3` shows all resources
- [ ] All pods in `Running` state with `READY 1/1`
- [ ] All deployments show `AVAILABLE`
- [ ] Frontend accessible via browser
- [ ] Backend health endpoint returns 200
- [ ] Database accepting connections
- [ ] Ingress routing correctly (/api/* → backend, /* → frontend)
- [ ] No error logs in any pod

---

## Phase D – Scaling & Optimization

**Objective:** Validate auto-scaling and optimize resource usage  
**Duration:** 2-3 hours  
**Success Criteria:** HPA functional, resources optimized, load testing passed  

### Task D.1: Verify HPA Configuration

- [ ] D.1.1 List HPAs: `kubectl get hpa -n phase3`
- [ ] D.1.2 Describe frontend HPA: `kubectl describe hpa frontend-hpa -n phase3`
- [ ] D.1.3 Describe backend HPA: `kubectl describe hpa backend-hpa -n phase3`
- [ ] D.1.4 Verify target deployment references
- [ ] D.1.5 Verify min/max replica counts
- [ ] D.1.6 Verify CPU/memory targets

### Task D.2: Verify Metrics Collection

- [ ] D.2.1 Check metrics availability: `kubectl top pods -n phase3`
- [ ] D.2.2 Check node metrics: `kubectl top nodes`
- [ ] D.2.3 Verify Metrics Server pods: `kubectl get pods -n kube-system | grep metrics-server`
- [ ] D.2.4 Troubleshoot if metrics unavailable

### Task D.3: Baseline Resource Usage

- [ ] D.3.1 Record current CPU usage for all pods
- [ ] D.3.2 Record current memory usage for all pods
- [ ] D.3.3 Document baseline metrics
- [ ] D.3.4 Compare against configured requests/limits

### Task D.4: Load Testing Setup

- [ ] D.4.1 Install load testing tool (k6, wrk, or Apache Bench)
- [ ] D.4.2 Create load test script for frontend
- [ ] D.4.3 Create load test script for backend API
- [ ] D.4.4 Define load test scenarios:
  - [ ] Scenario 1: 10 concurrent users
  - [ ] Scenario 2: 50 concurrent users
  - [ ] Scenario 3: 100 concurrent users

### Task D.5: Execute Load Test - Frontend

- [ ] D.5.1 Run baseline test (10 users)
- [ ] D.5.2 Record response times
- [ ] D.5.3 Monitor pod scaling: `kubectl get pods -n phase3 --watch`
- [ ] D.5.4 Run stress test (100 users)
- [ ] D.5.5 Record scaling behavior
- [ ] D.5.6 Record HPA metrics during test

### Task D.6: Execute Load Test - Backend

- [ ] D.6.1 Run baseline test (10 users) on `/api/health`
- [ ] D.6.2 Run API load test on `/api/v1/todos`
- [ ] D.6.3 Record response times
- [ ] D.6.4 Monitor pod scaling
- [ ] D.6.5 Record database connection pool behavior
- [ ] D.6.6 Record HPA metrics during test

### Task D.7: Analyze Scaling Behavior

- [ ] D.7.1 Review HPA events: `kubectl get events -n phase3 --field-selector reason=SuccessfulRescale`
- [ ] D.7.2 Check scale-up timing
- [ ] D.7.3 Check scale-down timing
- [ ] D.7.4 Verify stabilization windows working correctly
- [ ] D.7.5 Identify any scaling issues

### Task D.8: Optimize Resource Requests/Limits

- [ ] D.8.1 Analyze actual resource usage vs. configured
- [ ] D.8.2 Identify over-provisioned resources
- [ ] D.8.3 Identify under-provisioned resources
- [ ] D.8.4 Update `values-minikube.yaml` with optimized values
- [ ] D.8.5 Document optimization rationale

### Task D.9: Apply Resource Optimizations

- [ ] D.9.1 Upgrade Helm release with new values:
  ```
  helm upgrade phase3-todo . \
    --namespace phase3 \
    --values values-minikube-optimized.yaml
  ```
- [ ] D.9.2 Monitor rollout: `kubectl rollout status deployment/frontend -n phase3`
- [ ] D.9.3 Verify new resource limits applied
- [ ] D.9.4 Re-run load test to validate optimizations

### Task D.10: Test Pod Disruption Budgets

- [ ] D.10.1 List PDBs: `kubectl get pdb -n phase3`
- [ ] D.10.2 Describe PDBs: `kubectl describe pdb frontend-pdb -n phase3`
- [ ] D.10.3 Test PDB by draining node (simulated)
- [ ] D.10.4 Verify minimum pods maintained
- [ ] D.10.5 Verify application remains available

### Task D.11: Test High Availability

- [ ] D.11.1 Delete frontend pod: `kubectl delete pod -n phase3 -l app=frontend`
- [ ] D.11.2 Observe auto-healing
- [ ] D.11.3 Delete backend pod: `kubectl delete pod -n phase3 -l app=backend`
- [ ] D.11.4 Observe auto-healing
- [ ] D.11.5 Verify zero downtime during pod replacement

### Task D.12: Optimize Image Pull Policies

- [ ] D.12.1 Review current pull policies
- [ ] D.12.2 Verify `IfNotPresent` for tagged images
- [ ] D.12.3 Document pull policy recommendations

### Task D.13: Configure Pod Anti-Affinity

- [ ] D.13.1 Verify anti-affinity rules in deployments
- [ ] D.13.2 Test pod distribution across nodes (if multi-node)
- [ ] D.13.3 Verify high availability configuration

### Task D.14: Performance Tuning

- [ ] D.14.1 Review application logs for slow queries
- [ ] D.14.2 Check database connection pool settings
- [ ] D.14.3 Review frontend build optimization
- [ ] D.14.4 Document performance tuning recommendations

### Task D.15: Create Scaling Report

- [ ] D.15.1 Document HPA behavior observed
- [ ] D.15.2 Record scaling thresholds triggered
- [ ] D.15.3 Document resource optimization changes
- [ ] D.15.4 Record load test results
- [ ] D.15.5 Provide recommendations for production

### Phase D Deliverables

- [ ] HPA validated and functional
- [ ] Load test scripts created
- [ ] Load test results document
- [ ] Optimized `values-minikube.yaml`
- [ ] Scaling behavior report
- [ ] Performance tuning recommendations

### Phase D Acceptance Criteria

- [ ] HPA scales up under load
- [ ] HPA scales down after load decreases
- [ ] Metrics Server providing accurate data
- [ ] Resource usage within configured limits
- [ ] Load test passes without errors
- [ ] PDBs maintain minimum availability
- [ ] Pod auto-healing working correctly
- [ ] Optimized resources reduce waste by >20%

---

## Phase E – Observability & Debugging

**Objective:** Implement monitoring, logging, and debugging capabilities  
**Duration:** 2-3 hours  
**Success Criteria:** Full observability stack operational, troubleshooting documented  

### Task E.1: Verify Basic Logging

- [ ] E.1.1 Test frontend logs: `kubectl logs -n phase3 -l app=frontend`
- [ ] E.1.2 Test backend logs: `kubectl logs -n phase3 -l app=backend`
- [ ] E.1.3 Test postgres logs: `kubectl logs -n phase3 -l app=postgres`
- [ ] E.1.4 Test log streaming: `kubectl logs -n phase3 -l app=backend --follow`
- [ ] E.1.5 Test multi-container log access (if applicable)

### Task E.2: Configure Log Aggregation (Optional)

- [ ] E.2.1 Deploy Loki stack (if required):
  ```
  helm repo add grafana https://grafana.github.io/helm-charts
  helm install loki grafana/loki-stack --namespace monitoring --create-namespace
  ```
- [ ] E.2.2 Verify Loki pods running
- [ ] E.2.3 Access Grafana dashboard
- [ ] E.2.4 Configure log queries

### Task E.3: Install Prometheus Stack (Optional)

- [ ] E.3.1 Add Prometheus repo: `helm repo add prometheus-community https://prometheus-community.github.io/helm-charts`
- [ ] E.3.2 Install kube-prometheus-stack:
  ```
  helm install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace
  ```
- [ ] E.3.3 Verify Prometheus pods running
- [ ] E.3.4 Access Grafana: `kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80`
- [ ] E.3.5 Login to Grafana (admin/prom-operator)
- [ ] E.3.6 Import Phase 3 dashboards

### Task E.4: Create Custom Metrics Dashboards

- [ ] E.4.1 Create dashboard for frontend metrics:
  - [ ] Request rate
  - [ ] Error rate
  - [ ] Response time (p50, p95, p99)
  - [ ] Pod CPU/memory usage
- [ ] E.4.2 Create dashboard for backend metrics:
  - [ ] API request rate
  - [ ] Error rate by endpoint
  - [ ] Database query latency
  - [ ] Pod CPU/memory usage
- [ ] E.4.3 Create dashboard for database metrics:
  - [ ] Connection count
  - [ ] Query rate
  - [ ] Storage usage
  - [ ] Pod CPU/memory usage

### Task E.5: Configure Alerts (Optional)

- [ ] E.5.1 Create Alertmanager config
- [ ] E.5.2 Define alert rules:
  - [ ] Pod restart alert
  - [ ] High CPU usage alert (>80% for 5m)
  - [ ] High memory usage alert (>80% for 5m)
  - [ ] High error rate alert (>5% for 5m)
  - [ ] Pod not ready alert
- [ ] E.5.3 Configure notification channels (email, Slack)
- [ ] E.5.4 Test alert firing

### Task E.6: Implement Distributed Tracing (Optional)

- [ ] E.6.1 Deploy Jaeger or Tempo
- [ ] E.6.2 Configure application instrumentation
- [ ] E.6.3 Verify traces appearing
- [ ] E.6.4 Create trace queries

### Task E.7: Test Debugging Workflows

- [ ] E.7.1 Test pod exec: `kubectl exec -it -n phase3 <pod> -- /bin/sh`
- [ ] E.7.2 Test port forwarding:
  - [ ] Frontend: `kubectl port-forward svc/frontend -n phase3 3000:80`
  - [ ] Backend: `kubectl port-forward svc/backend -n phase3 4000:8080`
- [ ] E.7.3 Test describe for troubleshooting: `kubectl describe pod <pod> -n phase3`
- [ ] E.7.4 Test events viewing: `kubectl get events -n phase3 --sort-by='.lastTimestamp'`

### Task E.8: Create Troubleshooting Runbook

- [ ] E.8.1 Document common issues and solutions:
  - [ ] ImagePullBackOff
  - [ ] CrashLoopBackOff
  - [ ] Pending pods
  - [ ] Service not accessible
  - [ ] Ingress 404 errors
  - [ ] Database connection failures
  - [ ] HPA not scaling
- [ ] E.8.2 Include diagnostic commands for each issue
- [ ] E.8.3 Include escalation procedures

### Task E.9: Test Failure Scenarios

- [ ] E.9.1 Simulate frontend failure:
  - [ ] Modify frontend to return 500
  - [ ] Observe health check failures
  - [ ] Verify pod restart
- [ ] E.9.2 Simulate backend failure:
  - [ ] Modify backend to crash
  - [ ] Observe restart behavior
  - [ ] Verify frontend error handling
- [ ] E.9.3 Simulate database failure:
  - [ ] Delete postgres pod
  - [ ] Observe recovery time
  - [ ] Verify data persistence

### Task E.10: Verify Health Endpoints

- [ ] E.10.1 Test frontend health: `curl http://todo-app.local/`
- [ ] E.10.2 Test backend health: `curl http://todo-app.local/api/health`
- [ ] E.10.3 Verify health check response times
- [ ] E.10.4 Document health endpoint URLs

### Task E.11: Create Monitoring Dashboard

- [ ] E.11.1 Deploy Kubernetes Dashboard (if not enabled):
  ```
  minikube addons enable dashboard
  minikube dashboard
  ```
- [ ] E.11.2 Verify dashboard access
- [ ] E.11.3 Navigate to Phase 3 namespace
- [ ] E.11.4 Verify all resources visible

### Task E.12: Document Observability Stack

- [ ] E.12.1 List all monitoring tools deployed
- [ ] E.12.2 Document access URLs:
  - [ ] Grafana URL
  - [ ] Prometheus URL
  - [ ] Kubernetes Dashboard URL
  - [ ] Loki URL (if deployed)
- [ ] E.12.3 Document credentials
- [ ] E.12.4 Document retention policies

### Task E.13: Create Debugging Cheat Sheet

- [ ] E.13.1 List common kubectl commands:
  - [ ] Get all resources
  - [ ] Describe resource
  - [ ] View logs
  - [ ] Exec into container
  - [ ] Port forward
  - [ ] Restart deployment
- [ ] E.13.2 Include Helm debugging commands
- [ ] E.13.3 Include Minikube debugging commands

### Task E.14: Final Health Check

- [ ] E.14.1 Run comprehensive health check:
  ```
  kubectl get all -n phase3
  kubectl get hpa -n phase3
  kubectl get ingress -n phase3
  kubectl top pods -n phase3
  ```
- [ ] E.14.2 Verify all metrics collecting
- [ ] E.14.3 Verify all logs accessible
- [ ] E.14.4 Verify all dashboards showing data

### Task E.15: Create Phase IV Completion Report

- [ ] E.15.1 Summarize all phases completed
- [ ] E.15.2 Document final architecture
- [ ] E.15.3 Record final resource allocations
- [ ] E.15.4 Document lessons learned
- [ ] E.15.5 Provide production deployment recommendations
- [ ] E.15.6 List future improvements

### Phase E Deliverables

- [ ] Logging verified and functional
- [ ] Prometheus stack deployed (optional)
- [ ] Grafana dashboards created
- [ ] Alert rules configured (optional)
- [ ] Troubleshooting runbook
- [ ] Debugging cheat sheet
- [ ] Failure scenario test results
- [ ] Phase IV completion report

### Phase E Acceptance Criteria

- [ ] All pod logs accessible via `kubectl logs`
- [ ] Metrics available via `kubectl top`
- [ ] Grafana dashboards showing all components
- [ ] Alerts configured and tested (if implemented)
- [ ] Troubleshooting runbook complete
- [ ] All failure scenarios tested and documented
- [ ] Health endpoints responding correctly
- [ ] Phase IV completion report approved

---

## Summary Checklist

### Phase A – Dockerization

- [ ] All 8 tasks complete
- [ ] Both Docker images built and tested
- [ ] Docker Compose validation passed
- [ ] Image sizes optimized

### Phase B – Helm Chart Creation

- [ ] All 20 tasks complete
- [ ] Helm chart structure complete
- [ ] All templates created
- [ ] Helm lint passed
- [ ] Template rendering validated

### Phase C – Kubernetes Deployment

- [ ] All 16 tasks complete
- [ ] Minikube cluster running
- [ ] All addons enabled
- [ ] Helm chart installed
- [ ] All pods running
- [ ] Application accessible
- [ ] Ingress functional

### Phase D – Scaling & Optimization

- [ ] All 15 tasks complete
- [ ] HPA validated
- [ ] Load tests passed
- [ ] Resources optimized
- [ ] High availability verified

### Phase E – Observability & Debugging

- [ ] All 15 tasks complete
- [ ] Monitoring operational
- [ ] Logging verified
- [ ] Dashboards created
- [ ] Runbook documented
- [ ] Phase IV complete

---

**Total Tasks:** 74  
**Estimated Duration:** 11-16 hours  
**Success Criteria:** All phases complete with all acceptance criteria met

**Next Step:** Execute Phase A, Task A.1
