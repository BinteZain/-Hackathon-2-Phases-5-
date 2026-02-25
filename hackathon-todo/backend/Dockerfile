# =============================================================================
# Phase III Todo Chatbot - Backend Dockerfile (Production-Optimized)
# =============================================================================
# Multi-stage build for minimal image size
# Security: Non-root user, minimal attack surface
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install production dependencies only
# -----------------------------------------------------------------------------
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install only production dependencies
RUN npm install --omit=dev && \
    npm cache clean --force

# -----------------------------------------------------------------------------
# Stage 2: Builder - Compile TypeScript to JavaScript
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install all dependencies (including devDependencies for build)
COPY package.json package-lock.json ./
RUN npm ci

# Copy TypeScript config
COPY tsconfig.json ./

# Copy source code
COPY src/ ./src/

# Build TypeScript to JavaScript
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM node:20-alpine AS production

# Set production environment
ENV NODE_ENV=production

WORKDIR /app

# Create non-root user and group for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Install production dependencies from dependencies stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Change ownership to non-root user
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Expose application port
EXPOSE 3001

# Health check - verify the application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Start the server
CMD ["node", "dist/server.js"]
