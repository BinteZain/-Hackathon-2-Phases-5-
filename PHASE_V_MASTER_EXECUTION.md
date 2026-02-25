# Phase V: Master Execution Plan

**Cloud-Native AI Todo Chatbot - Complete Implementation Guide**

---

## Document Control

| Field | Value |
|-------|-------|
| **Document ID** | PHASE-V-MASTER-001 |
| **Version** | 1.0 |
| **Status** | Ready for Execution |
| **Date** | February 25, 2026 |
| **Based On** | SPEC-PHASE-V-001, PLAN-PHASE-V-001 |

---

## Executive Summary

This document provides the **exact execution order** for Phase V implementation. Each step is sequential and must be completed before proceeding to the next. The plan covers:

- ✅ Advanced Features Implementation
- ✅ Event-Driven Architecture (Kafka)
- ✅ Dapr Integration
- ✅ Microservices Deployment
- ✅ Cloud Deployment (AKS/GKE/OKE)
- ✅ CI/CD Pipeline
- ✅ Monitoring & Observability

---

## Execution Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase V Execution Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐         │
│  │  1   │ → │  2   │ → │  3   │ → │  4   │ → │  5   │         │
│  │ SPEC │   │ PLAN │   │  DB  │   │ FEAT │   │KAFKA │         │
│  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘         │
│     │          │          │          │          │               │
│     ▼          ▼          ▼          ▼          ▼               │
│  Written   Generated   Updated   Implemented  Installed         │
│                                                                  │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐         │
│  │  6   │ → │  7   │ → │  8   │ → │  9   │ → │ 10   │         │
│  │DAPR  │   │RECUR │   │ NOTIFY│  │ TEST │   │MINI  │         │
│  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘         │
│     │          │          │          │          │               │
│     ▼          ▼          ▼          ▼          ▼               │
│  Integrated Created   Created   Verified  Deployed             │
│                                                                  │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐                     │
│  │ 11   │ → │ 12   │ → │ 13   │ → │ 14   │                     │
│  │CLOUD │   │ HELM │   │ CI/CD│   │ MON  │                     │
│  └──────┘   └──────┘   └──────┘   └──────┘                     │
│     │          │          │          │                          │
│     ▼          ▼          ▼          ▼                          │
│  Configured Deployed  Automated  Monitoring                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Execution

### Step 1: Write Specification ✅ COMPLETED

**Status:** ✅ Complete  
**Document:** `SPEC-PHASE-V-001`  
**Location:** `specs/phase-v/spec.md`

**Deliverables:**
- [x] Advanced Features Specification (Recurring, Due Dates, Reminders, Priorities, Tags, Search)
- [x] Event-Driven Architecture (Kafka Topics, Producers, Consumers, Event Schemas)
- [x] Dapr Integration (Pub/Sub, State Management, Jobs, Secrets)
- [x] Microservices Architecture (5 Services)
- [x] Deployment Strategies (Local, Cloud, CI/CD, Monitoring)

**Files Created:**
```
specs/phase-v/
├── spec.md                     # Main specification
└── (related spec documents)
```

**Acceptance Criteria:**
- [x] All 6 advanced features documented
- [x] 3 Kafka topics defined with schemas
- [x] 4 Dapr components specified
- [x] 5 microservices architected
- [x] Deployment strategies documented

---

### Step 2: Generate Implementation Plan ✅ COMPLETED

**Status:** ✅ Complete  
**Document:** `PLAN-PHASE-V-001`  
**Location:** `specs/phase-v/plan.md`

**Deliverables:**
- [x] Backend Changes (Service modifications, New services)
- [x] Database Schema Updates (PostgreSQL, Redis)
- [x] Event Publishing Points (Producers, Consumers, Subscriptions)
- [x] API Changes (New endpoints, Request/Response models)
- [x] UI Changes (Components, Pages, Animations)
- [x] Dapr Component Files (YAML configurations)
- [x] Helm Chart Updates (Values, Templates)

**Files Created:**
```
specs/phase-v/
├── plan.md                     # Implementation plan
└── tasks.md                    # Detailed tasks
```

**Acceptance Criteria:**
- [x] All work streams defined
- [x] Dependencies mapped
- [x] Effort estimated (46 days total)
- [x] Critical path identified

