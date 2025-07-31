#!/usr/bin/env python3
"""
Simple Custodes Test
===================

This script tests if the Custodes system is working properly.
"""

import asyncio
import sys
import os
import pytest

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.custody_protocol_service import CustodyProtocolService
    print("✅ CustodyProtocolService imported successfully")
except Exception as e:
    print(f"❌ Error importing CustodyProtocolService: {str(e)}")
    sys.exit(1)

@pytest.mark.asyncio
async def test_custodes():
    """Test the Custodes system"""
    try:
        print("🛡️ Testing Custodes system...")
        
        # Initialize custody service
        print("🔧 Initializing custody protocol service...")
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody service initialized")
        
        # Test conquest AI specifically
        print("🎯 Testing conquest AI...")
        test_result = await custody_service.administer_custody_test("conquest")
        print(f"✅ Conquest test result: {test_result}")
        
        # Get analytics
        print("📊 Getting analytics...")
        analytics = await custody_service.get_custody_analytics()
        
        # Check conquest metrics
        conquest_metrics = analytics.get('ai_specific_metrics', {}).get('conquest', {})
        tests_given = conquest_metrics.get('total_tests_given', 0)
        tests_passed = conquest_metrics.get('total_tests_passed', 0)
        tests_failed = conquest_metrics.get('total_tests_failed', 0)
        can_create_proposals = conquest_metrics.get('can_create_proposals', False)
        
        print(f"📊 Conquest metrics:")
        print(f"  Tests given: {tests_given}")
        print(f"  Tests passed: {tests_passed}")
        print(f"  Tests failed: {tests_failed}")
        print(f"  Can create proposals: {can_create_proposals}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Custodes: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Custodes Test")
    print("=" * 30)
    
    success = asyncio.run(test_custodes())
    
    if success:
        print("\n✅ Custodes test completed successfully!")
    else:
        print("\n❌ Custodes test failed!")
        sys.exit(1) 