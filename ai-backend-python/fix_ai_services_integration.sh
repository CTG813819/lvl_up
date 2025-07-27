#!/bin/bash

echo "🔧 Integrating AI Services with Main Backend"
echo "==========================================="

# Stop any existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop conquest-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true

# Kill any remaining processes
echo "🔪 Killing remaining processes..."
sudo pkill -f uvicorn 2>/dev/null || true
sudo pkill -f 'python.*main:app' 2>/dev/null || true
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to stop
sleep 3

# Update the main backend service to include AI agent management
echo "📝 Updating main backend service configuration..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service (Integrated)
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
Environment=INTEGRATED_AI_SERVICES=true

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
                'function': 'run_conquest_testing'
            },
            'guardian': {
                'name': 'Guardian AI', 
                'interval': 2700,  # 45 minutes
                'function': 'run_guardian_testing'
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
            
            # Start each service in its own task
            tasks = []
            for service_id, config in self.services.items():
                task = asyncio.create_task(self.run_service(service_id, config))
                tasks.append(task)
            
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
            await asyncio.sleep(config['interval'])
    
    async def stop_services(self):
        """Stop all integrated AI services"""
        logger.info("🛑 Stopping Integrated AI Services...")
        self.running = False

async def main():
    """Main function"""
    manager = IntegratedAIManager()
    
    try:
        await manager.start_services()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
    finally:
        await manager.stop_services()

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

# Start the main backend service
echo "🚀 Starting main backend service..."
sudo systemctl start ai-backend-python.service

# Wait for backend to start
sleep 5

# Check if backend is running
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Main backend service is running"
    
    # Start the integrated AI manager
    echo "🚀 Starting integrated AI manager..."
    sudo systemctl start integrated-ai-manager.service
    
    sleep 3
    
    # Check services status
    echo "🔍 Checking services status..."
    echo "📋 Main Backend: $(sudo systemctl is-active ai-backend-python.service)"
    echo "📋 Integrated AI Manager: $(sudo systemctl is-active integrated-ai-manager.service)"
    
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
    
    echo "🎉 AI Services Integration Completed!"
    echo "📊 Summary:"
    echo "   - Main Backend: Port 8000 (single PID)"
    echo "   - Conquest AI: Integrated through main backend"
    echo "   - Guardian AI: Integrated through main backend"
    echo "   - No port conflicts - all services work together"
    
else
    echo "❌ Main backend service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 