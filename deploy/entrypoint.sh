#!/bin/bash
set -e

echo "=== Starting Finance Automation Service ==="

# Set default port if not provided by Render
export PORT=${PORT:-10000}
echo "Container will listen on port: $PORT"

# Substitute PORT in nginx config
envsubst '${PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
echo "✓ Nginx configuration prepared"

# Verify required environment variables
if [ -z "$SUPABASE_URL" ]; then
    echo "ERROR: SUPABASE_URL environment variable is required"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "ERROR: SUPABASE_SERVICE_ROLE_KEY environment variable is required"
    exit 1
fi

echo "✓ Environment variables verified"

# Start FastAPI backend in the background
echo "Starting FastAPI backend on http://127.0.0.1:8000..."
cd /app
uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info &
BACKEND_PID=$!
echo "✓ FastAPI started (PID: $BACKEND_PID)"

# Give backend a moment to initialize
sleep 2

# Start Nginx in the foreground (keeps container alive)
echo "Starting Nginx on port $PORT..."
nginx -g "daemon off;" &
NGINX_PID=$!
echo "✓ Nginx started (PID: $NGINX_PID)"

echo "=== Service Ready ==="
echo "  Frontend: http://0.0.0.0:$PORT"
echo "  Backend API: http://0.0.0.0:$PORT/api"
echo "  Health Check: http://0.0.0.0:$PORT/api/health"

# Wait for either process to exit
wait -n $BACKEND_PID $NGINX_PID

# If one process dies, kill the other and exit
kill $BACKEND_PID $NGINX_PID 2>/dev/null || true
echo "ERROR: Service stopped unexpectedly"
exit 1

