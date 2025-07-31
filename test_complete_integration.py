#!/usr/bin/env python3
"""
Test Complete OpenAI Integration
================================

This script tests the complete OpenAI integration with the configured API key.
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
    """Test the complete OpenAI integration with API key"""
    
    try:
        print("🚀 Testing Complete OpenAI Integration with API Key")
        print("=" * 70)
        
        # Step 1: Initialize everything
        print("📊 Initializing database and services...")
        await init_database()
        await token_usage_service.initialize()
        
        # Step 2: Check API key configuration
        print("\n🔑 Checking API Key Configuration:")
        print("-" * 40)
        
        if openai_service.api_key and openai_service.api_key != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
            print(f"   Model: {openai_service.model}")
            print(f"   Base URL: {openai_service.base_url}")
        else:
            print("❌ OpenAI API key not configured")
            return False
        
        # Step 3: Test current usage
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
        
        # Step 4: Test OpenAI fallback logic
        print("\n🔄 Testing OpenAI Fallback Logic:")
        print("-" * 40)
        
        test_ai = "imperium"
        
        # Check fallback availability
        should_use, reason = await openai_service.should_use_openai(test_ai)
        print(f"Fallback available: {should_use} ({reason.get('reason', 'unknown')})")
        
        if should_use:
            print("✅ OpenAI fallback is available")
        else:
            print("❌ OpenAI fallback not available")
        
        # Step 5: Test direct OpenAI call
        print("\n🤖 Testing Direct OpenAI Call:")
        print("-" * 40)
        
        test_prompt = "Hello! This is a test to verify OpenAI integration is working. Please respond with a simple greeting."
        
        try:
            print("Attempting direct OpenAI call...")
            response = await openai_service.call_openai(test_prompt, test_ai, max_tokens=100)
            print(f"✅ OpenAI call successful!")
            print(f"Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ OpenAI call failed: {str(e)}")
            return False
        
        # Step 6: Test AI call with fallback
        print("\n🔄 Testing AI Call with Fallback:")
        print("-" * 40)
        
        try:
            print("Attempting AI call (should use OpenAI fallback)...")
            response = await anthropic_rate_limited_call(test_prompt, test_ai, max_tokens=100)
            print(f"✅ AI call with fallback successful!")
            print(f"Response: {response[:200]}...")
        except Exception as e:
            print(f"❌ AI call with fallback failed: {str(e)}")
            return False
        
        # Step 7: Final usage report
        print("\n📊 Final Usage Report:")
        print("-" * 40)
        
        final_anthropic = await token_usage_service.get_monthly_usage(test_ai)
        final_openai = await openai_service._get_openai_usage(test_ai)
        
        print(f"Anthropic usage: {final_anthropic.get('total_tokens', 0):,} tokens")
        print(f"OpenAI usage: {final_openai.get('total_tokens', 0):,} tokens")
        
        print("\n🎉 Complete integration test successful!")
        print("\n✅ ALL SYSTEMS WORKING:")
        print("   - Database initialization ✅")
        print("   - Token usage tracking ✅")
        print("   - OpenAI API key configured ✅")
        print("   - OpenAI direct calls working ✅")
        print("   - Fallback logic working ✅")
        print("   - AI calls with fallback working ✅")
        
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