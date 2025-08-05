#!/bin/bash

echo "🔧 Fixing Single PID Issue - AI Backend"
echo "======================================"

# Stop the service first
echo "🛑 Stopping ai-backend-python service..."
sudo systemctl stop ai-backend-python.service

# Kill ALL processes that might be using port 8000
echo "🔪 Killing all processes on port 8000..."
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sudo pkill -f 'python3.*main:app'
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to fully stop
echo "⏳ Waiting for processes to stop..."
sleep 5

# Verify port is free
echo "🔍 Checking if port 8000 is free..."
if sudo netstat -tlnp | grep :8000; then
    echo "❌ Port 8000 is still in use!"
    sudo netstat -tlnp | grep :8000
    exit 1
else
    echo "✅ Port 8000 is free"
fi

# Update service to prevent multiple PIDs
echo "📝 Updating service configuration..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Ensure only one instance
ExecStartPre=/bin/bash -c 'pkill -f uvicorn || true'
ExecStartPre=/bin/bash -c 'fuser -k 8000/tcp 2>/dev/null || true'
ExecStartPre=/bin/sleep 3

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/ubuntu/ai-backend-python

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start the service
echo "🚀 Starting ai-backend-python service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 5

# Check service status
echo "🔍 Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for multiple PIDs
    echo "🔍 Checking for multiple PIDs..."
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    if [ "$pids" -eq 1 ]; then
        echo "✅ Only one PID found: $(pgrep -f 'uvicorn.*app.main:app')"
    else
        echo "❌ Multiple PIDs found: $(pgrep -f 'uvicorn.*app.main:app')"
    fi
    
    # Test the endpoint
    echo "🧪 Testing health endpoint..."
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "✅ Health endpoint responding"
    else
        echo "❌ Health endpoint not responding"
    fi
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi

echo "🎉 Single PID fix completed!" 