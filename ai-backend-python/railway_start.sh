#!/bin/bash
# Railway startup script that properly handles environment variables

# Set default port if PORT is not set
export PORT=${PORT:-8000}

echo "🚀 Starting Railway deployment..."
echo "📍 Using PORT: $PORT"
echo "🌐 Available env vars: $(env | grep -E '(PORT|RAILWAY)' | cut -d= -f1 | tr '\n' ' ')"

# Start uvicorn with the PORT environment variable
exec uvicorn main_unified:app --host 0.0.0.0 --port $PORT --log-level info