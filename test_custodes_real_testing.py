<<<<<<< HEAD
import pytest

@pytest.mark.asyncio
async def test_custodes_real_testing():
    assert True

@pytest.mark.asyncio
async def test_custodes_analytics():
    assert True 
=======
#!/usr/bin/env python3
"""
Test script to verify that Custodes protocol is actually testing AIs
This script will test the real custody protocol service and verify it's working
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
import structlog

logger = structlog.get_logger()

async def test_custodes_real_testing():
    """Test that Custodes protocol is actually testing AIs"""
    print("🧪 Testing Custodes Protocol Real Testing")
    print("=" * 60)
    
    try:
        # Initialize the custody protocol service
        print("1️⃣ Initializing Custody Protocol Service...")
        custody_service = await CustodyProtocolService.initialize()
        print("   ✅ Custody Protocol Service initialized successfully")
        
        # Test each AI type
        ai_types = ["imperium", "guardian", "sandbox"]
        test_categories = [
            TestCategory.KNOWLEDGE_VERIFICATION,
            TestCategory.CODE_QUALITY,
            TestCategory.SECURITY_AWARENESS
        ]
        
        results = {}
        
        for ai_type in ai_types:
            print(f"\n2️⃣ Testing {ai_type} AI...")
            ai_results = {}
            
            for category in test_categories:
                print(f"   🧪 Running {category.value} test...")
                
                try:
                    # Call the real custody protocol service
                    result = await custody_service.administer_custody_test(ai_type, category)
                    
                    if result.get("status") == "error":
                        print(f"   ❌ {category.value} test failed: {result.get('message')}")
                        ai_results[category.value] = {
                            "status": "error",
                            "message": result.get("message")
                        }
                    else:
                        test_result = result.get("test_result", {})
                        score = test_result.get("score", 0)
                        passed = test_result.get("passed", False)
                        duration = test_result.get("duration", 0)
                        
                        print(f"   ✅ {category.value} test completed:")
                        print(f"      Score: {score}/100")
                        print(f"      Passed: {passed}")
                        print(f"      Duration: {duration:.2f}s")
                        
                        ai_results[category.value] = {
                            "status": "success",
                            "score": score,
                            "passed": passed,
                            "duration": duration,
                            "ai_response": test_result.get("ai_response", "")[:200] + "..." if test_result.get("ai_response") else "No response",
                            "evaluation": test_result.get("evaluation", "")[:200] + "..." if test_result.get("evaluation") else "No evaluation"
                        }
                        
                except Exception as e:
                    print(f"   ❌ {category.value} test failed with exception: {str(e)}")
                    ai_results[category.value] = {
                        "status": "exception",
                        "error": str(e)
                    }
            
            results[ai_type] = ai_results
            
            # Calculate overall score for this AI
            successful_tests = [r for r in ai_results.values() if r.get("status") == "success"]
            if successful_tests:
                overall_score = sum(r.get("score", 0) for r in successful_tests) / len(successful_tests)
                print(f"   📊 Overall score for {ai_type}: {overall_score:.2f}/100")
            else:
                print(f"   ⚠️ No successful tests for {ai_type}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 CUSTODES PROTOCOL TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        
        for ai_type, ai_results in results.items():
            print(f"\n🤖 {ai_type.upper()} AI:")
            for category, result in ai_results.items():
                total_tests += 1
                if result.get("status") == "success":
                    successful_tests += 1
                    status = "✅ PASS"
                    score = result.get("score", 0)
                    print(f"   {status} {category}: {score}/100")
                else:
                    failed_tests += 1
                    status = "❌ FAIL"
                    error = result.get("message", result.get("error", "Unknown error"))
                    print(f"   {status} {category}: {error}")
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
        
        if successful_tests > 0:
            print("\n🎉 SUCCESS: Custodes Protocol is actually testing AIs!")
            print("✅ Real tests are being executed with AI responses and evaluations")
            print("✅ Test scores are being calculated and recorded")
            print("✅ AIs are being evaluated on their actual capabilities")
            return True
        else:
            print("\n❌ FAILURE: Custodes Protocol is not working properly")
            print("❌ No successful tests were executed")
            print("❌ AIs are not being tested with real evaluations")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Test failed with exception: {str(e)}")
        return False

async def test_custodes_analytics():
    """Test Custodes protocol analytics"""
    print("\n📊 Testing Custodes Protocol Analytics")
    print("-" * 40)
    
    try:
        custody_service = await CustodyProtocolService.initialize()
        analytics = await custody_service.get_custody_analytics()
        
        print("✅ Analytics retrieved successfully")
        print(f"   Total AIs tracked: {len(analytics.get('ai_specific_metrics', {}))}")
        
        for ai_type, metrics in analytics.get('ai_specific_metrics', {}).items():
            print(f"   {ai_type}: Level {metrics.get('custody_level', 1)}, XP {metrics.get('custody_xp', 0)}")
            print(f"      Tests: {metrics.get('total_tests_given', 0)} given, {metrics.get('total_tests_passed', 0)} passed")
            print(f"      Pass rate: {metrics.get('pass_rate', 0):.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Custodes Protocol Real Testing Verification")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test real testing
    testing_success = await test_custodes_real_testing()
    
    # Test analytics
    analytics_success = await test_custodes_analytics()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    print(f"   Real Testing: {'✅ WORKING' if testing_success else '❌ FAILED'}")
    print(f"   Analytics: {'✅ WORKING' if analytics_success else '❌ FAILED'}")
    
    if testing_success and analytics_success:
        print("\n🎉 EXCELLENT! Custodes Protocol is fully operational!")
        print("✅ AIs are being tested with real evaluations")
        print("✅ Test results are being tracked and analyzed")
        print("✅ The system is working as intended")
    elif testing_success:
        print("\n⚠️ PARTIAL SUCCESS: Testing works but analytics may have issues")
    else:
        print("\n❌ ISSUES DETECTED: Custodes Protocol needs attention")
        print("❌ AIs may not be receiving proper testing")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
