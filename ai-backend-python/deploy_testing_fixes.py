#!/usr/bin/env python3
"""
Deploy testing fixes to EC2 instance
"""

import os
import subprocess
import sys
from pathlib import Path

# EC2 instance details (update these with your actual values)
EC2_HOST = "your-ec2-ip-address"  # Replace with your EC2 IP
EC2_USER = "ubuntu"  # Replace with your EC2 username
EC2_KEY_PATH = "path/to/your/key.pem"  # Replace with your key path

def run_ssh_command(command):
    """Run a command on EC2 via SSH"""
    ssh_cmd = f"ssh -i {EC2_KEY_PATH} -o StrictHostKeyChecking=no {EC2_USER}@{EC2_HOST} '{command}'"
    print(f"🔧 Running: {command}")
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result

def upload_file(local_path, remote_path):
    """Upload a file to EC2"""
    scp_cmd = f"scp -i {EC2_KEY_PATH} -o StrictHostKeyChecking=no {local_path} {EC2_USER}@{EC2_HOST}:{remote_path}"
    print(f"📤 Uploading: {local_path} -> {remote_path}")
    result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
    return result

def deploy_testing_fixes():
    """Deploy all testing fixes to EC2"""
    print("🚀 Deploying testing fixes to EC2...")
    
    # 1. Install testing dependencies
    print("\n📦 Installing testing dependencies...")
    install_script = """
    sudo apt-get update
    sudo apt-get install -y python3-pip
    pip3 install flake8
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo apt-get install -y apt-transport-https
    wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'wget -qO- https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
    sudo apt-get update
    sudo apt-get install -y dart
    """
    
    result = run_ssh_command(install_script)
    if result.returncode == 0:
        print("✅ Testing dependencies installed successfully")
    else:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False
    
    # 2. Upload updated files
    print("\n📤 Uploading updated files...")
    
    files_to_upload = [
        ("ai-backend-python/app/routers/proposals.py", "/home/ubuntu/ai-backend-python/app/routers/proposals.py"),
        ("ai-backend-python/app/services/testing_service.py", "/home/ubuntu/ai-backend-python/app/services/testing_service.py"),
        ("ai-backend-python/.env", "/home/ubuntu/ai-backend-python/.env"),
        ("retest_pending_proposals.py", "/home/ubuntu/retest_pending_proposals.py"),
    ]
    
    for local_path, remote_path in files_to_upload:
        if os.path.exists(local_path):
            result = upload_file(local_path, remote_path)
            if result.returncode == 0:
                print(f"✅ Uploaded: {local_path}")
            else:
                print(f"❌ Failed to upload {local_path}: {result.stderr}")
        else:
            print(f"⚠️  File not found: {local_path}")
    
    # 3. Restart the backend service
    print("\n🔄 Restarting backend service...")
    restart_cmd = """
    cd /home/ubuntu/ai-backend-python
    sudo systemctl restart ai-backend
    sudo systemctl status ai-backend
    """
    
    result = run_ssh_command(restart_cmd)
    if result.returncode == 0:
        print("✅ Backend service restarted successfully")
    else:
        print(f"❌ Failed to restart service: {result.stderr}")
    
    # 4. Run the retesting script on EC2
    print("\n🧪 Running proposal retesting on EC2...")
    retest_cmd = """
    cd /home/ubuntu
    python3 retest_pending_proposals.py
    """
    
    result = run_ssh_command(retest_cmd)
    if result.returncode == 0:
        print("✅ Proposal retesting completed successfully")
        print(result.stdout)
    else:
        print(f"❌ Failed to retest proposals: {result.stderr}")
    
    print("\n🎉 Deployment completed!")

def main():
    """Main function"""
    print("🚀 EC2 Testing Fixes Deployment")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        "ai-backend-python/app/routers/proposals.py",
        "ai-backend-python/app/services/testing_service.py",
        "ai-backend-python/.env",
        "retest_pending_proposals.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        return
    
    # Check if EC2 details are configured
    if EC2_HOST == "your-ec2-ip-address":
        print("❌ Please update the EC2_HOST variable in this script")
        return
    
    if not os.path.exists(EC2_KEY_PATH):
        print(f"❌ SSH key not found: {EC2_KEY_PATH}")
        return
    
    deploy_testing_fixes()

if __name__ == "__main__":
    main() 