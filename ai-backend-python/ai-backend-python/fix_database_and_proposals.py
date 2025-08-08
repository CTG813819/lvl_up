#!/usr/bin/env python3
"""
Fix Database and Proposals Issue
===============================

This script fixes the database initialization issue and gets proposals working
on the EC2 instance. The database tables don't exist, so we need to initialize them.
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
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True, timeout=60)
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

def fix_database_and_proposals():
    """Fix the database initialization and get proposals working"""
    
    print("🔧 Fixing Database and Proposals Issue...")
    print("=" * 50)
    
    # 1. Check current database status
    print("\n1. Checking current database status...")
    success, output, error = run_ssh_command(
        "sudo -u postgres psql -d ai_backend -c '\\dt'",
        "Checking existing database tables"
    )
    
    if success and "Did not find any relations" in output:
        print("❌ Database is empty - no tables exist")
    else:
        print("✅ Database has tables")
    
    # 2. Check backend logs for database initialization errors
    print("\n2. Checking backend logs for database errors...")
    success, output, error = run_ssh_command(
        "journalctl -u ai-backend-python -n 100 --no-pager | grep -i 'database\\|table\\|init\\|error'",
        "Checking backend logs for database issues"
    )
    
    if success and output:
        print("📋 Recent database-related logs:")
        print(output[:500] + "..." if len(output) > 500 else output)
    
    # 3. Restart the backend service to trigger database initialization
    print("\n3. Restarting backend service to trigger database initialization...")
    success, output, error = run_ssh_command(
        "sudo systemctl restart ai-backend-python",
        "Restarting backend service"
    )
    
    if success:
        print("✅ Service restarted successfully")
    else:
        print(f"❌ Service restart failed: {error}")
    
    # 4. Wait a moment for initialization
    print("\n4. Waiting for database initialization...")
    import time
    time.sleep(10)
    
    # 5. Check if tables were created
    print("\n5. Checking if database tables were created...")
    success, output, error = run_ssh_command(
        "sudo -u postgres psql -d ai_backend -c '\\dt'",
        "Checking if tables were created"
    )
    
    if success and "Did not find any relations" not in output:
        print("✅ Database tables created successfully")
        print(f"📋 Tables found:\n{output}")
    else:
        print("❌ Database tables still not created")
        print("Attempting manual database initialization...")
        
        # 6. Manual database initialization
        print("\n6. Attempting manual database initialization...")
        success, output, error = run_ssh_command(
            "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python -c \"from app.core.database import init_database, create_tables, create_indexes; import asyncio; asyncio.run(init_database()); asyncio.run(create_tables()); asyncio.run(create_indexes())\"",
            "Running manual database initialization"
        )
        
        if success:
            print("✅ Manual database initialization completed")
        else:
            print(f"❌ Manual database initialization failed: {error}")
    
    # 7. Check proposals endpoint
    print("\n7. Testing proposals endpoint...")
    success, output, error = run_ssh_command(
        "curl -s http://localhost:8000/api/proposals",
        "Testing proposals endpoint"
    )
    
    if success:
        if output and output != "[]":
            print("✅ Proposals endpoint working")
            print(f"📋 Response: {output[:200]}...")
        else:
            print("✅ Proposals endpoint working but no proposals yet")
    else:
        print(f"❌ Proposals endpoint failed: {error}")
    
    # 8. Check all proposals endpoint (admin)
    print("\n8. Testing all proposals endpoint (admin)...")
    success, output, error = run_ssh_command(
        "curl -s http://localhost:8000/api/proposals/all",
        "Testing all proposals endpoint"
    )
    
    if success:
        if "validation error" in output.lower():
            print("⚠️ All proposals endpoint has validation errors")
        elif output and output != "[]":
            print("✅ All proposals endpoint working")
            print(f"📋 Response: {output[:200]}...")
        else:
            print("✅ All proposals endpoint working but no proposals yet")
    else:
        print(f"❌ All proposals endpoint failed: {error}")
    
    # 9. Check service status
    print("\n9. Checking service status...")
    success, output, error = run_ssh_command(
        "sudo systemctl status ai-backend-python --no-pager",
        "Checking service status"
    )
    
    if success:
        print("✅ Service status:")
        print(output[:300] + "..." if len(output) > 300 else output)
    else:
        print(f"❌ Failed to check service status: {error}")
    
    # 10. Check recent logs
    print("\n10. Checking recent logs...")
    success, output, error = run_ssh_command(
        "journalctl -u ai-backend-python -n 20 --no-pager",
        "Checking recent service logs"
    )
    
    if success:
        print("📋 Recent logs:")
        print(output[:500] + "..." if len(output) > 500 else output)
    else:
        print(f"❌ Failed to check logs: {error}")

def main():
    """Main function"""
    print("🚀 Database and Proposals Fix Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("New.pem"):
        print("❌ Error: New.pem SSH key not found in current directory")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run the fix
    fix_database_and_proposals()
    
    print("\n" + "=" * 50)
    print("🎯 Database and proposals fix completed!")
    print("\nNext steps:")
    print("1. Check if proposals are now showing in the app")
    print("2. Monitor the logs: journalctl -u ai-backend-python -f")
    print("3. Test proposal generation: curl -X POST http://localhost:8000/api/proposals/cycle/reset")
    print("4. If still no proposals, check the AI agents are running")

if __name__ == "__main__":
    main() 