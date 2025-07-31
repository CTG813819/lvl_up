#!/usr/bin/env python3
"""
Test script to verify enhanced adversarial testing service is working properly
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_adversarial_service():
    """Test enhanced adversarial testing service"""
    try:
        print("🔍 Testing Enhanced Adversarial Testing Service...")
        
        # Import and initialize the service
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
        service = EnhancedAdversarialTestingService()
        await service.initialize()
        print("✅ Enhanced Adversarial Testing Service initialized successfully")
        
        # Test generating a scenario
        print("🔧 Testing scenario generation...")
        ai_types = ["imperium", "guardian"]
        scenario = await service.generate_diverse_adversarial_scenario(ai_types)
        print("✅ Scenario generated successfully:", scenario.get('scenario_id', 'No ID'))
        
        # Test executing the scenario
        print("🔧 Testing scenario execution...")
        result = await service.execute_diverse_adversarial_test(scenario)
        print("✅ Scenario executed successfully:", result.get('status', 'Unknown'))
        
        print("\n🎉 Enhanced Adversarial Testing Service test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing Enhanced Adversarial Testing Service: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_adversarial_service()) 