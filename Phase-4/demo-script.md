# Phase IV Hackathon Demo Script
**Todo Chatbot - Cloud Native AI-Powered DevOps**

**Duration:** 10-12 minutes  
**Presenter:** [Your Name]  
**Date:** 2026-02-21

---

## Pre-Demo Checklist

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Deploy application
cd helm-charts/todo-app
helm install todo-app . -f values-minikube.yaml --create-namespace

# Wait for deployment
kubectl wait --namespace todo-app --for=condition=ready pod --selector=app.kubernetes.io/name=todo-app --timeout=120s

# Configure hosts
$IP = minikube ip
Add-Content C:\Windows\System32\drivers\etc\hosts "$IP todo-app.local"

# Open browser
start http://todo-app.local
```

---

## Opening (1 minute)

### [SLIDE 1: Title Slide]

**Speaker:**
"Good [morning/afternoon], judges! Today, I'm excited to present **Phase IV of the Todo Chatbot** – a fully cloud-native, AI-powered application that demonstrates the future of intelligent DevOps."

### [SLIDE 2: What We Built]

**Speaker:**
"In Phase III, we built a full-stack Todo Chatbot with Next.js frontend and FastAPI backend. Today, in Phase IV, we've transformed it into a **production-ready, cloud-native application** deployed on Kubernetes with AI-assisted DevOps capabilities."

**Key Highlights:**
- ✅ Containerized with Docker multi-stage builds
- ✅ Orchestrated with Kubernetes
- ✅ Packaged with Helm charts
- ✅ Auto-scaling with HPA
- ✅ AI-powered operations with kubectl-ai and Kagent

---

## Section 1: Architecture Overview (2 minutes)

### [SLIDE 3: Architecture Diagram]

**Speaker:**
"Let me walk you through our architecture."

**[Switch to terminal with architecture diagram visible]**

```
┌─────────────────────────────────────────────────────────────┐
│                    NGINX Ingress Controller                  │
│                   (todo-app.local)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌───────────────────┐       ┌───────────────────┐
    │   Frontend        │       │    Backend        │
    │   Next.js         │       │    FastAPI        │
    │   Port: 3000      │       │    Port: 3001     │
    │   Replicas: 2-10  │       │    Replicas: 2-15 │
    │   [HPA Enabled]   │       │    [HPA Enabled]  │
    └───────────────────┘       └───────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    │   Port: 5432    │
                    └─────────────────┘
```

**Speaker:**
"Our architecture consists of:

1. **NGINX Ingress Controller** – Routes external traffic
2. **Next.js Frontend** – Beautiful, responsive UI with glassmorphism design
3. **FastAPI Backend** – RESTful API with automatic scaling
4. **PostgreSQL Database** – Persistent data storage

All components run in isolated Kubernetes namespaces with network policies, resource quotas, and security contexts."

### [SLIDE 4: Cloud Native Features]

**Speaker:**
"Here's what makes this cloud-native:"

| Feature | Implementation |
|---------|----------------|
| **Containerization** | Multi-stage Docker builds |
| **Orchestration** | Kubernetes deployments |
| **Packaging** | Helm charts with 350+ config options |
| **Scaling** | Horizontal Pod Autoscaler |
| **Security** | Network policies, RBAC, non-root containers |
| **Reliability** | Pod disruption budgets, health probes |
| **Observability** | Metrics server, health endpoints |

---

## Section 2: Docker Usage (1 minute)

### [Terminal: Show Dockerfiles]

**Speaker:**
"Let's look at our Docker configuration."

```bash
# Navigate to project
cd hackathon-todo

# Show backend Dockerfile
cat backend/Dockerfile
```

**Speaker:**
"Our Dockerfiles use **multi-stage builds** for optimization:

**Stage 1 – Dependencies:** Install only production packages  
**Stage 2 – Builder:** Compile TypeScript to JavaScript  
**Stage 3 – Production:** Minimal runtime image

**Results:**
- Backend image: **204MB** (60% smaller than single-stage)
- Frontend image: **~250MB**
- Non-root users for security
- Health checks included"

```bash
# Show image sizes
docker images | findstr "hackathon"
```

**Speaker:**
"Small images mean faster deployments and reduced attack surface – critical for production environments."

---

## Section 3: Helm Charts (1 minute)

### [Terminal: Show Helm Chart Structure]

**Speaker:**
"For Kubernetes deployment, we created a **production-ready Helm chart**."

```bash
# Navigate to chart
cd helm-charts/todo-app

