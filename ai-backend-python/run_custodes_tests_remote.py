#!/usr/bin/env python3
"""
Run Custodes Tests on Remote EC2 Instance
=========================================

This script runs Custodes tests for all AI agents on the remote EC2 instance.
It's designed to be run directly without user interaction.
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

async def run_custodes_tests():
    """Run Custodes tests for all AI agents"""
    try:
        print(f"🛡️ [{datetime.now()}] Starting Custodes tests for all AI agents...")
        
        # Initialize custody service
        custody_service = await CustodyProtocolService.initialize()
        
        # Get current analytics
        analytics = await custody_service.get_custody_analytics()
        print(f"📊 [{datetime.now()}] Current custody status:")
        for ai_type, metrics in analytics.get("ai_specific_metrics", {}).items():
            tests_given = metrics.get("total_tests_given", 0)
            tests_passed = metrics.get("total_tests_passed", 0)
            can_create = metrics.get("can_create_proposals", False)
            print(f"  {ai_type}: {tests_given} tests given, {tests_passed} passed, Can create proposals: {can_create}")
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                print(f"🧪 [{datetime.now()}] Running Custodes test for {ai_type}...")
                
                # Administer test
                test_result = await custody_service.administer_custody_test(ai_type)
                
                if test_result.get("passed", False):
                    print(f"✅ [{datetime.now()}] {ai_type} passed the test!")
                else:
                    print(f"❌ [{datetime.now()}] {ai_type} failed the test: {test_result.get('score', 0)}/100")
                
                # Wait between tests to avoid rate limiting
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ [{datetime.now()}] Error testing {ai_type}: {str(e)}")
        
        # Get updated analytics
        print(f"\n📊 [{datetime.now()}] Updated custody status:")
        updated_analytics = await custody_service.get_custody_analytics()
        for ai_type, metrics in updated_analytics.get("ai_specific_metrics", {}).items():
            can_create = metrics.get("can_create_proposals", False)
            tests_given = metrics.get("total_tests_given", 0)
            tests_passed = metrics.get("total_tests_passed", 0)
            print(f"  {ai_type}: {tests_given} tests given, {tests_passed} passed, Can create proposals: {can_create}")
        
        print(f"✅ [{datetime.now()}] Custodes tests completed!")
        
        # Check if any AIs can now create proposals
        eligible_ais = []
        for ai_type, metrics in updated_analytics.get("ai_specific_metrics", {}).items():
            if metrics.get("can_create_proposals", False):
                eligible_ais.append(ai_type)
        
        if eligible_ais:
            print(f"🎉 [{datetime.now()}] AIs that can now create proposals: {', '.join(eligible_ais)}")
        else:
            print(f"⚠️ [{datetime.now()}] No AIs are eligible to create proposals yet")
        
    except Exception as e:
        print(f"❌ [{datetime.now()}] Error running Custodes tests: {str(e)}")
        raise

async def main():
    """Main function"""
    print(f"🚀 [{datetime.now()}] Custodes Test Runner Starting...")
    print("=" * 60)
    
    await run_custodes_tests()
    
    print("=" * 60)
    print(f"🏁 [{datetime.now()}] Custodes Test Runner Completed!")

if __name__ == "__main__":
    asyncio.run(main()) 