#!/bin/bash

# Simple and Robust Fix Script
# Avoids complex ExecStartPre commands that can cause issues

set -e

echo "🔧 Simple and Robust System Fix"
echo "==============================="

# Function to kill processes by name
kill_processes_by_name() {
    local process_name=$1
    echo "🛑 Killing processes containing '$process_name'..."
    
    # Use pgrep to find processes
    pids=$(pgrep -f "$process_name" 2>/dev/null || echo "")
    if [ -n "$pids" ]; then
        echo "📊 Found processes: $pids"
        for pid in $pids; do
            echo "🛑 Killing process $pid..."
            kill -9 $pid 2>/dev/null || echo "Process $pid already dead"
        done
        sleep 3
    else
        echo "✅ No processes found with '$process_name'"
    fi
}

# Function to clean specific ports
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
        sleep 3
    else
        echo "✅ Port $port is clean"
    fi
}

# Step 1: Stop the systemd service
echo "🛑 Stopping systemd service..."
sudo systemctl stop ai-backend-python || echo "Service was not running"

# Step 2: Kill all uvicorn and python processes
echo "🛑 Cleaning up all uvicorn and python processes..."
kill_processes_by_name "uvicorn"
kill_processes_by_name "python.*app.main:app"
kill_processes_by_name "python.*main:app"

# Step 3: Clean specific ports
echo "🧹 Cleaning specific ports..."
clean_port 8000
clean_port 4000
clean_port 5000

# Step 4: Wait a bit to ensure everything is cleaned up
echo "⏳ Waiting for cleanup to complete..."
sleep 5

# Step 5: Verify ports are free
echo "🔍 Verifying ports are free..."
echo "Port 8000:"
sudo lsof -i :8000 2>/dev/null || echo "  ✅ Free"

echo "Port 4000:"
sudo lsof -i :4000 2>/dev/null || echo "  ✅ Free"

echo "Port 5000:"
sudo lsof -i :5000 2>/dev/null || echo "  ✅ Free"

# Step 6: Check for any remaining processes
echo "🔍 Checking for remaining processes..."
ps aux | grep -E "(uvicorn|python.*app.main)" | grep -v grep || echo "  ✅ No remaining processes found"

# Step 7: Update service configuration with simple, reliable commands
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
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
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

# Step 8: Reload systemd and start service
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "🚀 Starting AI backend service..."
sudo systemctl start ai-backend-python

# Step 9: Wait and check status
echo "⏳ Waiting for service to start..."
sleep 10

echo "📊 Service status:"
sudo systemctl status ai-backend-python --no-pager

# Step 10: Test the service
echo "🌐 Testing service..."
if curl -s --connect-timeout 10 http://localhost:8000/health > /dev/null; then
    echo "✅ Service is running successfully on port 8000"
else
    echo "❌ Service failed to start"
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 20 --no-pager
    exit 1
fi

# Step 11: Final verification
echo "🔍 Final verification:"
echo "Port 8000:"
sudo lsof -i :8000 || echo "  Not listening"

echo "Service processes:"
ps aux | grep -E "(uvicorn|python.*app.main)" | grep -v grep || echo "  No processes found"

# Step 12: Test API endpoints
echo "🧪 Testing API endpoints..."
echo "Health check:"
curl -s http://localhost:8000/health | jq '.' || echo "Health check completed"

echo "Learning status:"
curl -s http://localhost:8000/api/learning/stats/Imperium | jq '.' || echo "Learning status check completed"

echo ""
echo "🎉 Simple fix completed!"
echo "======================="
echo "✅ All conflicting processes cleaned up"
echo "✅ Service configuration simplified"
echo "✅ Service running on port 8000"
echo "✅ No more port conflicts"
echo ""
echo "📊 Service Information:"
echo "- URL: http://localhost:8000"
echo "- Health: http://localhost:8000/health"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "🚀 To monitor the service:"
echo "   sudo journalctl -u ai-backend-python -f"
echo ""
echo "🔄 To restart the service:"
echo "   sudo systemctl restart ai-backend-python" 