---

### Step 3: Update Database Schema ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 3 days

**Tasks:**

#### 3.1 Create Migration Files

```bash
# Create migration directory
mkdir -p backend/db/migration

# Create migration files
cd backend/db/migration
```

**Files to Create:**

| File | Purpose | Tables |
|------|---------|--------|
| `V2__add_task_advanced_fields.sql` | Task extensions | `tasks` |
| `V3__create_tags_tables.sql` | Tag management | `tags`, `task_tags` |
| `V4__create_reminders_tables.sql` | Reminders | `reminders` |
| `V5__create_recurring_tasks_tables.sql` | Recurrence | `recurring_tasks` |
| `V6__create_notifications_tables.sql` | Notifications | `notifications`, `notification_preferences` |
| `V7__create_audit_events_table.sql` | Audit log | `audit_events` |
| `V8__add_indexes_for_performance.sql` | Performance | All tables |
| `V9__add_triggers_and_constraints.sql` | Integrity | All tables |

#### 3.2 Apply Migrations

```bash
# Local development
cd backend
flyway migrate

# Or using psql
psql -h localhost -U postgres -d todo_chatbot -f db/migration/V2__*.sql
psql -h localhost -U postgres -d todo_chatbot -f db/migration/V3__*.sql
# ... repeat for all migrations
```

#### 3.3 Verify Schema

```sql
-- Check tables
\dt

-- Check indexes
\di

-- Check constraints
SELECT conname, conrelid::regclass 
FROM pg_constraint 
WHERE conrelid IN (SELECT oid FROM pg_class WHERE relname LIKE 'task%');
```

**Acceptance Criteria:**
- [ ] All 8 migration files created
- [ ] Migrations applied successfully
- [ ] All tables created with correct structure
- [ ] Indexes created for performance
- [ ] Foreign key constraints working
- [ ] Rollback tested

---

### Step 4: Implement Advanced Features ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 10 days

**Tasks:**

#### 4.1 Update Task Entity

**File:** `backend/models/task.py`

```python
# Add fields:
# - due_date: DateTime
# - due_date_type: Enum
# - timezone: String
# - priority: Enum (NONE, LOW, MEDIUM, HIGH, URGENT)
# - is_recurring: Boolean
# - recurring_task_id: UUID (FK)
# - recurrence_rule: String
# - recurrence_start_date: DateTime
# - recurrence_end_date: DateTime
# - max_occurrences: Integer
# - current_occurrence: Integer
# - completed_at: DateTime
```

#### 4.2 Implement Recurring Tasks

**Files:**
- `backend/services/recurring_task_service.py`
- `backend/utils/rrule_parser.py`

**Features:**
- Parse iCal RRule format
- Calculate next occurrence
- Generate task instances
- Handle end conditions

#### 4.3 Implement Reminders

**Files:**
- `backend/services/reminder_service.py`
- `backend/models/reminder.py`

**Features:**
- Create/delete reminders
- Relative and absolute triggers
- Multiple reminders per task
- Reminder channels (In-app, Email, Push)

#### 4.4 Implement Tags

**Files:**
- `backend/services/tag_service.py`
- `backend/models/tag.py`
- `backend/models/task_tag.py`

**Features:**
- CRUD operations
- Tag assignment
- Tag filtering
- Color customization

#### 4.5 Implement Priorities

**Files:**
- `backend/services/priority_service.py`

**Features:**
- 5-level priority system
- Priority-based sorting
- Priority change audit

#### 4.6 Implement Search/Filter/Sort

**Files:**
- `backend/services/search_service.py`
- `backend/repositories/task_repository.py`

**Features:**
- Full-text search
- Multi-criteria filtering
- Multiple sort options
- Pagination

#### 4.7 Update API Endpoints

**File:** `backend/routes/tasks.py`

**New/Updated Endpoints:**
```python
POST   /api/v1/tasks                    # Create (with advanced fields)
GET    /api/v1/tasks                    # List (with filters)
GET    /api/v1/tasks/{id}               # Get details
PUT    /api/v1/tasks/{id}               # Update
DELETE /api/v1/tasks/{id}               # Delete
POST   /api/v1/tasks/{id}/complete      # Complete
POST   /api/v1/tasks/{id}/reminder      # Add reminder
GET    /api/v1/tags                     # List tags
POST   /api/v1/tags                     # Create tag
GET    /api/v1/search                   # Search tasks
POST   /api/v1/recurring                # Create recurring
```

