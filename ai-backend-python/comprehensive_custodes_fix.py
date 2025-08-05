#!/usr/bin/env python3
"""
Comprehensive Custodes Fix
=========================

This script provides a comprehensive fix for Custodes automatic testing that:
1. Runs tests every 2 hours (instead of 4)
2. Triggers tests when AIs have proposals
3. Properly obeys the existing Custodes functions
4. Focuses on conquest AI and all other AIs
"""

import asyncio
import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta

def create_comprehensive_custodes_scheduler():
    """Create a comprehensive Custodes scheduler that runs every 2 hours and checks for proposals"""
    
    try:
        print("🚀 Creating comprehensive Custodes scheduler...")
        
        # Create the comprehensive scheduler script
        scheduler_script = '''#!/usr/bin/env python3
"""
Comprehensive Custodes Scheduler
Runs Custodes tests every 2 hours and when AIs have proposals
"""

import asyncio
import sys
import os
import requests
import time
from datetime import datetime, timedelta

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

def check_ai_proposals():
    """Check if any AIs have pending proposals"""
    try:
        base_url = "http://localhost:8000"
        response = requests.get(f"{base_url}/api/proposals/", timeout=10)
        
        if response.status_code == 200:
            proposals = response.json()
            pending_proposals = [p for p in proposals if p.get('status') == 'pending']
            
            if pending_proposals:
                print(f"[{datetime.now()}] 📋 Found {len(pending_proposals)} pending proposals")
                # Group by AI type
                ai_proposals = {}
                for proposal in pending_proposals:
                    ai_type = proposal.get('ai_type', '').lower()
                    if ai_type not in ai_proposals:
                        ai_proposals[ai_type] = []
                    ai_proposals[ai_type].append(proposal)
                
                return ai_proposals
            else:
                print(f"[{datetime.now()}] 📋 No pending proposals found")
                return {}
        else:
            print(f"[{datetime.now()}] ❌ Could not get proposals: HTTP {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error checking proposals: {str(e)}")
        return {}

def run_custodes_tests_for_ai(ai_type):
    """Run Custodes test for a specific AI"""
    try:
        base_url = "http://localhost:8000"
        print(f"[{datetime.now()}] 🧪 Testing {ai_type}...")
        
        response = requests.post(
            f"{base_url}/api/custody/test/{ai_type}/force",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[{datetime.now()}] ✅ {ai_type} test initiated successfully")
            return True
        else:
            print(f"[{datetime.now()}] ❌ {ai_type} test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ {ai_type} test error: {str(e)}")
        return False

def run_comprehensive_custodes_tests():
    """Run comprehensive Custodes tests for all AIs"""
    try:
        # Wait for backend to be ready
        if not wait_for_backend():
            print(f"[{datetime.now()}] ❌ Cannot run tests - backend not ready")
            return False
        
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"[{datetime.now()}] 🧪 Running comprehensive Custodes tests for all AIs...")
        
        success_count = 0
        for ai_type in ai_types:
            if run_custodes_tests_for_ai(ai_type):
                success_count += 1
        
        print(f"[{datetime.now()}] ✅ Comprehensive test cycle completed: {success_count}/{len(ai_types)} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in comprehensive test cycle: {str(e)}")
        return False

def run_proposal_triggered_tests():
    """Run tests for AIs that have pending proposals"""
    try:
        # Check for pending proposals
        ai_proposals = check_ai_proposals()
        
        if not ai_proposals:
            return False
        
        print(f"[{datetime.now()}] 🚀 Running proposal-triggered tests...")
        
        success_count = 0
        for ai_type, proposals in ai_proposals.items():
            print(f"[{datetime.now()}] 📋 {ai_type} has {len(proposals)} pending proposals - running test")
            if run_custodes_tests_for_ai(ai_type):
                success_count += 1
        
        print(f"[{datetime.now()}] ✅ Proposal-triggered tests completed: {success_count}/{len(ai_proposals)} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in proposal-triggered tests: {str(e)}")
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
                can_create_proposals = metrics.get('can_create_proposals', False)
                print(f"[{datetime.now()}]   {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed, can_create_proposals: {can_create_proposals}")
        else:
            print(f"[{datetime.now()}] ❌ Could not get analytics: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error getting analytics: {str(e)}")

def main():
    """Main function"""
    print(f"[{datetime.now()}] 🛡️ Comprehensive Custodes Scheduler started")
    print(f"[{datetime.now()}] ⏰ Tests will run every 2 hours and when AIs have proposals")
    print(f"[{datetime.now()}] 🎯 Focus: conquest, imperium, guardian, sandbox")
    
    # Run initial comprehensive test cycle
    print(f"[{datetime.now()}] 🚀 Running initial comprehensive test cycle...")
    run_comprehensive_custodes_tests()
    
    # Wait for tests to complete
    print(f"[{datetime.now()}] ⏳ Waiting for tests to complete...")
    time.sleep(30)
    
    # Check results
    check_test_results()
    
    # Start continuous loop
    last_comprehensive_test = time.time()
    last_proposal_check = time.time()
    
    while True:
        try:
            current_time = time.time()
            
            # Check for proposals every 30 minutes
            if current_time - last_proposal_check >= 1800:  # 30 minutes
                print(f"[{datetime.now()}] 📋 Checking for pending proposals...")
                run_proposal_triggered_tests()
                last_proposal_check = current_time
                
                # Wait for proposal tests to complete
                time.sleep(30)
                check_test_results()
            
            # Run comprehensive tests every 2 hours
            if current_time - last_comprehensive_test >= 7200:  # 2 hours
                print(f"[{datetime.now()}] 🧪 Running scheduled comprehensive tests...")
                run_comprehensive_custodes_tests()
                last_comprehensive_test = current_time
                
                # Wait for tests to complete
                time.sleep(30)
                check_test_results()
            
            # Sleep for 5 minutes before next check
            print(f"[{datetime.now()}] ⏰ Sleeping for 5 minutes...")
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] 🛑 Comprehensive Custodes Scheduler stopped")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error in main loop: {str(e)}")
            time.sleep(600)  # Wait 10 minutes on error

if __name__ == "__main__":
    main()
'''
        
        # Save the scheduler script
        with open('custodes_comprehensive_scheduler.py', 'w') as f:
            f.write(scheduler_script)
        
        # Make it executable
        os.chmod('custodes_comprehensive_scheduler.py', 0o755)
        
        print("✅ Comprehensive Custodes scheduler created")
        
    except Exception as e:
        print(f"❌ Error creating comprehensive scheduler: {str(e)}")

