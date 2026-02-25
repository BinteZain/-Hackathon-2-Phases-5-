# Monitoring Quick Start Guide

## Quick Installation (5 minutes)

### Option 1: Automated Script

**Linux/Mac:**
```bash
./deploy-monitoring.sh
```

**Windows:**
```powershell
.\deploy-monitoring.bat
```

### Option 2: Manual Commands

```bash
# 1. Create namespace
kubectl create namespace monitoring

# 2. Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add loki https://grafana.github.io/helm-charts
helm repo update

# 3. Install Prometheus Stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin \
  --wait

# 4. Install Loki
helm install loki loki/loki-stack \
  --namespace monitoring \
  --create-namespace \
  --wait

# 5. Apply configurations
kubectl apply -f monitoring/prometheus-rules.yaml
kubectl apply -f monitoring/alertmanager-config.yaml
kubectl apply -f monitoring/servicemonitor.yaml
```

---

## Access Dashboards

### Grafana

```bash
# Port forward
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80

# Or get LoadBalancer IP
kubectl get svc monitoring-grafana -n monitoring
```

**Access:** http://localhost:3000  
**Username:** `admin`  
**Password:** `admin` (change this!)

---

### Prometheus

```bash
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
```

**Access:** http://localhost:9090

---

### Alertmanager

```bash
kubectl port-forward svc/monitoring-alertmanager -n monitoring 9093:9093
```

**Access:** http://localhost:9093

---

## Import Dashboards

### In Grafana UI:

1. Go to **Dashboards** → **Import**
2. Enter dashboard ID:
   - **6417** - Kubernetes Cluster
   - **1860** - Node Exporter
   - **13817** - Dapr Dashboard
   - **7589** - Kafka Overview
3. Select **Prometheus** datasource
4. Click **Import**

---

## Verify Installation

```bash
# Check all pods
kubectl get pods -n monitoring

# Expected:
# alertmanager-monitoring-alertmanager-0    2/2   Running
# monitoring-grafana-xxxxxxxxxx-xxxxx       3/3   Running
# monitoring-kube-state-metrics-xxxxx       1/1   Running
# monitoring-prometheus-xxxxxxxxxx-xxxxx    2/2   Running
# monitoring-prometheus-node-exporter-xxx   1/1   Running
# loki-xxxxxxxxxx-xxxxx                     1/1   Running
# promtail-xxxxx                            1/1   Running

# Check services
kubectl get svc -n monitoring

# Check Prometheus targets
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# Visit: http://localhost:9090/targets

# All targets should be UP
```

---

## Configure Alerting

### Update Slack Webhook

Edit `monitoring/alertmanager-config.yaml`:

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

Apply:
```bash
kubectl apply -f monitoring/alertmanager-config.yaml
kubectl rollout restart statefulset alertmanager-monitoring-alertmanager -n monitoring
```

---

## Add Application Metrics

### 1. Create ServiceMonitor

```bash
kubectl apply -f monitoring/servicemonitor.yaml
```

### 2. Verify Scraping

```bash
# Check ServiceMonitors
kubectl get servicemonitor -n default

# Check Prometheus targets
# Visit: http://localhost:9090/targets
# Your application endpoints should appear
```

---

## Query Examples

### Prometheus Queries

```promql
# Request rate
sum(rate(http_requests_total[5m]))

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# p95 latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# CPU usage
sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)

# Memory usage
sum(container_memory_working_set_bytes) by (pod)

# Dapr sidecar health
dapr_runtime_component_status

# Kafka consumer lag
sum(kafka_consumer_group_lag) by (group, topic)
```

### Loki Log Queries

```logql
# All logs from chat-api
{app="chat-api"}

# Error logs
{app="chat-api"} |= "error"

# Logs with label
{namespace="default"} |= "TASK_CREATED"

# Rate of error logs
rate({app="chat-api"} |= "error" [5m])
```

---

## Uninstall

```bash
# Uninstall monitoring stack
helm uninstall monitoring -n monitoring
helm uninstall loki -n monitoring

# Delete namespace
kubectl delete namespace monitoring

# Delete PVCs (optional - removes all data)
kubectl delete pvc -n monitoring --all
```

---

## Troubleshooting

### Prometheus Not Scraping

```bash
# Check ServiceMonitor
kubectl get servicemonitor -n default
kubectl describe servicemonitor todo-chat-api -n default

# Check endpoints
kubectl get endpoints -n default

# Check Prometheus config
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
# Visit: http://localhost:9090/targets
```

### Grafana Dashboards Empty

```bash
# Check datasource
# Grafana → Configuration → Data sources → Prometheus
# URL: http://monitoring-prometheus:9090

# Test query
# Grafana → Explore → Run: up{job="kubernetes-pods"}
```

### Loki Not Receiving Logs

```bash
# Check Promtail
kubectl get pods -n monitoring -l app=promtail
kubectl logs -l app=promtail -n monitoring

# Test Loki
curl http://loki:3100/ready
curl http://loki:3100/loki/api/v1/labels
```

---

## Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Prometheus | 500m-1000m | 2-4Gi | 50Gi |
| Grafana | 100-500m | 256-512Mi | 10Gi |
| Alertmanager | 100-200m | 100-200Mi | 10Gi |
| Loki | 100-500m | 256-512Mi | 10Gi |
| Promtail | 50-200m | 128-256Mi | - |
| **Total** | **~2 CPU** | **~4GB** | **~80GB** |

---

## Next Steps

1. ✅ **Import Dashboards** - Kubernetes, Dapr, Kafka
2. ✅ **Configure Alerts** - Update Slack webhook
3. ✅ **Add ServiceMonitors** - For all microservices
4. ✅ **Set Up Recording Rules** - For complex queries
5. ✅ **Configure Retention** - Based on storage budget
6. ✅ **Enable TLS** - For secure access
7. ✅ **Set Up On-Call** - PagerDuty/OpsGenie integration

---

**Full Documentation:** [MONITORING_SETUP.md](./MONITORING_SETUP.md)
