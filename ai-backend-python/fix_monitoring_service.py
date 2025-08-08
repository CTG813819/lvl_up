#!/usr/bin/env python3
"""
Fix Monitoring Service
=====================
Installs missing packages and ensures monitoring service runs correctly
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"🔄 {description}")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🔧 Fix Monitoring Service")
    print("=" * 50)
    
    # Check if we're in the virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print("⚠️  Not in virtual environment. Activating...")
        venv_path = "/home/ubuntu/ai-backend-python/venv"
        if os.path.exists(venv_path):
            activate_script = f"source {venv_path}/bin/activate"
            print(f"   Activating: {activate_script}")
            os.environ['VIRTUAL_ENV'] = venv_path
            os.environ['PATH'] = f"{venv_path}/bin:{os.environ.get('PATH', '')}"
        else:
            print("❌ Virtual environment not found!")
            return False
    
    # Install missing packages
    print("\n📦 Installing missing packages...")
    
    packages = [
        "aiohttp",
        "asyncio",
        "psutil",
        "structlog"
    ]
    
    for package in packages:
        success = run_command(
            f"pip install {package}",
            f"Installing {package}"
        )
        if not success:
            print(f"❌ Failed to install {package}")
            return False
    
    # Stop any existing monitoring service
    print("\n🛑 Stopping existing monitoring service...")
    run_command("pkill -f imperium_monitoring_service.py", "Killing existing processes")
    
    # Test the monitoring service
    print("\n🧪 Testing monitoring service...")
    test_cmd = "cd /home/ubuntu/imperium_deployment_fixed && python3 imperium_monitoring_service.py --test"
    success = run_command(test_cmd, "Testing monitoring service")
    
    if success:
        print("\n✅ Monitoring service test successful!")
        
        # Start the monitoring service in background
        print("\n🚀 Starting monitoring service...")
        start_cmd = "cd /home/ubuntu/imperium_deployment_fixed && nohup python3 imperium_monitoring_service.py > monitoring.log 2>&1 &"
        success = run_command(start_cmd, "Starting monitoring service in background")
        
        if success:
            print("✅ Monitoring service started!")
            
            # Wait a moment and check if it's running
            import time
            time.sleep(3)
            
            # Check if port 4000 is listening
            print("\n🔍 Checking if port 4000 is listening...")
            check_cmd = "netstat -tlnp | grep :4000"
            success = run_command(check_cmd, "Checking port 4000")
            
            if success:
                print("✅ Port 4000 is now listening!")
            else:
                print("⚠️  Port 4000 is not listening yet. Checking logs...")
                run_command("tail -n 10 /home/ubuntu/imperium_deployment_fixed/monitoring.log", "Checking monitoring log")
        else:
            print("❌ Failed to start monitoring service")
            return False
    else:
        print("❌ Monitoring service test failed")
        return False
    
    print("\n🎉 Monitoring service fix complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 