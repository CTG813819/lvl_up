#!/usr/bin/env python3
"""
Fix Port 4000 Backend
=====================
Start the main FastAPI backend server on port 4000
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
    print("🔧 Fix Port 4000 Backend")
    print("=" * 40)
    
    # Stop any existing services on port 4000
    print("\n🛑 Stopping existing services on port 4000...")
    run_cmd("pkill -f 'port 4000'")
    run_cmd("pkill -f 'uvicorn.*4000'")
    run_cmd("pkill -f imperium_monitoring_service")
    
    # Wait for processes to stop
    time.sleep(3)
    
    # Check if we're in the right directory and virtual environment
    print("\n🔍 Checking environment...")
    if not run_cmd("cd /home/ubuntu/ai-backend-python && pwd"):
        print("❌ Cannot access ai-backend-python directory")
        return False
    
    # Check if virtual environment exists
    if not run_cmd("ls /home/ubuntu/ai-backend-python/venv/bin/python3"):
        print("❌ Virtual environment not found")
        return False
    
    # Start the main backend server on port 4000
    print("\n🚀 Starting main backend server on port 4000...")
    start_cmd = "cd /home/ubuntu/ai-backend-python && nohup /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000 > backend_4000.log 2>&1 &"
    
    if run_cmd(start_cmd):
        print("✅ Backend server started!")
        
        # Wait for server to start
        print("\n⏳ Waiting for server to start...")
        time.sleep(10)
        
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
            "http://localhost:4000/api/imperium/agents",
            "http://localhost:4000/docs"
        ]
        
        for endpoint in test_endpoints:
            test_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {endpoint}"
            if run_cmd(test_cmd):
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Failed")
        
        # Check logs
        print("\n📋 Checking backend logs...")
        run_cmd("tail -n 10 /home/ubuntu/ai-backend-python/backend_4000.log")
        
    else:
        print("❌ Failed to start backend server")
        return False
    
    print("\n🎉 Port 4000 backend fix complete!")
    print("\n📊 You can now access:")
    print("   - Main API: http://your-ec2-ip:4000")
    print("   - API Docs: http://your-ec2-ip:4000/docs")
    print("   - Health: http://your-ec2-ip:4000/health")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 