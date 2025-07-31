#!/bin/bash

# Kill any existing uvicorn processes
echo "🔪 Killing existing uvicorn processes..."
/usr/bin/pkill -f uvicorn || true
/usr/bin/pkill -f 'python.*main:app' || true
/usr/bin/fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to fully stop
/usr/bin/sleep 3

# Verify port is free
if /usr/bin/lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 is still in use"
    exit 1
fi

# Change to the correct directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Start uvicorn with single process
echo "🚀 Starting uvicorn with single process..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop asyncio 