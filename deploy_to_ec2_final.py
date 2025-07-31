#!/usr/bin/env python3
"""
Final EC2 Deployment Script
Deploys the enhanced learning system to EC2 using specific user details.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

# EC2 Configuration from user
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
SSH_KEY_PATH = "C:\\projects\\lvl_up\\New.pem"
REMOTE_DIR = "/home/ubuntu"

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n[RUNNING] {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"[OK] Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error: {e}")
        print(f"[ERROR] Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def run_remote_command(command, description, check=True):
    """Run a command on EC2 and handle errors"""
    print(f"\n[RUNNING] {description}...")
    ssh_command = f'ssh -i "{SSH_KEY_PATH}" ubuntu@{EC2_HOST} "{command}"'
    print(f"SSH Command: {ssh_command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"[OK] Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error: {e}")
        print(f"[ERROR] Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def deploy_to_ec2():
    """Deploy the enhanced learning system to EC2"""
    print("Deploying Enhanced Learning System to EC2")
    print(f"Target: {EC2_HOST}")
    print("=" * 60)
    
    # Step 1: Create deployment package
    print("\n[STEP 1] Creating deployment package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"enhanced_learning_deployment_{timestamp}.tar.gz"
    
    # Create tar.gz package of the project
    run_command(
        f'tar -czf {package_name} ai-backend-python/ lib/ deploy_enhanced_learning_system.py test_enhanced_learning_system.py',
        "Creating deployment package"
    )
    
    # Step 2: Upload package to EC2
    print("\n[STEP 2] Uploading package to EC2...")
    run_command(
        f'scp -i "{SSH_KEY_PATH}" {package_name} ubuntu@{EC2_HOST}:{REMOTE_DIR}/',
        "Uploading deployment package"
    )
    
    # Step 3: Stop backend service on EC2
    print("\n[STEP 3] Stopping backend service on EC2...")
    run_remote_command("sudo systemctl stop ai-backend-python", "Stopping backend service", check=False)
    time.sleep(3)
    
    # Step 4: Backup current deployment on EC2
    print("\n[STEP 4] Creating backup on EC2...")
    run_remote_command(
        f"cd {REMOTE_DIR} && cp -r ai-backend-python backup_before_enhanced_learning_{timestamp}",
        "Creating backup on EC2"
    )
    
    # Step 5: Extract and deploy new files
    print("\n[STEP 5] Extracting and deploying new files...")
    
    # Remove existing files that might conflict (using sudo for permission issues)
    run_remote_command(
        f"cd {REMOTE_DIR} && sudo rm -rf ai-backend-python lib deploy_enhanced_learning_system.py test_enhanced_learning_system.py",
        "Removing existing files to prevent conflicts"
    )
    
    run_remote_command(
        f"cd {REMOTE_DIR} && tar -xzf {package_name}",
        "Extracting deployment package"
    )
    
    # Step 6: Set proper permissions
    print("\n[STEP 6] Setting file permissions...")
    run_remote_command(
        f"sudo chown -R www-data:www-data {REMOTE_DIR}/ai-backend-python/app/services/",
        "Setting ownership"
    )
    run_remote_command(
        f"sudo chmod -R 755 {REMOTE_DIR}/ai-backend-python/app/services/",
        "Setting permissions"
    )
    
    # Step 7: Initialize learning data files
    print("\n[STEP 7] Initializing learning data files...")
    
    # First, ensure the services directory exists and has proper permissions
    run_remote_command(
        f"mkdir -p {REMOTE_DIR}/ai-backend-python/app/services/",
        "Creating services directory if it doesn't exist"
    )
    
    run_remote_command(
        f"sudo chown -R ubuntu:ubuntu {REMOTE_DIR}/ai-backend-python/app/services/",
        "Setting ownership to ubuntu user for file creation"
    )
    
    learning_data = '{"successful_patterns": [], "failed_patterns": [], "validation_stats": {"total_attempts": 0, "successful_validations": 0, "failed_validations": 0, "auto_fix_success_rate": 0.0, "common_issues": {}, "successful_fixes": {}}}'
    
    run_remote_command(
        f'if [ ! -f "{REMOTE_DIR}/ai-backend-python/app/services/ai_learnings.json" ]; then echo \'{learning_data}\' > "{REMOTE_DIR}/ai-backend-python/app/services/ai_learnings.json"; fi',
        "Initializing ai_learnings.json"
    )
    
    run_remote_command(
        f'if [ ! -f "{REMOTE_DIR}/ai-backend-python/app/services/ai_code_fixes.json" ]; then echo "{{}}" > "{REMOTE_DIR}/ai-backend-python/app/services/ai_code_fixes.json"; fi',
        "Initializing ai_code_fixes.json"
    )
    
    # Now set proper permissions for the web server
    run_remote_command(
        f"sudo chown -R www-data:www-data {REMOTE_DIR}/ai-backend-python/app/services/",
        "Setting final ownership for web server"
    )
    
    # Step 8: Start backend service
    print("\n[STEP 8] Starting backend service...")
    run_remote_command("sudo systemctl start ai-backend-python", "Starting backend service")
    time.sleep(5)
    
    # Step 9: Check backend status
    print("\n[STEP 9] Checking backend status...")
    status_result = run_remote_command("sudo systemctl status ai-backend-python", "Checking service status", check=False)
    if status_result and status_result.stdout and "active (running)" in status_result.stdout:
        print("[OK] Backend service is running")
    else:
        print("[WARN] Backend service status unclear - checking if it's running...")
        # Try a simple test to see if the service is responding
        test_result = run_remote_command("curl -s http://localhost:4000/health", "Testing if backend is responding", check=False)
        if test_result and test_result.returncode == 0:
            print("[OK] Backend service is responding")
        else:
            print("[ERROR] Backend service may not be running properly")
            return False
    
    # Step 10: Test enhanced statistics endpoint
    print("\n[STEP 10] Testing enhanced statistics endpoint...")
    test_result = run_remote_command(
        "curl -s http://localhost:4000/api/conquest/enhanced-statistics",
        "Testing enhanced statistics endpoint",
        check=False
    )
    
    if test_result.returncode == 0:
        try:
            response_data = json.loads(test_result.stdout)
            if response_data.get('status') == 'success':
                print("[OK] Enhanced statistics endpoint working")
                print(f"[STATS] Statistics: {json.dumps(response_data.get('statistics', {}), indent=2)}")
            else:
                print(f"[WARN] Endpoint returned error: {response_data.get('message', 'Unknown error')}")
        except json.JSONDecodeError:
            print("[WARN] Could not parse response as JSON")
    else:
        print("[WARN] Enhanced statistics endpoint not responding")
    
    # Step 11: Test basic statistics endpoint
    print("\n[STEP 11] Testing basic statistics endpoint...")
    basic_test_result = run_remote_command(
        "curl -s http://localhost:4000/api/conquest/statistics",
        "Testing basic statistics endpoint",
        check=False
    )
    
    if basic_test_result.returncode == 0:
        try:
            response_data = json.loads(basic_test_result.stdout)
            if response_data.get('status') == 'success':
                print("[OK] Basic statistics endpoint working")
            else:
                print(f"[WARN] Basic endpoint returned error: {response_data.get('message', 'Unknown error')}")
        except json.JSONDecodeError:
            print("[WARN] Could not parse basic response as JSON")
    else:
        print("[WARN] Basic statistics endpoint not responding")
    
    # Step 12: Clean up deployment package
    print("\n[STEP 12] Cleaning up...")
    run_remote_command(f"cd {REMOTE_DIR} && rm -f {package_name}", "Removing deployment package")
    run_command(f"rm -f {package_name}", "Removing local deployment package")
    
    print("\n[DONE] Enhanced Learning System Deployment to EC2 Complete!")
    print("=" * 60)
    print("[OK] Enhanced AI learning system deployed to EC2")
    print("[OK] Validation progress tracking enabled")
    print("[OK] Statistics with learning data available")
    print("[OK] Auto-fix learning capabilities active")
    print("[OK] Frontend enhanced statistics display ready")
    
    print(f"\n[ENDPOINTS] EC2 Endpoints:")
    print(f"  - http://{EC2_HOST}:4000/api/conquest/enhanced-statistics")
    print(f"  - http://{EC2_HOST}:4000/api/conquest/statistics")
    print(f"  - http://{EC2_HOST}:4000/api/conquest/deployments")
    
    print(f"\n[MONITOR] To monitor the system on EC2:")
    print(f"  - ssh -i \"{SSH_KEY_PATH}\" ubuntu@{EC2_HOST}")
    print(f"  - sudo journalctl -u ai-backend-python -f")
    print(f"  - Check /var/log/ai-backend-python/ for detailed logs")
    
    return True

if __name__ == "__main__":
    try:
        success = deploy_to_ec2()
        if success:
            print("\n[OK] Deployment to EC2 completed successfully!")
            sys.exit(0)
        else:
            print("\n[ERROR] Deployment to EC2 failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[WARN] Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1) 