#!/usr/bin/env python3
"""
Deploy Proposal Approval Fix to EC2
"""

import subprocess
import os
import sys
import time

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
    """Deploy proposal approval fix"""
    print("🚀 Deploying Proposal Approval Fix to EC2")
    print("=" * 50)
    
    # Step 1: Upload fixed proposals.py file
    print("\n1. Uploading fixed proposals.py file...")
    
    proposals_upload = run_command(
        'scp -i "New.pem" ai-backend-python/app/routers/proposals.py ubuntu@34.202.215.209:/tmp/proposals_fixed.py',
        "Uploading proposals.py fix"
    )
    
    if proposals_upload is None:
        print("❌ Proposals upload failed")
        return
    
    # Step 2: Apply fix on server
    print("\n2. Applying fix on server...")
    
    move_proposals = run_command(
        'ssh -i "New.pem" ubuntu@34.202.215.209 "sudo mv /tmp/proposals_fixed.py /home/ubuntu/ai-backend-python/app/routers/proposals.py && sudo chown ubuntu:ubuntu /home/ubuntu/ai-backend-python/app/routers/proposals.py"',
        "Moving proposals.py to correct location"
    )
    
    if move_proposals is None:
        print("❌ Proposals move failed")
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
    time.sleep(5)
    
    # Step 5: Test the fix
    print("\n5. Testing the fix...")
    
    test_result = run_command(
        'curl -X POST http://34.202.215.209:4000/api/proposals/sandbox/accept',
        "Testing sandbox agent approval"
    )
    
    if test_result and '"status":"success"' in test_result:
        print("✅ Fix test successful!")
    else:
        print("❌ Fix test failed")
        print(f"Response: {test_result}")
    
    print("\n" + "=" * 50)
    print("✅ Deployment completed!")
    print("\nSummary of fix deployed:")
    print("- Added agent approval handling to proposals.py")
    print("- Agents (sandbox, imperium, guardian, conquest) can now be 'approved'")
    print("- Approval triggers agent execution instead of proposal testing")
    print("- Rejection logs agent rejection for AI learning")
    print("- Original proposal approval logic preserved for real proposals")

if __name__ == "__main__":
    main() 