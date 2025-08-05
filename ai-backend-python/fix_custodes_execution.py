#!/usr/bin/env python3
"""
Fix Custodes Execution
=====================

This script fixes the root cause of Custodes test execution hanging.
It directly calls the custody protocol service to bypass the API timeout issue.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import get_session

logger = structlog.get_logger()

async def fix_custodes_execution():
    """Fix Custodes execution by directly calling the service"""
    
    try:
        print("🛡️ Fixing Custodes execution...")
        
        # Initialize custody service
        print("🔧 Initializing custody protocol service...")
        custody_service = await CustodyProtocolService.initialize()
        
        # AI types to test
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print("🧪 Running Custodes tests directly...")
        results = {}
        
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                
                # Direct call to custody service
                test_result = await custody_service.administer_custody_test(ai_type)
                results[ai_type] = test_result
                
                if test_result.get('passed'):
                    print(f"  ✅ {ai_type}: PASSED")
                else:
                    print(f"  ❌ {ai_type}: FAILED")
                    
            except Exception as e:
                print(f"  ❌ {ai_type}: ERROR - {str(e)}")
                results[ai_type] = {"error": str(e)}
        
        # Wait for tests to complete
        print("⏳ Waiting for tests to complete...")
        await asyncio.sleep(10)
        
        # Check results
        print("\n📊 Checking test results...")
        analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = analytics.get('ai_specific_metrics', {})
        for ai_type, metrics in ai_metrics.items():
            tests_given = metrics.get('total_tests_given', 0)
            tests_passed = metrics.get('total_tests_passed', 0)
            tests_failed = metrics.get('total_tests_failed', 0)
            can_create_proposals = metrics.get('can_create_proposals', False)
            print(f"  {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed, can_create_proposals: {can_create_proposals}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error fixing Custodes execution: {str(e)}")
        return {}

async def create_direct_custodes_runner():
    """Create a direct Custodes runner that bypasses the API"""
    
    try:
        print("🚀 Creating direct Custodes runner...")
        
        # Create the direct runner script
        runner_script = '''#!/usr/bin/env python3
"""
Direct Custodes Runner
Runs Custodes tests directly every 2 hours, bypassing API timeouts
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import get_session

logger = structlog.get_logger()

async def run_direct_custodes_tests():
    """Run Custodes tests directly"""
    try:
        print(f"[{datetime.now()}] 🧪 Running direct Custodes tests...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # AI types to test
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        success_count = 0
        for ai_type in ai_types:
            try:
                print(f"[{datetime.now()}]   Testing {ai_type}...")
                
                # Direct call to custody service
                test_result = await custody_service.administer_custody_test(ai_type)
                
                if test_result.get('passed'):
                    print(f"[{datetime.now()}] ✅ {ai_type}: PASSED")
                    success_count += 1
                else:
                    print(f"[{datetime.now()}] ❌ {ai_type}: FAILED")
                    
            except Exception as e:
                print(f"[{datetime.now()}] ❌ {ai_type}: ERROR - {str(e)}")
        
        print(f"[{datetime.now()}] ✅ Direct test cycle completed: {success_count}/{len(ai_types)} successful")
        return success_count > 0
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in direct test cycle: {str(e)}")
        return False

async def check_direct_test_results():
    """Check the results of the tests directly"""
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = analytics.get('ai_specific_metrics', {})
        
        print(f"[{datetime.now()}] 📊 Current Test Results:")
        for ai_type, metrics in ai_metrics.items():
            tests_given = metrics.get('total_tests_given', 0)
            tests_passed = metrics.get('total_tests_passed', 0)
            tests_failed = metrics.get('total_tests_failed', 0)
            can_create_proposals = metrics.get('can_create_proposals', False)
            print(f"[{datetime.now()}]   {ai_type}: {tests_passed}/{tests_given} passed, {tests_failed} failed, can_create_proposals: {can_create_proposals}")
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error getting analytics: {str(e)}")

async def main():
    """Main function"""
    print(f"[{datetime.now()}] 🛡️ Direct Custodes Runner started")
    print(f"[{datetime.now()}] ⏰ Tests will run every 2 hours")
    print(f"[{datetime.now()}] 🎯 Focus: conquest, imperium, guardian, sandbox")
    
    # Run initial test cycle
    print(f"[{datetime.now()}] 🚀 Running initial test cycle...")
    await run_direct_custodes_tests()
    
    # Wait for tests to complete
    print(f"[{datetime.now()}] ⏳ Waiting for tests to complete...")
    await asyncio.sleep(10)
    
    # Check results
    await check_direct_test_results()
    
    # Start continuous loop
    while True:
        try:
            # Wait 2 hours
            print(f"[{datetime.now()}] ⏰ Waiting 2 hours until next test cycle...")
            await asyncio.sleep(7200)  # 2 hours
            
            # Run tests
            await run_direct_custodes_tests()
            
            # Wait for tests to complete
            await asyncio.sleep(10)
            
            # Check results
            await check_direct_test_results()
            
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] 🛑 Direct Custodes Runner stopped")
            break
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error in main loop: {str(e)}")
            await asyncio.sleep(600)  # Wait 10 minutes on error

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Save the runner script
        with open('custodes_direct_runner.py', 'w') as f:
            f.write(runner_script)
        
        # Make it executable
        os.chmod('custodes_direct_runner.py', 0o755)
        
        print("✅ Direct Custodes runner created")
        
    except Exception as e:
        print(f"❌ Error creating direct runner: {str(e)}")

def create_direct_systemd_service():
    """Create a systemd service for the direct runner"""
    
    try:
        print("⏰ Creating systemd service for direct runner...")
        
        # Create systemd service file
        service_content = '''[Unit]
Description=Direct Custodes Test Runner
After=network.target ai-backend-python.service
Wants=ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/custodes_direct_runner.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
'''
        
        with open('custodes-direct.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Direct systemd service file created")
        
    except Exception as e:
        print(f"❌ Error creating direct systemd service: {str(e)}")

def install_direct_service():
    """Install the direct service"""
    
    try:
        print("🔧 Installing direct Custodes service...")
        
        # Stop old service if running
        os.system("sudo systemctl stop custodes-scheduler.service 2>/dev/null || true")
        os.system("sudo systemctl disable custodes-scheduler.service 2>/dev/null || true")
        
        # Copy service file to systemd
        os.system("sudo cp custodes-direct.service /etc/systemd/system/custodes-scheduler.service")
        
        # Reload systemd
        os.system("sudo systemctl daemon-reload")
        
        # Enable and start service
        os.system("sudo systemctl enable custodes-scheduler.service")
        os.system("sudo systemctl start custodes-scheduler.service")
        
        print("✅ Direct Custodes service installed and started")
        
        # Check status
        os.system("sudo systemctl status custodes-scheduler.service")
        
    except Exception as e:
        print(f"❌ Error installing direct service: {str(e)}")

if __name__ == "__main__":
    print("🛡️ Fix Custodes Execution")
    print("=" * 50)
    
    # Fix Custodes execution
    results = asyncio.run(fix_custodes_execution())
    
    # Create direct runner
    asyncio.run(create_direct_custodes_runner())
    
    # Create systemd service
    create_direct_systemd_service()
    
    # Install service
    install_direct_service()
    
    print("\n✅ Custodes execution fix completed!")
    print("🛡️ Tests have been run directly")
    print("⏰ Direct Custodes service installed and running")
    print("🧪 Tests will now run every 2 hours directly")
    print("🎯 Focus: conquest, imperium, guardian, sandbox")
    print("🚀 You can also run: python custodes_direct_runner.py") 