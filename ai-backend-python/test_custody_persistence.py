#!/usr/bin/env python3
"""
Test script to verify custody protocol persistence fix
"""

import asyncio
import sys
import os
from datetime import datetime
import pytest

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import init_database
import structlog

logger = structlog.get_logger()

@pytest.mark.asyncio
async def test_custody_persistence():
    """Test that custody metrics are properly persisted"""
    try:
        print("🧪 Testing custody protocol persistence...")
        
        # Initialize database
        await init_database()
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n📊 Testing {ai_type} AI...")
            
            # Get initial status
            initial_analytics = await custody_service.get_custody_analytics()
            initial_metrics = initial_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Initial XP: {initial_metrics.get('custody_xp', 0)}")
            print(f"  Initial Level: {initial_metrics.get('custody_level', 1)}")
            
            # Force a test to generate some metrics
            print(f"  Running test for {ai_type}...")
            test_result = await custody_service.force_custody_test(ai_type)
            
            if test_result.get("status") == "error":
                print(f"  ❌ Test failed: {test_result.get('message')}")
                continue
            
            # Get updated status
            updated_analytics = await custody_service.get_custody_analytics()
            updated_metrics = updated_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Updated XP: {updated_metrics.get('custody_xp', 0)}")
            print(f"  Updated Level: {updated_metrics.get('custody_level', 1)}")
            print(f"  Tests Given: {updated_metrics.get('total_tests_given', 0)}")
            print(f"  Tests Passed: {updated_metrics.get('total_tests_passed', 0)}")
            
            # Verify persistence by reinitializing the service
            print(f"  Reinitializing service to test persistence...")
            custody_service2 = await CustodyProtocolService.initialize()
            
            # Get status after reinitialization
            final_analytics = await custody_service2.get_custody_analytics()
            final_metrics = final_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
            
            print(f"  Final XP: {final_metrics.get('custody_xp', 0)}")
            print(f"  Final Level: {final_metrics.get('custody_level', 1)}")
            
            # Check if metrics persisted
            if final_metrics.get('custody_xp', 0) > 0:
                print(f"  ✅ {ai_type} metrics persisted successfully!")
            else:
                print(f"  ❌ {ai_type} metrics did not persist!")
        
        print("\n🎯 Custody persistence test completed!")
        
    except Exception as e:
        print(f"❌ Error testing custody persistence: {str(e)}")
        logger.error(f"Error testing custody persistence: {str(e)}")

@pytest.mark.asyncio
async def test_custody_analytics():
    """Test custody analytics endpoint"""
    try:
        print("\n📈 Testing custody analytics...")
        
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        print("Overall Metrics:")
        overall = analytics.get("overall_metrics", {})
        print(f"  Total Tests: {overall.get('total_tests_given', 0)}")
        print(f"  Passed Tests: {overall.get('total_tests_passed', 0)}")
        print(f"  Failed Tests: {overall.get('total_tests_failed', 0)}")
        print(f"  Pass Rate: {overall.get('overall_pass_rate', 0):.1%}")
        
        print("\nAI-Specific Metrics:")
        ai_metrics = analytics.get("ai_specific_metrics", {})
        for ai_type, metrics in ai_metrics.items():
            print(f"  {ai_type}:")
            print(f"    XP: {metrics.get('custody_xp', 0)}")
            print(f"    Level: {metrics.get('custody_level', 1)}")
            print(f"    Tests: {metrics.get('total_tests_given', 0)}")
            print(f"    Pass Rate: {metrics.get('pass_rate', 0):.1%}")
            print(f"    Can Level Up: {metrics.get('can_level_up', False)}")
            print(f"    Can Create Proposals: {metrics.get('can_create_proposals', False)}")
        
        print("\n✅ Custody analytics test completed!")
        
    except Exception as e:
        print(f"❌ Error testing custody analytics: {str(e)}")
        logger.error(f"Error testing custody analytics: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Starting custody protocol persistence tests...")
    
    # Test persistence
    await test_custody_persistence()
    
    # Test analytics
    await test_custody_analytics()
    
    print("\n🎉 All custody protocol tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 