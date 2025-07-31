#!/usr/bin/env python3
"""
Test OpenAI Integration with Token Usage System
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.unified_ai_service_shared import unified_ai_service_shared
from app.services.token_usage_service import token_usage_service
from app.core.config import settings


async def test_openai_integration():
    """Test the OpenAI integration with token usage tracking"""
    print("🧪 Testing OpenAI Integration with Token Usage System")
    print("=" * 60)
    
    # Test 1: Check provider status
    print("\n1. Testing Provider Status...")
    try:
        status = await unified_ai_service_shared.get_all_provider_status()
        print("✅ Provider status retrieved successfully")
        print(f"   Timestamp: {status.get('timestamp', 'N/A')}")
        for ai_name, ai_status in status.get('ai_statuses', {}).items():
            print(f"   {ai_name}: {ai_status.get('recommendation', 'unknown')} - {ai_status.get('reason', 'unknown')}")
    except Exception as e:
        print(f"❌ Error getting provider status: {e}")
    
    # Test 2: Test AI call with provider selection
    print("\n2. Testing AI Call with Provider Selection...")
    test_prompt = "Hello, this is a test message. Please respond with a simple greeting."
    
    for ai_name in ["imperium", "guardian", "sandbox", "conquest"]:
        try:
            print(f"\n   Testing {ai_name}...")
            response, provider_info = await unified_ai_service_shared.call_ai(
                prompt=test_prompt,
                ai_name=ai_name
            )
            print(f"   ✅ {ai_name} call successful")
            print(f"   Provider: {provider_info.get('provider', 'unknown')}")
            print(f"   Model: {provider_info.get('model', 'unknown')}")
            print(f"   Reason: {provider_info.get('reason', 'unknown')}")
            print(f"   Response length: {len(response)} characters")
        except Exception as e:
            print(f"   ❌ {ai_name} call failed: {e}")
    
    # Test 3: Test token usage tracking
    print("\n3. Testing Token Usage Tracking...")
    try:
        usage_summary = await token_usage_service.get_all_monthly_usage()
        print("✅ Token usage summary retrieved")
        print(f"   Total AIs tracked: {len(usage_summary.get('ai_usage', {}))}")
        for ai_name, usage in usage_summary.get('ai_usage', {}).items():
            print(f"   {ai_name}: {usage.get('total_tokens', 0)} tokens ({usage.get('usage_percentage', 0):.1f}%)")
    except Exception as e:
        print(f"❌ Error getting token usage: {e}")
    
    # Test 4: Test provider recommendation
    print("\n4. Testing Provider Recommendation...")
    for ai_name in ["imperium", "guardian", "sandbox", "conquest"]:
        try:
            recommendation = await token_usage_service.get_provider_recommendation(ai_name)
            print(f"   {ai_name}: {recommendation.get('recommendation', 'unknown')} - {recommendation.get('reason', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Error getting recommendation for {ai_name}: {e}")
    
    # Test 5: Test emergency status
    print("\n5. Testing Emergency Status...")
    try:
        emergency_status = await token_usage_service.get_emergency_status()
        print("✅ Emergency status retrieved")
        print(f"   Status: {emergency_status.get('status', 'unknown')}")
        print(f"   Global usage: {emergency_status.get('global_usage_percentage', 0):.1f}%")
        print(f"   Emergency shutdown: {emergency_status.get('emergency_shutdown', False)}")
    except Exception as e:
        print(f"❌ Error getting emergency status: {e}")
    
    # Test 6: Test OpenAI fallback specifically
    print("\n6. Testing OpenAI Fallback...")
    try:
        # Test if OpenAI is configured
        if settings.openai_api_key:
            print("   ✅ OpenAI API key configured")
            
            # Test OpenAI service directly
            should_use, reason = await unified_ai_service_shared.unified_ai_service_shared.openai_service.should_use_openai("imperium")
            print(f"   Should use OpenAI for imperium: {should_use}")
            print(f"   Reason: {reason.get('reason', 'unknown')}")
        else:
            print("   ⚠️ OpenAI API key not configured")
    except Exception as e:
        print(f"   ❌ Error testing OpenAI fallback: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 OpenAI Integration Test Complete")


async def test_token_limits():
    """Test token limit enforcement"""
    print("\n🧪 Testing Token Limit Enforcement")
    print("=" * 60)
    
    # Test Anthropic limits
    print("\n1. Testing Anthropic Limits...")
    try:
        can_make_request, usage_info = await token_usage_service.enforce_strict_limits("imperium", 1000)
        print(f"   Can make request: {can_make_request}")
        print(f"   Usage info: {usage_info}")
    except Exception as e:
        print(f"   ❌ Error testing Anthropic limits: {e}")
    
    # Test OpenAI limits
    print("\n2. Testing OpenAI Limits...")
    try:
        from app.services.openai_service import openai_service
        can_make_request, usage_info = await openai_service._enforce_openai_limits("imperium", 1000)
        print(f"   Can make OpenAI request: {can_make_request}")
        print(f"   OpenAI usage info: {usage_info}")
    except Exception as e:
        print(f"   ❌ Error testing OpenAI limits: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Token Limit Test Complete")


async def main():
    """Main test function"""
    print("🚀 Starting OpenAI Integration Tests")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Check configuration
    print(f"\n📋 Configuration:")
    print(f"   Anthropic API Key: {'✅ Set' if settings.anthropic_api_key else '❌ Not set'}")
    print(f"   OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Not set'}")
    print(f"   Anthropic Monthly Limit: {settings.anthropic_monthly_limit:,}")
    print(f"   OpenAI Monthly Limit: {settings.openai_monthly_limit:,}")
    print(f"   OpenAI Fallback Threshold: {settings.openai_fallback_threshold * 100:.1f}%")
    
    await test_openai_integration()
    await test_token_limits()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 