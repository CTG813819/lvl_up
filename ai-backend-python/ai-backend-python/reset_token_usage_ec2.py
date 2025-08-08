#!/usr/bin/env python3
"""
Reset Token Usage on EC2 Instance
This script resets all token usage to zero and ensures proper connection to Anthropic and OpenAI
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the backend directory to the path
sys.path.append('/home/ubuntu/ai-backend-python')

async def reset_token_usage():
    """Reset all token usage to zero"""
    try:
        print("🔄 Resetting token usage on EC2 instance...")
        
        # Import token usage service
        from app.services.token_usage_service import token_usage_service
        
        # Initialize the service
        await token_usage_service.initialize()
        
        # Reset all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        current_month = datetime.utcnow().strftime("%Y-%m")
        
        for ai_type in ai_types:
            # Reset Anthropic usage
            success = await token_usage_service.reset_monthly_usage(ai_type, current_month)
            if success:
                print(f"✅ Reset {ai_type} Anthropic usage")
            else:
                print(f"❌ Failed to reset {ai_type} Anthropic usage")
            
            # Reset OpenAI usage
            openai_ai_type = f"{ai_type}_openai"
            success = await token_usage_service.reset_monthly_usage(openai_ai_type, current_month)
            if success:
                print(f"✅ Reset {ai_type} OpenAI usage")
            else:
                print(f"❌ Failed to reset {ai_type} OpenAI usage")
        
        print("🎉 Token usage reset complete!")
        
        # Show current usage
        print("\n📊 Current token usage:")
        for ai_type in ai_types:
            usage = await token_usage_service.get_monthly_usage(ai_type)
            if usage:
                print(f"  {ai_type}: {usage.get('total_tokens', 0)} tokens")
            else:
                print(f"  {ai_type}: 0 tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting token usage: {str(e)}")
        return False

async def test_llm_connections():
    """Test connections to Anthropic and OpenAI"""
    try:
        print("\n🔗 Testing LLM connections...")
        
        # Test Anthropic connection
        try:
            from app.services.anthropic_service import anthropic_rate_limited_call
            test_prompt = "Generate a simple test response"
            response = await anthropic_rate_limited_call(test_prompt, "imperium", max_tokens=50)
            print("✅ Anthropic connection successful")
        except Exception as e:
            print(f"❌ Anthropic connection failed: {str(e)}")
        
        # Test OpenAI connection
        try:
            from app.services.openai_service import openai_service
            test_prompt = "Generate a simple test response"
            response = await openai_service.call_openai(test_prompt, "imperium", max_tokens=50)
            print("✅ OpenAI connection successful")
        except Exception as e:
            print(f"❌ OpenAI connection failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM connections: {str(e)}")
        return False

async def enable_infinite_tokens():
    """Enable infinite token usage for adversarial testing"""
    try:
        print("\n♾️ Enabling infinite tokens for adversarial testing...")
        
        # Import and update token usage service
        from app.services.token_usage_service import token_usage_service
        
        # Set infinite limits for adversarial testing
        token_usage_service.ENFORCED_GLOBAL_LIMIT = float('inf')
        token_usage_service.OPENAI_MONTHLY_LIMIT = float('inf')
        
        print("✅ Infinite tokens enabled for adversarial testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error enabling infinite tokens: {str(e)}")
        return False

async def main():
    """Main function to reset token usage and test connections"""
    print("🚀 EC2 Token Usage Reset and LLM Connection Test")
    print("=" * 50)
    
    # Reset token usage
    success = await reset_token_usage()
    if not success:
        print("❌ Failed to reset token usage")
        return
    
    # Test LLM connections
    success = await test_llm_connections()
    if not success:
        print("❌ Failed to test LLM connections")
        return
    
    # Enable infinite tokens
    success = await enable_infinite_tokens()
    if not success:
        print("❌ Failed to enable infinite tokens")
        return
    
    print("\n🎉 All operations completed successfully!")
    print("✅ Token usage reset to zero")
    print("✅ LLM connections tested")
    print("✅ Infinite tokens enabled for adversarial testing")

if __name__ == "__main__":
    asyncio.run(main()) 