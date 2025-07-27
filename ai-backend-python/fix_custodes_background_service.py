#!/usr/bin/env python3
"""
Fix Custodes Background Service
===============================

This script checks and fixes the background service to ensure the custody testing cycle
is running properly. The issue is that custody tests are not being triggered automatically.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.background_service import BackgroundService
from app.services.custody_protocol_service import CustodyProtocolService

logger = structlog.get_logger()

async def check_background_service():
    """Check if background service is running and custody tests are scheduled"""
    try:
        print("🔍 Checking background service status...")
        
        # Initialize background service
        background_service = await BackgroundService.initialize()
        
        # Check if service is running
        status = await background_service.get_system_status()
        print(f"Background service running: {status.get('autonomous_cycle_running', False)}")
        print(f"Active tasks: {status.get('active_tasks', 0)}")
        
        # Check custody service
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        print("\n📊 Current custody status:")
        for ai_type, metrics in analytics.get("ai_specific_metrics", {}).items():
            tests_given = metrics.get("total_tests_given", 0)
            tests_passed = metrics.get("total_tests_passed", 0)
            last_test = metrics.get("last_test_date")
            can_create = metrics.get("can_create_proposals", False)
            
            print(f"  {ai_type}: {tests_given} tests given, {tests_passed} passed, Last test: {last_test}, Can create proposals: {can_create}")
        
        return status, analytics
        
    except Exception as e:
        print(f"❌ Error checking background service: {str(e)}")
        return None, None

async def restart_background_service():
    """Restart the background service to ensure custody testing is active"""
    try:
        print("🔄 Restarting background service...")
        
        # Initialize background service
        background_service = await BackgroundService.initialize()
        
        # Stop current cycle if running
        if background_service._running:
            await background_service.stop_autonomous_cycle()
            print("✅ Stopped current autonomous cycle")
        
        # Start new cycle
        await background_service.start_autonomous_cycle()
        print("✅ Started new autonomous cycle with custody testing")
        
        # Wait a moment for tasks to start
        await asyncio.sleep(5)
        
        # Check status again
        status = await background_service.get_system_status()
        print(f"✅ Background service restarted. Running: {status.get('autonomous_cycle_running', False)}")
        
    except Exception as e:
        print(f"❌ Error restarting background service: {str(e)}")

async def trigger_immediate_custody_tests():
    """Trigger custody tests immediately for all AIs"""
    try:
        print("🛡️ Triggering immediate custody tests...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                print(f"🧪 Testing {ai_type}...")
                result = await custody_service.administer_custody_test(ai_type)
                
                if result.get("passed", False):
                    print(f"✅ {ai_type} passed!")
                else:
                    print(f"❌ {ai_type} failed: {result.get('score', 0)}/100")
                
                # Wait between tests
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"❌ Error testing {ai_type}: {str(e)}")
        
        print("✅ Immediate custody tests completed!")
        
    except Exception as e:
        print(f"❌ Error in immediate custody tests: {str(e)}")

async def check_custody_testing_schedule():
    """Check the custody testing schedule configuration"""
    try:
        print("📅 Checking custody testing schedule...")
        
        # Check if enhanced schedule file exists
        schedule_file = "enhanced_custodes_schedule.json"
        if os.path.exists(schedule_file):
            import json
            with open(schedule_file, 'r') as f:
                schedule = json.load(f)
            
            print("Custodes testing schedule:")
            print(f"  Main testing: {schedule['custodes_testing_schedule']['main_testing']['interval']}")
            print(f"  Comprehensive testing: {schedule['custodes_testing_schedule']['comprehensive_testing']['schedule']}")
            print(f"  Dynamic testing: {schedule['custodes_testing_schedule']['dynamic_testing']['trigger']}")
        else:
            print("❌ Enhanced Custodes schedule file not found")
        
        # Check learning schedule
        learning_schedule_file = "learning_schedule_config.json"
        if os.path.exists(learning_schedule_file):
            import json
            with open(learning_schedule_file, 'r') as f:
                learning_schedule = json.load(f)
            
            print("\nLearning cycle schedule:")
            print(f"  Main cycle: {learning_schedule['learning_cycle_schedule']['main_cycle']['interval']}")
            print(f"  Custody tests: {learning_schedule['learning_cycle_schedule']['custody_tests']['regular']}")
        else:
            print("❌ Learning schedule file not found")
        
    except Exception as e:
        print(f"❌ Error checking schedule: {str(e)}")

async def fix_custody_testing_frequency():
    """Fix custody testing frequency to be more frequent"""
    try:
        print("⚡ Fixing custody testing frequency...")
        
        # Create more frequent schedule
        enhanced_schedule = {
            "custodes_testing_schedule": {
                "main_testing": {
                    "interval": "Every 30 minutes",
                    "description": "Custodes tests run every 30 minutes",
                    "trigger": "scheduled"
                },
                "comprehensive_testing": {
                    "schedule": "Every 2 hours",
                    "description": "Comprehensive testing for all AIs every 2 hours"
                },
                "dynamic_testing": {
                    "trigger": "new_learning_detected",
                    "description": "Additional tests when AIs learn new subjects"
                },
                "proposal_gate": {
                    "requirement": "Must pass Custodes test before proposal generation",
                    "cooldown": "15 minutes after test completion"
                },
                "knowledge_assessment": {
                    "frequency": "Every 30 minutes",
                    "focus": "AI knowledge verification and assessment",
                    "difficulty_scaling": "Based on AI level and recent learning"
                }
            },
            "learning_cycle_schedule": {
                "main_cycle": {
                    "start_time": "06:00",
                    "interval": "1 hour",
                    "description": "Main learning cycle starts at 6 AM and runs every hour"
                },
                "custodes_delay": "30 minutes after learning cycle completion",
                "proposal_delay": "After Custodes test completion"
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Save enhanced schedule
        with open('enhanced_custodes_schedule.json', 'w') as f:
            import json
            json.dump(enhanced_schedule, f, indent=2)
        
        print("✅ Enhanced Custodes schedule created with more frequent testing")
        print("   - Regular tests: Every 30 minutes")
        print("   - Comprehensive tests: Every 2 hours")
        print("   - Knowledge assessment: Every 30 minutes")
        
    except Exception as e:
        print(f"❌ Error fixing custody testing frequency: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Custodes Background Service Fix Script")
    print("=" * 60)
    
    # Check current status
    status, analytics = await check_background_service()
    
    print("\n" + "=" * 60)
    
    # Check schedule
    await check_custody_testing_schedule()
    
    print("\n" + "=" * 60)
    
    # Ask user what to do
    print("Choose an option:")
    print("1. Restart background service")
    print("2. Trigger immediate custody tests")
    print("3. Fix custody testing frequency")
    print("4. All of the above")
    print("5. Check status only")
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        await restart_background_service()
    elif choice == "2":
        await trigger_immediate_custody_tests()
    elif choice == "3":
        await fix_custody_testing_frequency()
    elif choice == "4":
        await fix_custody_testing_frequency()
        await restart_background_service()
        await trigger_immediate_custody_tests()
    elif choice == "5":
        print("Status check completed above.")
    else:
        print("Invalid choice. Running all fixes...")
        await fix_custody_testing_frequency()
        await restart_background_service()
        await trigger_immediate_custody_tests()
    
    print("\n" + "=" * 60)
    print("Final status check:")
    await check_background_service()

if __name__ == "__main__":
    asyncio.run(main()) 