**Acceptance Criteria:**
- [ ] All entities updated
- [ ] All services implemented
- [ ] All API endpoints working
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated

---

### Step 5: Install Kafka Locally ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 2 days

**Tasks:**

#### 5.1 Start Minikube

```bash
# Start Minikube
minikube start --memory=8192 --cpus=4 --disk-size=40gb

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify
kubectl cluster-info
kubectl get nodes
```

#### 5.2 Install Strimzi Operator

```bash
# Create namespace
kubectl create namespace kafka

# Install Strimzi Operator
kubectl apply -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.38.0/strimzi-cluster-operator-0.38.0.yaml -n kafka

# Wait for operator
kubectl wait --for=condition=Available deployment/strimzi-cluster-operator -n kafka --timeout=300s

# Verify
kubectl get pods -n kafka
```

#### 5.3 Deploy Kafka Cluster

```bash
# Apply Kafka cluster config
kubectl apply -f kafka-cluster.yaml -n kafka

# Wait for brokers
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kafka -n kafka --timeout=300s

# Verify
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

#### 5.4 Create Kafka Topics

```bash
# Create task-events topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic task-events \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 6 --replication-factor 3

# Create reminders topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic reminders \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 3 --replication-factor 3

# Create task-updates topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic task-updates \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 6 --replication-factor 3

# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092
```

#### 5.5 Verify Kafka

```bash
# Produce test message
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-producer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic task-events

# Consume test message
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning
```

**Acceptance Criteria:**
- [ ] Minikube running
- [ ] Strimzi Operator installed
- [ ] Kafka cluster deployed (3 brokers, 3 Zookeepers)
- [ ] All 3 topics created
- [ ] Can produce and consume messages
- [ ] Kafka UI accessible (optional)

---

### Step 6: Integrate Dapr Pub/Sub ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 3 days

**Tasks:**

#### 6.1 Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Or using Helm
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update
helm upgrade --install dapr dapr/dapr \
  --version=1.12.0 \
  --namespace dapr-system \
  --create-namespace \
  --wait

# Verify
dapr status -k
kubectl get pods -n dapr-system
```

#### 6.2 Deploy Redis (for Dapr State)

```bash
# Create namespace
kubectl create namespace redis

# Install Redis
helm install redis bitnami/redis \
  --namespace redis \
  --set auth.password=redis123 \
  --wait

# Verify
kubectl get pods -n redis
```

#### 6.3 Deploy PostgreSQL

```bash
# Create namespace
kubectl create namespace postgres

# Install PostgreSQL
helm install postgresql bitnami/postgresql \
  --namespace postgres \
  --set auth.password=postgres123 \
  --set auth.username=postgres \
  --wait

# Verify
kubectl get pods -n postgres
```

#### 6.4 Apply Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f helm/dapr-components/

# Components:
# - pubsub-kafka.yaml
# - state-redis.yaml
# - secret-kubernetes.yaml
# - job-reminder-scheduler.yaml
# - configuration.yaml
# - subscriptions/*.yaml

# Verify
kubectl get components.dapr.io
kubectl get subscriptions.dapr.io
```

#### 6.5 Update Application Code

**Files to Update:**

| Service | Files | Changes |
|---------|-------|---------|
| Chat API | `services/event_publisher.py` | Add Dapr Pub/Sub calls |
| Chat API | `routes/tasks.py` | Add event publishing after task operations |
| All Services | `Dockerfile` | Add Dapr sidecar annotations |
| All Services | `helm/templates/deployment.yaml` | Add Dapr annotations |

**Example: Publish Event**

```python
import httpx

async def publish_event(topic: str, event_type: str, data: dict):
    event = {
        "eventId": str(uuid.uuid4()),
        "eventType": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0",
        "source": "chat-api",
        "data": data
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:3500/v1.0/publish/pubsub-kafka/{topic}",
            json=event
        )
        response.raise_for_status()
