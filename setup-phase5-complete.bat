@echo off
echo ========================================
echo Phase V - Complete Infrastructure Setup
echo ========================================
echo.

echo Step 1: Starting Minikube...
minikube start --memory=8192 --cpus=4
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Minikube failed to start. Make sure Docker Desktop is running!
    pause
    exit /b 1
)
echo.

echo Step 2: Creating namespaces...
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace redis --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace postgres --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace dapr-system --dry-run=client -o yaml | kubectl apply -f -
echo.

echo Step 3: Initializing Dapr on Kubernetes...
dapr init -k
echo.

echo Step 4: Installing Strimzi Kafka Operator...
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
echo.

echo Step 5: Waiting for Strimzi Operator to be ready...
kubectl wait --for=condition=Available deployment/strimzi-cluster-operator -n kafka --timeout=300s
echo.

echo Step 6: Deploying Kafka cluster...
kubectl apply -f kafka-cluster.yaml -n kafka
echo.

echo Step 7: Waiting for Kafka brokers to be ready (this takes 3-5 minutes)...
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kafka -n kafka --timeout=300s
echo.

echo Step 8: Installing Redis...
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install redis bitnami/redis -n redis --set auth.password=redis123 --wait
echo.

echo Step 9: Installing PostgreSQL...
helm install postgresql bitnami/postgresql -n postgres --set auth.password=postgres123 --set auth.username=postgres --wait
echo.

echo Step 10: Creating Kafka topics...
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- bin/kafka-topics.sh --create --topic task-events --bootstrap-server kafka-cluster-kafka-bootstrap:9092 --partitions 6 --replication-factor 3
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- bin/kafka-topics.sh --create --topic reminders --bootstrap-server kafka-cluster-kafka-bootstrap:9092 --partitions 3 --replication-factor 3
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- bin/kafka-topics.sh --create --topic task-updates --bootstrap-server kafka-cluster-kafka-bootstrap:9092 --partitions 6 --replication-factor 3
echo.

echo Step 11: Applying Dapr components...
kubectl apply -f helm/dapr-components/
echo.

echo Step 12: Verifying installation...
echo.
echo === Dapr Status ===
dapr status -k
echo.
echo === Kafka Pods ===
kubectl get pods -n kafka
echo.
echo === Redis Pods ===
kubectl get pods -n redis
echo.
echo === PostgreSQL Pods ===
kubectl get pods -n postgres
echo.
echo === Dapr Components ===
kubectl get components.dapr.io
echo.

echo ========================================
echo Phase V Infrastructure Setup Complete!
echo ========================================
pause
