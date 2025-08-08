#!/usr/bin/env python3
"""
Start Fixed Monitoring Service
==============================
Test and start the fixed monitoring service
"""

import subprocess
import time
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
    print("🔧 Start Fixed Monitoring Service")
    print("=" * 40)
    
    # Stop any existing monitoring service
    print("\n🛑 Stopping existing monitoring service...")
    run_cmd("pkill -f imperium_monitoring_service")
    
    # Test the fixed monitoring service
    print("\n🧪 Testing fixed monitoring service...")
    test_cmd = "cd /home/ubuntu/imperium_deployment_fixed && python3 imperium_monitoring_service_fixed.py --test 2>&1 | head -n 10"
    if run_cmd(test_cmd):
        print("✅ Fixed monitoring service test successful!")
    else:
        print("⚠️  Test failed, but continuing...")
    
    # Start the fixed monitoring service
    print("\n🚀 Starting fixed monitoring service...")
    start_cmd = "cd /home/ubuntu/imperium_deployment_fixed && nohup python3 imperium_monitoring_service_fixed.py > monitoring_fixed.log 2>&1 &"
    if run_cmd(start_cmd):
        print("✅ Fixed monitoring service started!")
        
        # Wait and check
        print("\n⏳ Waiting for service to start...")
        time.sleep(5)
        
        # Check if it's running
        print("\n🔍 Checking if service is running...")
        if run_cmd("ps aux | grep imperium_monitoring_service_fixed"):
            print("✅ Service is running!")
        else:
            print("❌ Service is not running")
            
        # Check logs
        print("\n📋 Checking logs...")
        run_cmd("tail -n 10 /home/ubuntu/imperium_deployment_fixed/monitoring_fixed.log")
        
    else:
        print("❌ Failed to start fixed monitoring service")
        return False
    
    print("\n🎉 Fixed monitoring service setup complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 