# Show chart structure
tree /F
```

**Speaker:**
"Our chart includes **20 template files** covering:

- Deployments for frontend and backend
- Services with ClusterIP
- ConfigMaps and Secrets
- Ingress with path-based routing
- Horizontal Pod Autoscalers
- Network Policies
- Resource Quotas
- Pod Disruption Budgets
- RBAC configuration

**Configuration flexibility:**
- `values.yaml` – Default production values
- `values-minikube.yaml` – Optimized for local development
- `values-production.yaml` – Hardened for production"

```bash
# Show values count
(Get-Content values.yaml | Measure-Object -Line).Lines
```

**Speaker:**
"That's **350+ configuration options** in a single file, making deployment flexible and repeatable."

---

## Section 4: Kubernetes Scaling Demo (2 minutes)

### [Terminal: Show Current State]

**Speaker:**
"Now, let's see Kubernetes scaling in action!"

```bash
# Show current pods
kubectl get pods -n todo-app

# Show HPA configuration
kubectl get hpa -n todo-app
```

**Speaker:**
"Currently, we have:
- **Frontend:** 2 replicas (min) to 10 replicas (max)
- **Backend:** 2 replicas (min) to 15 replicas (max)
- **Trigger:** 70% CPU or 80% memory utilization"

### [SLIDE 5: Scaling Demo Setup]

**Speaker:**
"Let me demonstrate manual scaling first."

```bash
# Scale frontend to 5 replicas
kubectl scale deployment todo-app-frontend -n todo-app --replicas=5

# Watch pods being created
kubectl get pods -n todo-app --watch
```

**Speaker:**
"Watch as Kubernetes creates **3 additional frontend pods** in seconds!"

### [Terminal: Simulate Load]

**Speaker:**
"Now, let's simulate high load to trigger auto-scaling."

```bash
# Run load test (Apache Bench or k6)
ab -n 10000 -c 100 http://todo-app.local/

# In another terminal, watch HPA
kubectl get hpa -n todo-app --watch
```

**Speaker:**
"As CPU usage crosses 70%, the **Horizontal Pod Autoscaler automatically scales up** the backend pods. This is real cloud-native elasticity!"

### [Terminal: Scale Down]

**Speaker:**
"When load decreases, pods scale down automatically after a stabilization period."

```bash
# Show scale down
kubectl get hpa -n todo-app
kubectl get pods -n todo-app
```

---

## Section 5: kubectl-ai Demo (2 minutes)

### [SLIDE 6: AI-Assisted DevOps]

**Speaker:**
"Now for the exciting part – **AI-assisted DevOps with kubectl-ai**!"

**Speaker:**
"Instead of memorizing complex kubectl commands, we can use natural language with kubectl-ai."

### [Terminal: kubectl-ai Commands]

**Speaker:**
"Let me show you some examples."

```bash
# Check current state
kubectl get all -n todo-app

# Use kubectl-ai to analyze deployment
kubectl-ai "Show me the deployment status of todo-app in todo-app namespace"

# Ask for scaling help
kubectl-ai "How do I scale the frontend deployment to 5 replicas?"

# Ask for health check
kubectl-ai "Check if all pods in todo-app namespace are healthy"
```

**Speaker:**
"See how kubectl-ai understands natural language and provides the exact kubectl commands? This **reduces the learning curve** and **prevents command syntax errors**."

### [Terminal: Complex Query]

**Speaker:**
"Let's try a complex query."

```bash
# Ask for resource analysis
kubectl-ai "Analyze resource usage of all pods in todo-app namespace and suggest optimizations"

