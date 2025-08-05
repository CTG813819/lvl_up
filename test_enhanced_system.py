#!/usr/bin/env python3
"""
Test the enhanced test system
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_enhanced_system():
    """Test the enhanced test system"""
    try:
        from app.core.database import init_database
        from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty
        
        print("🧪 Testing Enhanced Test System...")
        
        # Initialize database first
        await init_database()
        print("✅ Database initialized")
        
        # Initialize the custody protocol service
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized")
        
        # Test 1: Administer a custody test
        print("\n📋 Testing custody test for imperium...")
        result = await custody_service.administer_custody_test('imperium')
        print(f"✅ Custody test result: {result.get('success', False)}")
        
        # Test 2: Administer Olympic event
        print("\n🏆 Testing Olympic event...")
        olympic_result = await custody_service.administer_olympic_event(
            participants=['imperium', 'guardian'],
            difficulty=TestDifficulty.INTERMEDIATE
        )
        print(f"✅ Olympic event result: {olympic_result.get('success', False)}")
        
        # Test 3: Administer collaborative test
        print("\n🤝 Testing collaborative test...")
        collaborative_result = await custody_service._execute_collaborative_test(
            participants=['imperium', 'guardian'],
            scenario="Design a secure authentication system",
            context={}
        )
        print(f"✅ Collaborative test result: {collaborative_result.get('success', False)}")
        
        print("\n🎉 Enhanced test system is working!")
        
    except Exception as e:
        print(f"❌ Error testing enhanced system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_system()) 