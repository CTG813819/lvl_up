#!/usr/bin/env python3
"""
Force Custody Tests Script
==========================

This script forces the custody testing system to run tests immediately
for all AI types to verify the system is working.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.services.custody_protocol_service import CustodyProtocolService

logger = structlog.get_logger()


async def force_custody_tests():
    """Force custody tests for all AI types"""
    try:
        print("🛡️ Forcing Custody Protocol tests for all AIs...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                print(f"🧪 Running Custody test for {ai_type}...")
                test_result = await custody_service.administer_custody_test(ai_type)
                
                if test_result.get('passed', False):
                    print(f"✅ {ai_type} PASSED custody test")
                else:
                    print(f"❌ {ai_type} FAILED custody test")
                
                print(f"   Score: {test_result.get('score', 'N/A')}")
                print(f"   Category: {test_result.get('category', 'N/A')}")
                print(f"   Difficulty: {test_result.get('difficulty', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Error testing {ai_type}: {str(e)}")
        
        # Get updated analytics
        print("\n📊 Getting updated custody analytics...")
        analytics = await custody_service.get_custody_analytics()
        
        print(f"📈 Overall metrics:")
        overall = analytics.get('overall_metrics', {})
        print(f"   Total tests given: {overall.get('total_tests_given', 0)}")
        print(f"   Total tests passed: {overall.get('total_tests_passed', 0)}")
        print(f"   Total tests failed: {overall.get('total_tests_failed', 0)}")
        print(f"   Overall pass rate: {overall.get('overall_pass_rate', 0):.2%}")
        
        print(f"\n🤖 AI-specific metrics:")
        ai_metrics = analytics.get('ai_specific_metrics', {})
        for ai_type, metrics in ai_metrics.items():
            print(f"   {ai_type}:")
            print(f"     Tests given: {metrics.get('total_tests_given', 0)}")
            print(f"     Tests passed: {metrics.get('total_tests_passed', 0)}")
            print(f"     Pass rate: {metrics.get('pass_rate', 0):.2%}")
            print(f"     Can create proposals: {metrics.get('can_create_proposals', False)}")
            print(f"     Can level up: {metrics.get('can_level_up', False)}")
        
        print("\n✅ Custody testing completed!")
        
    except Exception as e:
        print(f"❌ Error in custody testing: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(force_custody_tests()) 