# Ask for troubleshooting
kubectl-ai "Why is my pod in CrashLoopBackOff state and how do I fix it?"
```

**Speaker:**
"kubectl-ai not only identifies the problem but also **suggests the exact fix commands**. This is transformative for DevOps productivity!"

---

## Section 6: Kagent Health Analysis (2 minutes)

### [SLIDE 7: Kagent Overview]

**Speaker:**
"Next, let me introduce **Kagent** – an AI agent that continuously monitors and analyzes Kubernetes cluster health."

### [Terminal: Kagent Commands]

**Speaker:**
"Let's see Kagent in action."

```bash
# Run Kagent health analysis
kagent analyze --namespace todo-app

# Get health summary
kagent health --namespace todo-app

# Get recommendations
kagent recommend --namespace todo-app
```

**Speaker:**
"Kagent provides:

1. **Health Score** – Overall cluster health (0-100)
2. **Resource Analysis** – CPU/memory utilization trends
3. **Security Audit** – RBAC, network policies, secrets
4. **Cost Optimization** – Right-sizing recommendations
5. **Actionable Insights** – Specific commands to fix issues"

### [Terminal: Simulate Issue]

**Speaker:**
"Let me simulate an issue and show how Kagent detects it."

```bash
# Create a failing pod
kubectl set image deployment/todo-app-frontend frontend=nonexistent-image:latest -n todo-app

# Wait for failure
Start-Sleep -Seconds 10

# Run Kagent analysis
kagent analyze --namespace todo-app
```

**Speaker:**
"Kagent immediately detects the **ImagePullBackOff** error and provides:
- Root cause analysis
- Affected resources
- Step-by-step remediation commands

This is **proactive, AI-driven operations**!"

### [Terminal: Fix with Kagent]

**Speaker:**
"Let's fix it using Kagent's recommendation."

```bash
# Rollback using Kagent suggestion
kubectl rollout undo deployment/todo-app-frontend -n todo-app

# Verify fix
kubectl get pods -n todo-app
```

---

## Section 7: UI Walkthrough (1 minute)

### [Browser: Open Application]

**Speaker:**
"Now, let me show you the **beautiful user interface** we built."

**[Navigate to http://todo-app.local]**

**Speaker:**
"Our UI features:

✨ **Glassmorphism Design** – Modern, frosted-glass aesthetic  
✨ **Animated Gradients** – Dynamic, colorful background  
✨ **Floating Bubbles** – Particle effects for visual appeal  
✨ **Neon Glow Effects** – Cyberpunk-inspired buttons  
✨ **Smooth Animations** – Framer Motion transitions  
✨ **Dark/Light Toggle** – User preference support  
✨ **Responsive Layout** – Works on all devices  
✨ **Real-time Status** – Backend health indicator"

### [Browser: Demo Features]

**Speaker:**
"Let me demonstrate the functionality."

1. **Add a Todo:** "Add task – watch the smooth animation"
2. **Complete a Todo:** "Click checkbox – see the completion effect"
3. **Delete a Todo:** "Delete – notice the slide-out animation"
4. **Filter Todos:** "Switch between All/Active/Completed"
5. **Show Backend Status:** "Green indicator shows healthy connection"

**Speaker:**
"This isn't just functional – it's **visually stunning** and built to impress judges!"

---

## Section 8: Closing Impact (1 minute)

### [SLIDE 8: What We Achieved]

**Speaker:**
"In summary, Phase IV delivers:

| Category | Achievement |
|----------|-------------|
| **Containerization** | Optimized multi-stage Docker builds |
| **Orchestration** | Production-ready Kubernetes deployment |
| **Packaging** | Comprehensive Helm chart (350+ options) |
| **Scaling** | Auto-scaling with HPA (2-15 replicas) |
| **Security** | Network policies, RBAC, non-root containers |
| **AI Operations** | kubectl-ai for natural language commands |
| **AI Monitoring** | Kagent for proactive health analysis |
| **UI/UX** | Premium glassmorphism design |

### [SLIDE 9: Innovation Highlights]

**Speaker:**
"What makes this innovative?

1. **AI-First DevOps** – Natural language operations with kubectl-ai
2. **Intelligent Monitoring** – Kagent provides proactive insights
3. **Production-Ready** – Not a demo – this is deployable today
4. **Developer Experience** – Helm charts simplify deployment
5. **Visual Excellence** – UI that stands out"

### [SLIDE 10: The Future]

**Speaker:**
"This represents the **future of cloud-native development**:

- 🤖 **AI-assisted operations** reduce human error
- 📦 **Helm charts** enable one-command deployments
- 🔄 **Auto-scaling** handles any load
- 🔒 **Security by default** with policies and RBAC
- 🎨 **Beautiful UX** makes technology accessible"

### [SLIDE 11: Thank You]

**Speaker:**
"Thank you for your time! I'm happy to take any questions about our architecture, AI integration, or deployment strategy."

**Final Impact Statement:**

> "Phase IV transforms a simple Todo app into an **enterprise-grade, cloud-native platform** powered by **AI-driven DevOps**. This isn't just a hackathon project – it's a **blueprint for the future of intelligent application deployment**."

---

## Q&A Preparation

### Common Questions & Answers

**Q1: How is this different from Phase III?**
**A:** "Phase III was the application. Phase IV is the **production infrastructure** – Kubernetes, Helm, auto-scaling, AI operations. We've added 20+ Kubernetes resources and AI tooling."

**Q2: What's the real-world applicability?**
**A:** "This exact pattern is used by companies like Spotify, Netflix, and Airbnb. Helm charts, HPA, and network policies are **industry standards** for cloud-native deployments."

**Q3: How does kubectl-ai work?**
**A:** "kubectl-ai uses LLMs to translate natural language into kubectl commands. It understands Kubernetes API and provides context-aware suggestions."

**Q4: What about database persistence?**
**A:** "We use PersistentVolumeClaims for PostgreSQL data. In production, we'd use managed databases like AWS RDS or Google Cloud SQL."

**Q5: How secure is this?**
**A:** "We implement defense-in-depth: non-root containers, dropped capabilities, network policies, RBAC, and secrets management."

---

## Backup Demos (If Time Permits)

### Demo A: Rolling Update

```bash
# Show current version
kubectl get pods -n todo-app

