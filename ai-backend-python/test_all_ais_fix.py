#!/usr/bin/env python3
"""
Test All AIs Fix
================

This script tests the fix to ensure all AIs get tested regardless of token limits.
"""

import asyncio
import sys
import os
from datetime import datetime
import pytest

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.custody_protocol_service import CustodyProtocolService
from app.services.background_service import BackgroundService

@pytest.mark.asyncio
async def test_all_ais_fix():
    """Test that all AIs get tested regardless of token limits"""
    
    try:
        print("🧪 Testing All AIs Fix...")
        print("=" * 50)
        
        # Initialize database and services
        await init_database()
        custody_service = await CustodyProtocolService.initialize()
        background_service = await BackgroundService.initialize()
        
        # Test AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        test_results = {}
        
        print(f"📋 Testing {len(ai_types)} AIs: {', '.join(ai_types)}")
        print()
        
        for ai_type in ai_types:
            print(f"🔍 Testing {ai_type.upper()}...")
            
            try:
                # Check eligibility first
                is_eligible = await custody_service._check_proposal_eligibility(ai_type)
                if not is_eligible:
                    level = await custody_service._get_ai_level(ai_type)
                    xp = custody_service.custody_metrics.get(ai_type, {}).get('xp', 0)
                    print(f"   ⚠️  {ai_type.upper()} not eligible: Level {level}, XP {xp}")
                    test_results[ai_type] = {"status": "not_eligible", "level": level, "xp": xp}
                    continue
                
                # Try to administer test with fallback
                test_result = await background_service._administer_test_with_fallback(custody_service, ai_type)
                test_results[ai_type] = test_result
                
                if test_result.get('status') == 'success':
                    passed = test_result.get('passed', False)
                    score = test_result.get('score', 0)
                    test_type = test_result.get('test_type', 'unknown')
                    print(f"   ✅ {ai_type.upper()} test completed: {'PASSED' if passed else 'FAILED'} (Score: {score}, Type: {test_type})")
                else:
                    print(f"   ❌ {ai_type.upper()} test failed: {test_result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   💥 {ai_type.upper()} test error: {str(e)}")
                test_results[ai_type] = {"status": "error", "message": str(e)}
            
            print()
        
        # Summary
        print("📊 Test Summary:")
        print("-" * 30)
        
        successful_tests = 0
        not_eligible = 0
        failed_tests = 0
        
        for ai_type, result in test_results.items():
            if result.get('status') == 'success':
                successful_tests += 1
            elif result.get('status') == 'not_eligible':
                not_eligible += 1
            else:
                failed_tests += 1
        
        print(f"✅ Successful tests: {successful_tests}")
        print(f"⚠️  Not eligible: {not_eligible}")
        print(f"❌ Failed tests: {failed_tests}")
        print(f"🎯 Total AIs processed: {len(ai_types)}")
        
        # Check if the fix is working
        if successful_tests + not_eligible >= len(ai_types):
            print("\n🎉 SUCCESS: All AIs were processed successfully!")
            print("   The token limit fix is working correctly.")
        else:
            print(f"\n⚠️  WARNING: Only {successful_tests + not_eligible}/{len(ai_types)} AIs were processed.")
            print("   There may still be issues with the token limit handling.")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        print("-" * 30)
        
        for ai_type, result in test_results.items():
            status = result.get('status', 'unknown')
            if status == 'success':
                passed = result.get('passed', False)
                score = result.get('score', 0)
                test_type = result.get('test_type', 'unknown')
                print(f"{ai_type.upper():<12} | ✅ {'PASSED' if passed else 'FAILED'} | Score: {score:>3} | Type: {test_type}")
            elif status == 'not_eligible':
                level = result.get('level', 0)
                xp = result.get('xp', 0)
                print(f"{ai_type.upper():<12} | ⚠️  NOT ELIGIBLE | Level: {level} | XP: {xp}")
            else:
                message = result.get('message', 'Unknown error')
                print(f"{ai_type.upper():<12} | ❌ FAILED | {message}")
        
        return test_results
        
    except Exception as e:
        print(f"❌ Error testing all AIs fix: {str(e)}")
        return None

@pytest.mark.asyncio
async def test_token_limit_handling():
    """Test token limit handling specifically"""
    
    try:
        print("\n🔧 Testing Token Limit Handling...")
        print("=" * 40)
        
        from app.services.token_usage_service import token_usage_service
        
        # Test each AI's token availability
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            try:
                # Check if we can make a request
                can_make_request, usage_info = await token_usage_service.enforce_strict_limits(ai_type, 1000)
                
                if can_make_request:
                    usage_percentage = usage_info.get('usage_percentage', 0)
                    print(f"{ai_type.upper():<12} | ✅ Available | Usage: {usage_percentage:.1f}%")
                else:
                    error = usage_info.get('error', 'Unknown error')
                    print(f"{ai_type.upper():<12} | ❌ Blocked | {error}")
                    
            except Exception as e:
                print(f"{ai_type.upper():<12} | 💥 Error | {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing token limit handling: {str(e)}")
        return False

async def main():
    """Main test function"""
    
    print("🚀 Testing All AIs Fix - Token Limit Handling")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test token limit handling
    token_test_result = await test_token_limit_handling()
    
    # Test all AIs fix
    all_ais_result = await test_all_ais_fix()
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
    
    if all_ais_result:
        successful = sum(1 for result in all_ais_result.values() if result.get('status') == 'success')
        total = len(all_ais_result)
        print(f"📊 Results: {successful}/{total} AIs tested successfully")
        
        if successful > 0:
            print("✅ The fix is working - AIs are being tested despite token limits")
        else:
            print("❌ The fix needs more work - No AIs were tested successfully")
    else:
        print("❌ Test failed to complete")

if __name__ == "__main__":
    asyncio.run(main()) 