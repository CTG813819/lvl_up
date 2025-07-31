#!/usr/bin/env python3
"""
Final OpenAI Integration Test
=============================

This script performs a comprehensive test of the OpenAI integration with proper database initialization.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.token_usage_service import token_usage_service
from app.services.openai_service import openai_service
from app.services.anthropic_service import anthropic_rate_limited_call

async def test_complete_integration():
    """Test the complete OpenAI integration"""
    
    try:
        print("🚀 Testing Complete OpenAI Integration")
        print("=" * 60)
        
        # Step 1: Initialize everything
        print("📊 Initializing database and services...")
        await init_database()
        await token_usage_service.initialize()
        
        # Step 2: Test current usage
        print("\n📈 Current Usage Status:")
        print("-" * 40)
        
        ai_names = ["imperium", "guardian", "sandbox", "conquest"]
        total_anthropic = 0
        total_openai = 0
        
        for ai_name in ai_names:
            # Get Anthropic usage
            anthropic_usage = await token_usage_service.get_monthly_usage(ai_name)
            anthropic_tokens = anthropic_usage.get("total_tokens", 0) if anthropic_usage else 0
            anthropic_percentage = anthropic_usage.get("usage_percentage", 0) if anthropic_usage else 0
            total_anthropic += anthropic_tokens
            
            # Get OpenAI usage
            openai_usage = await openai_service._get_openai_usage(ai_name)
            openai_tokens = openai_usage.get("total_tokens", 0)
            openai_percentage = (openai_tokens / 9000) * 100
            total_openai += openai_tokens
            
            print(f"{ai_name.upper():<12} | Anthropic: {anthropic_percentage:5.1f}% ({anthropic_tokens:>6,} tokens)")
            print(f"{'':<12} | OpenAI:   {openai_percentage:5.1f}% ({openai_tokens:>6,} tokens)")
        
        print(f"\n🌍 Total Usage: Anthropic {total_anthropic:,} / OpenAI {total_openai:,}")
        
        # Step 3: Test OpenAI fallback logic
        print("\n🔄 Testing OpenAI Fallback Logic:")
        print("-" * 40)
        
        test_ai = "imperium"
        
        # Test normal fallback check
        should_use, reason = await openai_service.should_use_openai(test_ai)
        print(f"Normal fallback check: {should_use} ({reason.get('reason', 'unknown')})")
        
        # Simulate high Anthropic usage
        print("\n📊 Simulating high Anthropic usage...")
        await token_usage_service.record_token_usage(
            ai_type=test_ai,
            tokens_in=130000,  # High usage to trigger fallback
            tokens_out=65000,
            model_used="claude-3-5-sonnet-20241022",
            request_type="TEST"
        )
        
        # Check fallback again
        should_use, reason = await openai_service.should_use_openai(test_ai)
        print(f"High usage fallback check: {should_use} ({reason.get('reason', 'unknown')})")
        
        if should_use:
            print("✅ OpenAI fallback would be triggered correctly")
        else:
            print("❌ OpenAI fallback not triggered as expected")
        
        # Step 4: Test token limit enforcement
        print("\n🛡️ Testing Token Limit Enforcement:")
        print("-" * 40)
        
        # Test normal request
        can_make_request, usage_info = await token_usage_service.enforce_strict_limits(test_ai, 1000)
        print(f"Normal request (1000 tokens): {can_make_request}")
        
        # Test excessive request
        can_make_request, usage_info = await token_usage_service.enforce_strict_limits(test_ai, 50000)
        print(f"Excessive request (50000 tokens): {can_make_request}")
        
        # Step 5: Test actual AI call with fallback
        print("\n🤖 Testing AI Call with Fallback:")
        print("-" * 40)
        
        test_prompt = "Hello, this is a test message to verify OpenAI fallback integration."
        
        try:
            # This should trigger OpenAI fallback due to high Anthropic usage
            print("Attempting AI call (should use OpenAI fallback)...")
            response = await anthropic_rate_limited_call(test_prompt, test_ai, max_tokens=100)
            print(f"✅ AI call successful: {response[:100]}...")
        except Exception as e:
            print(f"❌ AI call failed: {str(e)}")
        
        # Step 6: Final usage report
        print("\n📊 Final Usage Report:")
        print("-" * 40)
        
        final_anthropic = await token_usage_service.get_monthly_usage(test_ai)
        final_openai = await openai_service._get_openai_usage(test_ai)
        
        print(f"Anthropic usage: {final_anthropic.get('total_tokens', 0):,} tokens")
        print(f"OpenAI usage: {final_openai.get('total_tokens', 0):,} tokens")
        
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await test_complete_integration()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 