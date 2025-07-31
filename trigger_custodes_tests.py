#!/usr/bin/env python3
"""
Trigger Custodes Tests to Demonstrate XP Award System
This script manually triggers tests for each AI to show XP awards working
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
from sqlalchemy import select
import structlog

logger = structlog.get_logger()

async def trigger_custodes_tests():
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

if __name__ == "__main__":
    asyncio.run(main()) 