#!/usr/bin/env python3
"""
Test Fallback System
====================

This script tests the Custodes fallback testing system to ensure it can generate
tests independently when main AI services hit token limits.
"""

import asyncio
import sys
import os
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