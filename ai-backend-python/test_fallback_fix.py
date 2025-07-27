#!/usr/bin/env python3
"""
Test script to verify OpenAI fallback mechanism is working correctly
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.token_usage_service import token_usage_service
from app.services.openai_service import openai_service
from app.services.anthropic_service import anthropic_rate_limited_call

async def test_fallback_mechanism():
    """Test the fallback mechanism"""
    print("🧪 Testing OpenAI Fallback Mechanism")
    print("=" * 50)
    
    # Initialize services
    await token_usage_service.initialize()
    await openai_service.initialize()
    
    # Test AI name
    ai_name = "sandbox"
    
    print(f"\n1. Checking current token usage for {ai_name}...")
    
    # Get current usage
    anthropic_usage = await token_usage_service.get_monthly_usage(ai_name)
    print(f"   Anthropic usage: {anthropic_usage}")
    
    # Check if OpenAI should be used
    should_use, reason = await openai_service.should_use_openai(ai_name)
    print(f"   Should use OpenAI: {should_use}")
    print(f"   Reason: {reason}")
    
    print(f"\n2. Testing fallback logic...")
    
    # Test with a simple prompt
    test_prompt = "Hello, this is a test message to verify the fallback mechanism."
    
    try:
        print(f"   Attempting to call Anthropic with fallback...")
        response = await anthropic_rate_limited_call(test_prompt, ai_name, max_tokens=100)
        print(f"   ✅ Success! Response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print(f"\n3. Testing OpenAI fallback directly...")
    
    try:
        # Check if OpenAI should be used
        should_use, reason = await openai_service.should_use_openai(ai_name)
        if should_use:
            print(f"   OpenAI fallback should be used: {reason}")
            response = await openai_service.call_openai(test_prompt, ai_name, max_tokens=100)
            print(f"   ✅ OpenAI fallback success! Response: {response[:100]}...")
        else:
            print(f"   OpenAI fallback not needed: {reason}")
    except Exception as e:
        print(f"   ❌ OpenAI fallback error: {str(e)}")
    
    print(f"\n4. Current usage after test...")
    
    # Get updated usage
    updated_usage = await token_usage_service.get_monthly_usage(ai_name)
    print(f"   Updated Anthropic usage: {updated_usage}")
    
    print(f"\n✅ Test completed!")

async def reset_token_usage():
    """Reset token usage for testing"""
    print("🔄 Resetting token usage for testing...")
    
    await token_usage_service.initialize()
    
    # Reset for all AI types
    ai_types = ["imperium", "guardian", "sandbox", "conquest"]
    
    for ai_type in ai_types:
        success = await token_usage_service.reset_monthly_usage(ai_type)
        print(f"   Reset {ai_type}: {'✅' if success else '❌'}")
    
    print("✅ Token usage reset completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        asyncio.run(reset_token_usage())
    else:
        asyncio.run(test_fallback_mechanism()) 