# kubectl-ai - AI-Assisted Kubernetes Operations

## Overview

kubectl-ai is a kubectl plugin that allows you to manage Kubernetes clusters using natural language commands powered by AI.

## Installation

### Windows

```powershell
# Download kubectl-ai
curl -L -o kubectl-ai.exe https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai_Windows_x86_64.zip

# Move to PATH
move kubectl-ai.exe C:\Windows\System32\kubectl-ai.exe

# Verify installation
kubectl-ai version
```

### Using the included binary

```powershell
# Use the included kubectl-ai.exe
copy kubectl-ai.exe C:\Windows\System32\
```

## Quick Start

```bash
# Start interactive session
kubectl-ai

# Or use single commands
kubectl-ai "deploy the todo frontend with 2 replicas"
```

## kubectl-ai Commands for Phase 4

### Deployment

```bash
# Create namespace
kubectl-ai "create a namespace called phase4"

# Deploy PostgreSQL
kubectl-ai "deploy postgresql with 5Gi storage in phase4 namespace"

# Deploy backend
kubectl-ai "deploy phase3-backend image with 2 replicas in phase4 namespace"

# Deploy frontend
kubectl-ai "deploy phase3-frontend image with 2 replicas in phase4 namespace"

# Create services
kubectl-ai "create clusterip services for frontend and backend"
```

### Scaling

```bash
# Scale deployments
kubectl-ai "scale the backend to 5 replicas to handle more load"
kubectl-ai "scale frontend to 3 replicas"

# Enable autoscaling
kubectl-ai "enable horizontal pod autoscaling for backend with min 2 max 10 replicas"
kubectl-ai "create HPA for frontend targeting 70% CPU"
```

### Troubleshooting

```bash
# Check pod issues
kubectl-ai "check why the pods are failing"
kubectl-ai "why is the backend pod crashing?"

# Analyze logs
kubectl-ai "show me the backend logs"
kubectl-ai "analyze the frontend pod issues"

# Check connectivity
kubectl-ai "check database connection issues"
kubectl-ai "why can't frontend connect to backend?"
```

### Resource Management

```bash
# Optimize resources
kubectl-ai "optimize resource allocation for the backend"
kubectl-ai "set CPU and memory limits for frontend pods"

# Add resource requests
kubectl-ai "add resource requests for all deployments"

# View resource usage
kubectl-ai "show resource usage for all pods in phase4"
```

### Security

```bash
# Add security context
kubectl-ai "add security context to backend deployment"

# Create network policies
kubectl-ai "create network policy to isolate backend from other namespaces"

# Pod security standards
kubectl-ai "add pod security standards for phase4 namespace"
```

### Configuration

```bash
# Create ConfigMaps
kubectl-ai "create configmap for backend configuration with LOG_LEVEL=INFO"

# Create Secrets
kubectl-ai "create secret for database credentials"

# Update environment
kubectl-ai "update DATABASE_URL environment variable for backend"
```

### Monitoring

```bash
# Check status
kubectl-ai "show me the status of all pods"
kubectl-ai "show deployment status"

# View endpoints
kubectl-ai "show service endpoints"

# Check health
kubectl-ai "check the health of phase3 deployment"
```

### Cleanup

```bash
# Delete resources
kubectl-ai "delete frontend deployment"
kubectl-ai "remove all resources in phase4 namespace"

# Rollback
kubectl-ai "rollback the backend deployment to previous version"
```

## Interactive Mode

```bash
# Start interactive session
kubectl-ai

# Example conversation:
# > deploy the todo app with 2 replicas each
# > scale backend to 5 replicas
# > show me the logs of the backend
# > why is the frontend pod failing?
# > create ingress for todo-app.local
# > exit
```

## Integration with Helm

```bash
# Deploy with Helm
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase4 --create-namespace

# Manage with kubectl-ai
kubectl-ai "scale the phase3 deployment to 3 replicas"
kubectl-ai "check the health of phase3 release"
kubectl-ai "show me the helm release status"
kubectl-ai "add monitoring for phase3 deployment"
```

## Complete Deployment Workflow

```bash
# 1. Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase4

# 2. Enable addons
minikube addons enable ingress --profile phase4
minikube addons enable metrics-server --profile phase4

# 3. Configure Docker
eval $(minikube -p phase4 docker-env)

# 4. Build images
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend

# 5. Deploy with kubectl-ai
kubectl-ai "create namespace phase4"
kubectl-ai "create secret generic phase3-secrets with POSTGRES_USER=phase3user,POSTGRES_PASSWORD=phase3password123,DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp,BETTER_AUTH_SECRET=dev_secret"
kubectl-ai "deploy postgresql:15-alpine with 5Gi storage in phase4"
kubectl-ai "deploy phase3-backend:latest with 2 replicas and DATABASE_URL from secret"
kubectl-ai "deploy phase3-frontend:latest with 2 replicas"
kubectl-ai "create services for frontend and backend"
kubectl-ai "create ingress for todo-app.local routing to frontend and backend"
kubectl-ai "enable HPA for frontend and backend"

# 6. Verify
kubectl-ai "show me all resources in phase4 namespace"
```

## Best Practices

1. **Be Specific**: Include namespace, image names, and replica counts
2. **Review Before Apply**: kubectl-ai shows generated manifests - review them
3. **Use Dry-Run**: For complex operations, ask to see the manifest first
4. **Combine with kubectl**: Use kubectl for fine-tuning after AI deployment
5. **Security First**: Always verify security contexts and RBAC

## Common Patterns

### Pattern 1: Deploy Application

```bash
kubectl-ai "deploy <image> with <replicas> replicas in <namespace>"
```

### Pattern 2: Scale Application

```bash
kubectl-ai "scale <deployment> to <replicas> replicas"
```

### Pattern 3: Troubleshoot

```bash
kubectl-ai "why is <pod/deployment> failing?"
```

### Pattern 4: Resource Management

```bash
kubectl-ai "set resources <cpu>/<memory> for <deployment>"
```

## Troubleshooting kubectl-ai

### Issue: Command not found

```bash
# Verify installation
where kubectl-ai

# Ensure kubectl is in PATH
where kubectl
```

### Issue: AI not responding

```bash
# Check OpenAI API key (if required)
kubectl-ai --help

# Verify connectivity
kubectl-ai "ping"
```

### Issue: Generated manifest errors

```bash
# Ask for fix
kubectl-ai "fix the error in the previous manifest"

# Or use kubectl directly
kubectl apply -f <generated-manifest.yaml>
```

## Resources

- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
- [Phase 4 Deployment Guide](../KUBERNETES_DEPLOYMENT.md)

---

**Next Steps:**
1. Install kubectl-ai
2. Run `.\kubectl-ai\kubectl-ai-commands.bat` for examples
3. Try deploying with AI assistance
4. Proceed to kagent integration
