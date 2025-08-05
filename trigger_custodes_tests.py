#!/usr/bin/env python3
"""
<<<<<<< HEAD
Trigger Custodes Tests for All AI Agents
========================================

This script manually triggers Custodes tests for all AI agents to get them started.
The issue is that all AIs have 0 test metrics, which means they haven't taken any tests yet,
preventing them from creating proposals.
=======
Trigger Custodes Tests to Demonstrate XP Award System
This script manually triggers tests for each AI to show XP awards working
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
<<<<<<< HEAD
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.custody_protocol_service import CustodyProtocolService
=======
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
from sqlalchemy import select
import structlog
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5

logger = structlog.get_logger()

async def trigger_custodes_tests():
<<<<<<< HEAD
    """Trigger Custodes tests for all AI agents"""
    try:
        print("🛡️ Triggering Custodes tests for all AI agents...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Get current analytics to see the state
        analytics = await custody_service.get_custody_analytics()
        print("📊 Current custody analytics:")
        for ai_type, metrics in analytics.get("ai_specific_metrics", {}).items():
            print(f"  {ai_type}: {metrics.get('total_tests_given', 0)} tests given, {metrics.get('total_tests_passed', 0)} passed")
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                print(f"🧪 Running Custodes test for {ai_type}...")
                
                # Administer test
                test_result = await custody_service.administer_custody_test(ai_type)
                
                if test_result.get("passed", False):
                    print(f"✅ {ai_type} passed the test!")
                else:
                    print(f"❌ {ai_type} failed the test: {test_result.get('score', 0)}/100")
                
                # Wait a bit between tests to avoid rate limiting
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ Error testing {ai_type}: {str(e)}")
        
        # Get updated analytics
        print("\n📊 Updated custody analytics:")
        updated_analytics = await custody_service.get_custody_analytics()
        for ai_type, metrics in updated_analytics.get("ai_specific_metrics", {}).items():
            can_create = metrics.get("can_create_proposals", False)
            print(f"  {ai_type}: {metrics.get('total_tests_given', 0)} tests given, {metrics.get('total_tests_passed', 0)} passed, Can create proposals: {can_create}")
        
        print("\n✅ Custodes tests completed!")
        
    except Exception as e:
        print(f"❌ Error triggering Custodes tests: {str(e)}")
        raise

async def force_test_all_ais():
    """Force test all AIs using the API endpoint"""
    try:
        import aiohttp
        
        print("🛡️ Force testing all AIs via API...")
        
        async with aiohttp.ClientSession() as session:
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                try:
                    print(f"🧪 Force testing {ai_type}...")
                    
                    response = await session.post(
                        f"http://localhost:8000/api/custody/test/{ai_type}/force",
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=60)
                    )
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ {ai_type} force test initiated: {result.get('status')}")
                    else:
                        print(f"❌ {ai_type} force test failed: {response.status}")
                    
                    # Wait between tests
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    print(f"❌ Error force testing {ai_type}: {str(e)}")
        
        print("✅ Force tests completed!")
        
    except Exception as e:
        print(f"❌ Error in force testing: {str(e)}")

async def check_custody_status():
    """Check current custody status"""
    try:
        import aiohttp
        
        print("📊 Checking custody status...")
        
        async with aiohttp.ClientSession() as session:
            response = await session.get(
                "http://localhost:8000/api/custody/",
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            if response.status == 200:
                data = await response.json()
                analytics = data.get("analytics", {})
                
                print("Current custody status:")
                for ai_type, metrics in analytics.get("ai_specific_metrics", {}).items():
                    tests_given = metrics.get("total_tests_given", 0)
                    tests_passed = metrics.get("total_tests_passed", 0)
                    can_create = metrics.get("can_create_proposals", False)
                    level = metrics.get("custody_level", 1)
                    
                    print(f"  {ai_type}: Level {level}, {tests_given} tests given, {tests_passed} passed, Can create proposals: {can_create}")
                
                recommendations = analytics.get("recommendations", [])
                if recommendations:
                    print("\nRecommendations:")
                    for rec in recommendations:
                        print(f"  - {rec}")
            else:
                print(f"❌ Failed to get custody status: {response.status}")
        
    except Exception as e:
        print(f"❌ Error checking custody status: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Custodes Test Trigger Script")
    print("=" * 50)
    
    # Check current status
    await check_custody_status()
    
    print("\n" + "=" * 50)
    
    # Ask user what to do
    print("Choose an option:")
    print("1. Trigger Custodes tests directly (recommended)")
    print("2. Force test via API endpoints")
    print("3. Check status only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        await trigger_custodes_tests()
    elif choice == "2":
        await force_test_all_ais()
    elif choice == "3":
        print("Status check completed above.")
    else:
        print("Invalid choice. Running direct tests...")
        await trigger_custodes_tests()
    
    print("\n" + "=" * 50)
    print("Final status check:")
    await check_custody_status()
=======
    """Trigger Custodes tests for each AI to demonstrate XP awards"""
    print("🧪 Triggering Custodes Tests for XP Demonstration")
    print("=" * 60)
    
    try:
        # Initialize database and custody service
        await init_database()
        custody_service = await CustodyProtocolService.initialize()
        
        # Test each AI type
        ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        
        for ai_type in ai_types:
            print(f"\n🎯 Testing {ai_type.upper()} AI...")
            
            try:
                # Trigger a knowledge verification test
                result = await custody_service.administer_custody_test(
                    ai_type, 
                    TestCategory.KNOWLEDGE_VERIFICATION
                )
                
                if result.get("status") == "success":
                    test_result = result.get("test_result", {})
                    passed = test_result.get("passed", False)
                    score = test_result.get("score", 0)
                    
                    print(f"  ✅ Test completed: {'PASSED' if passed else 'FAILED'}")
                    print(f"  📊 Score: {score}/100")
                    print(f"  🎁 XP Awarded: {10 if passed else 1}")
                else:
                    print(f"  ❌ Test failed: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ❌ Error testing {ai_type}: {e}")
        
        # Check XP values after tests
        print(f"\n📊 Checking XP Values After Tests...")
        await check_xp_values()
        
    except Exception as e:
        print(f"❌ Error triggering tests: {e}")
        logger.error(f"Error triggering tests: {str(e)}")

async def check_xp_values():
    """Check XP values for all AIs"""
    try:
        async with get_session() as session:
            result = await session.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            total_xp = 0
            for agent in agents:
                xp = agent.xp or 0
                custody_xp = getattr(agent, 'custody_xp', 0) or 0
                total_tests_passed = getattr(agent, 'total_tests_passed', 0) or 0
                total_tests_failed = getattr(agent, 'total_tests_failed', 0) or 0
                
                print(f"  {agent.agent_type}: XP={xp}, Custody XP={custody_xp}, Tests: {total_tests_passed} passed, {total_tests_failed} failed")
                total_xp += xp
            
            print(f"  📈 Total XP across all AIs: {total_xp}")
            
    except Exception as e:
        print(f"❌ Error checking XP values: {e}")

async def main():
    """Run the test trigger"""
    print("🚀 Starting Custodes Test XP Demonstration")
    print("=" * 60)
    
    await trigger_custodes_tests()
    
    print("\n🎉 XP Demonstration Complete!")
    print("=" * 60)
    print("📋 Summary:")
    print("  ✅ Custodes tests triggered for all AIs")
    print("  ✅ XP should be awarded: 10 for passed tests, 1 for failed tests")
    print("  ✅ Check the results above to see XP changes")
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5

if __name__ == "__main__":
    asyncio.run(main()) 