#!/usr/bin/env python3
"""
Fix Service Conflicts Script
============================

This script will fix the ai-backend-python.service to prevent port conflicts
by adding proper stop commands and restart policies.
"""

import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Error running command '{command}': {e}")
        return -1, "", str(e)

def create_improved_service_file():
    """Create an improved service file that handles conflicts properly"""
    logger.info("🔧 Creating improved service configuration...")
    
    service_content = """[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=exec
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

# Prevent port conflicts
ExecStartPre=/bin/bash -c 'pkill -f "uvicorn.*--host 0.0.0.0 --port 8000" || true'
ExecStartPre=/bin/sleep 2

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
    
    # Write the improved service file
    with open('/tmp/ai-backend-python-improved.service', 'w') as f:
        f.write(service_content)
    
    logger.info("✅ Improved service file created")

def install_improved_service():
    """Install the improved service file"""
    logger.info("📦 Installing improved service...")
    
    # Stop the current service
    logger.info("🛑 Stopping current service...")
    run_command("sudo systemctl stop ai-backend-python.service")
    
    # Kill any remaining processes
    logger.info("🔪 Killing any remaining processes...")
    run_command("sudo pkill -f uvicorn")
    run_command("sudo pkill -9 -f uvicorn")
    
    # Wait for processes to be killed
    run_command("sleep 3")
    
    # Copy the improved service file
    logger.info("📋 Installing service file...")
    run_command("sudo cp /tmp/ai-backend-python-improved.service /etc/systemd/system/ai-backend-python.service")
    
    # Reload systemd
    logger.info("🔄 Reloading systemd...")
    run_command("sudo systemctl daemon-reload")
    
    # Enable and start the service
    logger.info("🚀 Enabling and starting service...")
    run_command("sudo systemctl enable ai-backend-python.service")
    run_command("sudo systemctl start ai-backend-python.service")
    
    logger.info("✅ Improved service installed")

def test_service():
    """Test the service"""
    logger.info("🧪 Testing service...")
    
    # Wait for service to start
    run_command("sleep 5")
    
    # Check service status
    code, output, error = run_command("sudo systemctl status ai-backend-python.service")
    if code == 0:
        logger.info("✅ Service status:")
        for line in output.split('\n')[:10]:
            if line.strip():
                logger.info(f"  {line}")
    else:
        logger.error(f"❌ Service status check failed: {error}")
    
    # Test endpoints
    logger.info("🌐 Testing endpoints...")
    
    # Test health endpoint
    code, output, error = run_command("curl -s http://localhost:8000/api/health")
    if code == 0 and output:
        logger.info(f"✅ Health endpoint: {output[:100]}...")
    else:
        logger.error(f"❌ Health endpoint failed: {error}")
    
    # Test status endpoint
    code, output, error = run_command("curl -s http://localhost:8000/api/status")
    if code == 0 and output:
        logger.info(f"✅ Status endpoint: {output[:100]}...")
    else:
        logger.error(f"❌ Status endpoint failed: {error}")

def create_monitoring_script():
    """Create a monitoring script to check for conflicts"""
    logger.info("📊 Creating monitoring script...")
    
    monitor_script = """#!/bin/bash
# Monitor script for ai-backend-python service

echo "=== AI Backend Service Monitor ==="
echo "Timestamp: $(date)"
echo

# Check service status
echo "Service Status:"
sudo systemctl status ai-backend-python.service --no-pager -l
echo

# Check for duplicate processes
echo "Uvicorn Processes:"
ps aux | grep uvicorn | grep -v grep
echo

# Check port usage
echo "Port 8000 Usage:"
sudo netstat -tlnp | grep :8000
echo

# Check system resources
echo "System Resources:"
free -h
echo "CPU Load: $(uptime)"
echo

# Check logs
echo "Recent Logs:"
sudo journalctl -u ai-backend-python.service -n 10 --no-pager
echo

# Test endpoints
echo "Endpoint Tests:"
curl -s http://localhost:8000/api/health | jq . 2>/dev/null || echo "Health endpoint failed"
curl -s http://localhost:8000/api/status | jq . 2>/dev/null || echo "Status endpoint failed"
"""
    
    with open('/home/ubuntu/ai-backend-python/monitor_service.sh', 'w') as f:
        f.write(monitor_script)
    
    run_command("chmod +x /home/ubuntu/ai-backend-python/monitor_service.sh")
    logger.info("✅ Monitoring script created: /home/ubuntu/ai-backend-python/monitor_service.sh")

def main():
    """Main function"""
    logger.info("🚀 Starting service conflict fix...")
    
    # Create improved service file
    create_improved_service_file()
    
    # Install improved service
    install_improved_service()
    
    # Test the service
    test_service()
    
    # Create monitoring script
    create_monitoring_script()
    
    logger.info("✅ Service conflict fix complete!")
    logger.info("📊 Use ./monitor_service.sh to monitor the service")

if __name__ == "__main__":
    main() 