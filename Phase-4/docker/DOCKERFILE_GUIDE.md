# Production Dockerfiles - Todo Chatbot

**Location:** `Phase-4/backend/Dockerfile`, `Phase-4/frontend/Dockerfile`

---

## Backend Dockerfile (FastAPI/Express)

### Build Strategy: 3-Stage Multi-Stage Build

```dockerfile
# Stage 1: Dependencies (Production only)
FROM node:20-alpine AS dependencies
- Install production dependencies only (--omit=dev)
- Cache node_modules layer
- Clean npm cache

# Stage 2: Builder (TypeScript compilation)
FROM node:20-alpine AS builder
- Install all dependencies (including devDependencies)
- Copy TypeScript config
- Copy source code
- Compile TypeScript to JavaScript

# Stage 3: Production (Minimal runtime)
FROM node:20-alpine AS production
- Create non-root user (UID 1001)
- Copy production dependencies from Stage 1
- Copy compiled code from Stage 2
- Set ownership
- Configure health check
- Start server
```

### Specifications

| Property | Value |
|----------|-------|
| **Base Image** | `node:20-alpine` |
| **Final Size** | ~200MB |
| **User** | `nodejs` (UID 1001) |
| **Port** | 3001 |
| **Health Check** | HTTP GET /health every 30s |
| **Timeout** | 5s |
| **Retries** | 3 |
| **Start Period** | 10s |

### Build & Test

```bash
# Build image
cd Phase-4/backend
docker build -t phase3-backend:latest .

# Check image size
docker images phase3-backend

# Test locally
docker run -p 3001:3001 phase3-backend:latest

# Verify health check
curl http://localhost:3001/health
```

### Optimizations Applied

1. **Multi-stage build** - Separates build and runtime dependencies
2. **Alpine base** - Minimal attack surface, small size
3. **Production dependencies only** - Excludes devDependencies in final image
4. **Layer caching** - package.json copied before source code
5. **Non-root user** - Security best practice
6. **npm cache clean** - Reduces image size
7. **Health check** - Kubernetes-ready

---

## Frontend Dockerfile (Next.js)

### Build Strategy: 3-Stage Multi-Stage Build

```dockerfile
# Stage 1: Dependencies (All packages for build)
FROM node:20-alpine AS dependencies
- Install all dependencies (including devDependencies)
- Cache node_modules layer
- Clean npm cache

# Stage 2: Builder (Next.js production build)
FROM node:20-alpine AS builder
- Copy dependencies from Stage 1
- Copy source code and config
- Build Next.js production bundle (.next directory)

# Stage 3: Runner (Minimal production runtime)
FROM node:20-alpine AS production
- Create non-root user (UID 1001)
- Install production dependencies only
- Copy built assets from Stage 2
- Set ownership
- Configure health check
- Start production server
```

### Specifications

| Property | Value |
|----------|-------|
| **Base Image** | `node:20-alpine` |
| **Final Size** | ~250MB |
| **User** | `nextjs` (UID 1001) |
| **Port** | 3000 |
| **Health Check** | HTTP GET / every 30s |
| **Timeout** | 5s |
| **Retries** | 3 |
| **Start Period** | 10s |
| **Environment** | NODE_ENV=production |

### Build & Test

```bash
# Build image
cd Phase-4/frontend
docker build -t phase3-frontend:latest .

# Check image size
docker images phase3-frontend

# Test locally
docker run -p 3000:3000 phase3-frontend:latest

# Verify health check
curl http://localhost:3000
```

### Optimizations Applied

1. **Multi-stage build** - Build artifacts only, no build tools in final image
2. **Alpine base** - Minimal size and attack surface
3. **Production dependencies only** - Smaller runtime image
4. **Layer caching** - Dependencies cached separately
5. **Non-root user** - Security hardening
6. **Public folder** - Static assets included
7. **Health check** - Production-ready
8. **Next.js production build** - Optimized bundle

---

## Image Size Comparison

| Stage | Backend | Frontend |
|-------|---------|----------|
| **Base (node:20-alpine)** | ~180MB | ~180MB |
| **After dependencies** | ~200MB | ~220MB |
| **After builder** | ~250MB | ~350MB |
| **Final production** | **~200MB** | **~250MB** |

**Savings vs Single-Stage:** ~60% reduction

---

## Security Features

| Feature | Implementation |
|---------|----------------|
| **Non-root user** | UID 1001 (nodejs/nextjs) |
| **Minimal base** | Alpine Linux |
| **Production deps only** | --omit=dev flag |
| **No build tools** | Multi-stage isolation |
| **Health checks** | HTTP endpoint monitoring |
| **Read-only where possible** | Static assets only |
| **No secrets** | Environment variables only |

---

## Kubernetes Integration

### Deployment Snippet

```yaml
containers:
  - name: backend
    image: phase3-backend:latest
    ports:
      - containerPort: 3001
    healthCheck:
      httpGet:
        path: /health
        port: 3001
      initialDelaySeconds: 10
      periodSeconds: 30
      timeoutSeconds: 5
      retries: 3
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 1Gi
    securityContext:
      runAsNonRoot: true
      runAsUser: 1001
      allowPrivilegeEscalation: false
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build backend image
        run: |
          cd Phase-4/backend
          docker build -t phase3-backend:${{ github.sha }} .
      
      - name: Build frontend image
        run: |
          cd Phase-4/frontend
          docker build -t phase3-frontend:${{ github.sha }} .
      
      - name: Test images
        run: |
          docker run -d --name backend-test phase3-backend:${{ github.sha }}
          docker run -d --name frontend-test phase3-frontend:${{ github.sha }}
          sleep 15
          curl http://localhost:3001/health
          curl http://localhost:3000
      
      - name: Push to registry
        run: |
          # Push to your container registry
          docker push phase3-backend:${{ github.sha }}
          docker push phase3-frontend:${{ github.sha }}
```

---

## Troubleshooting

### Build Issues

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker build --no-cache -t phase3-backend:latest .

# Check build logs
docker build -t phase3-backend:latest . 2>&1 | tee build.log
```

### Runtime Issues

```bash
# View container logs
docker logs <container-id>

# Exec into container
docker exec -it <container-id> sh

# Check health manually
docker exec <container-id> wget -qO- http://localhost:3001/health
```

### Size Issues

```bash
# Analyze image layers
docker history phase3-backend:latest

# Check layer sizes
docker inspect phase3-backend:latest | grep Size
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-21  
**Compatible:** Docker 20+, Kubernetes 1.25+
