#!/usr/bin/env python3
"""
Comprehensive Project Warmaster Service Fix
==========================================

This script addresses the event loop issues and ensures proper service binding.
"""

import subprocess
import time
import sys
import os

EC2_HOST = "34.202.215.209"
SSH_KEY = "New.pem"
SSH_USER = "ubuntu"

def run_ssh_command(command, description=""):
    """Run a command via SSH on the EC2 instance"""
    full_command = f'ssh -i {SSH_KEY} {SSH_USER}@{EC2_HOST} "{command}"'
    
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description or 'Command executed successfully'}")
            return True, result.stdout, result.stderr
        else:
            print(f"❌ {description or 'Command failed'}: {result.stderr}")
            return False, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description or 'Command timed out'}")
        return False, "", "Timeout"
    except Exception as e:
        print(f"💥 {description or 'Command error'}: {e}")
        return False, "", str(e)

def create_fixed_service_config():
    """Create a fixed service configuration that addresses event loop issues"""
    service_config = """[Unit]
Description=HORUS Project Berserk AI System
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --workers 1
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
"""
    return service_config

def main():
    print("🔧 Comprehensive Project Warmaster Service Fix")
    print("=" * 50)
    
    # 1. Stop the current service
    print("\n🛑 Stopping Project Warmaster service...")
    run_ssh_command("sudo systemctl stop horus-project-berserk.service", "Stopping service")
    
    # 2. Kill any remaining processes
    print("\n💀 Killing any remaining processes...")
    run_ssh_command("sudo pkill -f 'uvicorn.*8003'", "Killing uvicorn processes")
    run_ssh_command("sudo pkill -f 'horus-project-berserk'", "Killing service processes")
    run_ssh_command("sudo pkill -f 'python.*8003'", "Killing Python processes on port 8003")
    
    # 3. Wait for processes to stop
    print("\n⏳ Waiting for processes to stop...")
    time.sleep(10)
    
    # 4. Check if port is now free
    print("\n🔍 Checking if port 8003 is now free...")
    run_ssh_command("sudo lsof -i :8003", "Checking port usage")
    
    # 5. Create fixed service configuration
    print("\n🔧 Creating fixed service configuration...")
    service_config = create_fixed_service_config()
    
    # Write config to a temporary file
    with open('/tmp/horus-project-berserk-fixed.service', 'w') as f:
        f.write(service_config)
    
    # 6. Upload and apply the fixed configuration
    print("\n📤 Uploading fixed service configuration...")
    run_ssh_command("sudo cp /tmp/horus-project-berserk-fixed.service /etc/systemd/system/horus-project-berserk.service", "Applying fixed config")
    
    # 7. Reload systemd
    print("\n🔄 Reloading systemd...")
    run_ssh_command("sudo systemctl daemon-reload", "Reloading systemd")
    
    # 8. Enable and start the service
    print("\n🚀 Starting Project Warmaster service with fixed configuration...")
    run_ssh_command("sudo systemctl enable horus-project-berserk.service", "Enabling service")
    run_ssh_command("sudo systemctl start horus-project-berserk.service", "Starting service")
    
    # 9. Wait for service to start
    print("\n⏳ Waiting for service to start...")
    time.sleep(15)
    
    # 10. Check service status
    print("\n🔍 Checking service status...")
    success, stdout, stderr = run_ssh_command("sudo systemctl status horus-project-berserk.service --no-pager", "Checking service status")
    if success:
        print("Service status:")
        print(stdout)
    
    # 11. Check if port is now listening
    print("\n🔍 Checking if port 8003 is now listening...")
    success, stdout, stderr = run_ssh_command("sudo netstat -tlnp | grep :8003", "Checking port listening")
    if success and stdout.strip():
        print("✅ Port 8003 is now listening!")
        print(stdout)
    else:
        print("❌ Port 8003 is still not listening")
    
    # 12. Check service logs for any errors
    print("\n📋 Checking service logs...")
    run_ssh_command("sudo journalctl -u horus-project-berserk.service --no-pager -n 20", "Checking recent logs")
    
    # 13. Test the service locally
    print("\n🧪 Testing service locally...")
    run_ssh_command("curl -s http://localhost:8003/api/project-warmaster/status", "Testing local endpoint")
    
    # 14. Test from external
    print("\n🌐 Testing from external...")
    run_ssh_command("curl -s http://34.202.215.209:8003/api/project-warmaster/status", "Testing external endpoint")
    
    # 15. Test docs endpoint
    print("\n📚 Testing docs endpoint...")
    run_ssh_command("curl -s http://34.202.215.209:8003/docs", "Testing docs endpoint")
    
    print("\n📋 Summary:")
    print("=" * 30)
    print("If the service is still not working:")
    print("1. Check service logs: sudo journalctl -u horus-project-berserk.service -f")
    print("2. Check if there are any Python errors in the logs")
    print("3. Verify the service configuration is correct")
    print("4. Check if the application code has any issues")
    print("5. Consider restarting the EC2 instance if needed")
    print("6. Check firewall settings: sudo ufw status")

if __name__ == "__main__":
    main()