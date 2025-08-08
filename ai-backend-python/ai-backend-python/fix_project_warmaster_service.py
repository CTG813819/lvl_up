#!/usr/bin/env python3
"""
Fix Project Warmaster Service Script
====================================

This script fixes the Project Warmaster service that's not properly binding to port 8003.
"""

import subprocess
import time
import sys

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

def main():
    print("🔧 Fixing Project Warmaster Service")
    print("=" * 40)
    
    # 1. Stop the current service
    print("\n🛑 Stopping Project Warmaster service...")
    run_ssh_command("sudo systemctl stop horus-project-berserk.service", "Stopping service")
    
    # 2. Check current service configuration
    print("\n📋 Checking current service configuration...")
    success, stdout, stderr = run_ssh_command("sudo cat /etc/systemd/system/horus-project-berserk.service", "Reading service config")
    if success:
        print("Current service configuration:")
        print(stdout)
    
    # 3. Check if there are any processes still using port 8003
    print("\n🔍 Checking for processes using port 8003...")
    run_ssh_command("sudo lsof -i :8003", "Checking port usage")
    
    # 4. Kill any remaining processes
    print("\n💀 Killing any remaining processes...")
    run_ssh_command("sudo pkill -f 'uvicorn.*8003'", "Killing uvicorn processes")
    run_ssh_command("sudo pkill -f 'horus-project-berserk'", "Killing service processes")
    
    # 5. Wait a moment
    print("\n⏳ Waiting for processes to stop...")
    time.sleep(5)
    
    # 6. Check if port is now free
    print("\n🔍 Checking if port 8003 is now free...")
    run_ssh_command("sudo netstat -tlnp | grep :8003", "Checking port status")
    
    # 7. Restart the service
    print("\n🚀 Restarting Project Warmaster service...")
    run_ssh_command("sudo systemctl start horus-project-berserk.service", "Starting service")
    
    # 8. Wait for service to start
    print("\n⏳ Waiting for service to start...")
    time.sleep(10)
    
    # 9. Check service status
    print("\n🔍 Checking service status...")
    success, stdout, stderr = run_ssh_command("sudo systemctl status horus-project-berserk.service --no-pager", "Checking service status")
    if success:
        print("Service status:")
        print(stdout)
    
    # 10. Check if port is now listening
    print("\n🔍 Checking if port 8003 is now listening...")
    success, stdout, stderr = run_ssh_command("sudo netstat -tlnp | grep :8003", "Checking port listening")
    if success and stdout.strip():
        print("✅ Port 8003 is now listening!")
        print(stdout)
    else:
        print("❌ Port 8003 is still not listening")
    
    # 11. Test the service locally
    print("\n🧪 Testing service locally...")
    run_ssh_command("curl -s http://localhost:8003/api/project-warmaster/status", "Testing local endpoint")
    
    # 12. Test from external
    print("\n🌐 Testing from external...")
    run_ssh_command("curl -s http://34.202.215.209:8003/api/project-warmaster/status", "Testing external endpoint")
    
    print("\n📋 Summary:")
    print("=" * 30)
    print("If the service is still not working:")
    print("1. Check service logs: sudo journalctl -u horus-project-berserk.service -f")
    print("2. Check if there are any Python errors in the logs")
    print("3. Verify the service configuration is correct")
    print("4. Check if the application code has any issues")
    print("5. Consider restarting the EC2 instance if needed")

if __name__ == "__main__":
    main()