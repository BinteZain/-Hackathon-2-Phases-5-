# Docker Compose AI Integration Guide

## Overview

This guide shows how to use AI agents (Gordon, kubectl-ai) with Docker Compose for local development and testing before deploying to Kubernetes.

## Docker Compose Configuration

### Standard Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:4000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/todoapp
      - BETTER_AUTH_SECRET=dev_secret_key
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=todoapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## AI-Assisted Docker Compose Operations

### Generate Docker Compose with Gordon

```bash
# Ask Gordon to generate a compose file
docker ai "Create docker-compose.yml for Next.js frontend, FastAPI backend, and PostgreSQL"

# Optimize existing compose file
docker ai "Optimize docker-compose.yml for production"

# Add health checks
docker ai "Add health checks to all services in docker-compose.yml"

# Add networking
docker ai "Configure networking for my services"
```

### Local Development with AI

```bash
# Start services with AI assistance
docker ai "Start all services in development mode"
docker-compose up -d

# Check service health
docker ai "Check health of all services"
docker-compose ps

# View logs
docker ai "Show me logs for backend service"
docker-compose logs -f backend

# Troubleshoot issues
docker ai "Why is backend not connecting to database?"
```

## Docker Compose Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start with build
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

### Scale Services

```bash
# Scale backend
docker-compose up -d --scale backend=3

# Scale frontend
docker-compose up -d --scale frontend=2
```

### Health Checks

```bash
# Check service status
docker-compose ps

# Check specific service
docker-compose ps backend

# Run health check
docker-compose exec backend curl http://localhost:4000/health
```

## AI-Assisted Troubleshooting

### Common Issues

#### Database Connection

```bash
# Ask Gordon
docker ai "Backend can't connect to PostgreSQL. Connection string: postgresql://user:password@db:5432/todoapp"

# Check network
docker-compose exec backend ping db

# Check database is ready
docker-compose exec db pg_isready
```

#### Port Conflicts

```bash
# Ask Gordon
docker ai "Port 3000 is already in use. How do I fix this?"

# Change ports in docker-compose.yml
# frontend: "3001:3000" instead of "3000:3000"
```

#### Build Failures

```bash
# Ask Gordon
docker ai "Docker build failed with error: [paste error]"

# Rebuild without cache
docker-compose build --no-cache
```

## From Docker Compose to Kubernetes

### Migration Path

```bash
# 1. Test locally with Docker Compose
docker-compose up -d

# 2. Verify functionality
docker-compose ps
curl http://localhost:3000

# 3. Use AI to generate Kubernetes manifests
kubectl-ai "Generate Kubernetes manifests from docker-compose.yml"

# 4. Or use Helm chart
helm install phase3 ./helm-charts/phase3-todo-chatbot -n phase4 --create-namespace
```

### Kompose Tool

```bash
# Install kompose
choco install kompose

# Convert docker-compose.yml to Kubernetes manifests
kompose convert

# Review generated manifests
ls -la *.yaml

# Apply to Kubernetes
kubectl apply -f . -n phase4
```

## Environment Variables Management

### Using .env File

```bash
# Create .env file
cat > .env << EOF
POSTGRES_USER=phase3user
POSTGRES_PASSWORD=phase3password123
POSTGRES_DB=todoapp
DATABASE_URL=postgresql://phase3user:phase3password123@db:5432/todoapp
BETTER_AUTH_SECRET=dev_secret_key_for_local
EOF

# Start with environment
docker-compose up -d

# AI assistance for environment
docker ai "What environment variables do I need for production?"
```

## Security Best Practices

### Secrets Management

```bash
# Don't hardcode secrets in docker-compose.yml
# Use Docker secrets or .env file

# Ask Gordon for security recommendations
docker ai "How do I manage secrets securely in Docker Compose?"

# Use environment files
docker-compose --env-file .env.production up -d
```

### Network Isolation

```yaml
# Add to docker-compose.yml
networks:
  frontend:
  backend:
  database:

services:
  frontend:
    networks:
      - frontend
      - backend
  
  backend:
    networks:
      - backend
      - database
  
  db:
    networks:
      - database
```

## Monitoring and Logging

### Centralized Logging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Export logs
docker-compose logs backend > backend.log

# AI analysis
docker ai "Analyze these logs for errors: [paste logs]"
```

### Resource Monitoring

```bash
# Check resource usage
docker stats

# Check specific container
docker stats phase3-backend-1

# AI recommendations
docker ai "How do I optimize resource usage?"
```

## CI/CD Integration

### GitHub Actions with Docker Compose

```yaml
name: Docker Compose CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: sleep 30
      
      - name: Run tests
        run: |
          docker-compose exec -T backend pytest
          docker-compose exec -T frontend npm test
      
      - name: Check health
        run: |
          curl http://localhost:3000
          curl http://localhost:4000/health
      
      - name: Stop services
        run: docker-compose down
```

## Quick Reference

| Task | Command |
|------|---------|
| Start services | `docker-compose up -d` |
| Stop services | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Scale service | `docker-compose up -d --scale backend=3` |
| Rebuild | `docker-compose build` |
| Restart | `docker-compose restart` |
| Check status | `docker-compose ps` |
| Execute command | `docker-compose exec backend bash` |

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gordon Docker AI](./gordon/README.md)
- [Phase 4 Deployment](./PHASE4_AI_WORKFLOWS.md)

---

**Next Steps:**
1. Test locally with Docker Compose
2. Use AI for troubleshooting
3. Deploy to Kubernetes when ready
