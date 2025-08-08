#!/usr/bin/env python3
"""
Check Monitoring Log
===================
This script checks the monitoring service log to see what's preventing it from starting.
"""

import os
import subprocess
import time

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result"""
    print(f"🔄 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout}")
        if result.stderr:
            print(f"⚠️  Stderr: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Stderr: {e.stderr}")
        return e

def check_monitoring_log():
    """Check the monitoring service log"""
    print("📄 Checking monitoring service log...")
    
    log_file = "/home/ubuntu/imperium_deployment_fixed/monitoring.log"
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
            print("📋 Monitoring log content:")
            print("=" * 50)
            print(content)
            print("=" * 50)
    else:
        print("❌ Monitoring log file not found")

def check_processes():
    """Check what processes are running"""
    print("🔍 Checking running processes...")
    
    # Check for Python processes
    result = run_command("ps aux | grep python", check=False)
    print("📋 Python processes:")
    print(result.stdout)
    
    # Check for processes on port 4000
    result = run_command("netstat -tlnp | grep :4000", check=False)
    print("🔌 Port 4000 processes:")
    print(result.stdout)

def test_monitoring_service_directly():
    """Test running the monitoring service directly to see errors"""
    print("🧪 Testing monitoring service directly...")
    
    service_dir = "/home/ubuntu/imperium_deployment_fixed"
    service_file = os.path.join(service_dir, "imperium_monitoring_service.py")
    
    if os.path.exists(service_file):
        print("🚀 Running monitoring service directly...")
        
        # Kill any existing processes
        run_command("pkill -f imperium_monitoring_service.py", check=False)
        time.sleep(2)
        
        # Run the service directly to see errors
        result = run_command(f"cd {service_dir} && python3 imperium_monitoring_service.py", check=False)
        
        if result.returncode != 0:
            print("❌ Service failed to start")
            print(f"Error: {result.stderr}")
        else:
            print("✅ Service started successfully")
    else:
        print("❌ Service file not found")

def check_service_file():
    """Check the monitoring service file for issues"""
    print("🔍 Checking monitoring service file...")
    
    service_file = "/home/ubuntu/imperium_deployment_fixed/imperium_monitoring_service.py"
    
    if os.path.exists(service_file):
        print(f"✅ Service file exists: {service_file}")
        
        # Check file size
        size = os.path.getsize(service_file)
        print(f"📏 File size: {size} bytes")
        
        # Check if it's a valid Python file
        result = run_command(f"python3 -m py_compile {service_file}", check=False)
        if result.returncode == 0:
            print("✅ Service file is valid Python")
        else:
            print("❌ Service file has syntax errors")
            print(f"Error: {result.stderr}")
    else:
        print(f"❌ Service file not found: {service_file}")

def main():
    print("🔧 Check Monitoring Log")
    print("=" * 30)
    
    # Check processes
    check_processes()
    
    # Check monitoring log
    check_monitoring_log()
    
    # Check service file
    check_service_file()
    
    # Test service directly
    test_monitoring_service_directly()
    
    print("\n🔍 Check complete!")
    print("💡 Check the output above to identify the issue.")

if __name__ == "__main__":
    main() 