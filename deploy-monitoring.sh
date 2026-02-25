#!/bin/bash

# Phase V - Monitoring Stack Deployment Script
# Deploys Prometheus, Grafana, Loki, and Alertmanager

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="monitoring"
RELEASE_NAME="monitoring"
GRAFANA_PASSWORD="admin"  # CHANGE THIS!

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Phase V - Monitoring Stack Deployment                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo -e "${YELLOW}[1/8] Checking prerequisites...${NC}"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi
print_status "kubectl installed: $(kubectl version --client --short 2>/dev/null | grep -oP 'Client Version: \K.*' || kubectl version --client -o yaml | grep gitVersion | head -1)"

# Check Helm
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    exit 1
fi
print_status "Helm installed: $(helm version --short)"

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi
print_status "Connected to cluster: $(kubectl config current-context)"

# Check node count
NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
if [ "$NODE_COUNT" -lt 2 ]; then
    print_warning "Cluster has only $NODE_COUNT node(s). Recommended: 4+ nodes"
else
    print_status "Cluster has $NODE_COUNT nodes"
fi

# Check available memory
echo -e "${YELLOW}[2/8] Checking cluster resources...${NC}"
TOTAL_MEMORY=$(kubectl top nodes --no-headers 2>/dev/null | awk '{sum += $3} END {print sum}' || echo "0")
if [ "$TOTAL_MEMORY" -eq 0 ]; then
    print_warning "Could not determine available memory (metrics-server may not be installed)"
else
    print_status "Total memory in use: ${TOTAL_MEMORY}Mi"
fi

# Create namespace
echo -e "${YELLOW}[3/8] Creating namespace...${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
print_status "Namespace '$NAMESPACE' created/verified"

# Add Helm repositories
echo -e "${YELLOW}[4/8] Adding Helm repositories...${NC}"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo add loki https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo update
print_status "Helm repositories added and updated"

# Install kube-prometheus-stack
echo -e "${YELLOW}[5/8] Installing kube-prometheus-stack...${NC}"
echo "   This may take 5-10 minutes..."

helm upgrade --install $RELEASE_NAME prometheus-community/kube-prometheus-stack \
    --namespace $NAMESPACE \
    --create-namespace \
    --values monitoring/values-production.yaml \
    --set grafana.adminPassword=$GRAFANA_PASSWORD \
    --wait \
    --timeout 15m \
    --atomic

print_status "kube-prometheus-stack installed"

# Install Loki stack
echo -e "${YELLOW}[6/8] Installing Loki stack...${NC}"

helm upgrade --install loki loki/loki-stack \
    --namespace $NAMESPACE \
    --create-namespace \
    --values monitoring/loki-values.yaml \
    --wait \
    --timeout 10m \
    --atomic

print_status "Loki stack installed"

# Apply Prometheus rules
echo -e "${YELLOW}[7/8] Applying Prometheus rules...${NC}"
kubectl apply -f monitoring/prometheus-rules.yaml
print_status "Prometheus rules applied"

# Apply Alertmanager configuration
echo -e "${YELLOW}[8/8] Applying Alertmanager configuration...${NC}"
kubectl apply -f monitoring/alertmanager-config.yaml
print_status "Alertmanager configuration applied"

# Wait for all pods to be ready
echo ""
echo -e "${YELLOW}Waiting for all components to be ready...${NC}"
sleep 30

kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE --timeout=300s 2>/dev/null || print_warning "Some pods may still be starting"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=loki -n $NAMESPACE --timeout=300s 2>/dev/null || print_warning "Loki may still be starting"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=promtail -n $NAMESPACE --timeout=300s 2>/dev/null || print_warning "Promtail may still be starting"

# Print access information
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Monitoring Stack Deployment Complete!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access Information:${NC}"
echo ""

# Get Grafana URL
GRAFANA_SERVICE=$(kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -n "$GRAFANA_SERVICE" ]; then
    echo -e "  ${GREEN}✓${NC} Grafana: http://$GRAFANA_SERVICE"
else
    echo -e "  ${YELLOW}⚠${NC} Grafana: kubectl port-forward svc/$RELEASE_NAME-grafana -n $NAMESPACE 3000:80"
fi
echo "     Username: admin"
echo "     Password: $GRAFANA_PASSWORD"
echo ""

# Get Prometheus URL
PROMETHEUS_SERVICE=$(kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=prometheus -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -n "$PROMETHEUS_SERVICE" ]; then
    echo -e "  ${GREEN}✓${NC} Prometheus: http://$PROMETHEUS_SERVICE"
else
    echo -e "  ${YELLOW}⚠${NC} Prometheus: kubectl port-forward svc/$RELEASE_NAME-prometheus -n $NAMESPACE 9090:9090"
fi
echo ""

# Get Alertmanager URL
ALERTMANAGER_SERVICE=$(kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=alertmanager -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -n "$ALERTMANAGER_SERVICE" ]; then
    echo -e "  ${GREEN}✓${NC} Alertmanager: http://$ALERTMANAGER_SERVICE"
else
    echo -e "  ${YELLOW}⚠${NC} Alertmanager: kubectl port-forward svc/$RELEASE_NAME-alertmanager -n $NAMESPACE 9093:9093"
fi
echo ""

# Get Loki URL
LOKI_SERVICE=$(kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=loki -o jsonpath='{.items[0].spec.clusterIP}' 2>/dev/null)
if [ -n "$LOKI_SERVICE" ]; then
    echo -e "  ${GREEN}✓${NC} Loki: Internal cluster IP: $LOKI_SERVICE:3100"
    echo "     External: kubectl port-forward svc/loki -n $NAMESPACE 3100:3100"
fi
echo ""

# Print resource usage
echo -e "${BLUE}Resource Usage:${NC}"
echo ""
kubectl get pods -n $NAMESPACE -o wide
echo ""

# Print storage
echo -e "${BLUE}Persistent Volumes:${NC}"
echo ""
kubectl get pvc -n $NAMESPACE
echo ""

# Next steps
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "  1. Access Grafana and configure datasources"
echo "  2. Import dashboards (IDs: 6417, 1860, 13817, 7589)"
echo "  3. Update Alertmanager Slack webhook URL"
echo "  4. Configure ServiceMonitors for your applications"
echo "  5. Set up alerting rules based on your SLOs"
echo ""
echo -e "${YELLOW}Documentation: MONITORING_SETUP.md${NC}"
echo ""
