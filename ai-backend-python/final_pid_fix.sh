#!/bin/bash

echo "🔧 Final PID Fix - Ensuring Single Process"
echo "========================================="

# Stop everything and kill all processes
echo "🛑 Stopping all services and killing processes..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo systemctl stop integrated-ai-manager.service 2>/dev/null || true
sudo systemctl stop conquest-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Kill ALL uvicorn processes
echo "🔪 Killing all uvicorn processes..."
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sudo pkill -f 'python3.*main:app'
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to fully stop
sleep 5

# Verify no uvicorn processes are running
echo "🔍 Verifying no uvicorn processes are running..."
if pgrep -f uvicorn > /dev/null; then
    echo "❌ Uvicorn processes still running:"
    pgrep -f uvicorn -a
    echo "🔪 Force killing remaining processes..."
    sudo pkill -9 -f uvicorn
    sleep 2
else
    echo "✅ No uvicorn processes running"
fi

# Create a wrapper script to ensure single process
echo "📝 Creating single process wrapper..."
cat > /home/ubuntu/ai-backend-python/start_backend.sh << 'EOF'
#!/bin/bash

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Start uvicorn with explicit single process
exec /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --loop uvloop
EOF

chmod +x /home/ubuntu/ai-backend-python/start_backend.sh

# Update service to use the wrapper
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
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

ExecStart=/home/ubuntu/ai-backend-python/start_backend.sh
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

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start the service
echo "🚀 Starting backend service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 8

# Check service status
echo "🔍 Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for multiple PIDs
    echo "🔍 Checking for multiple PIDs..."
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Only one PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,cmd
        
        # Test endpoint
        echo "🧪 Testing health endpoint..."
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo "✅ Health endpoint responding"
        else
            echo "❌ Health endpoint not responding"
        fi
        
        echo "🎉 Single PID fix completed successfully!"
        echo "📊 Summary:"
        echo "   - Single PID: $pid"
        echo "   - Port: 8000"
        echo "   - No conflicts"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        echo "🔪 Killing all processes and trying again..."
        sudo pkill -f uvicorn
        sleep 3
        sudo systemctl restart ai-backend-python.service
        sleep 5
        
        pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
        if [ "$pids" -eq 1 ]; then
            echo "✅ Fixed after restart! PID: $(pgrep -f 'uvicorn.*app.main:app')"
        else
            echo "❌ Still multiple PIDs after restart"
            exit 1
        fi
    fi
    
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 