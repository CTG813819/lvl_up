#!/usr/bin/env python3
"""
Comprehensive AI Services Fix Script
===================================

This script fixes all AI services and ensures they work properly on the backend:
- imperium-ai.service
- sandbox-ai.service  
- custodes-ai.service
- guardian-ai.service

Fixes include:
1. Proper sudo handling for Guardian
2. Correct Python paths and virtual environment usage
3. Proper error handling and logging
4. Service dependencies and startup order
5. Resource monitoring and health checks
"""

import os
import sys
import subprocess
import asyncio
import json
from datetime import datetime
import structlog

logger = structlog.get_logger()

class ComprehensiveAIServicesFix:
    """Comprehensive fix for all AI services"""
    
    def __init__(self):
        self.services = {
            'imperium': {
                'name': 'imperium-ai.service',
                'description': 'Imperium AI Optimization Service',
                'interval': 2700,  # 45 minutes
                'function': 'run_imperium_optimization'
            },
            'sandbox': {
                'name': 'sandbox-ai.service', 
                'description': 'Sandbox AI Experimentation Service',
                'interval': 2700,  # 45 minutes
                'function': 'run_sandbox_experimentation'
            },
            'custodes': {
                'name': 'custodes-ai.service',
                'description': 'Custodes AI Testing Service', 
                'interval': 2700,  # 45 minutes
                'function': 'run_custodes_testing'
            },
            'guardian': {
                'name': 'guardian-ai.service',
                'description': 'Guardian AI Self-Healing Service',
                'interval': 3600,  # 60 minutes
                'function': 'run_guardian_self_healing'
            }
        }
    
    def create_imperium_service(self):
        """Create Imperium AI service file"""
        service_content = '''[Unit]
Description=Imperium AI Optimization Service
After=network.target postgresql.service
Wants=postgresql.service

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

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python -c "
import asyncio
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/imperium.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_imperium():
        service = AIAgentService()
        logging.info('Imperium AI Service started')
        
        while True:
            try:
                logging.info('Starting Imperium optimization cycle')
                await service.run_imperium_agent()
                logging.info('Imperium optimization cycle completed')
            except Exception as e:
                logging.error(f'Imperium optimization error: {str(e)}')
            
            await asyncio.sleep(2700)  # 45 minutes
    
    asyncio.run(run_imperium())
except Exception as e:
    logging.error(f'Imperium service startup error: {str(e)}')
    sys.exit(1)
"

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=imperium-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
'''
        
        with open("imperium-ai.service", 'w') as f:
            f.write(service_content)
        
        logger.info("Created Imperium AI service file")
    
    def create_sandbox_service(self):
        """Create Sandbox AI service file"""
        service_content = '''[Unit]
Description=Sandbox AI Experimentation Service
After=network.target postgresql.service
Wants=postgresql.service

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

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python -c "
import asyncio
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/sandbox.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_sandbox():
        service = AIAgentService()
        logging.info('Sandbox AI Service started')
        
        while True:
            try:
                logging.info('Starting Sandbox experimentation cycle')
                await service.run_sandbox_agent()
                logging.info('Sandbox experimentation cycle completed')
            except Exception as e:
                logging.error(f'Sandbox experimentation error: {str(e)}')
            
            await asyncio.sleep(2700)  # 45 minutes
    
    asyncio.run(run_sandbox())
except Exception as e:
    logging.error(f'Sandbox service startup error: {str(e)}')
    sys.exit(1)
"

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sandbox-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
'''
        
        with open("sandbox-ai.service", 'w') as f:
            f.write(service_content)
        
        logger.info("Created Sandbox AI service file")
    
    def create_custodes_service(self):
        """Create Custodes AI service file"""
        service_content = '''[Unit]
Description=Custodes AI Testing Service
After=network.target postgresql.service
Wants=postgresql.service

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

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python -c "
import asyncio
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/custodes.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_custodes():
        service = AIAgentService()
        logging.info('Custodes AI Service started')
        counter = 0
        
        while True:
            try:
                if counter % 2 == 0:
                    logging.info('Starting comprehensive Custodes testing cycle')
                    await service.run_comprehensive_custodes_testing()
                else:
                    logging.info('Starting regular Custodes testing cycle')
                    await service.run_custodes_testing()
                
                counter += 1
                logging.info('Custodes testing cycle completed')
            except Exception as e:
                logging.error(f'Custodes testing error: {str(e)}')
            
            await asyncio.sleep(2700)  # 45 minutes
    
    asyncio.run(run_custodes())
except Exception as e:
    logging.error(f'Custodes service startup error: {str(e)}')
    sys.exit(1)
"

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=custodes-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
'''
        
        with open("custodes-ai.service", 'w') as f:
            f.write(service_content)
        
        logger.info("Created Custodes AI service file")
    
    def create_guardian_service(self):
        """Create Guardian AI service file with proper sudo handling"""
        service_content = '''[Unit]
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

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python -c "
import asyncio
import sys
import os
import logging
import subprocess
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/guardian.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

def check_sudo_availability():
    \"\"\"Check if sudo is available and working\"\"\"
    try:
        # Check if sudo exists
        sudo_path = shutil.which('sudo')
        if not sudo_path:
            logging.warning('sudo not found in PATH, using alternative methods')
            return False
        
        # Test sudo access
        result = subprocess.run(['sudo', '-n', 'true'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logging.info('sudo access confirmed')
            return True
        else:
            logging.warning(f'sudo access failed: {result.stderr}')
            return False
    except Exception as e:
        logging.warning(f'sudo check failed: {str(e)}')
        return False

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_guardian():
        service = AIAgentService()
        logging.info('Guardian AI Service started')
        
        # Check sudo availability
        sudo_available = check_sudo_availability()
        
        while True:
            try:
                logging.info('Starting Guardian self-healing cycle')
                
                if sudo_available:
                    await service.run_guardian_agent()
                else:
                    # Run without sudo capabilities
                    logging.info('Running Guardian without sudo capabilities')
                    await service.run_guardian_agent(sudo_required=False)
                
                logging.info('Guardian self-healing cycle completed')
            except Exception as e:
                logging.error(f'Guardian self-healing error: {str(e)}')
            
            await asyncio.sleep(3600)  # 60 minutes
    
    asyncio.run(run_guardian())
except Exception as e:
    logging.error(f'Guardian service startup error: {str(e)}')
    sys.exit(1)
"

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=guardian-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
'''
        
        with open("guardian-ai.service", 'w') as f:
            f.write(service_content)
        
        logger.info("Created Guardian AI service file")
    
    def create_log_directories(self):
        """Create log directories for all services"""
        log_dirs = [
            '/home/ubuntu/ai-backend-python/logs',
            '/home/ubuntu/ai-backend-python/logs/imperium',
            '/home/ubuntu/ai-backend-python/logs/sandbox', 
            '/home/ubuntu/ai-backend-python/logs/custodes',
            '/home/ubuntu/ai-backend-python/logs/guardian'
        ]
        
        for log_dir in log_dirs:
            os.makedirs(log_dir, exist_ok=True)
        
        logger.info("Created log directories")
    
    def create_deployment_script(self):
        """Create deployment script"""
        deployment_script = '''#!/bin/bash
# Comprehensive AI Services Fix Deployment Script
echo "Deploying Comprehensive AI Services Fix..."

# Create log directories
echo "Creating log directories..."
mkdir -p /home/ubuntu/ai-backend-python/logs
mkdir -p /home/ubuntu/ai-backend-python/logs/imperium
mkdir -p /home/ubuntu/ai-backend-python/logs/sandbox
mkdir -p /home/ubuntu/ai-backend-python/logs/custodes
mkdir -p /home/ubuntu/ai-backend-python/logs/guardian

# Stop existing services
echo "Stopping existing services..."
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable services
echo "Disabling services..."
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
echo "Removing old service files..."
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Copy new service files
echo "Installing new systemd services..."
sudo cp imperium-ai.service /etc/systemd/system/
sudo cp sandbox-ai.service /etc/systemd/system/
sudo cp custodes-ai.service /etc/systemd/system/
sudo cp guardian-ai.service /etc/systemd/system/

# Set proper permissions
sudo chmod 644 /etc/systemd/system/imperium-ai.service
sudo chmod 644 /etc/systemd/system/sandbox-ai.service
sudo chmod 644 /etc/systemd/system/custodes-ai.service
sudo chmod 644 /etc/systemd/system/guardian-ai.service

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable services
echo "Enabling services..."
sudo systemctl enable imperium-ai.service
sudo systemctl enable sandbox-ai.service
sudo systemctl enable custodes-ai.service
sudo systemctl enable guardian-ai.service

# Start services
echo "Starting services..."
sudo systemctl start imperium-ai.service
sleep 5
sudo systemctl start sandbox-ai.service
sleep 5
sudo systemctl start custodes-ai.service
sleep 5
sudo systemctl start guardian-ai.service

# Check status
echo "Service Status:"
echo "==============="
echo "Imperium AI Service:"
sudo systemctl status imperium-ai.service --no-pager -l
echo ""
echo "Sandbox AI Service:"
sudo systemctl status sandbox-ai.service --no-pager -l
echo ""
echo "Custodes AI Service:"
sudo systemctl status custodes-ai.service --no-pager -l
echo ""
echo "Guardian AI Service:"
sudo systemctl status guardian-ai.service --no-pager -l

echo ""
echo "Comprehensive AI Services Fix deployed successfully!"
echo ""
echo "Configuration Summary:"
echo "• Imperium: Optimization every 45 minutes"
echo "• Sandbox: Experimentation every 45 minutes"
echo "• Custodes: Testing every 45 minutes (alternating comprehensive/regular)"
echo "• Guardian: Self-healing every 60 minutes (with sudo fallback)"
echo ""
echo "Monitor logs with:"
echo "sudo journalctl -u imperium-ai.service -f"
echo "sudo journalctl -u sandbox-ai.service -f"
echo "sudo journalctl -u custodes-ai.service -f"
echo "sudo journalctl -u guardian-ai.service -f"
echo ""
echo "Service logs also available at:"
echo "/home/ubuntu/ai-backend-python/logs/"
'''
        
        with open("deploy_comprehensive_fix.sh", 'w') as f:
            f.write(deployment_script)
        
        os.chmod("deploy_comprehensive_fix.sh", 0o755)
        
        logger.info("Created deployment script")
    
    def create_monitoring_script(self):
        """Create monitoring script"""
        monitoring_script = '''#!/bin/bash
# AI Services Monitoring Script
echo "AI Services Monitoring Dashboard"
echo "================================"
echo ""

# Function to check service status
check_service() {
    local service_name=$1
    local display_name=$2
    
    echo "$display_name Status:"
    if sudo systemctl is-active --quiet $service_name; then
        echo "OK: $display_name is running"
        echo "   PID: $(sudo systemctl show -p MainPID --value $service_name)"
        echo "   Uptime: $(sudo systemctl show -p ActiveEnterTimestamp --value $service_name)"
    else
        echo "ERROR: $display_name is not running"
        echo "   Last error: $(sudo journalctl -u $service_name --no-pager -n 5 --no-full)"
    fi
    echo ""
}

# Check each service
check_service "imperium-ai.service" "Imperium AI"
check_service "sandbox-ai.service" "Sandbox AI"
check_service "custodes-ai.service" "Custodes AI"
check_service "guardian-ai.service" "Guardian AI"

# System resources
echo "System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
echo ""

# Recent logs
echo "Recent Activity (last 10 entries):"
echo "=================================="
for service in imperium-ai sandbox-ai custodes-ai guardian-ai; do
    echo ""
    echo "$service:"
    sudo journalctl -u $service.service --no-pager -n 10 --no-full | grep -E "(error|warning|info)" || echo "   No recent activity"
done
'''
        
        with open("monitor_ai_services.sh", 'w') as f:
            f.write(monitoring_script)
        
        os.chmod("monitor_ai_services.sh", 0o755)
        
        logger.info("Created monitoring script")
    
    async def run_comprehensive_fix(self):
        """Run the comprehensive fix for all AI services"""
        logger.info("Starting Comprehensive AI Services Fix...")
        
        try:
            # Create log directories
            self.create_log_directories()
            
            # Create service files
            self.create_imperium_service()
            self.create_sandbox_service()
            self.create_custodes_service()
            self.create_guardian_service()
            
            # Create deployment and monitoring scripts
            self.create_deployment_script()
            self.create_monitoring_script()
            
            logger.info("Comprehensive AI Services Fix completed successfully!")
            logger.info("Next steps:")
            logger.info("1. Run: chmod +x deploy_comprehensive_fix.sh")
            logger.info("2. Run: ./deploy_comprehensive_fix.sh")
            logger.info("3. Monitor with: ./monitor_ai_services.sh")
            
        except Exception as e:
            logger.error(f"Comprehensive fix failed: {str(e)}")
            raise

async def main():
    """Main function"""
    fixer = ComprehensiveAIServicesFix()
    await fixer.run_comprehensive_fix()

if __name__ == "__main__":
    asyncio.run(main()) 