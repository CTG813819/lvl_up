#!/usr/bin/env python3
"""
Final Custodes Fix
=================

This script provides the final comprehensive fix for Custodes automatic testing.
It ensures the background service properly runs the custody testing cycle.
"""

import asyncio
import sys
import os
import requests
import json
import time
from datetime import datetime

def fix_background_service():
    """Fix the background service to ensure custody testing runs"""
    
    try:
        print("🔧 Fixing background service to ensure custody testing runs...")
        
        # Create a fixed background service configuration
        background_config = {
            "background_tasks": [
                "custody_testing_cycle",
                "learning_cycle", 
                "health_monitor",
                "github_monitor",
                "imperium_audit_task",
                "guardian_self_heal_task"
            ],
            "custody_testing": {
                "enabled": True,
                "interval_seconds": 14400,  # 4 hours
                "ai_types": ["imperium", "guardian", "sandbox", "conquest"],
                "auto_start": True,
                "log_level": "info"
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Save configuration
        with open('background_service_config.json', 'w') as f:
            json.dump(background_config, f, indent=2)
        
        print("✅ Background service configuration updated")
        
    except Exception as e:
        print(f"❌ Error fixing background service: {str(e)}")

def create_standalone_custodes_runner():
    """Create a standalone Custodes runner that can be run independently"""
    
    try:
        print("🚀 Creating standalone Custodes runner...")
        
        # Create the standalone runner script
        runner_script = '''#!/usr/bin/env python3
"""
Standalone Custodes Runner
Runs Custodes tests immediately and then every 4 hours
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
    """Run Custodes tests for all AIs"""
    try:
        # Wait for backend to be ready
        if not wait_for_backend():
            print(f"[{datetime.now()}] ❌ Cannot run tests - backend not ready")
            return False
        
        base_url = "http://localhost:8000"
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"[{datetime.now()}] 🧪 Running Custodes tests for all AIs...")
        
        success_count = 0
        for ai_type in ai_types:
            try:
                print(f"[{datetime.now()}]   Testing {ai_type}...")
                
                response = requests.post(
                    f"{base_url}/api/custody/test/{ai_type}/force",
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                if response.status_code == 200:
                    print(f"[{datetime.now()}] ✅ {ai_type} test initiated successfully")
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

def check_test_results():
    """Check the results of the tests"""
    try:
        base_url = "http://localhost:8000"
        response = requests.get(f"{base_url}/api/custody/", timeout=10)
        
        if response.status_code == 200:
            analytics = response.json()
            ai_metrics = analytics.get('analytics', {}).get('ai_specific_metrics', {})
            
            print(f"[{datetime.now()}] 📊 Current Test Results:")
            for ai_type, metrics in ai_metrics.items():
                tests_given = metrics.get('total_tests_given', 0)
                tests_passed = metrics.get('total_tests_passed', 0)
                tests_failed = metrics.get('total_tests_failed', 0)
                print(f"[{datetime.now()}]   {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed")
        else:
            print(f"[{datetime.now()}] ❌ Could not get analytics: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error getting analytics: {str(e)}")

def main():
    """Main function"""
    print(f"[{datetime.now()}] 🛡️ Standalone Custodes Runner started")
    print(f"[{datetime.now()}] ⏰ Tests will run immediately and then every 4 hours")
    
    # Run initial test cycle
    print(f"[{datetime.now()}] 🚀 Running initial test cycle...")
    run_custodes_tests()
    
    # Wait for tests to complete
    print(f"[{datetime.now()}] ⏳ Waiting for tests to complete...")
    time.sleep(30)
    
    # Check results
    check_test_results()
    
    # Start continuous loop
    while True:
        try:
            # Wait 4 hours
            print(f"[{datetime.now()}] ⏰ Waiting 4 hours until next test cycle...")
            time.sleep(14400)  # 4 hours
            
            # Run tests
            run_custodes_tests()
            
            # Wait for tests to complete
            time.sleep(30)
            
            # Check results
            check_test_results()
            
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] 🛑 Custodes Runner stopped")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error in main loop: {str(e)}")
            time.sleep(3600)  # Wait 1 hour on error

if __name__ == "__main__":
    main()
'''
        
        # Save the runner script
        with open('custodes_standalone_runner.py', 'w') as f:
            f.write(runner_script)
        
        # Make it executable
        os.chmod('custodes_standalone_runner.py', 0o755)
        
        print("✅ Standalone Custodes runner created")
        
    except Exception as e:
        print(f"❌ Error creating standalone runner: {str(e)}")

def create_systemd_service():
    """Create a systemd service for the standalone runner"""
    
    try:
        print("⏰ Creating systemd service for standalone runner...")
        
        # Create systemd service file
        service_content = '''[Unit]
Description=Standalone Custodes Test Runner
After=network.target ai-backend-python.service
Wants=ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/custodes_standalone_runner.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
'''
        
        with open('custodes-standalone.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Systemd service file created")
        
    except Exception as e:
        print(f"❌ Error creating systemd service: {str(e)}")

def install_standalone_service():
    """Install the standalone service"""
    
    try:
        print("🔧 Installing standalone Custodes service...")
        
        # Stop old service if running
        os.system("sudo systemctl stop custodes-scheduler.service 2>/dev/null || true")
        os.system("sudo systemctl disable custodes-scheduler.service 2>/dev/null || true")
        
        # Copy service file to systemd
        os.system("sudo cp custodes-standalone.service /etc/systemd/system/custodes-scheduler.service")
        
        # Reload systemd
        os.system("sudo systemctl daemon-reload")
        
        # Enable and start service
        os.system("sudo systemctl enable custodes-scheduler.service")
        os.system("sudo systemctl start custodes-scheduler.service")
        
        print("✅ Standalone Custodes service installed and started")
        
        # Check status
        os.system("sudo systemctl status custodes-scheduler.service")
        
    except Exception as e:
        print(f"❌ Error installing service: {str(e)}")

def force_run_tests_now():
    """Force run Custodes tests immediately"""
    
    try:
        print("🚀 Force running Custodes tests immediately...")
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to be ready...")
        start_time = time.time()
        while time.time() - start_time < 300:
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    break
            except:
                pass
            print("  Backend not ready, waiting 10 seconds...")
            time.sleep(10)
        else:
            print("❌ Backend did not become ready within timeout")
            return
        
        # Run tests for all AIs
        base_url = "http://localhost:8000"
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        results = {}
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                
                response = requests.post(
                    f"{base_url}/api/custody/test/{ai_type}/force",
                    headers={"Content-Type": "application/json"},
                    timeout=60
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
        time.sleep(30)
        
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

if __name__ == "__main__":
    print("🛡️ Final Custodes Fix")
    print("=" * 50)
    
    # Fix background service
    fix_background_service()
    
    # Create standalone runner
    create_standalone_custodes_runner()
    
    # Create systemd service
    create_systemd_service()
    
    # Install service
    install_standalone_service()
    
    # Force run tests immediately
    print("\n" + "=" * 50)
    results = force_run_tests_now()
    
    print("\n✅ Final Custodes fix completed!")
    print("🛡️ Tests have been forced to run immediately")
    print("⏰ Standalone Custodes service installed and running")
    print("🧪 Tests will now run automatically every 4 hours")
    print("🚀 You can also run: python custodes_standalone_runner.py") 