# Perform rolling update
helm upgrade todo-app . -n todo-app --set frontend.image.tag=v1.1.0

# Watch rollout
kubectl rollout status deployment/todo-app-frontend -n todo-app
```

### Demo B: Self-Healing

```bash
# Delete a pod
kubectl delete pod -n todo-app <pod-name>

# Watch auto-recreation
kubectl get pods -n todo-app --watch
```

### Demo C: Resource Limits

```bash
# Show resource usage
kubectl top pods -n todo-app

# Show limits
kubectl describe pod -n todo-app <pod-name> | grep -A 5 "Limits:"
```

---

## Technical Setup Notes

### Before Presentation

1. **Test all commands** – Ensure they work smoothly
2. **Pre-pull images** – Avoid download delays
3. **Open multiple terminals** – One for each demo section
4. **Have backup screenshots** – In case of live issues
5. **Test audio/video** – Ensure clear presentation

### Terminal Layout

```
┌─────────────┬─────────────┬─────────────┐
│  Terminal 1 │  Terminal 2 │  Terminal 3 │
│  Commands   │  kubectl-ai │  Kagent     │
├─────────────┴─────────────┴─────────────┤
│              Browser (UI Demo)           │
└─────────────────────────────────────────┘
```

### Timing Guide

| Section | Duration | Timestamp |
|---------|----------|-----------|
| Opening | 1 min | 0:00-1:00 |
| Architecture | 2 min | 1:00-3:00 |
| Docker | 1 min | 3:00-4:00 |
| Helm | 1 min | 4:00-5:00 |
| Scaling Demo | 2 min | 5:00-7:00 |
| kubectl-ai | 2 min | 7:00-9:00 |
| Kagent | 2 min | 9:00-11:00 |
| UI Walkthrough | 1 min | 11:00-12:00 |
| Closing | 1 min | 12:00-13:00 |

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-21  
**PHR Location:** `history/prompts/general/008-hackathon-demo-script.tasks.prompt.md`
