#!/usr/bin/env python3
"""
Comprehensive Test for All AI Agents in Adversarial Testing
Tests that all AI agents (Imperium, Sandbox, Conquest, Guardian) generate responses
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_all_ai_agents():
    """Test all AI agents in adversarial testing"""
    print("🧪 Testing All AI Agents in Adversarial Testing")
    print("=" * 60)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
        print("✅ Imports successful")
        
        # Initialize the enhanced adversarial testing service
        print("\n🔧 Initializing Enhanced Adversarial Testing Service...")
        enhanced_service = EnhancedAdversarialTestingService()
        await enhanced_service.initialize()
        print("✅ Enhanced Adversarial Testing Service initialized")
        
        # Test scenario generation
        print("\n📋 Generating adversarial scenario...")
        scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=["imperium", "guardian", "sandbox", "conquest"],
            target_domain=None,
            complexity=None
        )
        print(f"✅ Scenario generated: {scenario.get('scenario_id', 'unknown')}")
        print(f"   Domain: {scenario.get('domain', 'unknown')}")
        print(f"   Complexity: {scenario.get('complexity', 'unknown')}")
        print(f"   Description: {scenario.get('description', 'No description')[:100]}...")
        
        # Test all AI agents
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        results = {}
        
        print(f"\n🤖 Testing AI Response Generation for {len(ai_types)} AI agents...")
        print("-" * 50)
        
        for ai_type in ai_types:
            print(f"\n🧠 Testing {ai_type.title()} AI...")
            try:
                response = await enhanced_service._get_ai_scenario_response(ai_type, scenario)
                
                results[ai_type] = {
                    "success": True,
                    "method": response.get('response_method', 'unknown'),
                    "confidence": response.get('confidence_score', 0),
                    "has_code": response.get('has_code', False),
                    "has_algorithm": response.get('has_algorithm', False),
                    "response_length": len(response.get('approach', ''))
                }
                
                print(f"   ✅ {ai_type.title()} response generated successfully")
                print(f"      Method: {response.get('response_method', 'unknown')}")
                print(f"      Confidence: {response.get('confidence_score', 0)}")
                print(f"      Has Code: {response.get('has_code', False)}")
                print(f"      Response Length: {len(response.get('approach', ''))} characters")
                
                # Show a preview of the response
                approach = response.get('approach', '')
                if approach:
                    preview = approach[:200] + "..." if len(approach) > 200 else approach
                    print(f"      Preview: {preview}")
                
            except Exception as e:
                print(f"   ❌ {ai_type.title()} failed: {str(e)}")
                results[ai_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 50)
        
        successful_agents = sum(1 for result in results.values() if result.get('success', False))
        total_agents = len(ai_types)
        
        print(f"Total AI Agents Tested: {total_agents}")
        print(f"Successful Responses: {successful_agents}")
        print(f"Success Rate: {(successful_agents/total_agents)*100:.1f}%")
        
        print(f"\nDetailed Results:")
        for ai_type, result in results.items():
            if result.get('success', False):
                print(f"  ✅ {ai_type.title()}: {result['method']} (Confidence: {result['confidence']})")
            else:
                print(f"  ❌ {ai_type.title()}: Failed - {result.get('error', 'Unknown error')}")
        
        # Check if all agents are working
        if successful_agents == total_agents:
            print(f"\n🎉 All AI agents are generating responses successfully!")
            print(f"✅ Enhanced adversarial testing service is fully functional!")
            return True
        else:
            print(f"\n⚠️  Some AI agents failed to generate responses")
            print(f"   {successful_agents}/{total_agents} agents working")
            return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive AI Agent Test")
    result = asyncio.run(test_all_ai_agents())
    
    if result:
        print("\n✅ All tests completed successfully!")
        print("🎯 AI agents are now generating responses to adversarial scenarios!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 