```

#### 6.6 Test Event Flow

```bash
# Port forward to test
kubectl port-forward svc/chat-api -n default 8080:80

# Create a task
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","priority":"high"}'

# Check Kafka for event
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning
```

**Acceptance Criteria:**
- [ ] Dapr installed and running
- [ ] Redis deployed
- [ ] PostgreSQL deployed
- [ ] All Dapr components applied
- [ ] All subscriptions active
- [ ] Events published to Kafka
- [ ] Events consumed by subscribers

---

### Step 7: Create Recurring Service ✅ COMPLETED

**Status:** ✅ Complete  
**Location:** `services/recurring-service/`

**Files Created:**
```
services/recurring-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   └── events.py
│   ├── services/
│   │   ├── recurrence.py
│   │   ├── task_creator.py
│   │   └── event_publisher.py
│   ├── repositories/
│   │   └── database.py
│   └── routes/
│       ├── health.py
│       └── dapr.py
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

**Features Implemented:**
- [x] Dapr Pub/Sub subscription to `task-events`
- [x] Filter for `TASK_COMPLETED` events
- [x] iCal RRule parsing
- [x] Next occurrence calculation
- [x] New task instance creation
- [x] Event publishing for new occurrences
- [x] Helm chart for deployment

**Next Steps:**
- [ ] Deploy to Minikube
- [ ] Test with completed recurring task
- [ ] Verify next occurrence generated

---

### Step 8: Create Notification Service ✅ COMPLETED

**Status:** ✅ Complete  
**Location:** `services/notification-service/`

**Files Created:**
```
services/notification-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   └── events.py
│   ├── services/
│   │   ├── notification.py
│   │   ├── email_provider.py
│   │   ├── push_provider.py
│   │   ├── inapp_provider.py
│   │   └── delivery_tracker.py
│   ├── repositories/
│   │   └── database.py
│   └── routes/
│       ├── health.py
│       ├── dapr.py
│       └── api.py
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

**Features Implemented:**
- [x] Dapr Pub/Sub subscription to `reminders`
- [x] Email delivery (SMTP)
- [x] Push notification (Firebase/APNS)
- [x] In-app notification storage
- [x] Delivery tracking
- [x] Structured logging
- [x] REST API for notifications
- [x] Helm chart for deployment

**Next Steps:**
- [ ] Deploy to Minikube
- [ ] Configure SMTP credentials
- [ ] Test reminder delivery
- [ ] Verify delivery tracking

---

### Step 9: Test Full Event Flow Locally ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 3 days

**Test Scenarios:**

#### 9.1 Test: Create Task → Event Published

```bash
# Create task
curl -X POST http://localhost:8080/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task 1","priority":"high"}'

# Check Kafka
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Expected: TASK_CREATED event
```

#### 9.2 Test: Complete Recurring Task → Next Occurrence Generated

```bash
# Create recurring task
curl -X POST http://localhost:8080/api/v1/recurring \
  -H "Content-Type: application/json" \
  -d '{
    "taskId": "task-123",
    "recurrenceRule": "FREQ=DAILY",
    "startDate": "2026-02-25T00:00:00Z"
  }'

# Complete the task
curl -X POST http://localhost:8080/api/v1/tasks/task-123/complete

# Check recurring-service logs
kubectl logs -l app.kubernetes.io/name=recurring-task-service -n default

# Check for new task event
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic task-events \
  --from-beginning

# Expected: New TASK_CREATED event for next occurrence
```

#### 9.3 Test: Schedule Reminder → Notification Sent

```bash
# Schedule reminder
curl -X POST http://localhost:8080/api/v1/tasks/task-123/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "triggerTime": "2026-02-26T09:00:00Z",
    "channel": "EMAIL",
    "message": "Task due tomorrow"
  }'

# Check reminders topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --topic reminders \
  --from-beginning

# Check notification-service logs
kubectl logs -l app.kubernetes.io/name=notification-service -n default

# Expected: REMINDER_SCHEDULED event → Email sent
```

#### 9.4 Test: Audit Service Receives All Events

```bash
# Check audit-service logs
kubectl logs -l app.kubernetes.io/name=audit-service -n default

