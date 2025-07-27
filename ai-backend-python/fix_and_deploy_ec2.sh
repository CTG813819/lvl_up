#!/bin/bash

# Comprehensive EC2 Fix and Deploy Script
# Fixes all service issues, memory problems, and deploys the backend

set -e

echo "🚀 Starting Comprehensive EC2 Fix and Deploy"
echo "============================================="

# Configuration
BASE_PATH="/home/ubuntu/ai-backend-python"
VENV_PATH="$BASE_PATH/venv"

echo "📂 Working directory: $BASE_PATH"

# Function to run commands with error handling
run_cmd() {
    echo "🔧 Running: $1"
    if ! eval "$1"; then
        echo "❌ Failed: $1"
        return 1
    fi
    echo "✅ Success: $1"
}

# Phase 1: Stop problematic services and processes
echo ""
echo "🛑 PHASE 1: Stopping Problematic Services"
echo "========================================="

run_cmd "sudo systemctl stop docker.socket || true"
run_cmd "sudo systemctl stop docker || true"
run_cmd "sudo systemctl disable docker || true"
run_cmd "sudo systemctl disable docker.socket || true"

# Stop current backend services
run_cmd "sudo systemctl stop ai-backend-optimized.service || true"
run_cmd "sudo systemctl stop guardian-ai.service || true"

# Kill any hanging Python processes (except the current one)
run_cmd "pkill -f 'uvicorn.*8000' || true"
run_cmd "pkill -f 'python.*custodes' || true"
run_cmd "pkill -f 'python.*autonomous_subject' || true"

# Phase 2: Memory cleanup
echo ""
echo "🧹 PHASE 2: Memory Cleanup"
echo "=========================="

run_cmd "sudo sync"
run_cmd "sudo sysctl vm.drop_caches=3"
run_cmd "free -h"

# Phase 3: Fix service files
echo ""
echo "🔧 PHASE 3: Fixing Service Files"
echo "================================"

# Create fixed ai-backend-optimized.service
cat > /tmp/ai-backend-optimized.service << 'EOF'
[Unit]
Description=AI Backend Optimized Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819
Environment=PROPOSAL_TIMEOUT=600
Environment=LEARNING_INTERVAL=600
Environment=GROWTH_ANALYSIS_INTERVAL=7200
Environment=LEARNING_CYCLE_INTERVAL=3600
Environment=MAX_LEARNING_HISTORY=500
Environment=ML_CONFIDENCE_THRESHOLD=0.8

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python main.py

Restart=always
RestartSec=60
StartLimitInterval=600
StartLimitBurst=3

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-backend-optimized

LimitNOFILE=131072
LimitNPROC=8192

[Install]
WantedBy=multi-user.target
EOF

# Create fixed guardian-ai.service
cat > /tmp/guardian-ai.service << 'EOF'
[Unit]
Description=Guardian AI Self-Healing Service
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python run_guardian.py

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

StandardOutput=journal
StandardError=journal
SyslogIdentifier=guardian-ai

LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Copy service files
run_cmd "sudo cp /tmp/ai-backend-optimized.service /etc/systemd/system/"
run_cmd "sudo cp /tmp/guardian-ai.service /etc/systemd/system/"

# Phase 4: Create necessary directories and files
echo ""
echo "📁 PHASE 4: Setting Up Directories and Files"
echo "============================================"

run_cmd "mkdir -p $BASE_PATH/logs"
run_cmd "mkdir -p $BASE_PATH/cache"

# Create a simple run_guardian.py if it doesn't exist
if [ ! -f "$BASE_PATH/run_guardian.py" ]; then
    cat > "$BASE_PATH/run_guardian.py" << 'EOF'
#!/usr/bin/env python3
"""
Simple Guardian AI Service Runner
"""

import asyncio
import logging
import sys
import os

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/guardian.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def run_guardian():
    """Run guardian service"""
    try:
        from app.services.ai_agent_service import AIAgentService
        
        service = AIAgentService()
        logger.info('Guardian AI Service started')
        
        while True:
            try:
                logger.info('Starting Guardian self-healing cycle')
                await service.run_guardian_agent()
                logger.info('Guardian self-healing cycle completed')
            except Exception as e:
                logger.error(f'Guardian self-healing error: {str(e)}')
            
            await asyncio.sleep(3600)  # 60 minutes
            
    except Exception as e:
        logger.error(f'Guardian service startup error: {str(e)}')
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_guardian())
EOF
    run_cmd "chmod +x $BASE_PATH/run_guardian.py"
fi

# Phase 5: Install dependencies
echo ""
echo "📦 PHASE 5: Installing Dependencies"
echo "==================================="

run_cmd "cd $BASE_PATH && source venv/bin/activate && pip install psutil requests"

# Phase 6: Reload and start services
echo ""
echo "🚀 PHASE 6: Starting Services"
echo "============================="

run_cmd "sudo systemctl daemon-reload"
run_cmd "sudo systemctl enable ai-backend-optimized.service"
run_cmd "sudo systemctl enable guardian-ai.service"
run_cmd "sudo systemctl start ai-backend-optimized.service"
run_cmd "sudo systemctl start guardian-ai.service"

# Phase 7: Wait for services to start
echo ""
echo "⏳ PHASE 7: Waiting for Services to Start"
echo "========================================="

sleep 30

# Phase 8: Verify deployment
echo ""
echo "✅ PHASE 8: Verifying Deployment"
echo "================================"

echo "🔍 Checking service status:"
run_cmd "sudo systemctl status ai-backend-optimized.service --no-pager"
run_cmd "sudo systemctl status guardian-ai.service --no-pager"

echo "🌐 Testing backend connectivity:"
run_cmd "curl -f http://localhost:4000/health || echo 'Port 4000 not responding'"
run_cmd "curl -f http://localhost:8000/health || echo 'Port 8000 not responding'"

echo "📊 Checking system resources:"
run_cmd "free -h"
run_cmd "df -h"

echo "🔍 Checking running processes:"
run_cmd "ps aux | grep python | grep -v grep"

echo "📝 Recent logs:"
run_cmd "tail -10 $BASE_PATH/logs/performance_optimization.log || echo 'No optimization logs'"
run_cmd "journalctl -u ai-backend-optimized.service --no-pager -n 10 || echo 'No service logs'"

# Phase 9: Performance monitoring
echo ""
echo "📊 PHASE 9: Setting Up Monitoring"
echo "================================="

# Start performance monitoring if not already running
if ! pgrep -f "monitor_performance.py" > /dev/null; then
    run_cmd "cd $BASE_PATH && nohup python monitor_performance.py > /dev/null 2>&1 &"
    echo "✅ Performance monitoring started"
else
    echo "ℹ️  Performance monitoring already running"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "🔗 Backend URLs:"
echo "   - Port 4000: http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"
echo "   - Port 8000: http://ec2-34-202-215-209.compute-1.amazonaws.com:8000"
echo ""
echo "📊 Health Checks:"
echo "   - http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/health"
echo "   - http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/health"
echo ""
echo "📋 Service Management:"
echo "   - Check status: sudo systemctl status ai-backend-optimized.service"
echo "   - View logs: journalctl -u ai-backend-optimized.service -f"
echo "   - Restart: sudo systemctl restart ai-backend-optimized.service"
echo ""
echo "📞 Troubleshooting:"
echo "   - Check memory: free -h"
echo "   - Check processes: ps aux | grep python"
echo "   - Check ports: sudo netstat -tlnp | grep :4000"
echo ""
echo "✅ Your backend should now be running with optimized performance!" 