#!/usr/bin/env python3
"""
Deploy Imperium Learning Controller to EC2
Deploys the new Imperium Learning Controller system to the EC2 instance
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Configuration
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER = "ubuntu"
EC2_PORT = 22
BACKEND_DIR = "/home/ubuntu/ai-backend-python"
SERVICE_NAME = "imperium-learning-controller"
SSH_KEY = "C:/projects/lvl_up/New.pem"

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Command successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e.stderr}")
        return False

def run_ssh_command(command):
    """Run a command on the EC2 instance via SSH"""
    ssh_command = f"ssh -i {SSH_KEY} -o StrictHostKeyChecking=no -p {EC2_PORT} {EC2_USER}@{EC2_HOST} '{command}'"
    return run_command(ssh_command)

def copy_file_to_ec2(local_path, remote_path):
    """Copy a file to the EC2 instance"""
    scp_command = f"scp -i {SSH_KEY} -o StrictHostKeyChecking=no -P {EC2_PORT} {local_path} {EC2_USER}@{EC2_HOST}:{remote_path}"
    return run_command(scp_command)

def check_backend_status():
    """Check if the backend is running"""
    try:
        response = requests.get(f"http://{EC2_HOST}:4000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def deploy_imperium_learning_controller():
    """Deploy the Imperium Learning Controller"""
    print("🚀 Deploying Imperium Learning Controller to EC2...")
    
    # Step 1: Check if backend is running
    print("\n1. Checking backend status...")
    if not check_backend_status():
        print("❌ Backend is not running. Please start the backend first.")
        return False
    
    # Step 2: Copy the new service file
    print("\n2. Copying Imperium Learning Controller service...")
    service_file = "ai-backend-python/app/services/imperium_learning_controller.py"
    if not os.path.exists(service_file):
        print(f"❌ Service file not found: {service_file}")
        return False
    
    remote_service_path = f"{BACKEND_DIR}/app/services/imperium_learning_controller.py"
    if not copy_file_to_ec2(service_file, remote_service_path):
        print("❌ Failed to copy service file")
        return False
    
    # Step 3: Copy the router file
    print("\n3. Copying Imperium Learning Controller router...")
    router_file = "ai-backend-python/app/routers/imperium_learning.py"
    if not os.path.exists(router_file):
        print(f"❌ Router file not found: {router_file}")
        return False
    
    remote_router_path = f"{BACKEND_DIR}/app/routers/imperium_learning.py"
    if not copy_file_to_ec2(router_file, remote_router_path):
        print("❌ Failed to copy router file")
        return False
    
    # Step 4: Copy the updated main.py
    print("\n4. Copying updated main.py...")
    main_file = "ai-backend-python/main.py"
    if not os.path.exists(main_file):
        print(f"❌ Main file not found: {main_file}")
        return False
    
    remote_main_path = f"{BACKEND_DIR}/main.py"
    if not copy_file_to_ec2(main_file, remote_main_path):
        print("❌ Failed to copy main.py")
        return False
    
    # Step 5: Restart the backend service
    print("\n5. Restarting backend service...")
    restart_commands = [
        f"cd {BACKEND_DIR}",
        "sudo systemctl stop ai-backend",
        "sleep 2",
        "sudo systemctl start ai-backend",
        "sleep 5"
    ]
    
    for command in restart_commands:
        if not run_ssh_command(command):
            print(f"❌ Failed to execute: {command}")
            return False
    
    # Step 6: Wait for backend to start
    print("\n6. Waiting for backend to start...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_backend_status():
            print("✅ Backend restarted successfully")
            break
        print(f"⏳ Waiting for backend to start... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)
    else:
        print("❌ Backend failed to start after restart")
        return False
    
    # Step 7: Test the new endpoints
    print("\n7. Testing Imperium Learning Controller endpoints...")
    test_endpoints = [
        "/api/imperium/status",
        "/api/imperium/agents",
        "/api/imperium/dashboard"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"http://{EC2_HOST}:4000{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Step 8: Trigger initial learning cycle
    print("\n8. Triggering initial learning cycle...")
    try:
        response = requests.post(f"http://{EC2_HOST}:4000/api/imperium/cycles/trigger", timeout=30)
        if response.status_code == 200:
            print("✅ Initial learning cycle triggered successfully")
        else:
            print(f"⚠️ Learning cycle trigger returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to trigger learning cycle: {e}")
    
    print("\n🎉 Imperium Learning Controller deployment completed!")
    return True

def test_imperium_learning_controller():
    """Test the deployed Imperium Learning Controller"""
    print("\n🧪 Testing Imperium Learning Controller...")
    
    base_url = f"http://{EC2_HOST}:4000"
    
    # Test endpoints
    test_cases = [
        {
            "name": "System Status",
            "method": "GET",
            "endpoint": "/api/imperium/status"
        },
        {
            "name": "All Agents",
            "method": "GET", 
            "endpoint": "/api/imperium/agents"
        },
        {
            "name": "Learning Dashboard",
            "method": "GET",
            "endpoint": "/api/imperium/dashboard"
        },
        {
            "name": "Learning Cycles",
            "method": "GET",
            "endpoint": "/api/imperium/cycles"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            if test_case["method"] == "GET":
                response = requests.get(f"{base_url}{test_case['endpoint']}", timeout=10)
            else:
                response = requests.post(f"{base_url}{test_case['endpoint']}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test_case['name']} - OK")
                results.append({
                    "test": test_case["name"],
                    "status": "PASS",
                    "response_time": response.elapsed.total_seconds()
                })
            else:
                print(f"❌ {test_case['name']} - Status {response.status_code}")
                results.append({
                    "test": test_case["name"],
                    "status": "FAIL",
                    "status_code": response.status_code
                })
                
        except Exception as e:
            print(f"❌ {test_case['name']} - Error: {e}")
            results.append({
                "test": test_case["name"],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Print summary
    print(f"\n📊 Test Summary:")
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
    
    return passed == total

def main():
    """Main deployment function"""
    print("🏆 Imperium Learning Controller Deployment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("ai-backend-python"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Deploy the system
    if deploy_imperium_learning_controller():
        print("\n✅ Deployment successful!")
        
        # Test the deployment
        if test_imperium_learning_controller():
            print("\n🎉 All tests passed! Imperium Learning Controller is ready.")
        else:
            print("\n⚠️ Some tests failed. Please check the system.")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 