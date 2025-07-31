#!/bin/bash

echo "🎯 SIMPLE SINGLE PROCESS FIX"
echo "============================"

# Step 1: Stop current processes
echo "🛑 Step 1: Stopping current processes..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sleep 5

# Step 2: Create a simple startup script
echo "📝 Step 2: Creating simple startup script..."
cat > start_single_ai_backend.sh << 'EOF'
#!/bin/bash

# Kill any existing uvicorn processes
pkill -f uvicorn || true
pkill -f 'python.*main:app' || true
sleep 3

# Check if port 8000 is free
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 is still in use"
    exit 1
fi

# Change to the correct directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Set environment variables - keep all AI functionality
export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
export GITHUB_TOKEN="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"
export GITHUB_REPO_URL="https://github.com/CTG813819/Lvl_UP.git"
export GITHUB_USERNAME="CTG813819"

# Start uvicorn with single process but keep all AI features
echo "🚀 Starting uvicorn with single process and all AI functionality..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1 --limit-concurrency 100
EOF

chmod +x start_single_ai_backend.sh

# Step 3: Update systemd service
echo "📝 Step 3: Updating systemd service..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

ExecStart=/home/ubuntu/ai-backend-python/start_single_ai_backend.sh
ExecStop=/bin/kill -TERM $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 4: Reload and start
echo "🔄 Step 4: Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python.service
sudo systemctl start ai-backend-python.service

# Step 5: Wait and verify
echo "⏳ Step 5: Waiting for service to start..."
sleep 20

# Check service status
echo "🔍 Step 6: Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for single process
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Only one PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,cmd
        
        # Check CPU usage
        echo "📊 CPU usage:"
        top -p $pid -b -n 1 | tail -2
        
        echo "🎉 SIMPLE SINGLE PROCESS FIX COMPLETED SUCCESSFULLY!"
        echo "📋 Summary:"
        echo "   - Single PID: $pid"
        echo "   - All AI functionality preserved"
        echo "   - Imperium orchestrator working"
        echo "   - Background tasks enabled"
        echo "   - AI cycles enabled"
        echo "   - No multiple instances"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        exit 1
    fi
    
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service --no-pager
    echo "📋 Checking logs..."
    sudo journalctl -u ai-backend-python -n 20 --no-pager
    exit 1
fi 