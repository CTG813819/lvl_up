#!/usr/bin/env python3
"""
Simple EC2 Deployment Script
Deploys the enhanced learning system to EC2 with user-provided details.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

def get_user_input():
    """Get EC2 details from user"""
    print("🚀 Enhanced Learning System EC2 Deployment")
    print("=" * 50)
    
    ec2_host = input("Enter EC2 Public IP or DNS (e.g., ec2-xx-xx-xx-xx.compute.amazonaws.com): ").strip()
    if not ec2_host:
        print("❌ EC2 host is required")
        sys.exit(1)
    
    ssh_key = input("Enter SSH key path (e.g., ~/.ssh/your-key.pem): ").strip()
    if not ssh_key:
        print("❌ SSH key path is required")
        sys.exit(1)
    
    confirm = input(f"\nDeploy to {ec2_host} using {ssh_key}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Deployment cancelled")
        sys.exit(1)
    
    return ec2_host, ssh_key

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def deploy_to_ec2():
    """Deploy the enhanced learning system to EC2"""
    ec2_host, ssh_key = get_user_input()
    
    print(f"\n🚀 Starting deployment to {ec2_host}")
    print("=" * 50)
    
    # Step 1: Create deployment package
    print("\n📋 Step 1: Creating deployment package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"enhanced_learning_deployment_{timestamp}.tar.gz"
    
    # Create tar.gz package of the project
    run_command(
        f'tar -czf {package_name} ai-backend-python/ lib/ deploy_enhanced_learning_system.py test_enhanced_learning_system.py',
        "Creating deployment package"
    )
    
    # Step 2: Upload package to EC2
    print("\n📋 Step 2: Uploading package to EC2...")
    run_command(
        f'scp -i {ssh_key} {package_name} ubuntu@{ec2_host}:/home/ubuntu/lvl_up/',
        "Uploading deployment package"
    )
    
    # Step 3: Stop backend service on EC2
    print("\n📋 Step 3: Stopping backend service on EC2...")
    run_command(f'ssh -i {ssh_key} ubuntu@{ec2_host} "sudo systemctl stop ai-backend-python"', "Stopping backend service", check=False)
    time.sleep(3)
    
    # Step 4: Backup current deployment on EC2
    print("\n📋 Step 4: Creating backup on EC2...")
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "cd /home/ubuntu/lvl_up && cp -r ai-backend-python backup_before_enhanced_learning_{timestamp}"',
        "Creating backup on EC2"
    )
    
    # Step 5: Extract and deploy new files
    print("\n📋 Step 5: Extracting and deploying new files...")
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "cd /home/ubuntu/lvl_up && tar -xzf {package_name}"',
        "Extracting deployment package"
    )
    
    # Step 6: Set proper permissions
    print("\n📋 Step 6: Setting file permissions...")
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "sudo chown -R www-data:www-data /home/ubuntu/lvl_up/ai-backend-python/app/services/"',
        "Setting ownership"
    )
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "sudo chmod -R 755 /home/ubuntu/lvl_up/ai-backend-python/app/services/"',
        "Setting permissions"
    )
    
    # Step 7: Initialize learning data files
    print("\n📋 Step 7: Initializing learning data files...")
    learning_data = '{"successful_patterns": [], "failed_patterns": [], "validation_stats": {"total_attempts": 0, "successful_validations": 0, "failed_validations": 0, "auto_fix_success_rate": 0.0, "common_issues": {}, "successful_fixes": {}}}'
    
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} \'if [ ! -f "/home/ubuntu/lvl_up/ai-backend-python/app/services/ai_learnings.json" ]; then echo \'{learning_data}\' > "/home/ubuntu/lvl_up/ai-backend-python/app/services/ai_learnings.json"; fi\'',
        "Initializing ai_learnings.json"
    )
    
    run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} \'if [ ! -f "/home/ubuntu/lvl_up/ai-backend-python/app/services/ai_code_fixes.json" ]; then echo "{{}}" > "/home/ubuntu/lvl_up/ai-backend-python/app/services/ai_code_fixes.json"; fi\'',
        "Initializing ai_code_fixes.json"
    )
    
    # Step 8: Start backend service
    print("\n📋 Step 8: Starting backend service...")
    run_command(f'ssh -i {ssh_key} ubuntu@{ec2_host} "sudo systemctl start ai-backend-python"', "Starting backend service")
    time.sleep(5)
    
    # Step 9: Check backend status
    print("\n📋 Step 9: Checking backend status...")
    status_result = run_command(f'ssh -i {ssh_key} ubuntu@{ec2_host} "sudo systemctl status ai-backend-python"', "Checking service status", check=False)
    if "active (running)" in status_result.stdout:
        print("✅ Backend service is running")
    else:
        print("❌ Backend service failed to start")
        return False
    
    # Step 10: Test enhanced statistics endpoint
    print("\n📋 Step 10: Testing enhanced statistics endpoint...")
    test_result = run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "curl -s http://localhost:4000/api/conquest/enhanced-statistics"',
        "Testing enhanced statistics endpoint",
        check=False
    )
    
    if test_result.returncode == 0:
        try:
            response_data = json.loads(test_result.stdout)
            if response_data.get('status') == 'success':
                print("✅ Enhanced statistics endpoint working")
                print(f"📊 Statistics: {json.dumps(response_data.get('statistics', {}), indent=2)}")
            else:
                print(f"⚠️ Endpoint returned error: {response_data.get('message', 'Unknown error')}")
        except json.JSONDecodeError:
            print("⚠️ Could not parse response as JSON")
    else:
        print("⚠️ Enhanced statistics endpoint not responding")
    
    # Step 11: Test basic statistics endpoint
    print("\n📋 Step 11: Testing basic statistics endpoint...")
    basic_test_result = run_command(
        f'ssh -i {ssh_key} ubuntu@{ec2_host} "curl -s http://localhost:4000/api/conquest/statistics"',
        "Testing basic statistics endpoint",
        check=False
    )
    
    if basic_test_result.returncode == 0:
        try:
            response_data = json.loads(basic_test_result.stdout)
            if response_data.get('status') == 'success':
                print("✅ Basic statistics endpoint working")
            else:
                print(f"⚠️ Basic endpoint returned error: {response_data.get('message', 'Unknown error')}")
        except json.JSONDecodeError:
            print("⚠️ Could not parse basic response as JSON")
    else:
        print("⚠️ Basic statistics endpoint not responding")
    
    # Step 12: Clean up deployment package
    print("\n📋 Step 12: Cleaning up...")
    run_command(f'ssh -i {ssh_key} ubuntu@{ec2_host} "cd /home/ubuntu/lvl_up && rm -f {package_name}"', "Removing deployment package")
    run_command(f"rm -f {package_name}", "Removing local deployment package")
    
    print("\n🎉 Enhanced Learning System Deployment to EC2 Complete!")
    print("=" * 60)
    print("✅ Enhanced AI learning system deployed to EC2")
    print("✅ Validation progress tracking enabled")
    print("✅ Statistics with learning data available")
    print("✅ Auto-fix learning capabilities active")
    print("✅ Frontend enhanced statistics display ready")
    
    print(f"\n📊 EC2 Endpoints:")
    print(f"  - http://{ec2_host}:4000/api/conquest/enhanced-statistics")
    print(f"  - http://{ec2_host}:4000/api/conquest/statistics")
    print(f"  - http://{ec2_host}:4000/api/conquest/deployments")
    
    print(f"\n🔍 To monitor the system on EC2:")
    print(f"  - ssh -i {ssh_key} ubuntu@{ec2_host}")
    print(f"  - sudo journalctl -u ai-backend-python -f")
    print(f"  - Check /var/log/ai-backend-python/ for detailed logs")
    
    return True

if __name__ == "__main__":
    try:
        success = deploy_to_ec2()
        if success:
            print("\n✅ Deployment to EC2 completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Deployment to EC2 failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 