# Phase V: AKS Deployment Guide

**Cloud-Native AI Todo Chatbot - Azure Kubernetes Service**

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Azure Setup](#2-azure-setup)
3. [AKS Cluster Creation](#3-aks-cluster-creation)
4. [Dapr Installation](#4-dapr-installation)
5. [Infrastructure Deployment](#5-infrastructure-deployment)
6. [Application Deployment](#6-application-deployment)
7. [Verification](#7-verification)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Azure CLI | v2.50+ | [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) |
| kubectl | v1.28+ | `az aks install-cli` |
| Helm | v3.13+ | [Install](https://helm.sh/docs/intro/install/) |
| Dapr CLI | v1.12+ | `winget install dapr.cli` |
| Docker Desktop | Latest | [Install](https://www.docker.com/products/docker-desktop) |

### Azure Account Requirements

- Active Azure subscription
- Contributor or Owner role on subscription
- Quota for:
  - 6+ vCPUs (for AKS cluster)
  - 3+ vCPUs (for Azure Database for PostgreSQL)
  - 2.5GB (for Azure Cache for Redis)

---

## 2. Azure Setup

### Step 1: Install Azure CLI

**Windows:**
```powershell
winget install Microsoft.AzureCLI
```

**Verify Installation:**
```bash
az --version
```

### Step 2: Login to Azure

```bash
az login
```

This will open a browser window for authentication.

**For Service Principal (CI/CD):**
```bash
az login --service-principal -u <app-id> -p <password> --tenant <tenant-id>
```

### Step 3: Set Subscription

```bash
# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "<subscription-id>"

# Verify
az account show
```

### Step 4: Register Required Providers

```bash
az provider register --namespace Microsoft.ContainerService
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.DBforPostgreSQL
az provider register --namespace Microsoft.Cache
```

---

## 3. AKS Cluster Creation

### Step 1: Create Resource Group

```bash
az group create \
  --name todo-rg \
  --location eastus
```

**Available Locations:**
```bash
az account list-locations --query "[].{Name:name, DisplayName:displayName}" --output table
```

### Step 2: Create AKS Cluster

**Basic Cluster (Development):**
```bash
az aks create \
  --resource-group todo-rg \
  --name todo-aks \
  --node-count 2 \
  --node-vm-size Standard_DS2_v2 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --enable-addons monitoring \
  --location eastus
```

**Production Cluster:**
```bash
az aks create \
  --resource-group todo-rg \
  --name todo-aks \
  --node-count 3 \
  --node-vm-size Standard_DS3_v2 \
  --enable-managed-identity \
  --generate-ssh-keys \
  --enable-addons monitoring \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10 \
  --network-plugin azure \
  --network-policy azure \
  --location eastus \
  --zones 1 2 3
```

### Step 3: Connect to Cluster

```bash
az aks get-credentials \
  --resource-group todo-rg \
  --name todo-aks \
  --overwrite-existing
```

### Step 4: Verify Connection

```bash
kubectl cluster-info
kubectl get nodes
```

---

## 4. Dapr Installation

### Step 1: Install Dapr on AKS

```bash
dapr init -k
```

**Or using Helm (Recommended for Production):**
```bash
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm upgrade --install dapr dapr/dapr \
  --version=1.12.0 \
  --namespace dapr-system \
  --create-namespace \
  --wait
```

### Step 2: Verify Dapr Installation

```bash
kubectl get pods -n dapr-system
dapr status -k
```

**Expected Output:**
```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION      AGE  CREATED
  dapr-sentry            dapr-system  True     Running  1         1.12.0       2m    2024-01-15 10:00:00
  dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0       2m    2024-01-15 10:00:00
  dapr-scheduler         dapr-system  True     Running  1         1.12.0       2m    2024-01-15 10:00:00
  dapr-operator          dapr-system  True     Running  1         1.12.0       2m    2024-01-15 10:00:00
  dapr-placement-server  dapr-system  True     Running  1         1.12.0       2m    2024-01-15 10:00:00
```

---

## 5. Infrastructure Deployment

### Step 1: Create Azure Services

#### Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group todo-rg \
  --name todo-postgres-server \
  --location eastus \
  --admin-user postgres \
  --admin-password <secure-password> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15 \
  --public-access 0.0.0.0 \
  --yes

# Get connection string
POSTGRES_HOST=$(az postgres flexible-server show \
  --resource-group todo-rg \
  --name todo-postgres-server \
  --query "fullyQualifiedDomainName" -o tsv)

# Create database
az postgres flexible-server db create \
  --resource-group todo-rg \
  --server-name todo-postgres-server \
  --database-name todo_chatbot
```

#### Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --resource-group todo-rg \
  --name todo-redis \
  --location eastus \
  --sku Basic \
  --vm-size C1 \
  --enable-non-ssl-port true

# Get Redis connection info
REDIS_HOST=$(az redis show \
  --resource-group todo-rg \
  --name todo-redis \
  --query "hostName" -o tsv)

REDIS_PASSWORD=$(az redis list-keys \
  --resource-group todo-rg \
  --name todo-redis \
  --query "primaryKey" -o tsv)
```

#### Azure Key Vault (for Secrets)

```bash
# Create Key Vault
az keyvault create \
  --resource-group todo-rg \
  --name todo-keyvault-$(openssl rand -hex 4) \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name <keyvault-name> \
  --name db-password \
  --value "<postgres-password>"

az keyvault secret set \
  --vault-name <keyvault-name> \
  --name redis-password \
  --value "$REDIS_PASSWORD"

# Get Key Vault ID
KEYVAULT_ID=$(az keyvault show \
  --resource-group todo-rg \
  --name <keyvault-name> \
  --query "id" -o tsv)
```

### Step 2: Create Kubernetes Secrets

```bash
# Database credentials secret
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password="<postgres-password>" \
  --from-literal host="$POSTGRES_HOST" \
  --from-literal port=5432 \
  --namespace default

# Redis secret
kubectl create secret generic redis-secret \
  --from-literal password="$REDIS_PASSWORD" \
  --namespace redis

# Email SMTP secret (example)
kubectl create secret generic email-smtp \
  --from-literal host=smtp.office365.com \
  --from-literal port=587 \
  --from-literal username=<your-email> \
  --from-literal password=<your-password> \
  --namespace default

# Push notification secret
kubectl create secret generic push-notification \
  --from-literal firebaseApiKey="<firebase-api-key>" \
  --namespace default
```

### Step 3: Deploy Kafka (Confluent Operator)

**Option A: Confluent for Kubernetes (Recommended for Production)**

```bash
# Add Confluent Helm repository
helm repo add confluentinc https://packages.confluent.io/helm
helm repo update

# Install Confluent Operator
helm install confluent-operator confluentinc/confluent-for-kubernetes \
  --namespace kafka \
  --create-namespace

# Wait for operator to be ready
kubectl wait --for=condition=Available deployment/confluent-operator -n kafka --timeout=300s
```

**Option B: Strimzi (Alternative)**

```bash
# Install Strimzi Operator
kubectl apply -f https://github.com/strimzi/strimzi-kafka-operator/releases/download/0.38.0/strimzi-cluster-operator-0.38.0.yaml -n kafka
```

### Step 4: Deploy Kafka Cluster

```bash
# Apply Kafka cluster configuration
kubectl apply -f kafka-cluster.yaml -n kafka

# Wait for Kafka to be ready
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kafka -n kafka --timeout=300s

# Verify Kafka cluster
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

### Step 5: Create Kafka Topics

```bash
# Create task-events topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic task-events \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 6 \
  --replication-factor 3

# Create reminders topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic reminders \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 3 \
  --replication-factor 3

# Create task-updates topic
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --create \
  --topic task-updates \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --partitions 6 \
  --replication-factor 3

# List topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092
```

---

## 6. Application Deployment

### Step 1: Update Dapr Components for Azure

Create `helm/dapr-components/azure-values.yaml`:

```yaml
# Azure-specific Dapr configurations
pubsub-kafka:
  brokers: "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"

state-redis:
  redisHost: "<redis-host>.redis.cache.windows.net:6380"
  ssl: true

secret-store:
  type: azure-keyvault
  keyVaultName: "<keyvault-name>"
  keyVaultNamespace: "default"
```

### Step 2: Apply Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f helm/dapr-components/ -n default

# Verify components
kubectl get components.dapr.io
```

### Step 3: Build and Push Docker Images

```bash
# Login to GitHub Container Registry
docker login ghcr.io -u <github-username>

# Build recurring-service
docker build -t ghcr.io/<org>/recurring-service:5.0.0 \
  -f services/recurring-service/Dockerfile \
  services/recurring-service/

# Build notification-service
docker build -t ghcr.io/<org>/notification-service:5.0.0 \
  -f services/notification-service/Dockerfile \
  services/notification-service/

# Push images
docker push ghcr.io/<org>/recurring-service:5.0.0
docker push ghcr.io/<org>/notification-service:5.0.0
```

### Step 4: Deploy Application with Helm

```bash
# Deploy with Azure-specific values
helm upgrade --install todo-app ./helm \
  --namespace default \
  --values helm/values.yaml \
  --values helm/values-aks.yaml \
  --set image.registry=ghcr.io/<org> \
  --set database.host="$POSTGRES_HOST" \
  --set redis.host="$REDIS_HOST" \
  --wait \
  --timeout 10m
```

### Step 5: Configure Ingress

```bash
# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."kubernetes\.azure\.com/mode"=system \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz

# Get Load Balancer IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Step 6: Configure DNS and TLS (Optional)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## 7. Verification

### Step 1: Check Pod Status

```bash
# All pods
kubectl get pods -n default

# Dapr sidecars
dapr status -k

# Kafka pods
kubectl get pods -n kafka

# Redis pods
kubectl get pods -n redis
```

### Step 2: Check Services

```bash
kubectl get services -n default
kubectl get services -n kafka
kubectl get services -n redis
```

### Step 3: Check Deployments

```bash
kubectl get deployments -n default
kubectl rollout status deployment/todo-app-chat-api
kubectl rollout status deployment/todo-app-recurring-task-service
kubectl rollout status deployment/todo-app-notification-service
```

### Step 4: Test Application

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoint
curl http://$EXTERNAL_IP/health

# Test task creation
curl -X POST http://$EXTERNAL_IP/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task from AKS",
    "description": "Testing AKS deployment",
    "priority": "high"
  }'

# Test list tasks
curl http://$EXTERNAL_IP/api/v1/tasks
```

### Step 5: Check Dapr Components

```bash
# List Dapr components
kubectl get components.dapr.io

# List Dapr subscriptions
kubectl get subscriptions.dapr.io

# Check Dapr logs
kubectl logs -l app.kubernetes.io/name=todo-app -c daprd
```

### Step 6: Monitor Kafka

```bash
# Check Kafka topics
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092

# Check consumer groups
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh --list \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092

# Tail topic messages
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
  --topic task-events \
  --bootstrap-server kafka-cluster-kafka-bootstrap:9092 \
  --from-beginning
```

### Step 7: Check Azure Monitor

```bash
# Enable Container Insights
az aks enable-addons \
  --resource-group todo-rg \
  --name todo-aks \
  --addons monitoring \
  --workspace-resource-id <log-analytics-workspace-id>

# View logs in Azure Portal
# Go to: Monitor > Logs > Container Insights
```

---

## 8. Troubleshooting

### Common Issues

#### Issue 1: Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> -c daprd

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

#### Issue 2: Dapr Sidecar Not Injecting

```bash
# Check Dapr injector logs
kubectl logs -l app=dapr-sidecar-injector -n dapr-system

# Verify annotations
kubectl get deployment <app-name> -o yaml | grep dapr.io
```

#### Issue 3: Database Connection Failed

```bash
# Test connectivity from pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h <postgres-host> -U postgres -d todo_chatbot

# Check secret
kubectl get secret db-credentials -o yaml
kubectl describe secret db-credentials
```

#### Issue 4: Kafka Connection Issues

```bash
# Test Kafka connectivity
kubectl run -it --rm kafka-test --image=bitnami/kafka:latest --restart=Never -- \
  kafka-console-consumer --topic task-events --bootstrap-server kafka-cluster-kafka-bootstrap:9092

# Check Kafka logs
kubectl logs -l app.kubernetes.io/name=kafka -n kafka
```

#### Issue 5: Ingress Not Working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl get ingress
kubectl describe ingress <ingress-name>

# Check external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Useful Commands

```bash
# Restart deployment
kubectl rollout restart deployment/<deployment-name>

# Scale deployment
kubectl scale deployment/<deployment-name> --replicas=3

# View resource usage
kubectl top pods
kubectl top nodes

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Port forward for debugging
kubectl port-forward svc/<service-name> 8080:80

# Delete and recreate pod
kubectl delete pod <pod-name>
```

### Azure-Specific Troubleshooting

```bash
# Check AKS cluster health
az aks show --resource-group todo-rg --name todo-aks

# View AKS logs
az aks get-logs --resource-group todo-rg --name todo-aks

# Check Azure Monitor
az monitor log-analytics workspace show \
  --resource-group todo-rg \
  --workspace-name <workspace-name>

# Check Azure Database
az postgres flexible-server show \
  --resource-group todo-rg \
  --name todo-postgres-server

# Check Azure Redis
az redis show \
  --resource-group todo-rg \
  --name todo-redis
```

---

## Cleanup

### Delete AKS Cluster

```bash
az aks delete \
  --resource-group todo-rg \
  --name todo-aks \
  --yes
```

### Delete Resource Group (All Resources)

```bash
az group delete \
  --name todo-rg \
  --yes \
  --no-wait
```

---

## Cost Estimation

| Resource | SKU | Monthly Cost (USD) |
|----------|-----|-------------------|
| AKS (3 nodes) | Standard_DS2_v2 | ~$150 |
| Azure Database for PostgreSQL | Burstable B1ms | ~$50 |
| Azure Cache for Redis | Basic C1 | ~$25 |
| Load Balancer | Standard | ~$20 |
| **Total (Estimated)** | | **~$245/month** |

---

## Next Steps

1. **Configure CI/CD** - Set up GitHub Actions for automated deployments
2. **Enable Monitoring** - Configure Azure Monitor and Application Insights
3. **Set Up Alerts** - Create alert rules for critical metrics
4. **Implement Backup** - Configure PostgreSQL automated backups
5. **Enable Auto-Scaling** - Configure HPA for application pods
6. **Secure Cluster** - Implement network policies and pod security policies

---

## Support Resources

- [AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Confluent Kubernetes](https://docs.confluent.io/operator/current/co-quickstart.html)
- [Azure PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/)
- [Azure Redis](https://docs.microsoft.com/en-us/azure/azure-cache-for-redis/)

---

**Document Version:** 1.0  
**Last Updated:** February 25, 2026  
**Author:** Phase V Development Team
