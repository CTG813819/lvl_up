#!/usr/bin/env python3
"""
Project Warmaster Service Diagnostic Script
==========================================

This script diagnoses connectivity issues with the Project Warmaster service
running on port 8003 of the EC2 instance.
"""

import requests
import socket
import subprocess
import sys
import time

EC2_HOST = "34.202.215.209"
PROJECT_WARMASTER_PORT = 8003
MAIN_BACKEND_PORT = 8000

def test_port_connectivity(host, port, description):
    """Test if a port is reachable"""
    print(f"\n🔍 Testing {description}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ {description} - Port {port} is reachable")
            return True
        else:
            print(f"❌ {description} - Port {port} is not reachable")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def test_http_endpoint(url, description):
    """Test HTTP endpoint"""
    print(f"\n🌐 Testing {description}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ {description} - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"📄 Response: {response.text[:200]}...")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print(f"⏰ {description} - Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 {description} - Connection Error")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_service_status():
    """Check the Project Warmaster service status via SSH"""
    print("\n🔧 Checking Project Warmaster service status...")
    
    try:
        # Check if service is running
        cmd = f'ssh -i "New.pem" ubuntu@{EC2_HOST} "sudo systemctl status horus-project-berserk.service --no-pager"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Service status check successful")
            print(result.stdout)
        else:
            print("❌ Service status check failed")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Service status check timed out")
    except Exception as e:
        print(f"❌ Service status check error: {e}")

def check_port_listening():
    """Check if port 8003 is listening on the server"""
    print("\n🔍 Checking if port 8003 is listening...")
    
    try:
        cmd = f'ssh -i "New.pem" ubuntu@{EC2_HOST} "sudo netstat -tlnp | grep :8003"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Port 8003 is listening")
            print(result.stdout)
        else:
            print("❌ Port 8003 is not listening")
            print("This indicates the service is not properly binding to the port")
            
    except subprocess.TimeoutExpired:
        print("⏰ Port check timed out")
    except Exception as e:
        print(f"❌ Port check error: {e}")

def main():
    print("🔧 Project Warmaster Service Diagnostic")
    print("=" * 50)
    
    # Test basic connectivity
    print("\n📡 Testing basic connectivity...")
    test_port_connectivity(EC2_HOST, PROJECT_WARMASTER_PORT, "Project Warmaster Service")
    test_port_connectivity(EC2_HOST, MAIN_BACKEND_PORT, "Main Backend Service")
    
    # Test HTTP endpoints
    print("\n🌐 Testing HTTP endpoints...")
    test_http_endpoint(f"http://{EC2_HOST}:{PROJECT_WARMASTER_PORT}/api/project-warmaster/status", "Project Warmaster Status")
    test_http_endpoint(f"http://{EC2_HOST}:{PROJECT_WARMASTER_PORT}/docs", "Project Warmaster Docs")
    test_http_endpoint(f"http://{EC2_HOST}:{MAIN_BACKEND_PORT}/api/imperium/status", "Main Backend Status")
    
    # Check service status on server
    check_service_status()
    
    # Check if port is listening
    check_port_listening()
    
    print("\n📋 Summary:")
    print("=" * 30)
    print("If Project Warmaster is not working:")
    print("1. Check if the service is running: sudo systemctl status horus-project-berserk.service")
    print("2. Check if port 8003 is listening: sudo netstat -tlnp | grep :8003")
    print("3. Check service logs: sudo journalctl -u horus-project-berserk.service -f")
    print("4. Restart the service: sudo systemctl restart horus-project-berserk.service")
    print("5. Check firewall settings: sudo ufw status")

if __name__ == "__main__":
    main()