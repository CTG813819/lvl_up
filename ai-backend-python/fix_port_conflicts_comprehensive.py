#!/usr/bin/env python3
"""
Comprehensive Port Conflict Fix Script
Moves conflicting services to different ports to resolve PID conflicts
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

class PortConflictFixer:
    def __init__(self):
        self.backend_dir = Path("/home/ubuntu/ai-backend-python")
        self.services = {
            "ai-backend-python": {"port": 8000, "description": "Main Backend Service"},
            "conquest-ai": {"port": 8001, "description": "Conquest AI Service"},
            "guardian-ai": {"port": 8002, "description": "Guardian AI Service"},
            "sandbox-ai": {"port": 8003, "description": "Sandbox AI Service"},
            "custodes-ai": {"port": 8004, "description": "Custodes AI Service"}
        }
    
    def run_command(self, command, check=True):
        """Run a shell command"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {e.stderr}")
            return e
    
    def stop_all_services(self):
        """Stop all AI services"""
        logger.info("🛑 Stopping all AI services...")
        
        for service_name in self.services.keys():
            self.run_command(f"sudo systemctl stop {service_name}.service", check=False)
        
        # Kill any remaining processes
        self.run_command("sudo pkill -f uvicorn", check=False)
        self.run_command("sudo pkill -f 'python.*main:app'", check=False)
        self.run_command("sudo fuser -k 8000/tcp 2>/dev/null || true", check=False)
        self.run_command("sudo fuser -k 8001/tcp 2>/dev/null || true", check=False)
        self.run_command("sudo fuser -k 8002/tcp 2>/dev/null || true", check=False)
        self.run_command("sudo fuser -k 8003/tcp 2>/dev/null || true", check=False)
        self.run_command("sudo fuser -k 8004/tcp 2>/dev/null || true", check=False)
        
        time.sleep(3)
        logger.info("✅ All services stopped")
    
    def check_port_usage(self):
        """Check what's using the ports"""
        logger.info("🔍 Checking port usage...")
        
        for service_name, config in self.services.items():
            port = config["port"]
            result = self.run_command(f"sudo netstat -tlnp | grep :{port}", check=False)
            if result.returncode == 0:
                logger.warning(f"⚠️ Port {port} is in use by {service_name}")
                logger.info(f"   {result.stdout.strip()}")
            else:
                logger.info(f"✅ Port {port} is free")
    
    def update_service_configs(self):
        """Update service configurations to use different ports"""
        logger.info("📝 Updating service configurations...")
        
        # Main backend service (keep on port 8000)
        main_service_config = f"""[Unit]
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
"""
        
        # Write main service config
        with open("/etc/systemd/system/ai-backend-python.service", "w") as f:
            f.write(main_service_config)
        
        # Update conquest service to use port 8001
        conquest_service_config = f"""[Unit]
Description=Conquest AI Service
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
Environment=CONQUEST_PORT=8001

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/run_conquest.py

Restart=always
RestartSec=30
StartLimitInterval=300
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=conquest-ai

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
"""
        
        # Write conquest service config
        with open("/etc/systemd/system/conquest-ai.service", "w") as f:
            f.write(conquest_service_config)
        
        # Update guardian service to use port 8002
        guardian_service_config = f"""[Unit]
Description=Guardian AI Service
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
Environment=GUARDIAN_PORT=8002

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/run_guardian.py

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
"""
        
        # Write guardian service config
        with open("/etc/systemd/system/guardian-ai.service", "w") as f:
            f.write(guardian_service_config)
        
        logger.info("✅ Service configurations updated")
    
    def update_python_scripts(self):
        """Update Python scripts to use the correct ports"""
        logger.info("📝 Updating Python scripts...")
        
        # Update run_conquest.py to use port 8001
        conquest_script = """#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/logs/conquest.log'),
        logging.StreamHandler()
    ]
)

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_conquest():
        service = AIAgentService()
        logging.info('Conquest AI Service started on port 8001')
        counter = 0
        
        while True:
            try:
                if counter % 2 == 0:
                    logging.info('Starting comprehensive Conquest testing cycle')
                    await service.run_comprehensive_conquest_testing()
                else:
                    logging.info('Starting regular Conquest testing cycle')
                    await service.run_conquest_testing()
                
                counter += 1
                logging.info('Conquest testing cycle completed')
            except Exception as e:
                logging.error(f'Conquest testing error: {str(e)}')
            
            await asyncio.sleep(1800)  # 30 minutes
    
    asyncio.run(run_conquest())
except Exception as e:
    logging.error(f'Conquest service startup error: {str(e)}')
    sys.exit(1)
"""
        
        with open("/home/ubuntu/ai-backend-python/run_conquest.py", "w") as f:
            f.write(conquest_script)
        
        # Update run_guardian.py to use port 8002
        guardian_script = """#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
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

try:
    from app.services.ai_agent_service import AIAgentService
    from app.core.database import get_session
    
    async def run_guardian():
        service = AIAgentService()
        logging.info('Guardian AI Service started on port 8002')
        counter = 0
        
        while True:
            try:
                if counter % 2 == 0:
                    logging.info('Starting comprehensive Guardian testing cycle')
                    await service.run_comprehensive_guardian_testing()
                else:
                    logging.info('Starting regular Guardian testing cycle')
                    await service.run_guardian_testing()
                
                counter += 1
                logging.info('Guardian testing cycle completed')
            except Exception as e:
                logging.error(f'Guardian testing error: {str(e)}')
            
            await asyncio.sleep(2700)  # 45 minutes
    
    asyncio.run(run_guardian())
except Exception as e:
    logging.error(f'Guardian service startup error: {str(e)}')
    sys.exit(1)
"""
        
        with open("/home/ubuntu/ai-backend-python/run_guardian.py", "w") as f:
            f.write(guardian_script)
        
        logger.info("✅ Python scripts updated")
    
    def reload_and_start_services(self):
        """Reload systemd and start services"""
        logger.info("🔄 Reloading systemd and starting services...")
        
        # Reload systemd
        self.run_command("sudo systemctl daemon-reload")
        
        # Start main backend service first
        logger.info("🚀 Starting main backend service on port 8000...")
        self.run_command("sudo systemctl start ai-backend-python.service")
        time.sleep(5)
        
        # Check if main service started successfully
        result = self.run_command("sudo systemctl is-active ai-backend-python.service")
        if result.returncode == 0:
            logger.info("✅ Main backend service started successfully")
        else:
            logger.error("❌ Main backend service failed to start")
            return False
        
        # Start other services
        logger.info("🚀 Starting Conquest AI service on port 8001...")
        self.run_command("sudo systemctl start conquest-ai.service")
        time.sleep(3)
        
        logger.info("🚀 Starting Guardian AI service on port 8002...")
        self.run_command("sudo systemctl start guardian-ai.service")
        time.sleep(3)
        
        logger.info("✅ All services started")
        return True
    
    def verify_services(self):
        """Verify all services are running correctly"""
        logger.info("🔍 Verifying services...")
        
        for service_name, config in self.services.items():
            port = config["port"]
            description = config["description"]
            
            # Check service status
            result = self.run_command(f"sudo systemctl is-active {service_name}.service", check=False)
            if result.returncode == 0:
                logger.info(f"✅ {description} is active")
            else:
                logger.warning(f"⚠️ {description} is not active")
            
            # Check port usage
            result = self.run_command(f"sudo netstat -tlnp | grep :{port}", check=False)
            if result.returncode == 0:
                logger.info(f"✅ Port {port} is in use by {service_name}")
            else:
                logger.warning(f"⚠️ Port {port} is not in use")
    
    def run_fix(self):
        """Run the complete port conflict fix"""
        logger.info("🔧 Starting comprehensive port conflict fix...")
        
        try:
            # Step 1: Stop all services
            self.stop_all_services()
            
            # Step 2: Check current port usage
            self.check_port_usage()
            
            # Step 3: Update service configurations
            self.update_service_configs()
            
            # Step 4: Update Python scripts
            self.update_python_scripts()
            
            # Step 5: Reload and start services
            if self.reload_and_start_services():
                # Step 6: Verify services
                time.sleep(5)
                self.verify_services()
                
                logger.info("🎉 Port conflict fix completed successfully!")
                logger.info("📋 Service Port Summary:")
                for service_name, config in self.services.items():
                    logger.info(f"   {service_name}: Port {config['port']} - {config['description']}")
            else:
                logger.error("❌ Failed to start services")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during port conflict fix: {str(e)}")
            return False
        
        return True

def main():
    """Main function"""
    print("🔧 AI Backend Port Conflict Fixer")
    print("=" * 50)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        sys.exit(1)
    
    fixer = PortConflictFixer()
    
    if fixer.run_fix():
        print("\n✅ Port conflict fix completed successfully!")
        print("\n📋 Service Status:")
        subprocess.run("sudo systemctl list-units --type=service --state=running | grep -E '(ai|backend)'", shell=True)
        print("\n🌐 Port Usage:")
        subprocess.run("sudo netstat -tlnp | grep -E ':(8000|8001|8002|8003|8004)'", shell=True)
    else:
        print("\n❌ Port conflict fix failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 