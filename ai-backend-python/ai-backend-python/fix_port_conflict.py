#!/usr/bin/env python3
"""
Diagnostic script to fix port conflict issues with ai-backend-python service
"""

import os
import sys
import subprocess
import time
import signal
import psutil

def run_command(cmd, shell=True):
    """Run a command and return the output"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_port_usage(port):
    """Check what's using a specific port"""
    print(f"🔍 Checking what's using port {port}...")
    
    # Try different methods to check port usage
    commands = [
        f"netstat -tlnp | grep :{port}",
        f"ss -tlnp | grep :{port}",
        f"lsof -i :{port}",
        f"fuser {port}/tcp"
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd)
        if code == 0 and stdout.strip():
            print(f"✅ Found process using port {port}:")
            print(stdout)
            return True
    
    print(f"❌ No process found using port {port}")
    return False

def kill_process_on_port(port):
    """Kill process using a specific port"""
    print(f"🔄 Attempting to kill process on port {port}...")
    
    # Try to find and kill the process
    code, stdout, stderr = run_command(f"fuser -k {port}/tcp")
    if code == 0:
        print(f"✅ Killed process on port {port}")
        return True
    
    # Alternative method using lsof and kill
    code, stdout, stderr = run_command(f"lsof -ti :{port}")
    if code == 0 and stdout.strip():
        pids = stdout.strip().split('\n')
        for pid in pids:
            if pid:
                print(f"🔄 Killing process {pid}...")
                run_command(f"kill -9 {pid}")
        return True
    
    print(f"❌ Could not kill process on port {port}")
    return False

def check_service_status():
    """Check the status of the ai-backend-python service"""
    print("🔍 Checking ai-backend-python service status...")
    
    code, stdout, stderr = run_command("sudo systemctl status ai-backend-python")
    print(stdout)
    
    return code == 0

def restart_service():
    """Restart the ai-backend-python service"""
    print("🔄 Restarting ai-backend-python service...")
    
    # Stop the service
    run_command("sudo systemctl stop ai-backend-python")
    time.sleep(2)
    
    # Start the service
    code, stdout, stderr = run_command("sudo systemctl start ai-backend-python")
    if code == 0:
        print("✅ Service restarted successfully")
    else:
        print(f"❌ Failed to restart service: {stderr}")
    
    return code == 0

def check_alternative_ports():
    """Check if alternative ports are available"""
    print("🔍 Checking alternative ports...")
    
    alternative_ports = [4001, 4002, 8000, 8001, 8080, 8081]
    
    for port in alternative_ports:
        code, stdout, stderr = run_command(f"netstat -tlnp | grep :{port}")
        if code != 0 or not stdout.strip():
            print(f"✅ Port {port} is available")
            return port
    
    print("❌ No alternative ports found")
    return None

def update_service_port(new_port):
    """Update the service file to use a new port"""
    print(f"🔄 Updating service to use port {new_port}...")
    
    service_file = "/etc/systemd/system/ai-backend-python.service"
    
    # Read current service file
    try:
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Replace port 4000 with new port
        new_content = content.replace("--port 4000", f"--port {new_port}")
        
        # Write updated content
        with open(service_file, 'w') as f:
            f.write(new_content)
        
        # Reload systemd
        run_command("sudo systemctl daemon-reload")
        
        print(f"✅ Service updated to use port {new_port}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update service file: {e}")
        return False

def main():
    """Main diagnostic and fix function"""
    print("🚀 AI Backend Python Service Port Conflict Fixer")
    print("=" * 50)
    
    port = 4000
    
    # Step 1: Check current service status
    print("\n1️⃣ Checking current service status...")
    check_service_status()
    
    # Step 2: Check what's using port 4000
    print("\n2️⃣ Checking port usage...")
    port_in_use = check_port_usage(port)
    
    if port_in_use:
        # Step 3: Try to kill the process using the port
        print("\n3️⃣ Attempting to free port...")
        if kill_process_on_port(port):
            time.sleep(2)
            
            # Step 4: Restart the service
            print("\n4️⃣ Restarting service...")
            if restart_service():
                print("\n✅ Service should now be running!")
                time.sleep(3)
                check_service_status()
                return
        
        # If killing didn't work, try alternative port
        print("\n3️⃣ Trying alternative port...")
        alt_port = check_alternative_ports()
        if alt_port:
            if update_service_port(alt_port):
                restart_service()
                time.sleep(3)
                check_service_status()
                return
    
    # If we get here, try restarting anyway
    print("\n4️⃣ Restarting service...")
    restart_service()
    time.sleep(3)
    check_service_status()

if __name__ == "__main__":
    main() 