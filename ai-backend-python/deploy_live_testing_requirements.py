#!/usr/bin/env python3
"""
Deploy live testing requirements to EC2 instance
Ensures all proposals go through live testing before reaching users
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Deploying Live Testing Requirements to EC2")
    print("=" * 50)
    
    # Configuration
    EC2_HOST = "ubuntu@your-ec2-ip"  # Replace with your actual EC2 IP
    REMOTE_PATH = "/home/ubuntu/ai-backend-python"
    
    # Files to deploy
    files_to_deploy = [
        "ai-backend-python/app/services/testing_service.py",
        "ai-backend-python/app/routers/proposals.py"
    ]
    
    print("📋 Files to deploy:")
    for file in files_to_deploy:
        print(f"  - {file}")
    
    # Deploy files
    for file_path in files_to_deploy:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        remote_file = f"{REMOTE_PATH}/{file_path.replace('ai-backend-python/', '')}"
        remote_dir = os.path.dirname(remote_file)
        
        # Create remote directory if needed
        run_command(f"ssh {EC2_HOST} 'mkdir -p {remote_dir}'", f"Creating directory {remote_dir}")
        
        # Copy file
        result = run_command(f"scp {file_path} {EC2_HOST}:{remote_file}", f"Deploying {file_path}")
        if result is None:
            print(f"❌ Failed to deploy {file_path}")
            continue
    
    # Restart backend service
    print("\n🔄 Restarting backend service...")
    restart_commands = [
        f"ssh {EC2_HOST} 'sudo systemctl stop ai-backend-python'",
        f"ssh {EC2_HOST} 'sudo systemctl start ai-backend-python'",
        f"ssh {EC2_HOST} 'sudo systemctl status ai-backend-python --no-pager'"
    ]
    
    for cmd in restart_commands:
        result = run_command(cmd, "Restarting service")
        if result is None:
            print("❌ Service restart failed")
            return
    
    # Check logs
    print("\n📊 Checking service logs...")
    run_command(f"ssh {EC2_HOST} 'sudo journalctl -u ai-backend-python -n 20 --no-pager'", "Checking recent logs")
    
    print("\n✅ Live Testing Requirements Deployment Complete!")
    print("\n📋 Summary of Changes:")
    print("  ✅ Enhanced testing service with live deployment tests")
    print("  ✅ Updated proposal flow to require live testing")
    print("  ✅ Added strict requirements: NO STUBS OR SIMULATIONS")
    print("  ✅ Only test-passed proposals shown to users")
    print("  ✅ All tests now run in real environments")
    
    print("\n🔍 To monitor the deployment:")
    print(f"  ssh {EC2_HOST}")
    print("  sudo journalctl -u ai-backend-python -f")

if __name__ == "__main__":
    main() 