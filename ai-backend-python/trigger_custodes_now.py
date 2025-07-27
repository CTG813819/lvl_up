#!/usr/bin/env python3
"""
Trigger Custodes Tests Now (Optimized)
======================================

This script manually triggers Custodes tests for all AI agents
now that the system is optimized for low CPU usage.
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

async def trigger_custodes_tests_now():
    """Trigger Custodes tests for all AI agents now"""
    try:
        print(f"🛡️ [{datetime.now()}] Triggering Custodes tests for all AI agents...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                print(f"🧪 Running Custody test for {ai_type}...")
                
                # Run the custody test
                test_result = await custody_service.administer_custody_test(ai_type)
                
                if test_result.get('passed', False):
                    print(f"✅ Custody test PASSED for {ai_type}")
                else:
                    print(f"❌ Custody test FAILED for {ai_type}")
                    print(f"   Reason: {test_result.get('reason', 'Unknown')}")
                
                # Wait a bit between tests to avoid overwhelming the system
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"❌ Error running Custody test for {ai_type}: {str(e)}")
        
        print(f"🛡️ [{datetime.now()}] All Custodes tests completed!")
        
        # Check the results
        print("\n📊 Checking Custodes test results...")
        
        for ai_type in ai_types:
            try:
                analytics = await custody_service.get_custody_analytics()
                ai_metrics = analytics.get("ai_specific_metrics", {}).get(ai_type, {})
                print(f"📈 {ai_type.capitalize()} metrics:")
                print(f"   Tests given: {ai_metrics.get('total_tests_given', 0)}")
                print(f"   Tests passed: {ai_metrics.get('total_tests_passed', 0)}")
                print(f"   Success rate: {ai_metrics.get('pass_rate', 0):.1f}%")
                print(f"   Last test: {ai_metrics.get('last_test_date', 'Never')}")
                print()
            except Exception as e:
                print(f"❌ Error getting metrics for {ai_type}: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error in Custodes test trigger: {str(e)}")

if __name__ == "__main__":
    asyncio.run(trigger_custodes_tests_now()) 