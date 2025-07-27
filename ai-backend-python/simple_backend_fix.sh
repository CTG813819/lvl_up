#!/bin/bash

echo "🔧 Simple Backend Fix - Single PID"
echo "=================================="

# Stop everything
echo "🛑 Stopping all services..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo systemctl stop integrated-ai-manager.service 2>/dev/null || true
sudo systemctl stop conquest-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Kill all processes
echo "🔪 Killing all processes..."
sudo pkill -f uvicorn 2>/dev/null || true
sudo pkill -f 'python.*main:app' 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait
sleep 5

# Simple backend service config
echo "📝 Creating simple backend service..."
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
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

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

# Reload and start
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo "🚀 Starting backend service..."
sudo systemctl start ai-backend-python.service

# Wait and check
sleep 5

if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Backend service is running"
    
    # Check PID count
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "🔍 Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        echo "✅ Only one PID - SUCCESS!"
        echo "📋 PID: $(pgrep -f 'uvicorn.*app.main:app')"
    else
        echo "❌ Multiple PIDs found: $(pgrep -f 'uvicorn.*app.main:app')"
    fi
    
    # Test endpoint
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "✅ Health endpoint working"
    else
        echo "❌ Health endpoint not working"
    fi
    
    echo "🎉 Simple backend fix completed!"
    echo "📊 Status: Single PID backend running on port 8000"
    
else
    echo "❌ Backend service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 