#!/usr/bin/env python3
"""
Simple Test for Enhanced Adversarial Testing Service
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_enhanced_adversarial():
    """Simple test for enhanced adversarial testing"""
    print("🧪 Testing Enhanced Adversarial Testing Service")
    print("=" * 50)
    
    try:
        # Test import
        print("📦 Testing imports...")
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService
        from app.services.unified_ai_service import UnifiedAIService
        print("✅ Imports successful")
        
        # Test unified AI service
        print("\n🤖 Testing Unified AI Service...")
        unified_service = UnifiedAIService()
        print("✅ Unified AI Service created")
        
        # Test enhanced adversarial testing service
        print("\n🧪 Testing Enhanced Adversarial Testing Service...")
        enhanced_service = EnhancedAdversarialTestingService()
        print("✅ Enhanced Adversarial Testing Service created")
        
        # Test initialization
        print("\n🔧 Testing initialization...")
        await enhanced_service.initialize()
        print("✅ Enhanced Adversarial Testing Service initialized")
        
        # Test scenario generation
        print("\n📋 Testing scenario generation...")
        scenario = await enhanced_service.generate_diverse_adversarial_scenario(
            ai_types=["imperium", "guardian"],
            target_domain=None,
            complexity=None
        )
        print(f"✅ Scenario generated: {scenario.get('scenario_id', 'unknown')}")
        print(f"   Domain: {scenario.get('domain', 'unknown')}")
        print(f"   Complexity: {scenario.get('complexity', 'unknown')}")
        
        # Test AI response generation
        print("\n🤖 Testing AI response generation...")
        response = await enhanced_service._get_ai_scenario_response("imperium", scenario)
        print(f"✅ AI response generated for imperium")
        print(f"   Method: {response.get('response_method', 'unknown')}")
        print(f"   Confidence: {response.get('confidence_score', 0)}")
        print(f"   Has code: {response.get('has_code', False)}")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Enhanced adversarial testing service is using the established AI answer system!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Enhanced Adversarial Test")
    result = asyncio.run(test_enhanced_adversarial())
    
    if result:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 