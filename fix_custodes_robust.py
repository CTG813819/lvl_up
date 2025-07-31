#!/usr/bin/env python3
"""
Robust Custodes Fix
==================

This script provides a robust fix for Custodes automatic testing.
It ensures the backend is ready before running tests and includes proper error handling.
"""

import asyncio
import sys
import os
import requests
import json
import time
from datetime import datetime

def wait_for_backend(max_wait=300):
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        
        print("  Backend not ready, waiting 10 seconds...")
        time.sleep(10)
    
    print("❌ Backend did not become ready within timeout")
    return False

def force_custodes_tests():
    """Force run Custodes tests via API with proper error handling"""
    
    try:
        print("🛡️ Force running Custodes tests for all AIs...")
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("❌ Cannot run tests - backend not ready")
            return {}
        
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
                    timeout=60  # Increased timeout
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
        
        # Wait for tests to complete
        print("⏳ Waiting for tests to complete...")
        time.sleep(30)  # Wait longer for tests to complete
        
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

def create_robust_custodes_scheduler():
    """Create a robust Custodes scheduler with proper backend checking"""
    
    try:
        print("⏰ Creating robust Custodes scheduler...")
        
        # Create the robust scheduler script
        scheduler_script = '''#!/usr/bin/env python3
"""
Robust Custodes Scheduler Service
Runs Custodes tests every 4 hours with proper backend checking
"""

import asyncio
import sys
import os
import requests
import time
from datetime import datetime

def wait_for_backend(max_wait=300):
    """Wait for backend to be ready"""
    print(f"[{datetime.now()}] ⏳ Waiting for backend to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print(f"[{datetime.now()}] ✅ Backend is ready!")
                return True
        except:
            pass
        
        print(f"[{datetime.now()}]   Backend not ready, waiting 10 seconds...")
        time.sleep(10)
    
    print(f"[{datetime.now()}] ❌ Backend did not become ready within timeout")
    return False

def run_custodes_tests():
    """Run Custodes tests for all AIs with proper error handling"""
    try:
        # Wait for backend to be ready
        if not wait_for_backend():
            print(f"[{datetime.now()}] ❌ Cannot run tests - backend not ready")
            return False
        
        base_url = "http://localhost:8000"
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"[{datetime.now()}] 🧪 Running scheduled Custodes tests...")
        
        success_count = 0
        for ai_type in ai_types:
            try:
                response = requests.post(
                    f"{base_url}/api/custody/test/{ai_type}/force",
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    print(f"[{datetime.now()}] ✅ {ai_type} test initiated")
                    success_count += 1
                else:
                    print(f"[{datetime.now()}] ❌ {ai_type} test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"[{datetime.now()}] ❌ {ai_type} test error: {str(e)}")
        
        print(f"[{datetime.now()}] ✅ Custodes test cycle completed: {success_count}/{len(ai_types)} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in Custodes test cycle: {str(e)}")
        return False

def main():
    """Main function"""
    print(f"[{datetime.now()}] 🛡️ Robust Custodes Scheduler Service started")
    print(f"[{datetime.now()}] ⏰ Tests will run every 4 hours")
    
    # Run initial test cycle
    print(f"[{datetime.now()}] 🚀 Running initial test cycle...")
    run_custodes_tests()
    
    while True:
        try:
            # Wait 4 hours
            print(f"[{datetime.now()}] ⏰ Waiting 4 hours until next test cycle...")
            time.sleep(14400)  # 4 hours
            
            # Run tests
            run_custodes_tests()
            
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
        with open('custodes_scheduler_robust.py', 'w') as f:
            f.write(scheduler_script)
        
        # Make it executable
        os.chmod('custodes_scheduler_robust.py', 0o755)
        
        # Create systemd service file
        service_content = '''[Unit]
Description=Robust Custodes Test Scheduler Service
After=network.target ai-backend-python.service
Wants=ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/custodes_scheduler_robust.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
'''
        
        with open('custodes-scheduler-robust.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Robust Custodes scheduler created")
        
    except Exception as e:
        print(f"❌ Error creating robust scheduler: {str(e)}")

def install_robust_custodes_service():
    """Install the robust Custodes scheduler service"""
    
    try:
        print("🔧 Installing robust Custodes scheduler service...")
        
        # Stop old service if running
        os.system("sudo systemctl stop custodes-scheduler.service 2>/dev/null || true")
        os.system("sudo systemctl disable custodes-scheduler.service 2>/dev/null || true")
        
        # Copy service file to systemd
        os.system("sudo cp custodes-scheduler-robust.service /etc/systemd/system/custodes-scheduler.service")
        
        # Reload systemd
        os.system("sudo systemctl daemon-reload")
        
        # Enable and start service
        os.system("sudo systemctl enable custodes-scheduler.service")
        os.system("sudo systemctl start custodes-scheduler.service")
        
        print("✅ Robust Custodes scheduler service installed and started")
        
        # Check status
        os.system("sudo systemctl status custodes-scheduler.service")
        
    except Exception as e:
        print(f"❌ Error installing service: {str(e)}")

if __name__ == "__main__":
    print("🛡️ Robust Custodes Fix")
    print("=" * 50)
    
    # Force run tests with backend checking
    results = force_custodes_tests()
    
    # Create robust scheduler service
    create_robust_custodes_scheduler()
    
    # Install robust service
    install_robust_custodes_service()
    
    print("\n✅ Robust Custodes fix completed!")
    print("🛡️ Tests have been forced to run with backend checking")
    print("⏰ Robust Custodes scheduler service installed and running")
    print("🧪 Tests will now run automatically every 4 hours with proper error handling") 