def create_systemd_service():
    """Create a systemd service for the comprehensive scheduler"""
    
    try:
        print("⏰ Creating systemd service for comprehensive scheduler...")
        
        # Create systemd service file
        service_content = '''[Unit]
Description=Comprehensive Custodes Test Scheduler
After=network.target ai-backend-python.service
Wants=ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/custodes_comprehensive_scheduler.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
'''
        
        with open('custodes-comprehensive.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Systemd service file created")
        
    except Exception as e:
        print(f"❌ Error creating systemd service: {str(e)}")

def install_comprehensive_service():
    """Install the comprehensive service"""
    
    try:
        print("🔧 Installing comprehensive Custodes service...")
        
        # Stop old service if running
        os.system("sudo systemctl stop custodes-scheduler.service 2>/dev/null || true")
        os.system("sudo systemctl disable custodes-scheduler.service 2>/dev/null || true")
        
        # Copy service file to systemd
        os.system("sudo cp custodes-comprehensive.service /etc/systemd/system/custodes-scheduler.service")
        
        # Reload systemd
        os.system("sudo systemctl daemon-reload")
        
        # Enable and start service
        os.system("sudo systemctl enable custodes-scheduler.service")
        os.system("sudo systemctl start custodes-scheduler.service")
        
        print("✅ Comprehensive Custodes service installed and started")
        
        # Check status
        os.system("sudo systemctl status custodes-scheduler.service")
        
    except Exception as e:
        print(f"❌ Error installing service: {str(e)}")

def force_run_comprehensive_tests():
    """Force run comprehensive Custodes tests immediately"""
    
    try:
        print("🚀 Force running comprehensive Custodes tests immediately...")
        
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
        
        # Check for proposals first
        print("📋 Checking for pending proposals...")
        ai_proposals = check_ai_proposals()
        
        if ai_proposals:
            print("🚀 Running proposal-triggered tests...")
            for ai_type, proposals in ai_proposals.items():
                print(f"  📋 {ai_type} has {len(proposals)} pending proposals - running test")
                run_custodes_tests_for_ai(ai_type)
        
        # Run comprehensive tests for all AIs
        print("🧪 Running comprehensive tests for all AIs...")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        results = {}
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                
                response = requests.post(
                    f"http://localhost:8000/api/custody/test/{ai_type}/force",
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
        check_test_results()
        
        return results
        
    except Exception as e:
        print(f"❌ Error force running tests: {str(e)}")
        return {}

def check_ai_proposals():
    """Check if any AIs have pending proposals"""
    try:
        base_url = "http://localhost:8000"
        response = requests.get(f"{base_url}/api/proposals/", timeout=10)
        
        if response.status_code == 200:
            proposals = response.json()
            pending_proposals = [p for p in proposals if p.get('status') == 'pending']
            
            if pending_proposals:
                print(f"📋 Found {len(pending_proposals)} pending proposals")
                # Group by AI type
                ai_proposals = {}
                for proposal in pending_proposals:
                    ai_type = proposal.get('ai_type', '').lower()
                    if ai_type not in ai_proposals:
                        ai_proposals[ai_type] = []
                    ai_proposals[ai_type].append(proposal)
                
                return ai_proposals
            else:
                print("📋 No pending proposals found")
                return {}
        else:
            print(f"❌ Could not get proposals: HTTP {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"❌ Error checking proposals: {str(e)}")
        return {}

def run_custodes_tests_for_ai(ai_type):
    """Run Custodes test for a specific AI"""
    try:
        base_url = "http://localhost:8000"
        print(f"🧪 Testing {ai_type}...")
        
        response = requests.post(
            f"{base_url}/api/custody/test/{ai_type}/force",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {ai_type} test initiated successfully")
            return True
        else:
            print(f"❌ {ai_type} test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {ai_type} test error: {str(e)}")
        return False

def check_test_results():
    """Check the results of the tests"""
    try:
        base_url = "http://localhost:8000"
        response = requests.get(f"{base_url}/api/custody/", timeout=10)
        
        if response.status_code == 200:
            analytics = response.json()
            ai_metrics = analytics.get('analytics', {}).get('ai_specific_metrics', {})
            
            print("📊 Current Test Results:")
            for ai_type, metrics in ai_metrics.items():
                tests_given = metrics.get('total_tests_given', 0)
                tests_passed = metrics.get('total_tests_passed', 0)
                tests_failed = metrics.get('total_tests_failed', 0)
                can_create_proposals = metrics.get('can_create_proposals', False)
                print(f"  {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed, can_create_proposals: {can_create_proposals}")
        else:
            print(f"❌ Could not get analytics: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting analytics: {str(e)}")

if __name__ == "__main__":
    print("🛡️ Comprehensive Custodes Fix")
    print("=" * 50)
    
    # Create comprehensive scheduler
    create_comprehensive_custodes_scheduler()
    
    # Create systemd service
    create_systemd_service()
    
    # Install service
    install_comprehensive_service()
    
    # Force run tests immediately
    print("\n" + "=" * 50)
    results = force_run_comprehensive_tests()
    
    print("\n✅ Comprehensive Custodes fix completed!")
    print("🛡️ Tests have been forced to run immediately")
    print("⏰ Comprehensive Custodes service installed and running")
    print("🧪 Tests will now run every 2 hours and when AIs have proposals")
    print("🎯 Focus: conquest, imperium, guardian, sandbox")
    print("🚀 You can also run: python custodes_comprehensive_scheduler.py") 