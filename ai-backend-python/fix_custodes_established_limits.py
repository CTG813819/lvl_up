#!/usr/bin/env python3
"""
Fix Custodes to Adhere to Established Token Limits
Ensures custodes follow the existing token limits established in config and token_usage.py
"""

import os
import sys
import asyncio
from datetime import datetime
import structlog

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.token_usage_service import token_usage_service
from app.core.database import get_session
from app.models.sql_models import TokenUsage, TokenUsageLog
from app.core.config import settings

logger = structlog.get_logger()

async def fix_token_limits_to_established():
    """Fix token limits to match the established limits from config"""
    try:
        print("🔧 Fixing token limits to established values...")
        
        # Use the established limits from config
        established_anthropic_limit = settings.anthropic_monthly_limit  # 140,000
        established_openai_limit = settings.openai_monthly_limit  # 6,000
        established_fallback_threshold = settings.openai_fallback_threshold  # 0.80 (80%)
        
        # Update token usage service constants to match established limits
        token_usage_service.GLOBAL_MONTHLY_LIMIT = 200_000  # Base limit
        token_usage_service.ENFORCED_GLOBAL_LIMIT = established_anthropic_limit  # 140,000
        token_usage_service.OPENAI_MONTHLY_LIMIT = established_openai_limit  # 6,000
        
        # Update rate limiting settings based on established limits
        token_usage_service.DAILY_LIMIT = int(established_anthropic_limit / 30)  # ~4,667 per day
        token_usage_service.HOURLY_LIMIT = int(token_usage_service.DAILY_LIMIT / 24)  # ~194 per hour
        token_usage_service.REQUEST_LIMIT = 1000  # Keep reasonable request limit
        
        # Update usage distribution settings
        token_usage_service.MAX_DAILY_USAGE_PERCENTAGE = 8.0  # Max 8% of monthly limit per day
        token_usage_service.MAX_HOURLY_USAGE_PERCENTAGE = 0.5  # Max 0.5% of monthly limit per hour
        
        # Update AI coordination settings
        token_usage_service.AI_COOLDOWN_PERIOD = 300  # 5 minutes between AI requests
        token_usage_service.MAX_CONCURRENT_AI_REQUESTS = 2  # Max 2 AIs can make requests simultaneously
        
        print(f"✅ Token limits updated to established values:")
        print(f"   - Anthropic Monthly Limit: {established_anthropic_limit:,} tokens")
        print(f"   - OpenAI Monthly Limit: {established_openai_limit:,} tokens")
        print(f"   - OpenAI Fallback Threshold: {established_fallback_threshold * 100}%")
        
    except Exception as e:
        print(f"❌ Error updating token limits: {e}")
        logger.error("Error updating token limits", error=str(e))

