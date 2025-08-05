#!/usr/bin/env python3
"""
Quick Monitoring Fix
===================
Quickly install missing packages and start monitoring service
"""

import subprocess
import time

def run_cmd(cmd):
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Error: {result.stderr.strip()}")
        return False

print("🔧 Quick Monitoring Fix")
print("=" * 30)

# Install missing package
print("\n📦 Installing aiohttp...")
if run_cmd("pip install aiohttp"):
    print("✅ aiohttp installed successfully")
else:
    print("❌ Failed to install aiohttp")
    exit(1)

# Stop any existing service
print("\n🛑 Stopping existing monitoring service...")
run_cmd("pkill -f imperium_monitoring_service.py")

# Start the monitoring service
print("\n🚀 Starting monitoring service...")
start_cmd = "cd /home/ubuntu/imperium_deployment_fixed && nohup python3 imperium_monitoring_service.py > monitoring.log 2>&1 &"
if run_cmd(start_cmd):
    print("✅ Monitoring service started")
    
    # Wait and check
    print("\n⏳ Waiting for service to start...")
    time.sleep(5)
    
    # Check if port 4000 is listening
    print("\n🔍 Checking port 4000...")
    if run_cmd("netstat -tlnp | grep :4000"):
        print("✅ Port 4000 is listening!")
    else:
        print("⚠️  Port 4000 not listening. Checking logs...")
        run_cmd("tail -n 5 /home/ubuntu/imperium_deployment_fixed/monitoring.log")
else:
    print("❌ Failed to start monitoring service")

print("\n🎉 Quick fix complete!") 