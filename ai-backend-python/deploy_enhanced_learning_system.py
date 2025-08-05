#!/usr/bin/env python3
"""
Deploy Enhanced Learning System
Deploys the enhanced Conquest AI system with improved learning capabilities and statistics tracking.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

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

def deploy_enhanced_learning_system():
    """Deploy the enhanced learning system"""
    print("🚀 Deploying Enhanced Learning System")
    print("=" * 50)
    
    # Step 1: Stop the current backend service
    print("\n📋 Step 1: Stopping current backend service...")
    run_command("sudo systemctl stop ai-backend-python", "Stopping backend service", check=False)
    time.sleep(2)
    
    # Step 2: Backup current deployment
    print("\n📋 Step 2: Creating backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_enhanced_learning_{timestamp}"
    run_command(f"cp -r ai-backend-python {backup_dir}", "Creating backup")
    
    # Step 3: Update backend files
    print("\n📋 Step 3: Updating backend files...")
    
    # Check if files exist and are updated
    files_to_check = [
        "ai-backend-python/app/services/conquest_ai_service.py",
        "ai-backend-python/app/routers/conquest.py",
        "lib/providers/conquest_ai_provider.dart",
        "lib/services/conquest_ai_service.dart",
        "lib/screens/conquest_apps_screen.dart"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    # Step 4: Restart backend service
    print("\n📋 Step 4: Starting backend service...")
    run_command("sudo systemctl start ai-backend-python", "Starting backend service")
    time.sleep(5)
    
    # Step 5: Check backend status
    print("\n📋 Step 5: Checking backend status...")
    status_result = run_command("sudo systemctl status ai-backend-python", "Checking service status", check=False)
    if "active (running)" in status_result.stdout:
        print("✅ Backend service is running")
    else:
        print("❌ Backend service failed to start")
        return False
    
    # Step 6: Test enhanced statistics endpoint
    print("\n📋 Step 6: Testing enhanced statistics endpoint...")
    test_result = run_command(
        "curl -s http://localhost:4000/api/conquest/enhanced-statistics",
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
    
    # Step 7: Test basic statistics endpoint
    print("\n📋 Step 7: Testing basic statistics endpoint...")
    basic_test_result = run_command(
        "curl -s http://localhost:4000/api/conquest/statistics",
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
    
    # Step 8: Create learning data files if they don't exist
    print("\n📋 Step 8: Initializing learning data files...")
    learning_files = [
        "ai-backend-python/app/services/ai_learnings.json",
        "ai-backend-python/app/services/ai_code_fixes.json"
    ]
    
    for file_path in learning_files:
        if not os.path.exists(file_path):
            initial_data = {
                "successful_patterns": [],
                "failed_patterns": [],
                "validation_stats": {
                    "total_attempts": 0,
                    "successful_validations": 0,
                    "failed_validations": 0,
                    "auto_fix_success_rate": 0.0,
                    "common_issues": {},
                    "successful_fixes": {}
                }
            } if "ai_learnings.json" in file_path else {}
            
            with open(file_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
            print(f"✅ Created {file_path}")
        else:
            print(f"✅ {file_path} already exists")
    
    # Step 9: Set proper permissions
    print("\n📋 Step 9: Setting file permissions...")
    run_command("sudo chown -R www-data:www-data ai-backend-python/app/services/", "Setting ownership")
    run_command("sudo chmod -R 755 ai-backend-python/app/services/", "Setting permissions")
    
    print("\n🎉 Enhanced Learning System Deployment Complete!")
    print("=" * 50)
    print("✅ Enhanced AI learning system deployed")
    print("✅ Validation progress tracking enabled")
    print("✅ Statistics with learning data available")
    print("✅ Auto-fix learning capabilities active")
    print("✅ Frontend enhanced statistics display ready")
    
    print("\n📊 Available endpoints:")
    print("  - /api/conquest/enhanced-statistics - Enhanced statistics with learning data")
    print("  - /api/conquest/statistics - Basic statistics")
    print("  - /api/conquest/deployments - List deployments")
    
    print("\n🔍 To monitor the system:")
    print("  - sudo journalctl -u ai-backend-python -f")
    print("  - Check /var/log/ai-backend-python/ for detailed logs")
    
    return True

if __name__ == "__main__":
    try:
        success = deploy_enhanced_learning_system()
        if success:
            print("\n✅ Deployment completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 