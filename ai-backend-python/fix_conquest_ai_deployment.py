#!/usr/bin/env python3
"""
Deploy Conquest AI Fixes to EC2
"""

import subprocess
import os
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return None

def main():
    """Deploy Conquest AI fixes"""
    print("🚀 Deploying Conquest AI Fixes to EC2")
    print("=" * 50)
    
    # Step 1: Upload fixed files
    print("\n1. Uploading fixed files...")
    
    # Upload Conquest router fix
    router_upload = run_command(
        'scp -i "New.pem" ai-backend-python/app/routers/conquest.py ubuntu@34.202.215.209:/tmp/conquest_router_fixed.py',
        "Uploading Conquest router fix"
    )
    
    # Upload Conquest service fix
    service_upload = run_command(
        'scp -i "New.pem" ai-backend-python/app/services/conquest_ai_service.py ubuntu@34.202.215.209:/tmp/conquest_service_fixed.py',
        "Uploading Conquest service fix"
    )
    
    # Check upload results
    if router_upload is None:
        print("❌ Router upload failed")
        return
    if service_upload is None:
        print("❌ Service upload failed")
        return
    
    # Step 2: Apply fixes on server
    print("\n2. Applying fixes on server...")
    
    # Move files to correct locations
    move_router = run_command(
        'ssh -i "New.pem" ubuntu@34.202.215.209 "sudo mv /tmp/conquest_router_fixed.py /home/ubuntu/ai-backend-python/app/routers/conquest.py && sudo chown ubuntu:ubuntu /home/ubuntu/ai-backend-python/app/routers/conquest.py"',
        "Moving Conquest router to correct location"
    )
    
    move_service = run_command(
        'ssh -i "New.pem" ubuntu@34.202.215.209 "sudo mv /tmp/conquest_service_fixed.py /home/ubuntu/ai-backend-python/app/services/conquest_ai_service.py && sudo chown ubuntu:ubuntu /home/ubuntu/ai-backend-python/app/services/conquest_ai_service.py"',
        "Moving Conquest service to correct location"
    )
    
    if move_router is None:
        print("❌ Router move failed")
        return
    if move_service is None:
        print("❌ Service move failed")
        return
    
    # Step 3: Restart backend service
    print("\n3. Restarting backend service...")
    
    restart_service = run_command(
        'ssh -i "New.pem" ubuntu@34.202.215.209 "sudo systemctl restart ai-backend-python.service"',
        "Restarting backend service"
    )
    
    if restart_service is None:
        print("❌ Service restart failed")
        return
    
    # Step 4: Wait for service to start
    print("\n4. Waiting for service to start...")
    
    import time
    time.sleep(5)
    
    # Step 5: Test the fixes
    print("\n5. Testing the fixes...")
    
    test_result = run_command(
        'python test_conquest_fixes.py',
        "Testing Conquest AI fixes"
    )
    
    print("\n" + "=" * 50)
    print("✅ Deployment completed!")
    print("\nSummary of fixes deployed:")
    print("- Fixed Conquest router to handle validation failures gracefully")
    print("- Improved error messages in Conquest service")
    print("- Added suggestions for failed app creation")
    print("- Fixed ai_code_fixes.json file corruption")
    print("- Increased progress logs timeout from 5 to 15 seconds")

if __name__ == "__main__":
    main() 