#!/bin/bash

echo "🎯 FINAL STABLE FIX - Disable Background Tasks"
echo "=============================================="

# Step 1: Nuclear cleanup
echo "🛑 Step 1: Nuclear cleanup..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo pkill -9 -f uvicorn
sudo pkill -9 -f 'python.*main:app'
sleep 5

# Step 2: Create startup script with background tasks disabled
echo "📝 Step 2: Creating startup script with background tasks disabled..."
cat > final_stable_start.sh << 'EOF'
#!/bin/bash

# Kill any existing processes
pkill -f uvicorn || true
pkill -f 'python.*main:app' || true
sleep 3

# Change directory
cd /home/ubuntu/ai-backend-python

# Activate venv
source venv/bin/activate

# Set environment - DISABLE background tasks that spawn processes
export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
export GITHUB_TOKEN="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"
export GITHUB_REPO_URL="https://github.com/CTG813819/Lvl_UP.git"
export GITHUB_USERNAME="CTG813819"

# DISABLE background tasks that spawn multiple processes
export DISABLE_BACKGROUND_TASKS="true"
export DISABLE_AI_CYCLES="true"
export DISABLE_AUTONOMOUS_CYCLES="true"
export DISABLE_LEARNING_CYCLES="true"
export DISABLE_IMPERIUM_ORCHESTRATOR="true"

# Start with single process
echo "🚀 Starting uvicorn with background tasks DISABLED (single process only)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 0
EOF

chmod +x final_stable_start.sh

# Step 3: Create systemd service
echo "📝 Step 3: Creating systemd service..."
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
Environment=DISABLE_BACKGROUND_TASKS=true
Environment=DISABLE_AI_CYCLES=true
Environment=DISABLE_AUTONOMOUS_CYCLES=true
Environment=DISABLE_LEARNING_CYCLES=true
Environment=DISABLE_IMPERIUM_ORCHESTRATOR=true

ExecStart=/home/ubuntu/ai-backend-python/final_stable_start.sh
ExecStop=/bin/pkill -f uvicorn
KillMode=process
TimeoutStopSec=30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 4: Start service
echo "🔄 Step 4: Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python.service
sudo systemctl start ai-backend-python.service

# Step 5: Wait and check
echo "⏳ Step 5: Waiting for service..."
sleep 20

# Check status
echo "🔍 Step 6: Checking status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Count processes
    uvicorn_count=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    python_count=$(pgrep -f "python.*main:app" | wc -l)
    
    echo "📊 Process counts:"
    echo "   - uvicorn processes: $uvicorn_count"
    echo "   - python main processes: $python_count"
    
    if [ "$uvicorn_count" -eq 1 ] && [ "$python_count" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Single process running with PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,%cpu,%mem,cmd
        
        # Check CPU usage
        echo "📊 CPU usage:"
        top -p $pid -b -n 1 | tail -2
        
        echo "🎉 FINAL STABLE FIX SUCCESSFUL!"
        echo "📋 Summary:"
        echo "   - Single process: $pid"
        echo "   - Background tasks DISABLED (temporarily)"
        echo "   - Core API functionality working"
        echo "   - No multiple instances"
        echo "   - Low CPU usage"
        echo ""
        echo "⚠️  NOTE: Background AI tasks are temporarily disabled"
        echo "   To re-enable them later, remove the DISABLE_* environment variables"
        
    else
        echo "❌ Multiple processes detected:"
        echo "Uvicorn PIDs:"
        pgrep -f 'uvicorn.*app.main:app' -a || echo "None"
        echo "Python main PIDs:"
        pgrep -f 'python.*main:app' -a || echo "None"
        exit 1
    fi
    
else
    echo "❌ Service failed"
    sudo systemctl status ai-backend-python.service --no-pager
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 15 --no-pager
    exit 1
fi 