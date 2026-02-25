# Recurring Service

Recurring Task Management Service for Phase V of the Cloud-Native AI Todo Chatbot.

## Overview

This service handles automatic generation of recurring task occurrences. It:

- Subscribes to `task-events` Kafka topic via Dapr Pub/Sub
- Listens for `TASK_COMPLETED` events
- Detects completed recurring tasks
- Calculates next occurrence using iCal RRule
- Creates new task instances
- Publishes `TASK_CREATED` events for new occurrences

## Architecture

```
┌─────────────┐
│  Chat API   │
└──────┬──────┘
       │ TASK_COMPLETED
       ▼
┌─────────────────────────────────┐
│        Dapr Pub/Sub             │
│      (task-events topic)        │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│     Recurring Service            │
│  ┌────────────────────────────┐  │
│  │  /dapr/subscribe/          │  │
│  │  task-events               │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  RecurrenceCalculator      │  │
│  │  - Parse RRule             │  │
│  │  - Calculate next date     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  TaskCreator               │  │
│  │  - Create new instance     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │  EventPublisher            │  │
│  │  - Publish TASK_CREATED    │  │
│  └────────────────────────────┘  │
└──────────────┬──────────────────┘
               │
               │ TASK_CREATED
               ▼
┌─────────────────────────────────┐
│        Dapr Pub/Sub             │
│      (task-events topic)        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Notification Service          │
│   Audit Service                 │
│   WebSocket Service             │
└─────────────────────────────────┘
```

## Features

- **iCal RRule Support**: Full support for RFC 5545 recurrence rules
- **Timezone Aware**: Handles timezone conversions correctly
- **Max Occurrences**: Respects occurrence limits
- **End Date Support**: Stops generating when end date is reached
- **Event-Driven**: Fully asynchronous via Kafka and Dapr
- **Scalable**: Horizontal scaling with Dapr sidecars

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run locally
python -m uvicorn app.main:app --reload --port 8081
```

### Docker

```bash
# Build
docker build -t recurring-service:latest .

# Run
docker run -p 8081:8081 --env-file .env recurring-service:latest
```

### Kubernetes (Helm)

```bash
# Install
helm install recurring-service ./helm -n default

# Upgrade
helm upgrade recurring-service ./helm -n default

# Uninstall
helm uninstall recurring-service -n default
```

## API Endpoints

### Health Checks

```
GET /health    - Health check
GET /ready     - Readiness probe
GET /live      - Liveness probe
```

### Dapr Subscriptions

```
POST /dapr/subscribe/task-events    - Task events from Kafka
GET  /dapr/subscribe/task-events    - Subscription metadata
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | `recurring-service` |
| `APP_PORT` | HTTP port | `8081` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_HOST` | PostgreSQL host | `postgresql.postgres.svc.cluster.local` |
| `DATABASE_PORT` | PostgreSQL port | `5432` |
| `DATABASE_NAME` | Database name | `todo_chatbot` |
| `DATABASE_USER` | Database user | `postgres` |
| `DATABASE_PASSWORD` | Database password | (from secret) |
| `DAPR_HTTP_PORT` | Dapr HTTP port | `3500` |
| `DAPR_PUBSUB_NAME` | Dapr pubsub component | `pubsub-kafka` |
| `KAFKA_TOPIC_TASK_EVENTS` | Task events topic | `task-events` |

## Event Flow

### Input: TASK_COMPLETED Event

```json
{
  "eventId": "uuid",
  "eventType": "TASK_COMPLETED",
  "timestamp": "2026-02-25T10:30:00Z",
  "version": "1.0",
  "source": "chat-api",
  "data": {
    "taskId": "uuid",
    "userId": "uuid",
    "completedAt": "2026-02-25T10:30:00Z",
    "isRecurring": true,
    "recurringTaskId": "uuid",
    "recurrenceRule": "FREQ=DAILY;INTERVAL=1",
    "recurrenceStartDate": "2026-01-01T00:00:00Z",
    "timezone": "UTC"
  },
  "metadata": {
    "correlationId": "uuid",
    "causationId": "uuid"
  }
}
```

### Output: TASK_CREATED Event

```json
{
  "eventId": "new-uuid",
  "eventType": "TASK_CREATED",
  "timestamp": "2026-02-25T10:30:01Z",
  "version": "1.0",
  "source": "recurring-service",
  "data": {
    "taskId": "new-task-uuid",
    "userId": "uuid",
    "title": "Daily Standup",
    "description": "Team standup meeting",
    "priority": "MEDIUM",
    "dueDate": "2026-02-26T09:00:00Z",
    "isRecurring": true,
    "recurringTaskId": "uuid",
    "currentOccurrence": 56,
    "createdAt": "2026-02-25T10:30:01Z"
  },
  "metadata": {
    "correlationId": "uuid",
    "causationId": "original-event-uuid"
  }
}
```

## Recurrence Rules

Supported frequencies:
- `DAILY` - Every day
- `WEEKLY` - Every week
- `MONTHLY` - Every month
- `YEARLY` - Every year

Examples:
- `FREQ=DAILY;INTERVAL=1` - Every day
- `FREQ=WEEKLY;BYDAY=MO,WE,FR` - Every Monday, Wednesday, Friday
- `FREQ=MONTHLY;BYMONTHDAY=1` - First day of every month
- `FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1` - January 1st every year

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Monitoring

### Metrics

- `recurring_task_processed_total` - Total recurring tasks processed
- `recurring_task_generation_duration_seconds` - Time to generate occurrence
- `recurring_task_errors_total` - Total errors

### Logs

Structured JSON logs with correlation IDs for distributed tracing.

## Deployment

### Prerequisites

- Kubernetes cluster
- Dapr installed
- Kafka cluster (Strimzi)
- PostgreSQL database
- Redis (for Dapr state)

### Deploy

```bash
# Apply Dapr components
kubectl apply -f ../../helm/dapr-components/

# Deploy service
helm install recurring-service ./helm -n default

# Verify
kubectl get pods -l app.kubernetes.io/name=recurring-service
dapr status -k
```

## Troubleshooting

### Service not receiving events

1. Check Dapr subscription:
   ```bash
   kubectl get subscriptions.dapr.io
   ```

2. Check Dapr sidecar logs:
   ```bash
   kubectl logs <pod-name> -c daprd
   ```

3. Verify Kafka topic exists:
   ```bash
   kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
     bin/kafka-topics.sh --list --bootstrap-server kafka-cluster-kafka-bootstrap:9092
   ```

### Recurrence calculation errors

1. Check RRule format in database
2. Verify timezone is valid
3. Check logs for parsing errors

## License

MIT
