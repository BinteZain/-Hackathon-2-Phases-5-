# Phase V: Monitoring & Observability Setup

**Cloud-Native AI Todo Chatbot - Complete Monitoring Stack**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Dashboards](#dashboards)
7. [Alerting](#alerting)
8. [Logging with Loki](#logging-with-loki)
9. [Access & Security](#access--security)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Monitoring Stack Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Prometheus** | Metrics collection & storage | 9090 |
| **Grafana** | Visualization & dashboards | 3000 |
| **Alertmanager** | Alert routing & notification | 9093 |
| **Loki** | Log aggregation | 3100 |
| **Promtail** | Log collector | - |
| **Node Exporter** | Node metrics | 9100 |
| **Kube State Metrics** | Kubernetes object metrics | 8080 |

### What We Monitor

- **Cluster Health**: Nodes, pods, deployments
- **Application Metrics**: Request rate, latency, errors
- **Dapr Metrics**: Sidecar health, pub/sub, state operations
- **Kafka Metrics**: Consumer lag, topic throughput
- **Resource Usage**: CPU, memory, disk, network
- **Logs**: Application logs, Dapr logs, system logs

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              Monitoring Namespace                       │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │     │
│  │  │  Prometheus  │  │   Grafana    │  │ Alertmanager │  │     │
│  │  │   (Stateful) │  │  (Deployment)│  │  (Deployment)│  │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │     │
│  │  ┌──────────────┐  ┌──────────────┐                     │     │
│  │  │     Loki     │  │   Promtail   │                     │     │
│  │  │   (Stateful) │  │  (DaemonSet) │                     │     │
│  │  └──────────────┘  └──────────────┘                     │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              Application Namespace                      │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │     │
│  │  │   Chat API   │  │   Recurring  │  │  Notification│  │     │
│  │  │  + Dapr SC   │  │  + Dapr SC   │  │  + Dapr SC   │  │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │     │
│  │         │                  │                  │          │     │
│  │         └──────────────────┼──────────────────┘          │     │
│  │                            │                              │     │
│  │         ┌──────────────────▼──────────────────┐          │     │
│  │         │      Prometheus ServiceMonitor      │          │     │
│  │         │      (Auto-discover endpoints)      │          │     │
│  │         └─────────────────────────────────────┘          │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              System Components                          │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │     │
│  │  │ Node Exporter│  │Kube State    │  │  cAdvisor    │  │     │
│  │  │  (DaemonSet) │  │  Metrics     │  │  (Built-in)  │  │     │
│  │  │              │  │  (Deployment)│  │              │  │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     Grafana     │
                    │   Dashboards    │
                    │  - Cluster      │
                    │  - Application  │
                    │  - Dapr         │
                    │  - Kafka        │
                    └─────────────────┘
```

---

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| kubectl | v1.28+ | `az aks install-cli` |
| Helm | v3.13+ | [Install](https://helm.sh/docs/intro/install/) |
| Azure CLI | v2.50+ | [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) |

### Cluster Requirements

- AKS cluster with 4+ nodes (Standard_DS2_v2 or equivalent)
- 8GB+ available memory
- 50GB+ available storage
- Azure Disk CSI driver enabled

---

## Installation

### Step 1: Connect to AKS Cluster

```bash
# Login to Azure
az login

# Get AKS credentials
az aks get-credentials \
  --resource-group todo-rg \
  --name todo-aks \
  --overwrite-existing

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Step 2: Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

### Step 3: Add Helm Repositories

```bash
# Prometheus Community
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add loki https://grafana.github.io/loki/charts

# Update repositories
helm repo update
```

### Step 4: Install kube-prometheus-stack

**Option A: Default Installation (Quick Start)**

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --wait \
  --timeout 10m
```

**Option B: Production Installation (Recommended)**

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/values-production.yaml \
  --wait \
  --timeout 15m
```

### Step 5: Install Loki Stack

```bash
helm install loki loki/loki-stack \
  --namespace monitoring \
  --create-namespace \
  --values monitoring/loki-values.yaml \
  --wait
```

### Step 6: Verify Installation

```bash
# Check all pods
kubectl get pods -n monitoring

# Expected output:
# NAME                                                        READY   STATUS    RESTARTS   AGE
# alertmanager-monitoring-alertmanager-0                      2/2     Running   0          5m
# monitoring-grafana-xxxxxxxxxx-xxxxx                         3/3     Running   0          5m
# monitoring-kube-state-metrics-xxxxxxxxxx-xxxxx              1/1     Running   0          5m
# monitoring-prometheus-xxxxxxxxxx-xxxxx                      2/2     Running   0          5m
# monitoring-prometheus-node-exporter-xxxxx                   1/1     Running   0          5m
# loki-xxxxxxxxxx-xxxxx                                       1/1     Running   0          3m
# promtail-xxxxx                                              1/1     Running   0          3m

# Check services
kubectl get svc -n monitoring

# Check deployments
kubectl get deployments -n monitoring

# Check statefulsets
kubectl get statefulsets -n monitoring
```

---

## Configuration

### Production Values (values-production.yaml)

```yaml
# monitoring/values-production.yaml

prometheus:
  enabled: true
  prometheusSpec:
    replicas: 2
    retention: 30d
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: 1000m
        memory: 4Gi
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: default
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    additionalScrapeConfigs: []

alertmanager:
  enabled: true
  alertmanagerSpec:
    replicas: 2
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: default
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 10Gi
    resources:
      requests:
        cpu: 100m
        memory: 100Mi
      limits:
        cpu: 200m
        memory: 200Mi

grafana:
  enabled: true
  replicas: 2
  adminPassword: admin  # Change this!
  persistence:
    enabled: true
    type: sts
    storageClassName: default
    size: 10Gi
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  service:
    type: LoadBalancer
    port: 80
  dashboardProviders:
    dashboardproviders.yaml:
      providers:
        - name: 'default'
          orgId: 1
          folder: ''
          type: file
          disableDeletion: false
          editable: true
          options:
            path: /var/lib/grafana/dashboards/default
  dashboards:
    default:
      kubernetes-cluster:
        gnetId: 6417
        revision: 1
        datasource: Prometheus
      node-exporter:
        gnetId: 1860
        revision: 1
        datasource: Prometheus
      prometheus-stats:
        gnetId: 2
        revision: 1
        datasource: Prometheus

kubeStateMetrics:
  enabled: true
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 200m
      memory: 512Mi

nodeExporter:
  enabled: true
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
```

### Loki Values (loki-values.yaml)

```yaml
# monitoring/loki-values.yaml

loki:
  enabled: true
  isDefault: true
  persistence:
    enabled: true
    size: 10Gi
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  config:
    limits_config:
      enforce_metric_name: false
      reject_old_samples: true
      reject_old_samples_max_age: 168h
    chunk_store_config:
      max_look_back_period: 0s
    table_manager:
      retention_deletes_enabled: false
      retention_period: 0s
    schema_config:
      configs:
        - from: 2020-10-24
          store: boltdb-shipper
          object_store: filesystem
          schema: v11
          index:
            prefix: index_
            period: 24h

promtail:
  enabled: true
  resources:
    requests:
      cpu: 50m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  config:
    snippets:
      scrapeConfigs: |
        - job_name: kubernetes-pods
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
              action: keep
              regex: true
            - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
              action: replace
              target_label: __metrics_path__
              regex: (.+)
            - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
              action: replace
              regex: ([^:]+)(?::\d+)?;(\d+)
              replacement: $1:$2
              target_label: __address__
            - action: labelmap
              regex: __meta_kubernetes_pod_label_(.+)
            - source_labels: [__meta_kubernetes_namespace]
              action: replace
              target_label: kubernetes_namespace
            - source_labels: [__meta_kubernetes_pod_name]
              action: replace
              target_label: kubernetes_pod_name

grafana:
  enabled: true
  loki:
    enabled: true
    url: http://loki:3100
```

---

## Dashboards

### Access Grafana

```bash
# Get Grafana admin password
kubectl get secret monitoring-grafana \
  -n monitoring \
  -o jsonpath="{.data.admin-password}" \
  | base64 --decode

# Port forward Grafana
kubectl port-forward svc/monitoring-grafana \
  -n monitoring \
  3000:80

# Or get LoadBalancer IP
kubectl get svc monitoring-grafana -n monitoring
```

**Access:** `http://<grafana-ip-or-localhost:3000>`  
**Username:** `admin`  
**Password:** (from command above)

---

### Import Dashboards

**Pre-configured Dashboards:**

| Dashboard | ID | Description |
|-----------|----|-------------|
| Kubernetes Cluster | 6417 | Cluster health & resources |
| Node Exporter | 1860 | Node-level metrics |
| Prometheus Stats | 2 | Prometheus health |
| Dapr Dashboard | 13817 | Dapr sidecar metrics |
| Kafka Overview | 7589 | Kafka cluster metrics |
| Application Metrics | Custom | Your app metrics |

**Import via Grafana UI:**
1. Go to **Dashboards** → **Import**
2. Enter dashboard ID
3. Select Prometheus datasource
4. Click **Import**

**Import via Helm:**

```yaml
# Add to values-production.yaml under grafana.dashboards
grafana:
  dashboards:
    default:
      dapr:
        gnetId: 13817
        revision: 1
        datasource: Prometheus
      kafka:
        gnetId: 7589
        revision: 5
        datasource: Prometheus
```

---

### Custom Application Dashboard

Create `monitoring/dashboards/application.json`:

```json
{
  "dashboard": {
    "title": "Todo Chatbot - Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=~\".*chat-api.*\"}[5m])) by (service)",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{job=~\".*chat-api.*\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{job=~\".*chat-api.*\"}[5m])) * 100",
            "legendFormat": "Error %"
          }
        ]
      },
      {
        "title": "Response Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=~\".*chat-api.*\"}[5m])) by (le))",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "Dapr Sidecar Health",
        "targets": [
          {
            "expr": "dapr_runtime_component_status",
            "legendFormat": "{{app_id}}"
          }
        ]
      }
    ]
  }
}
```

---

## Alerting

### Configure Alertmanager

Create `monitoring/alertmanager-config.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: alertmanager-monitoring-alertmanager
  namespace: monitoring
  labels:
    app: alertmanager
type: Opaque
stringData:
  alertmanager.yaml: |
    global:
      resolve_timeout: 5m
      slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    
    route:
      group_by: ['alertname', 'namespace']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 1h
      receiver: 'slack-notifications'
      routes:
        - match:
            severity: critical
          receiver: 'slack-critical'
        - match:
            severity: warning
          receiver: 'slack-warning'
    
    receivers:
      - name: 'slack-notifications'
        slack_configs:
          - channel: '#alerts'
            send_resolved: true
            title: '{{ .Status | toUpper }}: {{ .CommonAnnotations.summary }}'
            text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
      
      - name: 'slack-critical'
        slack_configs:
          - channel: '#alerts-critical'
            send_resolved: true
            title: '🚨 CRITICAL: {{ .CommonAnnotations.summary }}'
      
      - name: 'slack-warning'
        slack_configs:
          - channel: '#alerts-warning'
            send_resolved: true
            title: '⚠️ WARNING: {{ .CommonAnnotations.summary }}'
    
    inhibit_rules:
      - source_match:
          severity: 'critical'
        target_match:
          severity: 'warning'
        equal: ['alertname', 'namespace']
```

Apply the configuration:

```bash
kubectl apply -f monitoring/alertmanager-config.yaml
```

---

### Prometheus Rules

Create `monitoring/prometheus-rules.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: todo-app-alerts
  namespace: monitoring
  labels:
    release: monitoring
spec:
  groups:
    - name: todo-app.rules
      rules:
        # High Error Rate
        - alert: HighErrorRate
          expr: |
            sum(rate(http_requests_total{status=~"5..",job=~".*chat-api.*"}[5m])) 
            / sum(rate(http_requests_total{job=~".*chat-api.*"}[5m])) * 100 > 5
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate detected"
            description: "Error rate is {{ $value }}% (threshold: 5%)"
        
        # High Latency
        - alert: HighLatency
          expr: |
            histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job=~".*chat-api.*"}[5m])) by (le)) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High latency detected"
            description: "p95 latency is {{ $value }}s (threshold: 1s)"
        
        # Pod Not Ready
        - alert: PodNotReady
          expr: |
            kube_pod_status_ready{condition="true",namespace="default"} == 0
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "Pod {{ $labels.pod }} not ready"
            description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been not ready for 5 minutes"
        
        # High CPU Usage
        - alert: HighCPUUsage
          expr: |
            sum(rate(container_cpu_usage_seconds_total{namespace="default"}[5m])) by (pod) 
            / sum(kube_pod_container_resource_limits{resource="cpu",namespace="default"}) by (pod) * 100 > 80
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "High CPU usage for {{ $labels.pod }}"
            description: "CPU usage is {{ $value }}% (threshold: 80%)"
        
        # High Memory Usage
        - alert: HighMemoryUsage
          expr: |
            sum(container_memory_working_set_bytes{namespace="default"}) by (pod) 
            / sum(kube_pod_container_resource_limits{resource="memory",namespace="default"}) by (pod) * 100 > 85
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "High memory usage for {{ $labels.pod }}"
            description: "Memory usage is {{ $value }}% (threshold: 85%)"
        
        # Dapr Sidecar Down
        - alert: DaprSidecarDown
          expr: |
            dapr_runtime_component_status != 1
          for: 2m
          labels:
            severity: critical
          annotations:
            summary: "Dapr sidecar down for {{ $labels.app_id }}"
            description: "Dapr sidecar for application {{ $labels.app_id }} is not healthy"
        
        # Kafka Consumer Lag
        - alert: KafkaConsumerLag
          expr: |
            sum(kafka_consumer_group_lag{namespace="kafka"}) by (group, topic) > 1000
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High Kafka consumer lag"
            description: "Consumer group {{ $labels.group }} has lag of {{ $value }} on topic {{ $labels.topic }}"
        
        # Persistent Volume Almost Full
        - alert: PersistentVolumeAlmostFull
          expr: |
            (kubelet_volume_stats_capacity_bytes - kubelet_volume_stats_available_bytes) 
            / kubelet_volume_stats_capacity_bytes * 100 > 85
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "PersistentVolume almost full"
            description: "PersistentVolume {{ $labels.persistentvolumeclaim }} is {{ $value }}% full"
```

Apply the rules:

```bash
kubectl apply -f monitoring/prometheus-rules.yaml
```

---

## Logging with Loki

### Query Logs in Grafana

1. Go to **Explore** in Grafana
2. Select **Loki** as datasource
3. Use LogQL queries:

**Example Queries:**

```logql
# All logs from chat-api
{app="chat-api"}

# Error logs
{app="chat-api"} |= "error"

# Logs from specific pod
{kubernetes_pod_name="chat-api-xxxxxxxxxx-xxxxx"}

# Logs with label
{namespace="default"} |= "TASK_CREATED"

# Rate of error logs
rate({app="chat-api"} |= "error" [5m])
```

### Configure Promtail for Application Logs

Create `monitoring/promtail-config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0
    
    positions:
      filename: /tmp/positions.yaml
    
    clients:
      - url: http://loki:3100/loki/api/v1/push
    
    scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        
        pipeline_stages:
          - cri: {}
        
        relabel_configs:
          - source_labels:
              - __meta_kubernetes_pod_label_app
            target_label: app
          - source_labels:
              - __meta_kubernetes_namespace
            target_label: namespace
          - source_labels:
              - __meta_kubernetes_pod_name
            target_label: pod
```

---

## Access & Security

### Expose Grafana Securely

**Option 1: LoadBalancer (Simple)**

```yaml
# Already configured in values-production.yaml
grafana:
  service:
    type: LoadBalancer
    port: 80
```

**Option 2: Ingress with TLS**

```yaml
grafana:
  service:
    type: ClusterIP
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - grafana.todo-chatbot.com
    tls:
      - secretName: grafana-tls
        hosts:
          - grafana.todo-chatbot.com
```

**Option 3: Port Forward (Development)**

```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

---

### Expose Prometheus

```bash
# Port forward
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090

# Or use Ingress
kubectl apply -f monitoring/prometheus-ingress.yaml
```

---

### Expose Alertmanager

```bash
# Port forward
kubectl port-forward svc/monitoring-alertmanager -n monitoring 9093:9093
```

---

### RBAC Configuration

Create `monitoring/rbac.yaml`:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-reader
rules:
  - apiGroups: [""]
    resources: ["nodes", "nodes/metrics", "services", "endpoints", "pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["extensions"]
    resources: ["ingresses"]
    verbs: ["get", "list", "watch"]
  - nonResourceURLs: ["/metrics"]
    verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-reader-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: monitoring-reader
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: monitoring
```

Apply RBAC:

```bash
kubectl apply -f monitoring/rbac.yaml
```

---

## Troubleshooting

### Prometheus Not Scraping Targets

```bash
# Check Prometheus targets
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# Visit: http://localhost:9090/targets

# Check ServiceMonitor
kubectl get servicemonitor -n monitoring
kubectl describe servicemonitor <name> -n monitoring

# Check if endpoints exist
kubectl get endpoints -n default
```

---

### Grafana Dashboards Empty

```bash
# Check datasource
# Grafana → Configuration → Data sources → Prometheus
# URL should be: http://monitoring-prometheus:9090

# Check Prometheus queries
# Grafana → Explore → Run: up{job="kubernetes-pods"}

# Check if metrics exist
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# Visit: http://localhost:9090/api/v1/targets
```

---

### Loki Not Receiving Logs

```bash
# Check Promtail pods
kubectl get pods -n monitoring -l app=promtail

# Check Promtail logs
kubectl logs -l app=promtail -n monitoring

# Test Loki connection
curl http://loki:3100/ready
curl http://loki:3100/loki/api/v1/labels
```

---

### Alertmanager Not Sending Alerts

```bash
# Check Alertmanager config
kubectl get secret alertmanager-monitoring-alertmanager -n monitoring -o yaml

# Check Alertmanager UI
kubectl port-forward svc/monitoring-alertmanager -n monitoring 9093:9093
# Visit: http://localhost:9093

# Check silenced alerts
curl http://localhost:9093/api/v1/silences
```

---

### High Resource Usage

```bash
# Check Prometheus storage
kubectl get pvc -n monitoring

# Reduce retention
helm upgrade monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set prometheus.prometheusSpec.retention=15d

# Scale down replicas
helm upgrade monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  --set prometheus.prometheusSpec.replicas=1 \
  --set grafana.replicas=1
```

---

## Useful Commands

```bash
# List all monitoring resources
kubectl get all -n monitoring

# Check Prometheus targets
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090

# Check Grafana dashboards
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'

# Query Loki
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={app="chat-api"}' \
  --data-urlencode 'start=2024-01-01T00:00:00Z' \
  --data-urlencode 'end=2024-01-31T23:59:59Z'

# Uninstall monitoring stack
helm uninstall monitoring -n monitoring
helm uninstall loki -n monitoring
kubectl delete namespace monitoring
```

---

## Cost Estimation

| Resource | Size | Monthly Cost (USD) |
|----------|------|-------------------|
| Prometheus (2 replicas) | 2 vCPU, 4GB | ~$60 |
| Grafana (2 replicas) | 0.5 vCPU, 512MB | ~$30 |
| Loki (1 replica) | 0.5 vCPU, 512MB | ~$15 |
| Storage (70GB) | Standard SSD | ~$10 |
| **Total (Estimated)** | | **~$115/month** |

---

## Next Steps

1. **Configure Dapr Metrics** - Enable Dapr metrics endpoint
2. **Add Custom Dashboards** - Create application-specific dashboards
3. **Set Up On-Call** - Configure PagerDuty/OpsGenie integration
4. **Enable Distributed Tracing** - Install Jaeger/Zipkin
5. **Configure Log Retention** - Set up log rotation and retention policies
6. **Set Up Synthetic Monitoring** - Add uptime checks

---

## Support Resources

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [Loki Docs](https://grafana.com/docs/loki/)
- [kube-prometheus-stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Author:** Phase V Development Team
