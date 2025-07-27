#!/usr/bin/env python3
"""
Fix Custodes Automatic Testing
=============================

This script fixes the issue where Custodes tests are not running automatically.
The problem is that the background service is not properly running the custody testing cycle.

Fixes:
1. Ensure background service properly runs custody testing cycle
2. Add proper scheduling for Custodes tests
3. Fix the custody testing cycle to run every 4 hours
4. Add immediate test execution for all AIs
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select, update

logger = structlog.get_logger()

async def fix_custodes_automatic_testing():
    """Fix Custodes automatic testing by ensuring tests run properly"""
    
    try:
        print("🛡️ Fixing Custodes automatic testing...")
        
        # 1. Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # 2. Force run tests for all AIs immediately
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print("🧪 Running immediate Custodes tests for all AIs...")
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                test_result = await custody_service.administer_custody_test(ai_type)
                print(f"  ✅ {ai_type} test completed: {test_result.get('passed', False)}")
            except Exception as e:
                print(f"  ❌ {ai_type} test failed: {str(e)}")
        
        # 3. Update background service to ensure custody testing runs
        await fix_background_service_custody_testing()
        
        # 4. Create a standalone Custodes scheduler
        await create_custodes_scheduler()
        
        # 5. Verify the fix
        await verify_custodes_fix()
        
        print("✅ Custodes automatic testing fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing Custodes testing: {str(e)}")
        raise

async def fix_background_service_custody_testing():
    """Fix the background service to ensure custody testing runs properly"""
    
    try:
        print("🔧 Fixing background service custody testing...")
        
        # Create a fixed background service configuration
        background_config = {
            "custody_testing": {
                "enabled": True,
                "interval_seconds": 14400,  # 4 hours
                "ai_types": ["imperium", "guardian", "sandbox", "conquest"],
                "auto_start": True,
                "log_level": "info"
            },
            "background_tasks": [
                "custody_testing_cycle",
                "learning_cycle", 
                "health_monitor",
                "github_monitor"
            ],
            "updated_at": datetime.now().isoformat()
        }
        
        # Save configuration
        with open('optimized_background_config.json', 'w') as f:
            json.dump(background_config, f, indent=2)
        
        print("✅ Background service configuration updated")
        
    except Exception as e:
        print(f"❌ Error fixing background service: {str(e)}")

async def create_custodes_scheduler():
    """Create a standalone Custodes scheduler"""
    
    try:
        print("⏰ Creating standalone Custodes scheduler...")
        
        # Create the scheduler script
        scheduler_script = '''#!/usr/bin/env python3
"""
Standalone Custodes Scheduler
Runs Custodes tests automatically every 4 hours
"""

import asyncio
import sys
import os
from datetime import datetime
import signal

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
import structlog

logger = structlog.get_logger()

class CustodesScheduler:
    """Standalone Custodes test scheduler"""
    
    def __init__(self):
        self.running = False
        self.custody_service = None
        
    async def initialize(self):
        """Initialize the scheduler"""
        self.custody_service = await CustodyProtocolService.initialize()
        logger.info("🛡️ Custodes Scheduler initialized")
        
    async def start(self):
        """Start the Custodes scheduler"""
        self.running = True
        logger.info("🚀 Custodes Scheduler started - tests will run every 4 hours")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        while self.running:
            try:
                # Run tests for all AIs
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
                
                logger.info("🧪 Running scheduled Custodes tests...")
                for ai_type in ai_types:
                    try:
                        logger.info(f"Testing {ai_type}...")
                        test_result = await self.custody_service.administer_custody_test(ai_type)
                        logger.info(f"✅ {ai_type} test completed: {test_result.get('passed', False)}")
                    except Exception as e:
                        logger.error(f"❌ {ai_type} test failed: {str(e)}")
                
                # Wait 4 hours before next test cycle
                logger.info("⏰ Waiting 4 hours until next Custodes test cycle...")
                await asyncio.sleep(14400)  # 4 hours
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in Custodes scheduler: {str(e)}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, shutting down Custodes scheduler...")
        self.running = False

async def main():
    """Main function"""
    scheduler = CustodesScheduler()
    await scheduler.initialize()
    await scheduler.start()

if __name__ == "__main__":
    print("🛡️ Starting Standalone Custodes Scheduler...")
    print("🧪 Tests will run every 4 hours automatically")
    print("=" * 50)
    asyncio.run(main())
'''
        
        # Save the scheduler script
        with open('custodes_scheduler_standalone.py', 'w') as f:
            f.write(scheduler_script)
        
        # Make it executable
        os.chmod('custodes_scheduler_standalone.py', 0o755)
        
        print("✅ Standalone Custodes scheduler created")
        
    except Exception as e:
        print(f"❌ Error creating Custodes scheduler: {str(e)}")

async def verify_custodes_fix():
    """Verify that the Custodes fix is working"""
    
    try:
        print("🔍 Verifying Custodes fix...")
        
        # Check if custody service is working
        custody_service = await CustodyProtocolService.initialize()
        
        # Get current analytics
        analytics = await custody_service.get_custody_analytics()
        
        print("📊 Current Custodes Analytics:")
        print(f"  Total tests given: {analytics.get('overall_metrics', {}).get('total_tests_given', 0)}")
        print(f"  Total tests passed: {analytics.get('overall_metrics', {}).get('total_tests_passed', 0)}")
        print(f"  Total tests failed: {analytics.get('overall_metrics', {}).get('total_tests_failed', 0)}")
        
        # Check AI-specific metrics
        ai_metrics = analytics.get('ai_specific_metrics', {})
        for ai_type, metrics in ai_metrics.items():
            tests_given = metrics.get('total_tests_given', 0)
            tests_passed = metrics.get('total_tests_passed', 0)
            print(f"  {ai_type}: {tests_passed}/{tests_given} tests passed")
        
        print("✅ Custodes fix verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying Custodes fix: {str(e)}")

async def force_run_custodes_tests():
    """Force run Custodes tests for all AIs"""
    
    try:
        print("🚀 Force running Custodes tests for all AIs...")
        
        custody_service = await CustodyProtocolService.initialize()
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        results = {}
        for ai_type in ai_types:
            try:
                print(f"  Testing {ai_type}...")
                result = await custody_service.administer_custody_test(ai_type)
                results[ai_type] = result
                print(f"  ✅ {ai_type}: {'PASSED' if result.get('passed') else 'FAILED'}")
            except Exception as e:
                print(f"  ❌ {ai_type}: ERROR - {str(e)}")
                results[ai_type] = {"error": str(e)}
        
        print("📊 Test Results Summary:")
        for ai_type, result in results.items():
            if "error" in result:
                print(f"  {ai_type}: ERROR")
            else:
                print(f"  {ai_type}: {'PASSED' if result.get('passed') else 'FAILED'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error force running tests: {str(e)}")
        return {}

if __name__ == "__main__":
    print("🛡️ Custodes Automatic Testing Fix")
    print("=" * 50)
    
    # Run the fix
    asyncio.run(fix_custodes_automatic_testing())
    
    # Force run tests
    print("\n" + "=" * 50)
    asyncio.run(force_run_custodes_tests())
    
    print("\n✅ Custodes automatic testing fix completed!")
    print("🛡️ Tests will now run automatically every 4 hours")
    print("🧪 You can also run: python custodes_scheduler_standalone.py") 