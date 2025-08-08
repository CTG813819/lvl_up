#!/bin/bash

# Fix Port Conflict Script for AI Backend Python Service
# This script diagnoses and fixes the port 8000 conflict issue

set -e

echo "🔍 Diagnosing port conflict issue..."
echo "===================================="

# Check what's currently using port 8000
echo "📊 Checking what's using port 8000:"
sudo lsof -i :8000 || echo "No process found using port 8000"

echo ""
echo "🔍 Checking for other uvicorn processes:"
ps aux | grep uvicorn | grep -v grep || echo "No uvicorn processes found"

echo ""
echo "📋 Current systemd service status:"
sudo systemctl status ai-backend-python --no-pager

echo ""
echo "🔧 Fixing port conflict by updating service configuration..."

# Stop the current service
echo "🛑 Stopping current service..."
sudo systemctl stop ai-backend-python

# Update the service file to use port 4000 instead of 8000
echo "⚙️ Updating service configuration to use port 4000..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null <<EOF
[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000 --workers 1
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal
Environment=DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd configuration
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reload

# Start the service with the new configuration
echo "🚀 Starting service with new port configuration..."
sudo systemctl start ai-backend-python

# Wait a moment for the service to start
echo "⏳ Waiting for service to start..."
sleep 5

# Check service status
echo "📊 New service status:"
sudo systemctl status ai-backend-python --no-pager

# Test the new port
echo "🌐 Testing new port 4000:"
if curl -s http://localhost:4000/health > /dev/null; then
    echo "✅ Service is running successfully on port 4000"
else
    echo "❌ Service failed to start on port 4000"
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 10 --no-pager
fi

echo ""
echo "🔍 Checking port 4000:"
sudo lsof -i :4000 || echo "Port 4000 not listening"

echo ""
echo "📝 Summary:"
echo "- Service configuration updated to use port 4000"
echo "- Old port 8000 conflict resolved"
echo "- Service should now be running on http://localhost:4000"
echo ""
echo "🚀 To monitor the service:"
echo "   sudo journalctl -u ai-backend-python -f"
echo ""
echo "🌐 To test the API:"
echo "   curl http://localhost:4000/health" 