#!/usr/bin/env python3
"""
Fix Guardian Codex Port Issue
=============================

This script fixes the Guardian Codex service that's trying to connect to localhost:4000
but the backend is running on port 8000. It updates the background service files
and restarts the service on the EC2 instance.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_ssh_command(command, description=""):
    """Run a command via SSH on the EC2 instance"""
    ssh_key = "New.pem"
    ec2_host = "34.202.215.209"
    ec2_user = "ubuntu"
    
    full_command = f'ssh -i {ssh_key} {ec2_user}@{ec2_host} "{command}"'
    
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=30)
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

def fix_background_service():
    """Fix the background service files to use port 8000 instead of 4000"""
    
    print("🔧 Fixing Guardian Codex port issue...")
    print("=" * 50)
    
    # 1. Backup current files
    print("\n1. Creating backups...")
    success, output, error = run_ssh_command(
        "cp /home/ubuntu/ai-backend-python/app/services/background_service.py /home/ubuntu/ai-backend-python/app/services/background_service.py.backup",
        "Backing up background service file"
    )
    
    if not success:
        print("⚠️ Backup failed, but continuing...")
    
    # 2. Update the main background service file
    print("\n2. Updating main background service file...")
    update_commands = [
        "sed -i 's/localhost:4000/localhost:8000/g' /home/ubuntu/ai-backend-python/app/services/background_service.py",
        "sed -i 's/localhost:4000/localhost:8000/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/services/background_service.py"
    ]
    
    for cmd in update_commands:
        success, output, error = run_ssh_command(cmd, f"Updating port references: {cmd[:50]}...")
        if not success:
            print(f"⚠️ Failed to update: {error}")
    
    # 3. Verify the changes
    print("\n3. Verifying changes...")
    success, output, error = run_ssh_command(
        "grep -n 'localhost:8000' /home/ubuntu/ai-backend-python/app/services/background_service.py",
        "Checking for updated port references"
    )
    
    if success and output:
        print(f"✅ Found updated references:\n{output}")
    else:
        print("⚠️ No updated references found")
    
    # 4. Restart the backend service
    print("\n4. Restarting backend service...")
    success, output, error = run_ssh_command(
        "sudo systemctl restart ai-backend-python",
        "Restarting ai-backend-python service"
    )
    
    if success:
        print("✅ Service restarted successfully")
    else:
        print(f"❌ Service restart failed: {error}")
    
    # 5. Check service status
    print("\n5. Checking service status...")
    success, output, error = run_ssh_command(
        "sudo systemctl status ai-backend-python --no-pager",
        "Checking service status"
    )
    
    if success:
        print("✅ Service status:")
        print(output)
    else:
        print(f"❌ Failed to check service status: {error}")
    
    # 6. Test the health endpoint
    print("\n6. Testing health endpoint...")
    success, output, error = run_ssh_command(
        "curl -s http://localhost:8000/health",
        "Testing health endpoint on port 8000"
    )
    
    if success and "200" in output or "healthy" in output.lower():
        print("✅ Health endpoint working on port 8000")
    else:
        print(f"❌ Health endpoint test failed: {output}")
    
    # 7. Check logs for Guardian Codex errors
    print("\n7. Checking recent logs...")
    success, output, error = run_ssh_command(
        "journalctl -u ai-backend-python -n 20 --no-pager",
        "Checking recent service logs"
    )
    
    if success:
        print("📋 Recent logs:")
        print(output)
        
        # Check for Guardian Codex errors
        if "localhost:4000" in output:
            print("⚠️ Still seeing localhost:4000 references in logs")
        elif "Failed to log Guardian Codex event" in output:
            print("⚠️ Still seeing Guardian Codex errors")
        else:
            print("✅ No Guardian Codex errors found in recent logs")
    else:
        print(f"❌ Failed to check logs: {error}")

def main():
    """Main function"""
    print("🚀 Guardian Codex Port Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("New.pem"):
        print("❌ Error: New.pem SSH key not found in current directory")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the fix
    fix_background_service()
    
    print("\n" + "=" * 50)
    print("🎯 Fix completed!")
    print("\nNext steps:")
    print("1. Monitor the logs: journalctl -u ai-backend-python -f")
    print("2. Test the Guardian Codex: curl http://localhost:8000/api/codex/")
    print("3. Check for any remaining localhost:4000 references")

if __name__ == "__main__":
    main() 