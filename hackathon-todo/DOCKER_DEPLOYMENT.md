# Docker Deployment Guide

**Version:** 1.0.0  
**Date:** 2026-02-21  
**Project:** Phase III Todo Chatbot

---

## Quick Start

### Local Development with Docker Compose

```bash
# Navigate to project root
cd hackathon-todo

# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop all services
docker-compose down
```

### Access Points

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:3001 | 3001 |
| Backend Health | http://localhost:3001/health | 3001 |

---

## Dockerfiles

### Backend Dockerfile

**Location:** `hackathon-todo/backend/Dockerfile`

**Features:**
- ✅ Multi-stage build (3 stages)
- ✅ Non-root user (UID 1001)
- ✅ Production dependencies only
- ✅ TypeScript compilation
- ✅ Health check endpoint
- ✅ Resource limits configured

**Build Process:**
1. **Dependencies Stage:** Install production npm packages
2. **Builder Stage:** Compile TypeScript to JavaScript
3. **Production Stage:** Minimal runtime image

**Image Size:** ~180MB (optimized)

### Frontend Dockerfile

**Location:** `hackathon-todo/frontend/Dockerfile`

**Features:**
- ✅ Multi-stage build (3 stages)
- ✅ Non-root user (UID 1001)
- ✅ Next.js production build
- ✅ Optimized static assets
- ✅ Health check endpoint
- ✅ Resource limits configured

**Build Process:**
1. **Dependencies Stage:** Install all npm packages
2. **Builder Stage:** Create Next.js production build
3. **Production Stage:** Minimal runtime with production deps only

**Image Size:** ~250MB (optimized)

---

## Building Individual Images

### Backend Image

```bash
cd hackathon-todo/backend

# Build image
docker build -t phase3-backend:latest .

# Test locally
docker run -p 3001:3001 phase3-backend:latest

# Verify health check
curl http://localhost:3001/health
```

### Frontend Image

```bash
cd hackathon-todo/frontend

# Build image
docker build -t phase3-frontend:latest .

# Test locally
docker run -p 3000:3000 phase3-frontend:latest

# Verify health check
curl http://localhost:3000
```

---

## Docker Compose Commands

### Start Services

```bash
# Start in detached mode
docker-compose up -d

# Start with build
docker-compose up -d --build

# Start and view logs
docker-compose up --build

# Start specific service
docker-compose up -d backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Status

```bash
# List running containers
docker-compose ps

# Detailed status
docker-compose top

# Resource usage
docker stats
```

### Execute Commands

```bash
# Execute in backend container
docker-compose exec backend sh

# Execute in frontend container
docker-compose exec frontend sh

# Run specific command
docker-compose exec backend node -v
```

---

## Health Checks

### Backend Health Check

**Endpoint:** `/health`  
**Interval:** 30s  
**Timeout:** 5s  
**Retries:** 3  
**Start Period:** 10s

```bash
# Manual check
curl http://localhost:3001/health

# Expected response
{"status":"ok","timestamp":"2026-02-21T..."}
```

### Frontend Health Check

**Endpoint:** `/`  
**Interval:** 30s  
**Timeout:** 5s  
**Retries:** 3  
**Start Period:** 10s

```bash
# Manual check
curl http://localhost:3000

# Expected: HTML content with 200 status
```

---

## Environment Variables

### Backend Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node environment |
| `PORT` | `3001` | Server port |
| `CORS_ORIGIN` | `http://localhost:3000` | CORS allowed origin |

### Frontend Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node environment |
| `PORT` | `3000` | Server port |
| `HOSTNAME` | `0.0.0.0` | Bind address |
| `NEXT_PUBLIC_API_URL` | `http://backend:3001` | Backend API URL |

---

## Resource Limits

### Backend Resources

```yaml
limits:
  cpus: '0.5'
  memory: 256M
reservations:
  cpus: '0.1'
  memory: 64M
```

### Frontend Resources

```yaml
limits:
  cpus: '1.0'
  memory: 512M
reservations:
  cpus: '0.25'
  memory: 128M
```

---

## Network Configuration

**Network Name:** `phase3-network`  
**Driver:** `bridge`

### Service Discovery

Services can communicate using service names:

```
frontend → http://backend:3001
backend → http://frontend:3000
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Inspect container
docker inspect phase3-backend

# Check resource usage
docker stats
```

### Health Check Failing

```bash
# Test health endpoint manually
curl http://localhost:3001/health

# Check if port is in use
netstat -ano | findstr :3001

# Restart container
docker-compose restart backend
```

### Build Errors

```bash
# Clean build cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend

# Remove old images
docker rmi phase3-backend:latest
```

### Network Issues

```bash
# Inspect network
docker network inspect phase3-network

# Restart network
docker-compose down
docker-compose up -d

# Test connectivity
docker-compose exec backend ping frontend
```

---

## Production Considerations

### Image Optimization

- ✅ Multi-stage builds reduce image size by ~60%
- ✅ Alpine base images minimize attack surface
- ✅ Production dependencies only
- ✅ Non-root user for security

### Security Best Practices

- ✅ Non-root user (UID 1001)
- ✅ Read-only filesystem where possible
- ✅ No secrets in images
- ✅ Minimal base images (Alpine)

### Scaling

For Kubernetes deployment, see:
- `specs/infrastructure/phase4-deployment.md`
- `helm-charts/phase3-todo-chatbot/`

---

## Validation Checklist

- [ ] Backend image builds successfully
- [ ] Frontend image builds successfully
- [ ] Both images pass health checks
- [ ] Docker Compose starts all services
- [ ] Frontend can access backend API
- [ ] All endpoints respond correctly
- [ ] Resource limits are enforced
- [ ] Containers restart on failure
- [ ] Logs are accessible
- [ ] Images are under size targets

---

## Next Steps

1. **Local Testing:** Run `docker-compose up -d` and verify all services
2. **Image Tagging:** Tag images for registry: `docker tag phase3-backend:latest user/phase3-backend:v1.0.0`
3. **Registry Push:** Push to container registry: `docker push user/phase3-backend:v1.0.0`
4. **Kubernetes Deploy:** Use Helm chart for K8s deployment

---

**Document Status:** Complete  
**PHR Location:** `history/prompts/infrastructure/`
