# Phase 3 Todo Chatbot - Kubernetes Quick Reference

## 🚀 Quick Deploy

### Windows
```powershell
.\deploy-minikube.bat
```

### Linux/Mac
```bash
chmod +x deploy-minikube.sh && ./deploy-minikube.sh
```

---

## 📦 Components

| Component | Image | Replicas | Port | Resources |
|-----------|-------|----------|------|-----------|
| Frontend | `phase3-frontend:latest` | 2 | 3000 | 128Mi-512Mi / 100m-500m |
| Backend | `phase3-backend:latest` | 2 | 4000 | 256Mi-1Gi / 200m-1000m |
| PostgreSQL | `postgres:15-alpine` | 1 | 5432 | 256Mi-2Gi / 250m-2000m |

---

## 🔧 Essential Commands

### Start
```bash
# Start Minikube
minikube start --memory=6144 --cpus=4 --disk-size=20g --profile phase3

# Enable addons
minikube addons enable ingress --profile phase3
minikube addons enable metrics-server --profile phase3
```

### Build Images
```bash
eval $(minikube -p phase3 docker-env)
docker build -t phase3-frontend:latest ./frontend
docker build -t phase3-backend:latest ./backend
```

### Deploy
```bash
# Using Helm
helm install phase3 ./helm-charts/phase3-todo-chatbot \
  -f helm-charts/phase3-todo-chatbot/values-minikube.yaml \
  -n phase3 --create-namespace

# Using Kustomize
kubectl apply -k k8s/local/
```

### Access
```bash
# Open in browser
minikube service frontend-service -n phase3 --profile phase3

# Or port-forward
kubectl port-forward svc/frontend-service 3000:80 -n phase3
```

### Monitor
```bash
# Status
kubectl get all -n phase3

# Logs
kubectl logs -f deployment/frontend -n phase3
kubectl logs -f deployment/backend -n phase3

# Top resources
kubectl top pods -n phase3
```

### Scale
```bash
kubectl scale deployment/frontend --replicas=3 -n phase3
kubectl scale deployment/backend --replicas=5 -n phase3
```

### Database
```bash
# Connect
kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase3 -- psql -U phase3user todoapp

# Backup
kubectl exec -it postgres-phase3-todo-chatbot-0 -n phase3 -- pg_dump -U phase3user todoapp > backup.sql
```

### Uninstall
```bash
helm uninstall phase3 -n phase3
kubectl delete namespace phase3
minikube stop -p phase3
```

---

## 🌐 Access URLs

| Method | URL |
|--------|-----|
| Minikube Service | `minikube service frontend-service -n phase3` |
| Port Forward | http://localhost:3000 |
| Ingress | http://todo-app.local (add to hosts) |

---

## 🔐 Default Credentials

| User | Password |
|------|----------|
| admin@example.com | admin123 |
| user1@example.com | user123 |
| user2@example.com | user123 |

---

## 📊 Health Endpoints

| Component | Endpoint |
|-----------|----------|
| Frontend | `GET /` |
| Backend | `GET /health` |
| Database | `pg_isready` |

---

## ⚙️ Environment Variables

### Frontend
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://backend-service:8080/api/v1
NEXT_PUBLIC_BETTER_AUTH_SECRET=<from-secret>
```

### Backend
```bash
DATABASE_URL=postgresql://phase3user:phase3password123@postgres-service:5432/todoapp
BETTER_AUTH_SECRET=<from-secret>
OPENAI_API_KEY=<from-secret>
```

---

## 🐛 Troubleshooting

```bash
# Pod issues
kubectl describe pod <pod-name> -n phase3

# Events
kubectl get events -n phase3 --sort-by='.lastTimestamp'

# Restart deployment
kubectl rollout restart deployment/frontend -n phase3

# Check HPA
kubectl get hpa -n phase3
kubectl describe hpa frontend-hpa -n phase3

# Test ingress
curl -H "Host: todo-app.local" http://$(minikube ip -p phase3)/
```

---

## 📁 File Locations

```
helm-charts/phase3-todo-chatbot/  # Helm chart
k8s/local/                        # K8s manifests
deploy-minikube.bat               # Windows deploy script
deploy-minikube.sh                # Linux/Mac deploy script
KUBERNETES_DEPLOYMENT.md          # Full deployment guide
specs/infrastructure/             # Infrastructure specs
```

---

## 🎯 Acceptance Criteria

- [ ] Frontend accessible at port 3000
- [ ] Backend API accessible at `/api/v1`
- [ ] PostgreSQL persistent across restarts
- [ ] HPA configured and functional
- [ ] Network policies enforced
- [ ] All pods healthy (readiness probes passing)
- [ ] Resource limits enforced

---

## 📞 Support

- **Spec:** [specs/infrastructure/K8S_INFRASTRUCTURE_SPEC.md](specs/infrastructure/K8S_INFRASTRUCTURE_SPEC.md)
- **Guide:** [KUBERNETES_DEPLOYMENT.md](KUBERNETES_DEPLOYMENT.md)
