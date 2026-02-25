# =============================================================================
# Phase 3 Todo Chatbot - Frontend Dockerfile (Production-Ready)
# =============================================================================
# Multi-stage build for minimal image size and security
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies and build Next.js app
# -----------------------------------------------------------------------------
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install all dependencies (including devDependencies for build)
RUN npm ci

# Copy application source code
COPY . .

# Build the Next.js application for production
# This creates optimized static files in .next directory
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM node:18-alpine AS runtime

WORKDIR /app

# Create non-root user for security (UID 1000)
RUN addgroup -S nodejs && \
    adduser -S nextjs -G nodejs

# Copy only production dependencies from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Copy built Next.js application from builder stage
# .next directory contains the production build
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Set environment to production
ENV NODE_ENV=production

# Set Next.js specific environment variables
ENV PORT=3000 \
    HOSTNAME=0.0.0.0

# Switch to non-root user
USER nextjs

# Expose the application port
EXPOSE 3000

# Health check - verify the application is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the Next.js production server
CMD ["npm", "start"]
