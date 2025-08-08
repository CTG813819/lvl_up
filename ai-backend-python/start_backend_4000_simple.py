#!/usr/bin/env python3
"""
Start Backend 4000 Simple
=========================
Start the backend server on port 4000 using the same approach as port 8000
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
    print("🔧 Start Backend 4000 Simple")
    print("=" * 40)
    
    # Stop any existing processes on port 4000
    print("\n🛑 Stopping existing processes on port 4000...")
    run_cmd("pkill -f 'uvicorn.*4000'")
    run_cmd("pkill -f 'port 4000'")
    time.sleep(3)
    
    # Check if port 8000 is working (as reference)
    print("\n🔍 Checking if port 8000 is working...")
    if run_cmd("curl -s http://localhost:8000/api/imperium/status"):
        print("✅ Port 8000 is working - using same approach")
    else:
        print("❌ Port 8000 is not working")
        return False
    
    # Start backend on port 4000 using the same approach as 8000
    print("\n🚀 Starting backend on port 4000...")
    start_cmd = "cd /home/ubuntu/ai-backend-python && nohup /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000 --workers 1 > backend_4000_new.log 2>&1 &"
    
    if run_cmd(start_cmd):
        print("✅ Backend started!")
        
        # Wait for server to start
        print("\n⏳ Waiting for server to start...")
        time.sleep(15)
        
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
        
        # Check logs
        print("\n📋 Checking backend logs...")
        run_cmd("tail -n 20 /home/ubuntu/ai-backend-python/backend_4000_new.log")
        
    else:
        print("❌ Failed to start backend")
        return False
    
    print("\n🎉 Backend 4000 setup complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 