# Query audit events
curl http://localhost:8083/api/v1/audit/events

# Expected: All events logged
```

#### 9.5 Test: WebSocket Service Pushes Updates

```bash
# Connect to WebSocket
wscat -c ws://localhost:8084/ws

# Trigger task update
curl -X PUT http://localhost:8080/api/v1/tasks/task-123 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Task"}'

# Expected: Real-time update pushed to WebSocket
```

**Acceptance Criteria:**
- [ ] All 5 test scenarios pass
- [ ] Events flow correctly through Kafka
- [ ] All services receive expected events
- [ ] Notifications delivered successfully
- [ ] Audit trail complete
- [ ] Real-time updates working

---

### Step 10: Deploy to Minikube ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 2 days

**Tasks:**

#### 10.1 Build Docker Images

```bash
# Chat API
docker build -t ghcr.io/todo-chatbot/chat-api:5.0.0 \
  -f backend/Dockerfile .

# Recurring Service
docker build -t ghcr.io/todo-chatbot/recurring-service:5.0.0 \
  -f services/recurring-service/Dockerfile .

# Notification Service
docker build -t ghcr.io/todo-chatbot/notification-service:5.0.0 \
  -f services/notification-service/Dockerfile .

# Load images into Minikube
minikube image load ghcr.io/todo-chatbot/chat-api:5.0.0
minikube image load ghcr.io/todo-chatbot/recurring-service:5.0.0
minikube image load ghcr.io/todo-chatbot/notification-service:5.0.0
```

#### 10.2 Deploy with Helm

```bash
# Deploy umbrella chart
helm install todo-app ./helm \
  --namespace default \
  --values helm/values.yaml \
  --set chat-api.image.repository=ghcr.io/todo-chatbot/chat-api \
  --set chat-api.image.tag=5.0.0 \
  --set recurringTaskService.image.repository=ghcr.io/todo-chatbot/recurring-service \
  --set recurringTaskService.image.tag=5.0.0 \
  --set notificationService.image.repository=ghcr.io/todo-chatbot/notification-service \
  --set notificationService.image.tag=5.0.0 \
  --wait \
  --timeout 10m

# Verify deployment
kubectl get pods
kubectl get deployments
kubectl get services

# Verify Dapr
dapr status -k
kubectl get pods -l dapr.io/enabled=true
```

#### 10.3 Access Application

```bash
# Get Chat API URL
minikube service chat-api --url

# Or port forward
kubectl port-forward svc/chat-api 8080:80

# Test
curl http://localhost:8080/health
```

#### 10.4 Monitor Deployment

```bash
# View logs
kubectl logs -l app.kubernetes.io/name=chat-api

# View Dapr logs
kubectl logs -l app.kubernetes.io/name=chat-api -c daprd

# View events
kubectl get events --sort-by='.lastTimestamp'
```

**Acceptance Criteria:**
- [ ] All Docker images built
- [ ] All services deployed
- [ ] All pods running
- [ ] All services accessible
- [ ] Dapr sidecars injected
- [ ] End-to-end test passing

---

### Step 11: Setup Cloud (AKS / OKE / GKE) ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P1  
**Estimated Time:** 4 days

**Tasks:**

#### 11.1 Azure AKS (Primary)

```bash
# Login to Azure
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-rg \
  --name todo-aks \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-aks

# Verify
kubectl get nodes
```

#### 11.2 Create Azure Services

```bash
# Azure Database for PostgreSQL
az postgres flexible-server create \
  --resource-group todo-rg \
  --name todo-postgres \
  --admin-user postgres \
  --admin-password <secure-password>

# Azure Cache for Redis
az redis create \
  --resource-group todo-rg \
  --name todo-redis \
  --sku Basic \
  --vm-size C1

# Azure Key Vault
az keyvault create \
  --resource-group todo-rg \
  --name todo-keyvault \
  --location eastus
```

#### 11.3 Google GKE (Alternative)

```bash
# Create GKE cluster
gcloud container clusters create gke-todo-chatbot \
  --num-nodes=3 \
  --zone us-central1-a

