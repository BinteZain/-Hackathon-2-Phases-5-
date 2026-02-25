# Phase 4 - Spec-Driven Deployment Blueprints

## Overview

This document provides spec-driven deployment blueprints for Phase 4, enabling automated infrastructure provisioning using AI agents and spec-driven development principles.

## Blueprint Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Spec-Driven Deployment Pipeline                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Spec      │    │   Plan      │    │   Tasks     │         │
│  │  (YAML)     │ -> │  (AI Gen)   │ -> │ (AI Break)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │           Claude Code Agent Skills                   │       │
│  │  - SpecKit Plus for spec management                  │       │
│  │  - PHR for prompt history                            │       │
│  │  - ADR for architectural decisions                   │       │
│  └─────────────────────────────────────────────────────┘       │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Gordon     │    │  kubectl-ai │    │   kagent    │         │
│  │  (Docker)   │    │   (K8s)     │    │  (Cluster)  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Infrastructure Specification

### Phase 4 Infrastructure Spec (YAML)

```yaml
# specs/phase4/infrastructure-spec.yaml
apiVersion: specs.phase4/v1
kind: InfrastructureSpec
metadata:
  name: phase4-todo-chatbot
  version: 1.0.0
  description: "Cloud Native Todo Chatbot with AI-Assisted Operations"

spec:
  # Cluster Configuration
  cluster:
    type: minikube
    profile: phase4
    version: "1.32"
    resources:
      memory: 6144
      cpus: 4
      disk: 20g
    addons:
      - ingress
      - metrics-server
      - storage-provisioner

  # Network Configuration
  networking:
    ingress:
      enabled: true
      class: nginx
      host: todo-app.local
      tls: false
    networkPolicy:
      enabled: true
      isolateDatabase: true
      isolateBackend: true

  # Application Components
  components:
    frontend:
      type: deployment
      image:
        repository: phase3-frontend
        tag: latest
        pullPolicy: IfNotPresent
      replicas: 2
      port: 3000
      service:
        type: ClusterIP
        port: 80
      resources:
        requests:
          memory: "128Mi"
          cpu: "100m"
        limits:
          memory: "512Mi"
          cpu: "500m"
      autoscaling:
        enabled: true
        minReplicas: 2
        maxReplicas: 10
        targetCPU: 70
        targetMemory: 80
      healthCheck:
        path: /
        port: 3000
        initialDelay: 30
        period: 10
      security:
        runAsNonRoot: true
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false

    backend:
      type: deployment
      image:
        repository: phase3-backend
        tag: latest
        pullPolicy: IfNotPresent
      replicas: 2
      port: 4000
      service:
        type: ClusterIP
        port: 8080
      resources:
        requests:
          memory: "256Mi"
          cpu: "200m"
        limits:
          memory: "1Gi"
          cpu: "1000m"
      autoscaling:
        enabled: true
        minReplicas: 2
        maxReplicas: 15
        targetCPU: 60
        targetMemory: 75
      healthCheck:
        path: /health
        port: 4000
        initialDelay: 30
        period: 10
      security:
        runAsNonRoot: true
        readOnlyRootFilesystem: false
        allowPrivilegeEscalation: false
      environment:
        - name: LOG_LEVEL
          value: "INFO"
        - name: PYTHON_ENV
          value: "production"

    database:
      type: statefulset
      image:
        repository: postgres
        tag: 15-alpine
        pullPolicy: IfNotPresent
      replicas: 1
      port: 5432
      service:
        type: ClusterIP
        port: 5432
      storage:
        enabled: true
        size: 5Gi
        storageClass: "standard"
        accessModes:
          - ReadWriteOnce
      resources:
        requests:
          memory: "256Mi"
          cpu: "250m"
        limits:
          memory: "2Gi"
          cpu: "2000m"
      security:
        runAsNonRoot: true
        runAsUser: 999

  # Security Configuration
  security:
    secrets:
      enabled: true
      name: phase3-secrets
      keys:
        - POSTGRES_USER
        - POSTGRES_PASSWORD
        - DATABASE_URL
        - BETTER_AUTH_SECRET
        - OPENAI_API_KEY
    configMap:
      enabled: true
      name: phase3-config
    rbac:
      enabled: true
      serviceAccount:
        create: true
        name: phase3-sa
    podSecurityStandards:
      level: restricted
      mode: enforce

  # Observability Configuration
  observability:
    monitoring:
      enabled: true
      metricsServer: true
      hpa: true
    logging:
      enabled: true
      level: INFO
    tracing:
      enabled: false

  # Deployment Strategy
  deployment:
    strategy:
      type: RollingUpdate
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 0
    podDisruptionBudget:
      frontend:
        enabled: true
        minAvailable: 1
      backend:
        enabled: true
        minAvailable: 1
```

