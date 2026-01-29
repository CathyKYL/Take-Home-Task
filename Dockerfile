# ====================================
# Stage 1: Build Next.js Frontend
# ====================================
FROM node:18-alpine AS frontend-builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --prefer-offline --no-audit

# Copy all frontend source files
# (Next.js app router pages, components, lib, configs)
COPY app/layout.tsx app/page.tsx app/globals.css ./app/
COPY components/ ./components/
COPY lib/ ./lib/
COPY next.config.js tsconfig.json tailwind.config.js postcss.config.js ./

# Build Next.js static export
RUN npm run build

# Verify build output exists
RUN ls -la /build/out && test -f /build/out/index.html


# ====================================
# Stage 2: Prepare Python Backend
# ====================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend Python modules
COPY app/__init__.py app/config.py app/main.py ./app/
COPY app/models/ ./app/models/
COPY app/routes/ ./app/routes/
COPY app/services/ ./app/services/
COPY app/processing/ ./app/processing/


# ====================================
# Stage 3: Final Runtime Image
# ====================================
FROM python:3.11-slim

# Install nginx and envsubst (for PORT substitution)
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx gettext-base && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /etc/nginx/sites-enabled/default

WORKDIR /app

# Copy Python dependencies from backend builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY --from=backend-builder /app /app

# Copy frontend build output to nginx root
COPY --from=frontend-builder /build/out /usr/share/nginx/html

# Copy nginx config template (will be processed by entrypoint to inject PORT)
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf.template

# Copy and make entrypoint executable
COPY deploy/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Remove default nginx config
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

# Expose port (Render will set PORT env var)
EXPOSE 10000

# Environment variables (set these in Render dashboard)
ENV SUPABASE_URL=""
ENV SUPABASE_KEY=""
ENV PORT=10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start the service
CMD ["/app/entrypoint.sh"]