# Get credentials
gcloud container clusters get-credentials gke-todo-chatbot --zone us-central1-a
```

#### 11.4 Oracle OKE (Alternative)

```bash
# Create OKE cluster
oci ce cluster create \
  --compartment-id <compartment-ocid> \
  --name oke-todo-chatbot \
  --kubernetes-version v1.28.5

# Get credentials
oci ce cluster create-kubeconfig --cluster-id <cluster-ocid>
```

**Acceptance Criteria:**
- [ ] AKS cluster running (or GKE/OKE)
- [ ] Azure services provisioned
- [ ] kubectl connected to cluster
- [ ] Cluster meets production requirements

---

### Step 12: Deploy via Helm ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 2 days

**Tasks:**

#### 12.1 Prepare Cloud Values

```bash
# Create cloud-specific values file
cp helm/values.yaml helm/values-cloud.yaml

# Update for cloud:
# - Database host (Azure PostgreSQL)
# - Redis host (Azure Redis)
# - Image registry (GHCR)
# - Resource limits
# - Replica counts
```

#### 12.2 Create Kubernetes Secrets

```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=<password> \
  --from-literal host=<postgres-host>

# Redis password
kubectl create secret generic redis-secret \
  --from-literal=password=<redis-password>

# SMTP credentials
kubectl create secret generic email-smtp \
  --from-literal=host=smtp.office365.com \
  --from-literal=password=<smtp-password>

# Push notification
kubectl create secret generic push-notification \
  --from-literal=firebaseApiKey=<firebase-key>
```

#### 12.3 Deploy Application

```bash
# Deploy with cloud values
helm upgrade --install todo-app ./helm \
  --namespace default \
  --values helm/values-cloud.yaml \
  --wait \
  --timeout 15m \
  --atomic

# Verify
kubectl get pods
kubectl get deployments
helm list
```

#### 12.4 Configure Ingress

```bash
# Install NGINX Ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Get Load Balancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Configure DNS
# Point domain to Load Balancer IP
```

#### 12.5 Enable TLS (Optional)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f helm/tls-cluster-issuer.yaml

# Enable TLS in ingress
helm upgrade todo-app ./helm \
  --set ingress.tls[0].hosts[0]=todo-chatbot.com \
  --set ingress.tls[0].secretName=todo-tls
```

**Acceptance Criteria:**
- [ ] All secrets created
- [ ] Application deployed successfully
- [ ] Ingress configured
- [ ] Application accessible via domain
- [ ] TLS enabled (optional)
- [ ] Rollback tested

---

### Step 13: Setup CI/CD ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P0  
**Estimated Time:** 3 days

**Tasks:**

#### 13.1 Configure GitHub Repository

```bash
# Enable GitHub Actions
# Repository Settings → Actions → General → Allow all actions

# Create environments
# Settings → Environments → New environment: production
# Settings → Environments → New environment: staging
```

#### 13.2 Configure Secrets

**Repository Secrets:**
```
AZURE_CREDENTIALS          # Azure service principal
DB_PASSWORD                # Database password
REDIS_PASSWORD             # Redis password
SMTP_PASSWORD              # SMTP password
FIREBASE_API_KEY           # Firebase API key
SLACK_WEBHOOK_URL          # Slack webhook (optional)
VERCEL_TOKEN               # Vercel token (optional)
```

#### 13.3 Configure Workflows

**Files:**
- `.github/workflows/deploy.yml` (Production)
- `.github/workflows/deploy-staging.yml` (Staging)
- `.github/workflows/cleanup.yml` (Cleanup)

#### 13.4 Test CI/CD Pipeline

```bash
# Push to trigger
git add .
git commit -m "Phase V implementation"
git push origin main

# Monitor in GitHub Actions
# https://github.com/<org>/<repo>/actions
```

#### 13.5 Configure Branch Protection

```
# Settings → Branches → Add branch protection rule
# Branch: main
# Require pull request reviews: ✓
# Require status checks to pass: ✓
# Require branches to be up to date: ✓
```

**Acceptance Criteria:**
- [ ] All secrets configured
- [ ] Workflows created
- [ ] Build job passing
- [ ] Security scan passing
- [ ] Deployment to AKS successful
- [ ] Notifications working
- [ ] Rollback tested

---

### Step 14: Add Monitoring ⏳ PENDING