## AI-Generated Plan

### Generate Plan from Spec

```bash
# Use Claude Code to generate deployment plan
claude "Generate Kubernetes deployment plan from specs/phase4/infrastructure-spec.yaml"

# Use kubectl-ai to generate manifests
kubectl-ai "Generate Kubernetes manifests from this spec: [paste spec]"

# Use kagent to validate spec
kagent "Validate infrastructure spec for best practices"
```

### Generated Plan Structure

```yaml
# Generated: specs/phase4/deployment-plan.yaml
apiVersion: specs.phase4/v1
kind: DeploymentPlan
metadata:
  name: phase4-deployment-plan
  generatedFrom: infrastructure-spec.yaml

plan:
  phases:
    - name: Cluster Setup
      steps:
        - action: minikube start
          command: minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4
        - action: enable addons
          command: minikube addons enable ingress --profile phase4
        - action: verify cluster
          command: kubectl get nodes

    - name: Image Build
      steps:
        - action: configure docker
          command: eval $(minikube -p phase4 docker-env)
        - action: build frontend
          command: docker build -t phase3-frontend:latest ./frontend
        - action: build backend
          command: docker build -t phase3-backend:latest ./backend

    - name: Namespace & Secrets
      steps:
        - action: create namespace
          command: kubectl create namespace phase4
        - action: create secrets
          command: kubectl create secret generic phase3-secrets [...]

    - name: Database Deployment
      steps:
        - action: deploy postgresql
          command: helm install postgres ./helm-charts/postgresql -n phase4

    - name: Backend Deployment
      steps:
        - action: deploy backend
          command: helm install backend ./helm-charts/backend -n phase4
        - action: verify health
          command: kubectl wait --for=condition=available deployment/backend -n phase4

    - name: Frontend Deployment
      steps:
        - action: deploy frontend
          command: helm install frontend ./helm-charts/frontend -n phase4
        - action: verify health
          command: kubectl wait --for=condition=available deployment/frontend -n phase4

    - name: Verification
      steps:
        - action: check all resources
          command: kubectl get all -n phase4
        - action: test connectivity
          command: curl http://todo-app.local
```

## Task Breakdown

### AI-Generated Tasks

```bash
# Use Claude Code to break plan into tasks
claude "Break deployment plan into executable tasks for AI agents"

# Generated tasks stored in: specs/phase4/tasks.yaml
```

### Tasks YAML

