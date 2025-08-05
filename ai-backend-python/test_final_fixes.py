#!/usr/bin/env python3
"""
Final test script to verify custody protocol fixes
Tests difficulty logging, score variation, and AI-specific evaluation
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory

async def test_final_fixes():
    """Test all custody protocol fixes"""
    print("🧪 Testing final custody protocol fixes...")
    
    # Initialize services
    custody_service = CustodyProtocolService()
    
    # Test AI types
    test_ais = ["conquest", "guardian", "imperium", "sandbox"]
    
    print("\n🔧 Testing fixes:")
    print("1. Difficulty logging in test results")
    print("2. AI-specific score variation")
    print("3. Proper test result structure")
    
    results = {}
    
    for ai_type in test_ais:
        print(f"\n📊 Testing {ai_type}...")
        
        try:
            # Generate a test
            test = await custody_service.generate_test([ai_type], "standard", "basic")
            print(f"   ✅ Generated test for {ai_type}")
            print(f"   📝 Test structure: {list(test.keys())}")
            print(f"   🎯 Difficulty: {test.get('difficulty', 'NOT_FOUND')}")
            
            # Execute the test
            test_result = await custody_service.execute_test(test)
            print(f"   ✅ Executed test for {ai_type}")
            print(f"   📊 Test result structure: {list(test_result.keys())}")
            print(f"   🎯 Difficulty in result: {test_result.get('difficulty', 'NOT_FOUND')}")
            print(f"   📈 Score: {test_result.get('score', 'NOT_FOUND')}")
            print(f"   ✅ Passed: {test_result.get('passed', 'NOT_FOUND')}")
            
            # Store results
            results[ai_type] = {
                "test_structure": list(test.keys()),
                "result_structure": list(test_result.keys()),
                "difficulty_in_test": test.get('difficulty'),
                "difficulty_in_result": test_result.get('difficulty'),
                "score": test_result.get('score'),
                "passed": test_result.get('passed')
            }
            
        except Exception as e:
            print(f"   ❌ Error testing {ai_type}: {str(e)}")
            results[ai_type] = {"error": str(e)}
    
    # Test collaborative test
    print(f"\n🤝 Testing collaborative test...")
    try:
        collaborative_test = await custody_service.generate_test(["conquest", "guardian"], "collaborative", "intermediate")
        print(f"   ✅ Generated collaborative test")
        print(f"   📝 Test structure: {list(collaborative_test.keys())}")
        print(f"   🎯 Difficulty: {collaborative_test.get('difficulty', 'NOT_FOUND')}")
        
        collaborative_result = await custody_service.execute_test(collaborative_test)
        print(f"   ✅ Executed collaborative test")
        print(f"   📊 Result structure: {list(collaborative_result.keys())}")
        print(f"   🎯 Difficulty in result: {collaborative_result.get('difficulty', 'NOT_FOUND')}")
        print(f"   📈 Score: {collaborative_result.get('score', 'NOT_FOUND')}")
        
        results["collaborative"] = {
            "test_structure": list(collaborative_test.keys()),
            "result_structure": list(collaborative_result.keys()),
            "difficulty_in_test": collaborative_test.get('difficulty'),
            "difficulty_in_result": collaborative_result.get('difficulty'),
            "score": collaborative_result.get('score'),
            "passed": collaborative_result.get('passed')
        }
        
    except Exception as e:
        print(f"   ❌ Error testing collaborative: {str(e)}")
        results["collaborative"] = {"error": str(e)}
    
    # Summary
    print(f"\n📋 SUMMARY:")
    print("=" * 50)
    
    for ai_type, result in results.items():
        print(f"\n{ai_type.upper()}:")
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Test structure: {result['test_structure']}")
            print(f"   ✅ Result structure: {result['result_structure']}")
            print(f"   🎯 Difficulty in test: {result['difficulty_in_test']}")
            print(f"   🎯 Difficulty in result: {result['difficulty_in_result']}")
            print(f"   📈 Score: {result['score']}")
            print(f"   ✅ Passed: {result['passed']}")
            
            # Check if fixes are working
            if result['difficulty_in_test'] and result['difficulty_in_test'] != 'NOT_FOUND':
                print(f"   ✅ Difficulty logging: WORKING")
            else:
                print(f"   ❌ Difficulty logging: FAILED")
                
            if result['score'] and result['score'] != 'NOT_FOUND' and result['score'] != 40.08:
                print(f"   ✅ Score variation: WORKING (score: {result['score']})")
            else:
                print(f"   ❌ Score variation: FAILED (score: {result['score']})")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_final_fixes_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return results

async def main():
    """Main test function"""
    print("🚀 Starting final custody protocol fixes test...")
    
    try:
        results = await test_final_fixes()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 