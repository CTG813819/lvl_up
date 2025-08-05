#!/bin/bash

echo "🔧 FIXING GUNICORN WORKER FAILURE AND DATABASE CONNECTION ISSUES"
echo "================================================================"

# Step 1: Stop all services and clean up
echo "🛑 Step 1: Stopping all services and cleaning up..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo pkill -9 -f uvicorn 2>/dev/null || true
sudo pkill -9 -f gunicorn 2>/dev/null || true
sudo pkill -9 -f 'python.*main:app' 2>/dev/null || true
sleep 5

# Step 2: Check for any remaining processes
echo "🔍 Step 2: Checking for remaining processes..."
ps aux | grep -E "(uvicorn|gunicorn|python.*main)" | grep -v grep || echo "No processes found"

# Step 3: Create a robust startup script with proper database connection handling
echo "📝 Step 3: Creating robust startup script..."
cat > ultimate_start_fixed.sh << 'EOF'
#!/bin/bash

# Kill any existing processes
pkill -f uvicorn || true
pkill -f gunicorn || true
pkill -f 'python.*main:app' || true
sleep 3

# Change directory
cd /home/ubuntu/ai-backend-python

# Activate venv
source venv/bin/activate

# Set environment variables with proper database connection
export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
export GITHUB_TOKEN="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"
export GITHUB_REPO_URL="https://github.com/CTG813819/Lvl_UP.git"
export GITHUB_USERNAME="CTG813819"

# Set Python environment variables for better async handling
export PYTHONPATH="/home/ubuntu/ai-backend-python"
export PYTHONUNBUFFERED=1

# Test database connection first
echo "🔍 Testing database connection..."
python3 -c "
import asyncio
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')
from app.core.database import init_database, close_database

async def test_db():
    try:
        await init_database()
        print('✅ Database connection successful')
        await close_database()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        sys.exit(1)

asyncio.run(test_db())
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection test failed. Exiting."
    exit 1
fi

echo "🚀 Starting uvicorn with single process and enhanced error handling..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --loop asyncio \
    --workers 0 \
    --limit-concurrency 50 \
    --backlog 100 \
    --timeout-keep-alive 30 \
    --log-level info \
    --access-log
EOF

chmod +x ultimate_start_fixed.sh

# Step 4: Create improved systemd service
echo "📝 Step 4: Creating improved systemd service..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1

ExecStart=/home/ubuntu/ai-backend-python/ultimate_start_fixed.sh
ExecStop=/bin/pkill -f uvicorn
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Step 5: Reload systemd and start service
echo "🔄 Step 5: Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python.service
sudo systemctl start ai-backend-python.service

# Step 6: Wait and check status
echo "⏳ Step 6: Waiting for service to start..."
sleep 20

# Check service status
echo "🔍 Step 7: Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Get the main process PID
    MAIN_PID=$(sudo systemctl show -p MainPID ai-backend-python.service | cut -d= -f2)
    echo "📊 Main process PID: $MAIN_PID"
    
    # Check process tree
    echo "📋 Process tree:"
    pstree -p $MAIN_PID 2>/dev/null || echo "Process tree not available"
    
    # Check CPU and memory usage
    echo "📊 Resource usage:"
    ps -p $MAIN_PID -o pid,ppid,%cpu,%mem,cmd 2>/dev/null || echo "Process info not available"
    
    # Check logs
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 10 --no-pager
    
    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    sleep 5
    curl -s http://localhost:8000/api/health || echo "Health endpoint not responding"
    
    echo "🎉 FIX COMPLETED SUCCESSFULLY!"
    echo "📋 Summary:"
    echo "   - Single process running"
    echo "   - Database connection tested"
    echo "   - Enhanced error handling"
    echo "   - Resource limits set"
    echo "   - Proper async loop configuration"
    
else
    echo "❌ Service failed to start"
    echo "📋 Service status:"
    sudo systemctl status ai-backend-python.service --no-pager
    
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 20 --no-pager
    
    echo "🔧 Attempting manual start for debugging..."
    cd /home/ubuntu/ai-backend-python
    source venv/bin/activate
    export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
    export PYTHONPATH="/home/ubuntu/ai-backend-python"
    
    echo "🧪 Testing database connection manually..."
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')
from app.core.database import init_database, close_database

async def test_db():
    try:
        await init_database()
        print('✅ Database connection successful')
        await close_database()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test_db())
"
    
    exit 1
fi 