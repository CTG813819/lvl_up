#!/usr/bin/env python3
"""Test script to verify custody service fixes"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService

async def test_custody_service():
    """Test the custody service fixes"""
    try:
        print("🧪 Testing Custody Protocol Service fixes...")
        
        # Initialize the service
        service = await CustodyProtocolService.initialize()
        print("✅ Custody service initialized successfully")
        
        # Test custody test
        result = await service.administer_custody_test('imperium')
        print(f"✅ Custody test result: {result}")
        
        # Test collaborative test
        collab_result = await service._execute_collaborative_test(
            participants=['imperium', 'guardian'],
            scenario='Test collaborative scenario',
            context={'difficulty': 'intermediate'}
        )
        print(f"✅ Collaborative test result: {collab_result}")
        
        # Test Olympic event
        olympic_result = await service.administer_olympic_event(
            participants=['imperium', 'guardian', 'sandbox'],
            difficulty='intermediate',
            event_type='test_olympics'
        )
        print(f"✅ Olympic event result: {olympic_result}")
        
        # Test AI level
        level = await service._get_ai_level('imperium')
        print(f"✅ AI level for imperium: {level}")
        
        print("🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_custody_service()) 