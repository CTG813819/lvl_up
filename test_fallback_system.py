#!/usr/bin/env python3
"""
<<<<<<< HEAD
Test Fallback System
====================

This script tests the Custodes fallback testing system to ensure it can generate
tests independently when main AI services hit token limits.
=======
Test script for the fallback system
Tests the enhanced test generator and custody protocol service with fallback
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
"""

import asyncio
import sys
import os
<<<<<<< HEAD
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custodes_fallback_testing import custodes_fallback, FallbackTestCategory, FallbackTestDifficulty
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory, TestDifficulty

async def test_fallback_system():
    """Test the fallback testing system"""
    print("🧪 Testing Custodes Fallback System...")
    
    try:
        # Initialize the fallback system
        print("📚 Learning from all AIs...")
        ai_profiles = await custodes_fallback.learn_from_all_ais()
        print(f"✅ Learned from {len(ai_profiles)} AIs")
        
        # Test AI types
        test_ais = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in test_ais:
            print(f"\n🎯 Testing fallback test generation for {ai_type}...")
            
            # Test different categories and difficulties
            categories = [
                FallbackTestCategory.KNOWLEDGE_VERIFICATION,
                FallbackTestCategory.CODE_QUALITY,
                FallbackTestCategory.SECURITY_AWARENESS,
                FallbackTestCategory.PERFORMANCE_OPTIMIZATION
            ]
            
            difficulties = [
                FallbackTestDifficulty.BASIC,
                FallbackTestDifficulty.INTERMEDIATE,
                FallbackTestDifficulty.ADVANCED
            ]
            
            for category in categories:
                for difficulty in difficulties:
                    print(f"   Generating {category.value} test at {difficulty.value} difficulty...")
                    
                    # Generate fallback test
                    test_content = await custodes_fallback.generate_fallback_test(ai_type, difficulty, category)
                    
                    print(f"   ✅ Generated test: {test_content.get('test_type', 'unknown')}")
                    print(f"   📝 Question: {test_content.get('question', 'No question')[:100]}...")
                    
                    # Test evaluation
                    ai_response = f"This is a test response from {ai_type} AI for {category.value} test."
                    evaluation = await custodes_fallback.evaluate_fallback_test(ai_type, test_content, ai_response)
                    
                    print(f"   📊 Evaluation: Score={evaluation.get('score', 0):.2f}, Passed={evaluation.get('passed', False)}")
        
        # Test the main custody protocol service with fallback
        print(f"\n🔧 Testing main custody protocol service with fallback...")
        
        custody_service = CustodyProtocolService()
        await custody_service.initialize()
        
        for ai_type in test_ais:
            print(f"   Testing custody test for {ai_type}...")
            
            # This should use fallback if main AI services fail
            result = await custody_service.administer_custody_test(ai_type)
            
            print(f"   ✅ Custody test result: {result.get('status', 'unknown')}")
            if 'test_result' in result:
                test_result = result['test_result']
                print(f"   📊 Score: {test_result.get('score', 0)}, Passed: {test_result.get('passed', False)}")
        
        # Get fallback system statistics
        stats = await custodes_fallback.get_test_statistics()
        print(f"\n📈 Fallback System Statistics:")
        print(f"   Total tests generated: {stats.get('total_tests_generated', 0)}")
        print(f"   AI profiles created: {stats.get('ai_profiles_created', 0)}")
        print(f"   Fallback system active: {stats.get('fallback_system_active', False)}")
        
        print("\n🎉 Fallback system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback system: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fallback_system())
    sys.exit(0 if success else 1) 
=======

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
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
