#!/usr/bin/env python3
"""
Test script to verify custody service functionality
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append('.')

async def test_custody_service():
    """Test the custody service initialization and basic functionality"""
    try:
        print("🧪 Testing Custody Protocol Service...")
        
        # Import the custody service
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Initialize the service
        custody_service = await CustodyProtocolService.initialize()
        print("✅ Custody Protocol Service initialized successfully")
        
        # Test basic functionality
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                # Check AI level
                level = await custody_service._get_ai_level(ai_type)
                print(f"📊 {ai_type} level: {level}")
                
                # Check eligibility
                is_eligible = await custody_service._check_proposal_eligibility(ai_type)
                print(f"🎯 {ai_type} eligible for testing: {is_eligible}")
                
                # Try to generate a test
                test = await custody_service.generate_test([ai_type], "standard", "basic")
                print(f"🧪 Generated test for {ai_type}: {test.get('type', 'unknown')}")
                
            except Exception as e:
                print(f"❌ Error testing {ai_type}: {str(e)}")
        
        print("✅ Custody service test completed")
        
    except Exception as e:
        print(f"❌ Error in custody service test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_background_service():
    """Test the background service initialization"""
    try:
        print("🤖 Testing Background Service...")
        
        # Import the background service
        from app.services.background_service import BackgroundService
        
        # Initialize the service
        background_service = await BackgroundService.initialize()
        print("✅ Background Service initialized successfully")
        
        # Test starting the autonomous cycle
        await background_service.start_autonomous_cycle()
        print("✅ Background Service autonomous cycle started")
        
        # Wait a bit to see if tasks start
        await asyncio.sleep(5)
        
        # Stop the service
        await background_service.stop_autonomous_cycle()
        print("✅ Background Service stopped")
        
    except Exception as e:
        print(f"❌ Error in background service test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🚀 Starting custody service tests...")
    
    await test_custody_service()
    print("\n" + "="*50 + "\n")
    await test_background_service()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 