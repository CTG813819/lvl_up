#!/bin/bash

echo "🔧 Adding Back AI Services - Integrated Mode"
echo "==========================================="

# Create integrated AI service manager
echo "📝 Creating integrated AI service manager..."
cat > /home/ubuntu/ai-backend-python/integrated_ai_manager.py << 'EOF'
#!/usr/bin/env python3
"""
Integrated AI Service Manager
Manages Conquest AI and Guardian AI through the main backend
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/integrated_ai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class IntegratedAIManager:
    def __init__(self):
        self.services = {
            'conquest': {
                'name': 'Conquest AI',
                'interval': 1800,  # 30 minutes
                'description': 'Comprehensive conquest testing and analysis'
            },
            'guardian': {
                'name': 'Guardian AI', 
                'interval': 2700,  # 45 minutes
                'description': 'Guardian self-healing and monitoring'
            }
        }
        self.running = False
    
    async def start_services(self):
        """Start all integrated AI services"""
        logger.info("🚀 Starting Integrated AI Services...")
        self.running = True
        
        try:
            from app.services.ai_agent_service import AIAgentService
            self.ai_service = AIAgentService()
            logger.info("✅ AI Agent Service initialized")
            
            # Start each service in its own task
            tasks = []
            for service_id, config in self.services.items():
                task = asyncio.create_task(self.run_service(service_id, config))
                tasks.append(task)
                logger.info(f"🔄 Started {config['name']} service task")
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"❌ Error starting integrated AI services: {str(e)}")
            self.running = False
    
    async def run_service(self, service_id, config):
        """Run a specific AI service"""
        logger.info(f"🔄 Starting {config['name']} service...")
        counter = 0
        
        while self.running:
            try:
                if counter % 2 == 0:
                    logger.info(f"🔄 Running comprehensive {config['name']} cycle")
                    if service_id == 'conquest':
                        await self.ai_service.run_comprehensive_conquest_testing()
                    elif service_id == 'guardian':
                        await self.ai_service.run_comprehensive_guardian_testing()
                else:
                    logger.info(f"🔄 Running regular {config['name']} cycle")
                    if service_id == 'conquest':
                        await self.ai_service.run_conquest_testing()
                    elif service_id == 'guardian':
                        await self.ai_service.run_guardian_testing()
                
                counter += 1
                logger.info(f"✅ {config['name']} cycle completed")
                
            except Exception as e:
                logger.error(f"❌ {config['name']} error: {str(e)}")
            
            # Wait for next cycle
            logger.info(f"⏳ {config['name']} waiting {config['interval']} seconds until next cycle")
            await asyncio.sleep(config['interval'])
    
    async def stop_services(self):
        """Stop all integrated AI services"""
        logger.info("🛑 Stopping Integrated AI Services...")
        self.running = False

async def main():
    """Main function"""
    logger.info("🔧 Integrated AI Manager Starting...")
    manager = IntegratedAIManager()
    
    try:
        await manager.start_services()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
    finally:
        await manager.stop_services()
        logger.info("🛑 Integrated AI Manager stopped")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Create a background service for the integrated AI manager
echo "📝 Creating integrated AI background service..."
sudo tee /etc/systemd/system/integrated-ai-manager.service > /dev/null << 'EOF'
[Unit]
Description=Integrated AI Manager Service
After=ai-backend-python.service
Wants=ai-backend-python.service

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

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/integrated_ai_manager.py

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=integrated-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Create logs directory
mkdir -p /home/ubuntu/ai-backend-python/logs

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start the integrated AI manager
echo "🚀 Starting integrated AI manager..."
sudo systemctl start integrated-ai-manager.service

# Wait for service to start
sleep 5

# Check services status
echo "🔍 Checking services status..."
echo "📋 Main Backend: $(sudo systemctl is-active ai-backend-python.service)"
echo "📋 Integrated AI Manager: $(sudo systemctl is-active integrated-ai-manager.service)"

# Check for multiple PIDs on main backend
echo "🔍 Checking main backend PIDs..."
pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
if [ "$pids" -eq 1 ]; then
    echo "✅ Main backend still has single PID: $(pgrep -f 'uvicorn.*app.main:app')"
else
    echo "❌ Main backend has multiple PIDs: $(pgrep -f 'uvicorn.*app.main:app')"
fi

# Check integrated AI manager process
echo "🔍 Checking integrated AI manager process..."
if pgrep -f "integrated_ai_manager.py" > /dev/null; then
    echo "✅ Integrated AI manager running: $(pgrep -f 'integrated_ai_manager.py')"
else
    echo "❌ Integrated AI manager not running"
fi

# Test the endpoints
echo "🧪 Testing endpoints..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
fi

# Show running services
echo "📋 All running AI services:"
sudo systemctl list-units --type=service --state=running | grep -E '(ai|backend)' || echo "No AI services found"

# Show process tree
echo "🌳 Process tree:"
ps aux | grep -E "(uvicorn|integrated_ai_manager)" | grep -v grep

echo "🎉 AI Services Integration Completed!"
echo "📊 Summary:"
echo "   - Main Backend: Port 8000 (single PID)"
echo "   - Conquest AI: Integrated through background manager"
echo "   - Guardian AI: Integrated through background manager"
echo "   - No port conflicts - all services work together"
echo ""
echo "📋 Service Management:"
echo "   - Check status: sudo systemctl status integrated-ai-manager.service"
echo "   - View logs: sudo journalctl -u integrated-ai-manager.service -f"
echo "   - Restart: sudo systemctl restart integrated-ai-manager.service" 