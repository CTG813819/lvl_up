#!/usr/bin/env python3
"""
<<<<<<< HEAD
Simple Force Custodes Tests
==========================

This script forces Custodes tests to run immediately for all AIs.
It's a simple fix that doesn't require full database initialization.
"""

import asyncio
import sys
import os
import requests
import json
import time
from datetime import datetime

def force_custodes_tests():
    """Force run Custodes tests via API"""
    
    try:
        print("🛡️ Force running Custodes tests for all AIs...")
        
        # API base URL
        base_url = "http://localhost:8000"
        
        # AI types to test
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        results = {}
        
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                
                # Force test via API
                response = requests.post(
                    f"{base_url}/api/custody/test/{ai_type}/force",
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results[ai_type] = result
                    print(f"  ✅ {ai_type}: Test initiated successfully")
                else:
                    print(f"  ❌ {ai_type}: HTTP {response.status_code} - {response.text}")
                    results[ai_type] = {"error": f"HTTP {response.status_code}"}
                    
            except Exception as e:
                print(f"  ❌ {ai_type}: ERROR - {str(e)}")
                results[ai_type] = {"error": str(e)}
        
        # Wait a moment for tests to complete
        print("⏳ Waiting for tests to complete...")
        time.sleep(10)
        
        # Check results
        print("\n📊 Checking test results...")
        try:
            response = requests.get(f"{base_url}/api/custody/", timeout=10)
            if response.status_code == 200:
                analytics = response.json()
                ai_metrics = analytics.get('analytics', {}).get('ai_specific_metrics', {})
                
                for ai_type, metrics in ai_metrics.items():
                    tests_given = metrics.get('total_tests_given', 0)
                    tests_passed = metrics.get('total_tests_passed', 0)
                    tests_failed = metrics.get('total_tests_failed', 0)
                    print(f"  {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed")
            else:
                print(f"  ❌ Could not get analytics: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error getting analytics: {str(e)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error force running tests: {str(e)}")
        return {}

def create_custodes_scheduler_service():
    """Create a systemd service for Custodes scheduler"""
    
    try:
        print("⏰ Creating Custodes scheduler service...")
        
        # Create the scheduler script
        scheduler_script = '''#!/usr/bin/env python3
"""
Custodes Scheduler Service
Runs Custodes tests every 4 hours
"""

import asyncio
import sys
import os
import requests
import time
from datetime import datetime

def run_custodes_tests():
    """Run Custodes tests for all AIs"""
    try:
        base_url = "http://localhost:8000"
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"[{datetime.now()}] 🧪 Running scheduled Custodes tests...")
        
        for ai_type in ai_types:
            try:
                response = requests.post(
                    f"{base_url}/api/custody/test/{ai_type}/force",
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"[{datetime.now()}] ✅ {ai_type} test initiated")
                else:
                    print(f"[{datetime.now()}] ❌ {ai_type} test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"[{datetime.now()}] ❌ {ai_type} test error: {str(e)}")
        
        print(f"[{datetime.now()}] ✅ Custodes test cycle completed")
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in Custodes test cycle: {str(e)}")

def main():
    """Main function"""
    print(f"[{datetime.now()}] 🛡️ Custodes Scheduler Service started")
    print(f"[{datetime.now()}] ⏰ Tests will run every 4 hours")
    
    while True:
        try:
            # Run tests
            run_custodes_tests()
            
            # Wait 4 hours
            print(f"[{datetime.now()}] ⏰ Waiting 4 hours until next test cycle...")
            time.sleep(14400)  # 4 hours
            
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] 🛑 Custodes Scheduler Service stopped")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error in main loop: {str(e)}")
            time.sleep(3600)  # Wait 1 hour on error

if __name__ == "__main__":
    main()
'''
        
        # Save the scheduler script
        with open('custodes_scheduler_service.py', 'w') as f:
            f.write(scheduler_script)
        
        # Make it executable
        os.chmod('custodes_scheduler_service.py', 0o755)
        
        # Create systemd service file
        service_content = '''[Unit]
Description=Custodes Test Scheduler Service
After=network.target ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/custodes_scheduler_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
        
        with open('custodes-scheduler.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Custodes scheduler service created")
        
    except Exception as e:
        print(f"❌ Error creating scheduler service: {str(e)}")

def install_custodes_service():
    """Install the Custodes scheduler service"""
    
    try:
        print("🔧 Installing Custodes scheduler service...")
        
        # Copy service file to systemd
        os.system("sudo cp custodes-scheduler.service /etc/systemd/system/")
        
        # Reload systemd
        os.system("sudo systemctl daemon-reload")
        
        # Enable and start service
        os.system("sudo systemctl enable custodes-scheduler.service")
        os.system("sudo systemctl start custodes-scheduler.service")
        
        print("✅ Custodes scheduler service installed and started")
        
        # Check status
        os.system("sudo systemctl status custodes-scheduler.service")
        
    except Exception as e:
        print(f"❌ Error installing service: {str(e)}")

if __name__ == "__main__":
    print("🛡️ Simple Custodes Force Test")
    print("=" * 50)
    
    # Force run tests
    results = force_custodes_tests()
    
    # Create scheduler service
    create_custodes_scheduler_service()
    
    # Install service
    install_custodes_service()
    
    print("\n✅ Custodes fix completed!")
    print("🛡️ Tests have been forced to run")
    print("⏰ Custodes scheduler service installed and running")
    print("🧪 Tests will now run automatically every 4 hours") 
=======
Simple script to force Custodes tests by calling API endpoints directly
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

def force_custodes_tests():
    """Force Custodes tests for all AIs by calling API endpoints"""
    print("🛡️ Forcing Custodes Protocol Tests...")
    
    # Check current status first
    print("📊 Checking current custody status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Failed to get custody status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting custody status: {e}")
    
    # Use batch test to test all AIs at once
    print("\n🧪 Running batch test for all AIs...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/custody/batch-test",
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch test completed: {result.get('status', 'unknown')}")
            if 'results' in result:
                for ai_result in result['results']:
                    ai_name = ai_result.get('ai_type', 'unknown')
                    status = ai_result.get('status', 'unknown')
                    print(f"   {ai_name}: {status}")
        else:
            print(f"❌ Batch test failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error running batch test: {e}")
    
    # Also try individual force tests for each AI
    ai_types = ["imperium", "guardian", "conquest"]
    
    for ai_type in ai_types:
        print(f"\n🧪 Force testing {ai_type} AI...")
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/custody/test/{ai_type}/force",
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {ai_type} force test completed: {result.get('status', 'unknown')}")
                if 'result' in result:
                    print(f"   Test result: {result['result']}")
            else:
                print(f"❌ {ai_type} force test failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error testing {ai_type}: {e}")
    
    # Wait a moment for tests to complete
    print("\n⏳ Waiting for tests to complete...")
    time.sleep(5)
    
    # Check final status
    print("\n📊 Checking final custody status...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            
            # Check if any AIs can now create proposals
            for ai_name, ai_data in data.items():
                if ai_data.get('can_create_proposals', False):
                    print(f"✅ {ai_name} can now create proposals!")
                else:
                    print(f"❌ {ai_name} still cannot create proposals")
        else:
            print(f"❌ Failed to get final custody status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final custody status: {e}")
    
    print("\n🎉 Custodes tests completed!")

if __name__ == "__main__":
    force_custodes_tests() 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