```yaml
# specs/phase4/tasks.yaml
apiVersion: specs.phase4/v1
kind: TaskList
metadata:
  name: phase4-tasks
  plan: deployment-plan.yaml

tasks:
  - id: T001
    name: Start Minikube Cluster
    agent: kubectl-ai
    command: "start minikube cluster with 6GB RAM, 4 CPUs, profile phase4"
    verify: "minikube status --profile phase4"
    dependsOn: []

  - id: T002
    name: Enable Ingress
    agent: kubectl-ai
    command: "enable ingress addon on minikube"
    verify: "minikube addons list | grep ingress"
    dependsOn: [T001]

  - id: T003
    name: Build Frontend Image
    agent: Gordon
    command: "Build optimized Docker image for Next.js frontend"
    verify: "docker images | grep phase3-frontend"
    dependsOn: [T001]

  - id: T004
    name: Build Backend Image
    agent: Gordon
    command: "Build optimized Docker image for FastAPI backend"
    verify: "docker images | grep phase3-backend"
    dependsOn: [T001]

  - id: T005
    name: Create Namespace
    agent: kubectl-ai
    command: "create namespace phase4"
    verify: "kubectl get namespace phase4"
    dependsOn: [T001]

  - id: T006
    name: Create Secrets
    agent: kubectl-ai
    command: "create secret phase3-secrets with database credentials"
    verify: "kubectl get secret phase3-secrets -n phase4"
    dependsOn: [T005]

  - id: T007
    name: Deploy PostgreSQL
    agent: kubectl-ai
    command: "deploy postgresql:15-alpine with 5Gi storage"
    verify: "kubectl get pod postgres-0 -n phase4"
    dependsOn: [T005, T006]

  - id: T008
    name: Deploy Backend
    agent: kubectl-ai
    command: "deploy phase3-backend:latest with 2 replicas"
    verify: "kubectl get deployment backend -n phase4"
    dependsOn: [T005, T006, T007]

  - id: T009
    name: Deploy Frontend
    agent: kubectl-ai
    command: "deploy phase3-frontend:latest with 2 replicas"
    verify: "kubectl get deployment frontend -n phase4"
    dependsOn: [T008]

  - id: T010
    name: Verify Deployment
    agent: kagent
    command: "verify deployment health and report status"
    verify: "kubectl get all -n phase4"
    dependsOn: [T009]

  - id: T011
    name: Optimize Resources
    agent: kagent
    command: "analyze and optimize resource allocation"
    verify: "kubectl top pods -n phase4"
    dependsOn: [T010]
```

## Execution with AI Agents

### Automated Execution Script

```bash
#!/bin/bash
# specs/phase4/execute-tasks.sh

set -e

echo "Phase 4 - Executing Tasks with AI Agents"

# Load tasks
TASKS_FILE="specs/phase4/tasks.yaml"

# Execute each task
for task in $(yq e '.tasks[].id' $TASKS_FILE); do
    echo "Executing task: $task"
    
    # Get task details
    command=$(yq e ".tasks[] | select(.id == \"$task\") | .command" $TASKS_FILE)
    agent=$(yq e ".tasks[] | select(.id == \"$task\") | .agent" $TASKS_FILE)
    verify=$(yq e ".tasks[] | select(.id == \"$task\") | .verify" $TASKS_FILE)
    
    # Execute with appropriate agent
    case $agent in
        "kubectl-ai")
            kubectl-ai "$command"
            ;;
        "Gordon")
            docker ai "$command"
            ;;
        "kagent")
            kagent "$command"
            ;;
        *)
            eval "$command"
            ;;
    esac
    
    # Verify
    echo "Verifying task: $task"
    eval "$verify"
done

echo "All tasks completed!"
```

## Blueprint Usage

### Quick Deploy with Blueprint

```bash
# 1. Review spec
cat specs/phase4/infrastructure-spec.yaml

# 2. Generate plan
claude "Generate deployment plan from infrastructure-spec.yaml"

# 3. Review tasks
cat specs/phase4/tasks.yaml

# 4. Execute
.\specs\phase4\execute-tasks.sh

# Or use the automated script
.\deploy-all.bat
```

### Customization

```bash
# Modify spec for your needs
# Edit: specs/phase4/infrastructure-spec.yaml

# Change replicas
# frontend.replicas: 3
# backend.replicas: 5

# Change resources
# frontend.resources.limits.memory: "1Gi"

# Re-deploy with new spec
helm upgrade phase3 ./helm-charts/phase3-todo-chatbot -n phase4
```

## Architectural Decision Records (ADR)

### ADR Template

```markdown
# ADR-001: Phase 4 AI-Assisted Deployment

## Status
Accepted

## Context
Phase 4 requires AI-assisted deployment using Gordon, kubectl-ai, and kagent.

## Decision
Use spec-driven development with AI agents for deployment automation.

## Consequences
- Faster deployment
- Consistent configurations
- AI-powered troubleshooting
- Requires AI tool availability
```

## Resources

- [Infrastructure Spec](./specs/phase4/infrastructure-spec.yaml)
- [Deployment Plan](./specs/phase4/deployment-plan.yaml)
- [Tasks](./specs/phase4/tasks.yaml)
- [AI Workflows](./PHASE4_AI_WORKFLOWS.md)

---

**Phase 4 Blueprint Complete!** 🎉

Use these blueprints for automated, spec-driven deployment with AI assistance.
