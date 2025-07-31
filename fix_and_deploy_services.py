#!/usr/bin/env python3
"""
Fix and Deploy Guardian and Conquest AI Services
- Fix the unbalanced quoting issue in conquest-ai.service
- Deploy both services to /etc/systemd/system/
- Enable and start the services
- Verify they're working with live data
"""

import subprocess
import time
import requests
import json
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ServiceDeployer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.session.timeout = 30
        
    def create_fixed_guardian_service(self):
        """Create fixed Guardian AI service file"""
        logger.info("🔧 Creating fixed Guardian AI service file...")
        
        service_content = """[Unit]
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
        
        try:
            with open("guardian-ai-fixed.service", "w") as f:
                f.write(service_content)
            logger.info("✅ Fixed Guardian AI service file created")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating Guardian service file: {e}")
            return False
    
    def create_fixed_conquest_service(self):
        """Create fixed Conquest AI service file"""
        logger.info("🔧 Creating fixed Conquest AI service file...")
        
        service_content = """[Unit]
Description=Conquest AI Deployment Service
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
        
        try:
            with open("conquest-ai-fixed.service", "w") as f:
                f.write(service_content)
            logger.info("✅ Fixed Conquest AI service file created")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating Conquest service file: {e}")
            return False
    
    def deploy_service_file(self, service_file, service_name):
        """Deploy service file to systemd directory"""
        try:
            logger.info(f"📦 Deploying {service_name}...")
            
            # Copy service file to systemd directory
            result = subprocess.run(
                ["sudo", "cp", service_file, f"/etc/systemd/system/{service_name}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {service_name} deployed to systemd")
                
                # Set proper permissions
                subprocess.run(["sudo", "chmod", "644", f"/etc/systemd/system/{service_name}"])
                
                # Reload systemd daemon
                reload_result = subprocess.run(
                    ["sudo", "systemctl", "daemon-reload"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if reload_result.returncode == 0:
                    logger.info("✅ Systemd daemon reloaded")
                    return True
                else:
                    logger.error(f"❌ Failed to reload systemd: {reload_result.stderr}")
                    return False
            else:
                logger.error(f"❌ Failed to deploy {service_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deploying {service_name}: {e}")
            return False
    
    def enable_and_start_service(self, service_name):
        """Enable and start a systemd service"""
        try:
            logger.info(f"🚀 Enabling and starting {service_name}...")
            
            # Enable service
            enable_result = subprocess.run(
                ["sudo", "systemctl", "enable", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if enable_result.returncode != 0:
                logger.warning(f"⚠️ Could not enable {service_name}: {enable_result.stderr}")
            
            # Start service
            start_result = subprocess.run(
                ["sudo", "systemctl", "start", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if start_result.returncode == 0:
                logger.info(f"✅ {service_name} started successfully")
                return True
            else:
                logger.error(f"❌ Failed to start {service_name}: {start_result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {service_name}: {e}")
            return False
    
    def check_service_status(self, service_name):
        """Check service status"""
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                if "Active: active (running)" in result.stdout:
                    return "running"
                elif "Active: inactive" in result.stdout:
                    return "stopped"
                elif "Active: failed" in result.stdout:
                    return "failed"
                else:
                    return "unknown"
            else:
                return "not_found"
                
        except Exception as e:
            logger.error(f"Error checking {service_name}: {e}")
            return "error"
    
    def test_ai_endpoint(self, ai_name, timeout=60):
        """Test AI endpoint with live data"""
        try:
            logger.info(f"🧪 Testing {ai_name} endpoint with live data...")
            
            response = self.session.post(
                f"{self.base_url}/api/custody/test/{ai_name}",
                json={"timeout": timeout, "use_live_data": True},
                timeout=timeout + 10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {ai_name} endpoint working with live data")
                logger.info(f"   Response: {result.get('status', 'unknown')}")
                return True
            else:
                logger.warning(f"⚠️ {ai_name} endpoint returned {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏰ {ai_name} endpoint timed out")
            return False
        except Exception as e:
            logger.error(f"❌ {ai_name} endpoint error: {e}")
            return False
    
    def run_deployment(self):
        """Run complete service deployment"""
        logger.info("🚀 Starting Guardian and Conquest AI Service Deployment...")
        logger.info("=" * 60)
        
        # Step 1: Create fixed service files
        if not self.create_fixed_guardian_service():
            return False
        
        if not self.create_fixed_conquest_service():
            return False
        
        # Step 2: Deploy service files
        if not self.deploy_service_file("guardian-ai-fixed.service", "guardian-ai.service"):
            return False
        
        if not self.deploy_service_file("conquest-ai-fixed.service", "conquest-ai.service"):
            return False
        
        # Step 3: Enable and start services
        if not self.enable_and_start_service("guardian-ai.service"):
            logger.warning("⚠️ Guardian AI service failed to start")
        
        if not self.enable_and_start_service("conquest-ai.service"):
            logger.warning("⚠️ Conquest AI service failed to start")
        
        # Step 4: Wait for services to start
        logger.info("⏳ Waiting for services to start...")
        time.sleep(15)
        
        # Step 5: Check service status
        logger.info("🔍 Checking service status...")
        guardian_status = self.check_service_status("guardian-ai.service")
        conquest_status = self.check_service_status("conquest-ai.service")
        
        logger.info(f"Guardian AI: {guardian_status}")
        logger.info(f"Conquest AI: {conquest_status}")
        
        # Step 6: Test endpoints with live data
        logger.info("🧪 Testing AI endpoints with live data...")
        
        ai_services = ["imperium", "guardian", "sandbox", "conquest"]
        test_results = {}
        
        for ai_name in ai_services:
            test_results[ai_name] = self.test_ai_endpoint(ai_name, 120)
        
        # Step 7: Summary
        logger.info("=" * 60)
        logger.info("📊 Deployment Summary:")
        logger.info("=" * 60)
        
        logger.info(f"Guardian AI Service: {guardian_status}")
        logger.info(f"Conquest AI Service: {conquest_status}")
        
        logger.info("Endpoint Test Results:")
        for ai_name, result in test_results.items():
            status = "✅ Working" if result else "❌ Failed"
            logger.info(f"   {ai_name}: {status}")
        
        logger.info("=" * 60)
        logger.info("💡 Next Steps:")
        logger.info("=" * 60)
        
        if guardian_status != "running":
            logger.info("1. Check Guardian AI service logs:")
            logger.info("   journalctl -u guardian-ai.service -f")
        
        if conquest_status != "running":
            logger.info("2. Check Conquest AI service logs:")
            logger.info("   journalctl -u conquest-ai.service -f")
        
        logger.info("3. Monitor all services:")
        logger.info("   systemctl status guardian-ai.service")
        logger.info("   systemctl status conquest-ai.service")
        
        return True

def main():
    """Main entry point"""
    deployer = ServiceDeployer()
    success = deployer.run_deployment()
    
    if success:
        logger.info("✅ Service deployment completed")
        sys.exit(0)
    else:
        logger.error("❌ Service deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 