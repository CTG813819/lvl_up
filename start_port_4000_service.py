#!/usr/bin/env python3
"""
Start Port 4000 Service
=======================
This script starts the monitoring service on port 4000 and opens
the necessary firewall rules.
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
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"❌ Stderr: {e.stderr}")
        return e

def check_port_4000():
    """Check if port 4000 is open"""
    print("🔍 Checking port 4000 status...")
    
    # Check if anything is listening on port 4000
    result = run_command("netstat -tlnp | grep :4000", check=False)
    
    if result.returncode == 0:
        print("✅ Port 4000 is already in use")
        return True
    else:
        print("❌ Port 4000 is not in use")
        return False

def open_firewall_port_4000():
    """Open port 4000 in the firewall"""
    print("🔧 Opening port 4000 in firewall...")
    
    # Open port 4000 in UFW
    result = run_command("sudo ufw allow 4000", check=False)
    if result.returncode == 0:
        print("✅ Port 4000 opened in UFW firewall")
    else:
        print("⚠️  Could not open port 4000 in UFW")
    
    # Also try iptables
    result = run_command("sudo iptables -A INPUT -p tcp --dport 4000 -j ACCEPT", check=False)
    if result.returncode == 0:
        print("✅ Port 4000 opened in iptables")
    else:
        print("⚠️  Could not open port 4000 in iptables")

def start_monitoring_service():
    """Start the monitoring service on port 4000"""
    print("🚀 Starting monitoring service on port 4000...")
    
    # Check if monitoring service files exist
    monitoring_dir = "/home/ubuntu/imperium_deployment_fixed"
    
    if not os.path.exists(monitoring_dir):
        print(f"❌ Monitoring directory not found: {monitoring_dir}")
        return False
    
    # Check for the monitoring service file
    service_file = os.path.join(monitoring_dir, "imperium_monitoring_service.py")
    
    if not os.path.exists(service_file):
        print(f"❌ Monitoring service file not found: {service_file}")
        return False
    
    print(f"✅ Found monitoring service: {service_file}")
    
    # Start the monitoring service in the background
    cmd = f"cd {monitoring_dir} && python3 imperium_monitoring_service.py"
    
    # Run in background
    result = run_command(f"nohup {cmd} > monitoring.log 2>&1 &", cwd=monitoring_dir)
    
    if result.returncode == 0:
        print("✅ Monitoring service started in background")
        return True
    else:
        print("❌ Failed to start monitoring service")
        return False

def test_port_4000():
    """Test if port 4000 is now accessible"""
    print("🧪 Testing port 4000 accessibility...")
    
    # Wait a moment for service to start
    time.sleep(3)
    
    # Test with curl
    result = run_command("curl -s http://localhost:4000/health", check=False)
    
    if result.returncode == 0:
        print("✅ Port 4000 is accessible")
        print(f"📄 Response: {result.stdout}")
        return True
    else:
        print("❌ Port 4000 is not accessible")
        return False

def main():
    print("🔧 Start Port 4000 Service")
    print("=" * 30)
    
    # Check current status
    if check_port_4000():
        print("✅ Port 4000 is already active")
        return True
    
    # Open firewall
    open_firewall_port_4000()
    
    # Start monitoring service
    if not start_monitoring_service():
        return False
    
    # Test the port
    if test_port_4000():
        print("\n✅ Port 4000 service started successfully!")
        return True
    else:
        print("\n❌ Port 4000 service failed to start")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Port 4000 is now open and accessible!")
        print("🚀 You can now run your comprehensive system test again.")
    else:
        print("\n❌ Failed to start port 4000 service")
        exit(1) 