**Status:** ⏳ Ready to Execute  
**Priority:** P1  
**Estimated Time:** 3 days

**Tasks:**

#### 14.1 Install Monitoring Stack

```bash
# Run deployment script
./deploy-monitoring.sh    # Linux/Mac
.\deploy-monitoring.bat   # Windows

# Or manual installation
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/values-production.yaml \
  --wait

helm install loki loki/loki-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/loki-values.yaml \
  --wait
```

#### 14.2 Apply Configurations

```bash
# Apply Prometheus rules
kubectl apply -f monitoring/prometheus-rules.yaml

# Apply Alertmanager config
kubectl apply -f monitoring/alertmanager-config.yaml

# Apply ServiceMonitors
kubectl apply -f monitoring/servicemonitor.yaml
```

#### 14.3 Access Dashboards

```bash
# Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# http://localhost:3000 (admin/admin)

# Prometheus
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# http://localhost:9090

# Alertmanager
kubectl port-forward svc/monitoring-alertmanager -n monitoring 9093:9093
# http://localhost:9093

# Loki
kubectl port-forward svc/loki -n monitoring 3100:3100
# http://localhost:3100
```

#### 14.4 Import Dashboards

**In Grafana:**
1. Go to Dashboards → Import
2. Enter IDs:
   - **6417** - Kubernetes Cluster
   - **1860** - Node Exporter
   - **13817** - Dapr Dashboard
   - **7589** - Kafka Overview
3. Select Prometheus datasource
4. Click Import

#### 14.5 Configure Alerts

```bash
# Update Slack webhook in alertmanager-config.yaml
# Apply configuration
kubectl apply -f monitoring/alertmanager-config.yaml

# Test alerts
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# Visit: http://localhost:9090/alerts
```

**Acceptance Criteria:**
- [ ] Prometheus running
- [ ] Grafana running
- [ ] Loki running
- [ ] Alertmanager configured
- [ ] All dashboards imported
- [ ] Alerts configured and routing
- [ ] ServiceMonitors scraping all services

---

## Completion Checklist

### Phase V Deliverables

- [ ] **Specification Document** (SPEC-PHASE-V-001)
- [ ] **Implementation Plan** (PLAN-PHASE-V-001)
- [ ] **Database Schema** (8 migration files)
- [ ] **Advanced Features** (6 features implemented)
- [ ] **Kafka Cluster** (3 topics, local + cloud)
- [ ] **Dapr Integration** (4 components, 5 subscriptions)
- [ ] **Recurring Service** (Deployed and tested)
- [ ] **Notification Service** (Deployed and tested)
- [ ] **Event Flow Tests** (All scenarios passing)
- [ ] **Minikube Deployment** (Full stack running)
- [ ] **Cloud Deployment** (AKS/GKE/OKE configured)
- [ ] **Helm Charts** (All services packageable)
- [ ] **CI/CD Pipeline** (Automated build → deploy)
- [ ] **Monitoring Stack** (Prometheus, Grafana, Loki, Alerts)

### Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (p95) | < 500ms | ⏳ TBD |
| API Availability | 99.9% | ⏳ TBD |
| Event Processing Latency | < 1s | ⏳ TBD |
| Test Coverage | > 80% | ⏳ TBD |
| Deployment Frequency | On-demand | ⏳ TBD |
| Rollback Time | < 5 min | ⏳ TBD |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Kafka instability | Use 3 replicas, monitor consumer lag |
| Dapr sidecar failures | Enable health checks, configure restarts |
| Database migration failures | Test rollback, backup before migration |
| Cloud cost overruns | Set budgets, use spot instances |
| CI/CD pipeline failures | Test locally, maintain rollback capability |

---

## Next Actions

1. **Immediate:** Execute Step 3 (Database Schema)
2. **This Week:** Complete Steps 3-6 (DB, Features, Kafka, Dapr)
3. **Next Week:** Complete Steps 7-10 (Services, Testing, Minikube)
4. **Week 3:** Complete Steps 11-14 (Cloud, Helm, CI/CD, Monitoring)

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Status:** Ready for Execution

**Approvals:**
- [ ] Project Manager
- [ ] Technical Lead
- [ ] DevOps Lead

---

**END OF MASTER EXECUTION PLAN**