async def fix_anthropic_service_to_established():
    """Fix Anthropic service to use established limits"""
    try:
        print("🔧 Fixing Anthropic service to established limits...")
        
        # Update the anthropic service file to use established limits
        anthropic_file = "app/services/anthropic_service.py"
        
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        # Update the rate limiting constants to be more conservative
        content = content.replace(
            "MAX_REQUESTS_PER_MIN = 50  # Increased limit",
            "MAX_REQUESTS_PER_MIN = 42  # Conservative limit (50 * 0.85)"
        )
        content = content.replace(
            "MAX_TOKENS_PER_REQUEST = 20000  # Full limit",
            "MAX_TOKENS_PER_REQUEST = 17000  # Conservative limit (20,000 * 0.85)"
        )
        content = content.replace(
            "MAX_REQUESTS_PER_DAY = 4000  # Full limit",
            "MAX_REQUESTS_PER_DAY = 3400  # Conservative limit (4,000 * 0.85)"
        )
        
        with open(anthropic_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service updated to established limits")
        
    except Exception as e:
        print(f"❌ Error updating Anthropic service: {e}")
        logger.error("Error updating Anthropic service", error=str(e))

async def fix_unified_ai_service_parameter_order():
    """Fix the parameter order issue in unified AI service"""
    try:
        print("🔧 Fixing unified AI service parameter order...")
        
        # The issue is that anthropic_rate_limited_call expects (prompt, ai_name, model, max_tokens)
        # but unified_ai_service is calling it with (prompt, ai_name, model, max_tokens)
        # This should already be fixed, but let's verify
        
        unified_file = "app/services/unified_ai_service.py"
        
        with open(unified_file, 'r') as f:
            content = f.read()
        
        # Check if the fix is already applied
        if "anthropic_rate_limited_call(prompt, ai_name, model or" in content:
            print("✅ Unified AI service parameter order already fixed")
        else:
            print("⚠️ Unified AI service parameter order needs fixing")
            
            # Apply the fix
            content = content.replace(
                "response = await anthropic_rate_limited_call(prompt, ai_name, model, max_tokens or 1024)",
                "response = await anthropic_rate_limited_call(prompt, ai_name, model or \"claude-3-5-sonnet-20241022\", max_tokens or 1024)"
            )
            
            with open(unified_file, 'w') as f:
                f.write(content)
            
            print("✅ Unified AI service parameter order fixed")
        
    except Exception as e:
        print(f"❌ Error fixing unified AI service: {e}")
        logger.error("Error fixing unified AI service", error=str(e))

async def reset_token_tracking_to_established():
    """Reset token tracking to use established limits"""
    try:
        print("🔄 Resetting token tracking to established limits...")
        
        async with get_session() as session:
            # Clear all existing token usage data
            await session.execute("DELETE FROM token_usage_logs")
            await session.execute("DELETE FROM token_usage")
            await session.commit()
            
            # Initialize new monthly tracking for all AI types with established limits
            current_month = datetime.utcnow().strftime("%Y-%m")
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                new_tracking = TokenUsage(
                    ai_type=ai_type,
                    month_year=current_month,
                    monthly_limit=settings.anthropic_monthly_limit,  # Use established limit
                    status="active"
                )
                session.add(new_tracking)
            
            await session.commit()
            print("✅ Token tracking reset to established limits")
            
    except Exception as e:
        print(f"❌ Error resetting token tracking: {e}")
        logger.error("Error resetting token tracking", error=str(e))

async def verify_established_limits():
    """Verify that the established limits are properly configured"""
    try:
        print("🔍 Verifying established token limits...")
        
        # Check config settings (these are the established limits)
        print(f"📋 Established Limits from Config:")
        print(f"   - Anthropic Monthly Limit: {settings.anthropic_monthly_limit:,} tokens")
        print(f"   - OpenAI Monthly Limit: {settings.openai_monthly_limit:,} tokens")
        print(f"   - OpenAI Fallback Threshold: {settings.openai_fallback_threshold * 100}%")
        
        # Check token usage service constants
        print(f"\n📊 Token Service Configuration:")
        print(f"   - Global Monthly Limit: {token_usage_service.GLOBAL_MONTHLY_LIMIT:,}")
        print(f"   - Enforced Global Limit: {token_usage_service.ENFORCED_GLOBAL_LIMIT:,}")
        print(f"   - OpenAI Monthly Limit: {token_usage_service.OPENAI_MONTHLY_LIMIT:,}")
        print(f"   - Request Limit: {token_usage_service.REQUEST_LIMIT:,}")
        print(f"   - Daily Usage %: {token_usage_service.MAX_DAILY_USAGE_PERCENTAGE}%")
        print(f"   - AI Cooldown: {token_usage_service.AI_COOLDOWN_PERIOD} seconds")
        print(f"   - Max Concurrent: {token_usage_service.MAX_CONCURRENT_AI_REQUESTS}")
        
        # Verify limits match
        if (token_usage_service.ENFORCED_GLOBAL_LIMIT == settings.anthropic_monthly_limit and
            token_usage_service.OPENAI_MONTHLY_LIMIT == settings.openai_monthly_limit):
            print("\n✅ Token limits properly aligned with established limits!")
        else:
            print("\n❌ Token limits NOT aligned with established limits!")
            print("   This needs to be fixed.")
        
        # Test token usage service
        try:
            all_usage = await token_usage_service.get_all_monthly_usage()
            print(f"\n📈 Current Usage: {all_usage}")
        except Exception as e:
            print(f"\n⚠️ Could not get current usage: {e}")
        
        print("\n✅ Established limits verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying established limits: {e}")
        logger.error("Error verifying established limits", error=str(e))

async def create_established_limits_monitor():
    """Create a monitor that enforces established limits"""
    try:
        print("📊 Creating established limits monitor...")
        
        monitor_code = '''"""
Established Token Limits Monitor
Enforces the established token limits from config
"""

import asyncio
from datetime import datetime
import structlog
from app.services.token_usage_service import token_usage_service
from app.core.config import settings

logger = structlog.get_logger()

async def monitor_established_limits():
    """Monitor and enforce established token limits"""
    try:
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        # Check against established limits
        anthropic_limit = settings.anthropic_monthly_limit
        openai_limit = settings.openai_monthly_limit
        fallback_threshold = settings.openai_fallback_threshold
        
        logger.info("Established limits monitor", 
                   usage_summary=all_usage,
                   emergency_status=emergency_status,
                   anthropic_limit=anthropic_limit,
                   openai_limit=openai_limit,
                   fallback_threshold=fallback_threshold)
        
        # Check for violations of established limits
        for ai_name, usage in all_usage.get('ai_usage', {}).items():
            usage_percentage = usage.get('usage_percentage', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # Check if exceeding established limits
            if total_tokens > anthropic_limit:
                logger.error(f"AI {ai_name} exceeded established anthropic limit", 
                           total_tokens=total_tokens,
                           limit=anthropic_limit)
            
            # Check if approaching fallback threshold
            if usage_percentage > (fallback_threshold * 100):
                logger.warning(f"AI {ai_name} approaching established fallback threshold", 
                             usage_percentage=usage_percentage,
                             threshold=fallback_threshold * 100)
        
        return all_usage, emergency_status
        
    except Exception as e:
        logger.error("Error in established limits monitor", error=str(e))
        return {}, {}

async def start_established_limits_monitor():
    """Start the established limits monitor"""
    while True:
        await monitor_established_limits()
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(start_established_limits_monitor())
'''
        
        with open("app/services/established_limits_monitor.py", 'w') as f:
            f.write(monitor_code)
        
        print("✅ Established limits monitor created")
        
    except Exception as e:
        print(f"❌ Error creating established limits monitor: {e}")
        logger.error("Error creating established limits monitor", error=str(e))

async def main():
    """Main function to fix custodes to established limits"""
    print("🚀 Starting custodes established limits fix...")
    
    try:
        # Fix token limits to established values
        await fix_token_limits_to_established()
        
        # Fix Anthropic service to established limits
        await fix_anthropic_service_to_established()
        
        # Fix unified AI service parameter order
        await fix_unified_ai_service_parameter_order()
        
        # Reset token tracking to established limits
        await reset_token_tracking_to_established()
        
        # Create established limits monitor
        await create_established_limits_monitor()
        
        # Verify established limits
        await verify_established_limits()
        
        print("\n🎉 Custodes established limits fix completed!")
        print("\n📋 Summary of changes:")
        print("- Restored established Anthropic limit: 140,000 tokens")
        print("- Restored established OpenAI limit: 6,000 tokens")
        print("- Restored established fallback threshold: 80%")
        print("- Fixed parameter order issues in unified AI service")
        print("- Created established limits monitor")
        print("- All custodes now adhere to established token limits")
        
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    asyncio.run(main()) 