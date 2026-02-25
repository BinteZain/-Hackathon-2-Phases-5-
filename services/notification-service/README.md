# Notification Service

Multi-channel Notification Service for Phase V of the Cloud-Native AI Todo Chatbot.

## Overview

This service handles notification delivery across multiple channels:

- **Email** - SMTP-based email delivery
- **Push** - Firebase (FCM) and APNS push notifications
- **In-App** - In-app notification storage and retrieval

It subscribes to Kafka topics via Dapr Pub/Sub and delivers notifications based on user preferences.

## Architecture

```
┌─────────────────────────────────────────┐
│         Kafka (reminders topic)         │
└──────────────────┬──────────────────────┘
                   │
                   │ REMINDER_TRIGGERED
                   ▼
┌─────────────────────────────────────────┐
│         Dapr Pub/Sub                    │
│      (pubsub-kafka component)           │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│      Notification Service               │
│  ┌───────────────────────────────────┐  │
│  │  /dapr/subscribe/reminders        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  NotificationService              │  │
│  │  - Orchestrates delivery          │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  EmailProvider      (SMTP)        │  │
│  │  PushProvider       (FCM/APNS)    │  │
│  │  InAppProvider      (Database)    │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  DeliveryTracker                  │  │
│  │  - Track delivery status          │  │
│  │  - Metrics & logging              │  │
│  └───────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │  SMTP  │ │  FCM   │ │   DB   │
   │ Email  │ │  Push  │ │ In-App │
   └────────┘ └────────┘ └────────┘
```

## Features

- **Multi-Channel Delivery**: Email, Push, In-App notifications
- **User Preferences**: Respects user notification settings
- **Quiet Hours**: Configurable do-not-disturb periods
- **Delivery Tracking**: Complete audit trail of delivery attempts
- **Retry Logic**: Automatic retry for transient failures
- **Structured Logging**: JSON logs with correlation IDs
- **Batch Processing**: Send multiple notifications efficiently
- **Metrics**: Delivery rate, success/failure tracking

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run locally
python -m uvicorn app.main:app --reload --port 8082
```

### Docker

```bash
# Build
docker build -t notification-service:latest .

# Run
docker run -p 8082:8082 --env-file .env notification-service:latest
```

### Kubernetes (Helm)

```bash
# Install
helm install notification-service ./helm -n default

# Upgrade
helm upgrade notification-service ./helm -n default

# Uninstall
helm uninstall notification-service -n default
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
POST /dapr/subscribe/reminders     - Reminder events
POST /dapr/subscribe/task-events   - Task events
```

### REST API

```
POST   /notifications/send              - Send notification
POST   /notifications/batch             - Batch send
GET    /notifications/{user_id}         - Get user notifications
PUT    /notifications/{id}/read         - Mark as read
PUT    /notifications/read-all          - Mark all as read
DELETE /notifications/{id}              - Delete notification
GET    /notifications/preferences/{id}  - Get preferences
PUT    /notifications/preferences/{id}  - Update preferences
GET    /notifications/unread-count/{id} - Unread count
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | `notification-service` |
| `APP_PORT` | HTTP port | `8082` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATABASE_HOST` | PostgreSQL host | `postgresql.postgres.svc.cluster.local` |
| `DATABASE_PASSWORD` | Database password | (from secret) |
| `DAPR_HTTP_PORT` | Dapr HTTP port | `3500` |
| `DAPR_PUBSUB_NAME` | Dapr pubsub component | `pubsub-kafka` |
| `KAFKA_TOPIC_REMINDERS` | Reminders topic | `reminders` |
| `SMTP_HOST` | SMTP server | `smtp.mailtrap.io` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_FROM_EMAIL` | From email | `noreply@todo-chatbot.com` |
| `FIREBASE_API_KEY` | Firebase API key | (from secret) |
| `MAX_RETRIES` | Max delivery retries | `3` |

## Event Flow

### Input: REMINDER_TRIGGERED Event

