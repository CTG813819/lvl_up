#!/bin/bash

# Set PATH to include system binaries
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Kill any existing processes
/usr/bin/pkill -f uvicorn || true
/usr/bin/pkill -f gunicorn || true
/usr/bin/pkill -f 'python.*main:app' || true
sleep 3

# Change directory
cd /home/ubuntu/ai-backend-python

# Activate venv
source venv/bin/activate

# Set environment
export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
export GITHUB_TOKEN="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"
export GITHUB_REPO_URL="https://github.com/CTG813819/Lvl_UP.git"
export GITHUB_USERNAME="CTG813819"
export PYTHONPATH="/home/ubuntu/ai-backend-python"
export PYTHONUNBUFFERED=1

# Force asyncio loop
export UVICORN_LOOP=asyncio

echo "🚀 Starting with Gunicorn..."
exec gunicorn app.main:app --bind 0.0.0.0:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keep-alive 30 --max-requests 1000 --max-requests-jitter 100 --log-level info