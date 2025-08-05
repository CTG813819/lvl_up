#!/bin/bash

echo "🔧 Fixing Port Conflicts - AI Backend Services"
echo "=============================================="

# Stop all conflicting services
echo "🛑 Stopping conflicting services..."
sudo systemctl stop conquest-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true

# Kill any remaining processes
echo "🔪 Killing remaining processes..."
sudo pkill -f uvicorn 2>/dev/null || true
sudo pkill -f 'python.*main:app' 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true
sudo fuser -k 8001/tcp 2>/dev/null || true
sudo fuser -k 8002/tcp 2>/dev/null || true

# Wait for processes to stop
sleep 3

# Update the main backend service configuration
echo "📝 Updating main backend service configuration..."
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

# Prevent multiple instances and port conflicts
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

# Start the main backend service
echo "🚀 Starting main backend service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 5

# Check service status
echo "🔍 Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Main backend service is running"
else
    echo "❌ Main backend service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi

# Check port usage
echo "🌐 Checking port usage..."
sudo netstat -tlnp | grep -E ':(8000|8001|8002)' || echo "No processes found on ports 8000-8002"

# Show running services
echo "📋 Running AI services:"
sudo systemctl list-units --type=service --state=running | grep -E '(ai|backend)' || echo "No AI services found"

echo "🎉 Port conflict fix completed!"
echo "📊 Summary:"
echo "   - Main backend: Port 8000"
echo "   - Other AI services: Disabled to prevent conflicts"
echo "   - Only one PID will be generated on restart" 