#!/usr/bin/env python3
"""
Fix Port 4000 Service
=====================
Fix the service configuration to use port 4000
"""

import subprocess
import sys

def run_cmd(cmd):
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Error: {result.stderr.strip()}")
        return False

def main():
    print("🔧 Fix Port 4000 Service")
    print("=" * 40)
    
    # Stop the current service
    print("\n🛑 Stopping current service...")
    run_cmd("sudo systemctl stop ai-backend-python")
    
    # Check current service configuration
    print("\n📋 Current service configuration:")
    run_cmd("sudo cat /etc/systemd/system/ai-backend-python.service")
    
    # Create new service configuration with port 4000
    print("\n🔧 Creating new service configuration...")
    service_config = """[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10
Environment=DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb"

[Install]
WantedBy=multi-user.target
"""
    
    # Write the new configuration
    with open('/tmp/ai-backend-python.service', 'w') as f:
        f.write(service_config)
    
    # Copy the new configuration
    run_cmd("sudo cp /tmp/ai-backend-python.service /etc/systemd/system/")
    
    # Reload systemd
    print("\n🔄 Reloading systemd...")
    run_cmd("sudo systemctl daemon-reload")
    
    # Enable and start the service
    print("\n🚀 Starting service on port 4000...")
    run_cmd("sudo systemctl enable ai-backend-python")
    run_cmd("sudo systemctl start ai-backend-python")
    
    # Wait for service to start
    import time
    time.sleep(10)
    
    # Check service status
    print("\n🔍 Checking service status...")
    run_cmd("sudo systemctl status ai-backend-python --no-pager")
    
    # Check if port 4000 is listening
    print("\n🔍 Checking if port 4000 is listening...")
    if run_cmd("netstat -tlnp | grep :4000"):
        print("✅ Port 4000 is listening!")
    else:
        print("❌ Port 4000 is not listening")
    
    # Test the API endpoints
    print("\n🧪 Testing API endpoints...")
    test_endpoints = [
        "http://localhost:4000/health",
        "http://localhost:4000/api/imperium/status",
        "http://localhost:4000/api/imperium/agents"
    ]
    
    for endpoint in test_endpoints:
        test_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint}"
        if run_cmd(test_cmd):
            print(f"✅ {endpoint} - Working")
        else:
            print(f"❌ {endpoint} - Failed")
    
    print("\n🎉 Port 4000 service fix complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 