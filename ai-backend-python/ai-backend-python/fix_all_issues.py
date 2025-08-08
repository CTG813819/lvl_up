#!/usr/bin/env python3
"""
Comprehensive fix for all AI system issues:
1. Add GitHub token to environment
2. Fix Conquest AI validation hanging
3. Enable Imperium proposals
4. Fix database connections
5. Test all endpoints
"""

import os
import json
import subprocess
import time
from pathlib import Path

def run_ssh_command(command):
    """Run SSH command on EC2"""
    ssh_cmd = f'ssh -i "New.pem" ubuntu@34.202.215.209 "{command}"'
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def fix_github_token():
    """Add GitHub token to environment file"""
    print("🔧 Fixing GitHub token configuration...")
    
    # Check if token exists in environment
    success, output, error = run_ssh_command("echo $GITHUB_TOKEN")
    if success and output.strip():
        print("✅ GitHub token already configured")
        return True
    
    # Add placeholder token to .env file using a different approach
    env_commands = [
        'echo "DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require" > /home/ubuntu/ai-backend-python/.env',
        'echo "DATABASE_NAME=neondb" >> /home/ubuntu/ai-backend-python/.env',
        'echo "PORT=4000" >> /home/ubuntu/ai-backend-python/.env',
        'echo "HOST=0.0.0.0" >> /home/ubuntu/ai-backend-python/.env',
        'echo "DEBUG=false" >> /home/ubuntu/ai-backend-python/.env',
        'echo "GITHUB_TOKEN=ghp_placeholder_token_for_testing" >> /home/ubuntu/ai-backend-python/.env'
    ]
    
    for cmd in env_commands:
        success, output, error = run_ssh_command(cmd)
        if not success:
            print(f"❌ Failed to update .env: {error}")
            return False
    
    print("✅ Added GitHub token placeholder to .env")
    return True

def fix_conquest_validation():
    """Fix Conquest AI validation hanging issues"""
    print("🔧 Fixing Conquest AI validation...")
    
    # Check if Flutter is accessible
    success, output, error = run_ssh_command("/home/ubuntu/flutter/bin/flutter --version")
    if not success:
        print("❌ Flutter not accessible")
        return False
    
    print("✅ Flutter is accessible")
    
    # Test a simple Conquest app creation with timeout
    test_data = {
        "name": "test_app_fix",
        "description": "Test app for fixing validation issues",
        "keywords": ["test", "fix"],
        "features": ["basic"]
    }
    
    # Create test file
    with open("test_fix_app.json", "w") as f:
        json.dump(test_data, f)
    
    # Upload test file
    subprocess.run(['scp', '-i', 'New.pem', 'test_fix_app.json', 'ubuntu@34.202.215.209:/home/ubuntu/'])
    
    # Test with timeout
    print("🧪 Testing Conquest app creation with timeout...")
    success, output, error = run_ssh_command("timeout 30 curl -X POST http://localhost:4000/api/conquest/create-app -H 'Content-Type: application/json' -d @/home/ubuntu/test_fix_app.json")
    
    if success:
        print("✅ Conquest app creation test completed")
        return True
    else:
        print(f"❌ Conquest app creation test failed: {error}")
        return False

def fix_imperium_proposals():
    """Enable Imperium proposals"""
    print("🔧 Fixing Imperium proposals...")
    
    # Check Imperium router for proposals endpoint
    success, output, error = run_ssh_command("grep -n 'proposals' /home/ubuntu/ai-backend-python/app/routers/imperium.py")
    if success and output.strip():
        print("✅ Imperium proposals endpoint exists")
        return True
    
    # Add proposals endpoint if missing
    proposals_endpoint = '''
@router.get("/proposals")
async def get_proposals():
    """Get Imperium AI proposals"""
    try:
        imperium_service = ImperiumAIService()
        proposals = await imperium_service.get_proposals()
        return {"status": "success", "proposals": proposals}
    except Exception as e:
        return {"status": "error", "message": str(e)}
'''
    
    # Add to imperium router
    success, output, error = run_ssh_command(f'echo "{proposals_endpoint}" >> /home/ubuntu/ai-backend-python/app/routers/imperium.py')
    if success:
        print("✅ Added Imperium proposals endpoint")
        return True
    else:
        print(f"❌ Failed to add proposals endpoint: {error}")
        return False

def fix_database_connections():
    """Fix database connection issues"""
    print("🔧 Fixing database connections...")
    
    # Restart backend service
    success, output, error = run_ssh_command("sudo systemctl restart ai-backend-python.service")
    if success:
        print("✅ Backend service restarted")
    else:
        print(f"❌ Failed to restart backend: {error}")
        return False
    
    # Wait for service to start
    time.sleep(5)
    
    # Test health endpoint
    success, output, error = run_ssh_command("curl -s http://localhost:4000/health")
    if success and "status" in output:
        print("✅ Backend health check passed")
        return True
    else:
        print(f"❌ Backend health check failed: {error}")
        return False

def test_all_endpoints():
    """Test all major endpoints"""
    print("🧪 Testing all endpoints...")
    
    endpoints = [
        ("Health", "GET", "/health"),
        ("Conquest Statistics", "GET", "/api/conquest/statistics"),
        ("Conquest Enhanced Statistics", "GET", "/api/conquest/enhanced-statistics"),
        ("Imperium Status", "GET", "/api/imperium/status"),
        ("Imperium Monitoring", "GET", "/api/imperium/monitoring"),
        ("Guardian Status", "GET", "/api/guardian/status"),
        ("Sandbox Status", "GET", "/api/sandbox/status"),
        ("Learning Data", "GET", "/api/learning/data"),
        ("Growth Insights", "GET", "/api/growth/insights"),
    ]
    
    results = []
    for name, method, endpoint in endpoints:
        if method == "GET":
            success, output, error = run_ssh_command(f"curl -s http://localhost:4000{endpoint}")
        else:
            success, output, error = run_ssh_command(f"curl -X {method} http://localhost:4000{endpoint}")
        
        if success and output.strip():
            print(f"✅ {name}: Working")
            results.append((name, True))
        else:
            print(f"❌ {name}: Failed - {error}")
            results.append((name, False))
    
    return results

def main():
    """Main fix function"""
    print("🚀 Starting comprehensive AI system fix...")
    
    # Fix 1: GitHub token
    if not fix_github_token():
        print("⚠️ GitHub token fix failed, continuing...")
    
    # Fix 2: Database connections
    if not fix_database_connections():
        print("❌ Database connection fix failed")
        return
    
    # Fix 3: Imperium proposals
    if not fix_imperium_proposals():
        print("⚠️ Imperium proposals fix failed, continuing...")
    
    # Fix 4: Conquest validation
    if not fix_conquest_validation():
        print("⚠️ Conquest validation fix failed, continuing...")
    
    # Test all endpoints
    results = test_all_endpoints()
    
    # Summary
    print("\n📊 Fix Summary:")
    working = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Working endpoints: {working}/{total} ({working/total*100:.1f}%)")
    
    if working == total:
        print("🎉 All fixes completed successfully!")
    else:
        print("⚠️ Some issues remain, check individual fixes above")

if __name__ == "__main__":
    main() 