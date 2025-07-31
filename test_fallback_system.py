#!/usr/bin/env python3
"""
Test script for the fallback system
Tests the enhanced test generator and custody protocol service with fallback
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

async def test_enhanced_test_generator():
    """Test the enhanced test generator with fallback"""
    try:
        print("🧪 Testing Enhanced Test Generator...")
        
        # Test import
        from app.services.enhanced_test_generator_fixed import EnhancedTestGenerator
        print("✅ Enhanced Test Generator imports successfully")
        
        # Test initialization
        generator = EnhancedTestGenerator()
        print("✅ Enhanced Test Generator initializes successfully")
        
        # Test fallback scenario generation
        test_scenario = await generator._generate_with_fallback(
            ai_types=["guardian_ai", "imperium_ai"],
            difficulty="intermediate",
            test_type="custody",
            ai_levels={"guardian_ai": 5, "imperium_ai": 6}
        )
        
        print("✅ Fallback scenario generation works")
        print(f"📋 Generated scenario: {test_scenario.get('scenario_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Test Generator test failed: {str(e)}")
        return False

async def test_custody_protocol_service():
    """Test the custody protocol service with fallback"""
    try:
        print("🧪 Testing Custody Protocol Service...")
        
        # Test import
        from app.services.custody_protocol_service_fixed import CustodyProtocolService
        print("✅ Custody Protocol Service imports successfully")
        
        # Test initialization
        service = CustodyProtocolService()
        print("✅ Custody Protocol Service initializes successfully")
        
        # Test fallback test administration
        test_result = await service._administer_with_fallback(
            ai_type="guardian_ai",
            test_category=None
        )
        
        print("✅ Fallback test administration works")
        print(f"📋 Test result: {test_result.get('test_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Custody Protocol Service test failed: {str(e)}")
        return False

async def test_fallback_service():
    """Test the custodes fallback testing service"""
    try:
        print("🧪 Testing Custodes Fallback Testing Service...")
        
        # Test import
        from app.services.custodes_fallback_testing import CustodesFallbackTesting, FallbackTestDifficulty, FallbackTestCategory
        print("✅ Custodes Fallback Testing imports successfully")
        
        # Test initialization
        fallback_service = CustodesFallbackTesting()
        print("✅ Custodes Fallback Testing initializes successfully")
        
        # Test fallback test generation
        test_content = fallback_service.generate_fallback_test(
            difficulty=FallbackTestDifficulty.INTERMEDIATE,
            category=FallbackTestCategory.KNOWLEDGE_VERIFICATION
        )
        
        print("✅ Fallback test generation works")
        print(f"📋 Generated test: {test_content.get('test_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Custodes Fallback Testing test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Fallback System Tests...")
    print("=" * 50)
    
    tests = [
        test_fallback_service(),
        test_enhanced_test_generator(),
        test_custody_protocol_service()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    test_names = [
        "Custodes Fallback Testing",
        "Enhanced Test Generator", 
        "Custody Protocol Service"
    ]
    
    all_passed = True
    for i, (name, result) in enumerate(zip(test_names, results)):
        if isinstance(result, Exception):
            print(f"❌ {name}: Failed - {str(result)}")
            all_passed = False
        elif result:
            print(f"✅ {name}: Passed")
        else:
            print(f"❌ {name}: Failed")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Fallback system is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)