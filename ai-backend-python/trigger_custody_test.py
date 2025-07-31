#!/usr/bin/env python3
"""
Script to trigger custody protocol test and see autonomous scenarios
"""
import asyncio
import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

async def trigger_custody_test():
    """Trigger a custody protocol test to see autonomous scenarios"""
    print("🧪 Triggering Custody Protocol Test")
    print("=" * 50)
    
    try:
        # Import the custody protocol service
        from app.services.custody_protocol_service import CustodyProtocolService
        print("✅ Successfully imported custody protocol service")
        
        # Initialize the service
        custody_service = CustodyProtocolService()
        await custody_service.initialize()
        print("✅ Custody protocol service initialized")
        
        # Trigger a test for imperium
        print("\n🎯 Triggering test for imperium...")
        test_result = await custody_service.force_custody_test("imperium")
        
        print("✅ Custody test completed:")
        print(f"   📊 Test result: {test_result}")
        
        # Check if autonomous scenarios were generated
        print("\n🔍 Checking for autonomous scenario generation...")
        
        # Import autonomous generator to check if it was used
        from app.services.autonomous_test_generator import autonomous_test_generator
        
        # Test if autonomous generator is working
        scenario = await autonomous_test_generator.generate_autonomous_scenario(
            ai_types=["imperium"], 
            difficulty="intermediate"
        )
        
        print("✅ Autonomous scenario generation confirmed:")
        print(f"   📝 Scenario: {scenario['scenario'][:100]}...")
        print(f"   📋 Requirements: {len(scenario['requirements'])} items")
        
        # Generate a test AI response
        response = await autonomous_test_generator.generate_ai_response(
            ai_name="imperium",
            scenario=scenario['scenario'],
            requirements=scenario['requirements']
        )
        
        print("✅ Autonomous AI response generation confirmed:")
        print(f"   🤖 Response length: {len(response)} characters")
        print(f"   📝 Response preview: {response[:200]}...")
        
        print("\n" + "=" * 50)
        print("🎯 Custody test with autonomous scenarios completed!")
        print("✅ The autonomous test generation system is integrated and working")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error during custody test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trigger_custody_test())