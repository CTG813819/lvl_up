#!/usr/bin/env python3
"""
Token System Status Checker
"""

import asyncio
import sys
import os

# Add the backend path
sys.path.append('ai-backend-python')

async def check_token_system():
    """Check the token system status"""
    try:
        from app.services.token_usage_service import TokenUsageService
        from app.services.unified_ai_service import UnifiedAIService
        
        print("🔍 Checking Token System Status...")
        print("=" * 60)
        
        # Initialize token usage service
        token_service = await TokenUsageService.initialize()
        print("✅ Token Usage Service initialized")
        
        # Check all monthly usage
        print("\n📊 Current Token Usage:")
        print("-" * 40)
        usage = await token_service.get_all_monthly_usage()
        for ai_type, data in usage.get('ai_usage', {}).items():
            total = data.get('total_tokens', 0)
            percentage = data.get('usage_percentage', 0)
            print(f"  {ai_type}: {total} tokens ({percentage:.1f}%)")
        
        # Check emergency status
        print("\n🚨 Emergency Status:")
        print("-" * 40)
        emergency = await token_service.get_emergency_status()
        print(f"  Global Total: {emergency.get('global_total_tokens', 0)} tokens")
        print(f"  Global Usage: {emergency.get('global_usage_percentage', 0):.1f}%")
        print(f"  Status: {emergency.get('status', 'unknown')}")
        print(f"  Emergency Shutdown: {emergency.get('emergency_shutdown', False)}")
        
        # Check provider recommendations
        print("\n🔗 Provider Recommendations:")
        print("-" * 40)
        from app.services.unified_ai_service_shared import get_unified_ai_service_shared
        unified_service = get_unified_ai_service_shared()
        for ai_type in ['imperium', 'guardian', 'sandbox', 'conquest']:
            try:
                recommendation = await unified_service.get_provider_recommendation(ai_type)
                print(f"  {ai_type}: {recommendation.get('recommendation', 'unknown')}")
            except Exception as e:
                print(f"  {ai_type}: Error - {str(e)}")
        
        # Test rate limits
        print("\n⚡ Rate Limit Test:")
        print("-" * 40)
        for ai_type in ['imperium', 'guardian', 'sandbox', 'conquest']:
            try:
                can_make_request, info = await token_service.enforce_strict_limits(ai_type, 100, "anthropic")
                print(f"  {ai_type}: {'✅ Allowed' if can_make_request else '❌ Blocked'} - {info.get('error', 'OK')}")
            except Exception as e:
                print(f"  {ai_type}: Error - {str(e)}")
        
        print("\n" + "=" * 60)
        print("✅ Token system check completed")
        
    except Exception as e:
        print(f"❌ Error checking token system: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_token_system()) 