# =============================================================================
# Phase III Todo Chatbot - Frontend Dockerfile (Production-Optimized)
# =============================================================================
# Multi-stage build for minimal image size
# Security: Non-root user, minimal attack surface
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Dependencies - Install all dependencies for build
# -----------------------------------------------------------------------------
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci && \
    npm cache clean --force

# -----------------------------------------------------------------------------
# Stage 2: Builder - Build Next.js application
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies and package files from previous stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=dependencies /app/package.json ./

# Copy source code and config
COPY . .

# Set environment for build
ENV NODE_ENV=production

# Build Next.js application (creates optimized production bundle in .next)
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Runner - Minimal production runtime
# -----------------------------------------------------------------------------
FROM node:20-alpine AS production

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

WORKDIR /app

# Create non-root user and group for security
RUN addgroup -S nodejs || true && \
    adduser -S nextjs -G nodejs || true

# Copy package files from builder (includes package.json with all deps listed)
COPY --from=builder /app/package.json ./

# Install only production dependencies
# Using npm install instead of ci since we don't have lock file in production stage
RUN npm install --omit=dev && \
    npm cache clean --force

# Copy built Next.js application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./

# Change ownership to non-root user
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose application port
EXPOSE 3000

# Health check - verify the application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Start Next.js production server
CMD ["npm", "start"]