```json
{
  "eventId": "uuid",
  "eventType": "REMINDER_TRIGGERED",
  "timestamp": "2026-02-25T10:30:00Z",
  "version": "1.0",
  "source": "dapr-jobs",
  "data": {
    "reminderId": "uuid",
    "taskId": "uuid",
    "userId": "uuid",
    "channel": "EMAIL",
    "message": "Task 'Submit report' is due in 15 minutes",
    "title": "Task Reminder",
    "triggeredAt": "2026-02-25T10:30:00Z"
  },
  "metadata": {
    "correlationId": "uuid"
  }
}
```

### Processing Flow

1. **Receive Event** via Dapr Pub/Sub
2. **Validate** required fields
3. **Check User Preferences** (channel enabled, quiet hours)
4. **Create Notification** record in database
5. **Send via Channel** (Email/Push/In-App)
6. **Track Delivery** (success/failure, message ID)
7. **Update Status** in database
8. **Log** structured delivery event

### Structured Log Output

```json
{
  "event": "notification_delivered",
  "level": "info",
  "timestamp": "2026-02-25T10:30:01.123Z",
  "service": "notification-service",
  "user_id": "user-123",
  "notification_id": "notif-456",
  "channel": "EMAIL",
  "type": "REMINDER",
  "message_id": "<msg-789@todo-chatbot.com>",
  "delivery_time_ms": 245
}
```

## Notification Channels

### Email (SMTP)

- Supports plain text and HTML
- TLS encryption
- Configurable from address
- Simulated in development (no SMTP configured)

### Push (FCM/APNS)

- Firebase Cloud Messaging for Android
- Apple Push Notification Service for iOS
- Topic-based subscriptions
- Rich notifications with images

### In-App

- Database storage
- Unread tracking
- Pagination support
- Bulk operations

## User Preferences

Users can configure:

```json
{
  "userId": "user-123",
  "emailEnabled": true,
  "pushEnabled": true,
  "inAppEnabled": true,
  "quietHoursStart": "22:00",
  "quietHoursEnd": "08:00",
  "timezone": "UTC"
}
```

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Test email provider
pytest tests/test_providers.py::test_email_provider

# Test API endpoints
pytest tests/test_api.py
```

## Monitoring

### Metrics

- `notifications_sent_total` - Total notifications sent
- `notifications_delivered_total` - Successfully delivered
- `notifications_failed_total` - Failed deliveries
- `notification_delivery_duration_seconds` - Delivery latency
- `notifications_by_channel` - Per-channel breakdown
- `notifications_by_type` - Per-type breakdown

### Alerts

- High error rate (> 5% for 5 minutes)
- High latency (p95 > 1s for 5 minutes)
- Low delivery rate (< 90% for 10 minutes)

## Deployment

### Prerequisites

- Kubernetes cluster
- Dapr installed
- Kafka cluster (Strimzi)
- PostgreSQL database
- Redis (for Dapr state)
- SMTP server (or use simulation)
- Firebase project (for push)

### Deploy

```bash
# Create secrets
kubectl create secret generic email-smtp \
  --from-literal=password=your-smtp-password \
  -n default

kubectl create secret generic push-notification \
  --from-literal=firebaseApiKey=your-firebase-key \
  -n default

# Apply Dapr components
kubectl apply -f ../../helm/dapr-components/

# Deploy service
helm install notification-service ./helm -n default

# Verify
kubectl get pods -l app.kubernetes.io/name=notification-service
dapr status -k
```

## Troubleshooting

### Not receiving notifications

1. Check Dapr subscription:
   ```bash
   kubectl get subscriptions.dapr.io
   ```

2. Check user preferences:
   ```bash
   curl http://localhost:8082/notifications/preferences/{user_id}
   ```

3. Check logs:
   ```bash
   kubectl logs <pod-name> -c notification-service
   kubectl logs <pod-name> -c daprd
   ```

### Email not sending

1. Verify SMTP configuration
2. Check SMTP credentials in secret
3. Test SMTP connectivity:
   ```bash
   kubectl exec -it <pod-name> -- telnet smtp.mailtrap.io 587
   ```

### Push not working

1. Verify Firebase API key
2. Check device tokens registered
3. Test FCM endpoint manually

## License

MIT
