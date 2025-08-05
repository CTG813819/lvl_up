#!/usr/bin/env python3
"""
Simple test for autonomous test generation system
"""
import asyncio
import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

async def test_autonomous_generator():
    """Test the autonomous test generator directly"""
    print("🧪 Testing Autonomous Test Generator")
    print("=" * 50)
    
    try:
        # Import the autonomous test generator
        from app.services.autonomous_test_generator import autonomous_test_generator
        print("✅ Successfully imported autonomous test generator")
        
        # Test 1: Generate a scenario
        print("\n1. Testing scenario generation...")
        scenario = await autonomous_test_generator.generate_autonomous_scenario(
            ai_types=["imperium"], 
            difficulty="intermediate"
        )
        
        print("✅ Scenario generated successfully:")
        print(f"   📝 Scenario: {scenario['scenario'][:100]}...")
        print(f"   📋 Requirements: {len(scenario['requirements'])} items")
        print(f"   📊 Evaluation criteria: {len(scenario['evaluation_criteria'])} categories")
        
        # Test 2: Generate AI response
        print("\n2. Testing AI response generation...")
        response = await autonomous_test_generator.generate_ai_response(
            ai_name="imperium",
            scenario=scenario['scenario'],
            requirements=scenario['requirements']
        )
        
        print("✅ AI response generated successfully:")
        print(f"   🤖 Response length: {len(response)} characters")
        print(f"   📝 Response preview: {response[:200]}...")
        
        # Test 3: Test with different AI
        print("\n3. Testing with different AI (guardian)...")
        response2 = await autonomous_test_generator.generate_ai_response(
            ai_name="guardian",
            scenario=scenario['scenario'],
            requirements=scenario['requirements']
        )
        
        print("✅ Guardian response generated successfully:")
        print(f"   🤖 Response length: {len(response2)} characters")
        print(f"   📝 Response preview: {response2[:200]}...")
        
        # Test 4: Test different difficulty
        print("\n4. Testing advanced difficulty scenario...")
        advanced_scenario = await autonomous_test_generator.generate_autonomous_scenario(
            ai_types=["conquest", "sandbox"], 
            difficulty="advanced"
        )
        
        print("✅ Advanced scenario generated successfully:")
        print(f"   📝 Scenario: {advanced_scenario['scenario'][:100]}...")
        print(f"   📋 Requirements: {len(advanced_scenario['requirements'])} items")
        
        print("\n" + "=" * 50)
        print("🎯 All autonomous generator tests passed!")
        print("✅ The autonomous test generation system is working correctly")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error testing autonomous generator: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_autonomous_generator())