#!/bin/bash

# Final Port Conflict Fix Script
# This script thoroughly cleans up all conflicting processes

set -e

echo "🔧 Final Port Conflict Fix"
echo "=========================="

# Function to kill all uvicorn processes
kill_all_uvicorn() {
    echo "🛑 Killing all uvicorn processes..."
    pkill -f uvicorn || echo "No uvicorn processes found"
    sleep 3
    
    # Force kill any remaining uvicorn processes
    pkill -9 -f uvicorn || echo "No uvicorn processes to force kill"
    sleep 2
}

# Function to check and kill processes on specific ports
clean_port() {
    local port=$1
    echo "🧹 Cleaning port $port..."
    
    local pids=$(sudo lsof -t -i :$port 2>/dev/null || echo "")
    if [ -n "$pids" ]; then
        echo "📊 Found processes on port $port: $pids"
        for pid in $pids; do
            echo "🛑 Killing process $pid on port $port..."
            sudo kill -9 $pid 2>/dev/null || echo "Process $pid already dead"
        done
        sleep 2
    else
        echo "✅ Port $port is clean"
    fi
}

# Step 1: Stop the systemd service
echo "🛑 Stopping systemd service..."
sudo systemctl stop ai-backend-python || echo "Service was not running"

# Step 2: Kill all uvicorn processes
kill_all_uvicorn

# Step 3: Clean specific ports
clean_port 8000
clean_port 4000
clean_port 5000

# Step 4: Verify ports are free
echo "🔍 Verifying ports are free..."
echo "Port 8000:"
sudo lsof -i :8000 2>/dev/null || echo "  ✅ Free"

echo "Port 4000:"
sudo lsof -i :4000 2>/dev/null || echo "  ✅ Free"

echo "Port 5000:"
sudo lsof -i :5000 2>/dev/null || echo "  ✅ Free"

# Step 5: Check for any remaining uvicorn processes
echo "🔍 Checking for remaining uvicorn processes..."
ps aux | grep uvicorn | grep -v grep || echo "  ✅ No uvicorn processes found"

# Step 6: Update service configuration to prevent conflicts
echo "⚙️ Updating service configuration..."
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
ExecStartPre=/bin/bash -c 'pkill -f uvicorn || true'
ExecStartPre=/bin/sleep 2
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
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

# Step 7: Reload systemd and start service
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "🚀 Starting AI backend service..."
sudo systemctl start ai-backend-python

# Step 8: Wait and check status
echo "⏳ Waiting for service to start..."
sleep 15

echo "📊 Service status:"
sudo systemctl status ai-backend-python --no-pager

# Step 9: Test the service
echo "🌐 Testing service..."
if curl -s --connect-timeout 10 http://localhost:8000/health > /dev/null; then
    echo "✅ Service is running successfully on port 8000"
else
    echo "❌ Service failed to start"
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 20 --no-pager
    exit 1
fi

# Step 10: Final verification
echo "🔍 Final port verification:"
echo "Port 8000:"
sudo lsof -i :8000 || echo "  Not listening"

echo ""
echo "🎉 Port conflict fix completed!"
echo "==============================="
echo "✅ All conflicting processes cleaned up"
echo "✅ Service running on port 8000"
echo "✅ No more port conflicts"
echo ""
echo "🚀 To monitor: sudo journalctl -u ai-backend-python -f"
echo "🔄 To restart: sudo systemctl restart ai-backend-python" 