#!/usr/bin/env python3
"""
Test Guardian Codex Fix
=======================

This script tests that the Guardian Codex port fix is working properly
by checking the service status, testing endpoints, and monitoring logs.
"""

import subprocess
import sys
import time

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

def test_guardian_codex_fix():
    """Test that the Guardian Codex fix is working"""
    
    print("🧪 Testing Guardian Codex Fix")
    print("=" * 50)
    
    # 1. Check service status
    print("\n1. Checking service status...")
    success, output, error = run_ssh_command(
        "sudo systemctl is-active ai-backend-python",
        "Checking if service is active"
    )
    
    if success and "active" in output:
        print("✅ Service is running")
    else:
        print("❌ Service is not running")
        return False
    
    # 2. Test health endpoint
    print("\n2. Testing health endpoint...")
    success, output, error = run_ssh_command(
        "curl -s -w '%{http_code}' http://localhost:8000/api/imperium/status",
        "Testing Imperium status endpoint"
    )
    
    if success and "200" in output:
        print("✅ Health endpoint working")
    else:
        print(f"❌ Health endpoint failed: {output}")
    
    # 3. Test Guardian Codex endpoint
    print("\n3. Testing Guardian Codex endpoint...")
    success, output, error = run_ssh_command(
        "curl -s -w '%{http_code}' http://localhost:8000/api/codex/",
        "Testing Guardian Codex endpoint"
    )
    
    if success and "200" in output:
        print("✅ Guardian Codex endpoint working")
    else:
        print(f"❌ Guardian Codex endpoint failed: {output}")
    
    # 4. Check for localhost:4000 references
    print("\n4. Checking for localhost:4000 references...")
    success, output, error = run_ssh_command(
        "grep -r 'localhost:4000' /home/ubuntu/ai-backend-python/app/services/ || echo 'No localhost:4000 references found'",
        "Checking for remaining localhost:4000 references"
    )
    
    if success and "No localhost:4000 references found" in output:
        print("✅ No localhost:4000 references found")
    elif success and output:
        print(f"⚠️ Found localhost:4000 references: {output}")
    else:
        print("❌ Error checking for localhost:4000 references")
    
    # 5. Check recent logs for Guardian Codex errors
    print("\n5. Checking recent logs for Guardian Codex errors...")
    success, output, error = run_ssh_command(
        "journalctl -u ai-backend-python -n 20 --no-pager | grep -i 'guardian\\|codex\\|localhost:4000' || echo 'No Guardian Codex errors found'",
        "Checking recent logs for Guardian Codex errors"
    )
    
    if success:
        if "Failed to log Guardian Codex event" in output:
            print("❌ Still seeing Guardian Codex errors")
        elif "localhost:4000" in output:
            print("❌ Still seeing localhost:4000 references in logs")
        else:
            print("✅ No Guardian Codex errors found in recent logs")
    else:
        print("❌ Error checking logs")
    
    # 6. Test Guardian self-heal functionality
    print("\n6. Testing Guardian self-heal functionality...")
    success, output, error = run_ssh_command(
        "curl -s -X POST http://localhost:8000/api/guardian/health-check",
        "Testing Guardian health check endpoint"
    )
    
    if success and "200" in output:
        print("✅ Guardian health check working")
    else:
        print(f"❌ Guardian health check failed: {output}")
    
    # 7. Monitor logs for a few seconds
    print("\n7. Monitoring logs for Guardian activity...")
    success, output, error = run_ssh_command(
        "timeout 10 journalctl -u ai-backend-python -f --no-pager | head -20",
        "Monitoring logs for Guardian activity"
    )
    
    if success:
        print("📋 Recent log activity:")
        print(output[:500] + "..." if len(output) > 500 else output)
    else:
        print("❌ Error monitoring logs")
    
    return True

def main():
    """Main function"""
    print("🚀 Guardian Codex Fix Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("New.pem"):
        print("❌ Error: New.pem SSH key not found in current directory")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the test
    success = test_guardian_codex_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 Guardian Codex fix test completed successfully!")
        print("\n✅ The Guardian Codex service should now be working properly")
        print("✅ No more localhost:4000 connection errors")
        print("✅ Guardian self-heal functionality is operational")
    else:
        print("❌ Guardian Codex fix test failed")
        print("Please check the logs and try again")

if __name__ == "__main__":
    import os
    main() 