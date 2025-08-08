#!/usr/bin/env python3
"""
Diagnose Backend Startup
=======================
Check why the backend server isn't starting on port 4000
"""

import subprocess
import time
import sys

def run_cmd(cmd):
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {result.stdout.strip()}")
        return True, result.stdout.strip()
    else:
        print(f"❌ Error: {result.stderr.strip()}")
        return False, result.stderr.strip()

def main():
    print("🔧 Diagnose Backend Startup")
    print("=" * 40)
    
    # Check if any processes are using port 4000
    print("\n🔍 Checking port 4000 usage...")
    run_cmd("netstat -tlnp | grep :4000")
    run_cmd("lsof -i :4000")
    
    # Check if the backend directory exists
    print("\n📁 Checking backend directory...")
    run_cmd("ls -la /home/ubuntu/ai-backend-python/")
    
    # Check if the main app file exists
    print("\n📄 Checking main app file...")
    run_cmd("ls -la /home/ubuntu/ai-backend-python/app/main.py")
    
    # Test the app import directly
    print("\n🧪 Testing app import...")
    test_cmd = "cd /home/ubuntu/ai-backend-python && python3 -c 'from app.main import app; print(\"App imported successfully\")'"
    success, output = run_cmd(test_cmd)
    
    if not success:
        print("❌ App import failed. Let's check the specific error...")
        
        # Try importing individual modules
        print("\n🔍 Testing individual module imports...")
        modules = [
            "app.core.config",
            "app.core.database", 
            "app.services.ai_learning_service",
            "app.services.ml_service",
            "app.routers.imperium"
        ]
        
        for module in modules:
            test_module = f"cd /home/ubuntu/ai-backend-python && python3 -c 'import {module}; print(\"✅ {module} imported\")'"
            run_cmd(test_module)
    
    # Check the backend log file
    print("\n📋 Checking backend log file...")
    run_cmd("ls -la /home/ubuntu/ai-backend-python/backend_4000.log")
    run_cmd("cat /home/ubuntu/ai-backend-python/backend_4000.log")
    
    # Try starting the server in foreground to see errors
    print("\n🚀 Testing server startup in foreground...")
    print("🔄 Starting server in foreground (will show errors)...")
    foreground_cmd = "cd /home/ubuntu/ai-backend-python && timeout 10 /home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 4000"
    success, output = run_cmd(foreground_cmd)
    
    if not success:
        print("❌ Server startup failed. Let's check the Python path...")
        run_cmd("cd /home/ubuntu/ai-backend-python && python3 -c 'import sys; print(\"Python path:\", sys.path)'")
        
        # Check if we're in the right virtual environment
        print("\n🔍 Checking virtual environment...")
        run_cmd("which python3")
        run_cmd("echo $VIRTUAL_ENV")
        run_cmd("cd /home/ubuntu/ai-backend-python && source venv/bin/activate && which python3")
    
    print("\n🎉 Diagnosis complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 