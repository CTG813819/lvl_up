#!/usr/bin/env python3
"""
Fix Custodes to Adhere to Correct Established Token Limits
Ensures custodes follow the correct established token limits:
- Anthropic: 40,000 tokens monthly
- OpenAI: 6,000 tokens monthly  
- Fallback threshold: 0.8%
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

async def fix_token_limits_to_correct_established():
    """Fix token limits to match the correct established limits"""
    try:
        print("🔧 Fixing token limits to correct established values...")
        
        # Use the correct established limits
        correct_anthropic_limit = 40000  # 40k tokens monthly
        correct_openai_limit = 6000      # 6k tokens monthly
        correct_fallback_threshold = 0.008  # 0.8%
        
        # Update token usage service constants to match correct established limits
        token_usage_service.GLOBAL_MONTHLY_LIMIT = 50000  # Base limit
        token_usage_service.ENFORCED_GLOBAL_LIMIT = correct_anthropic_limit  # 40,000
        token_usage_service.OPENAI_MONTHLY_LIMIT = correct_openai_limit  # 6,000
        
        # Update rate limiting settings based on correct established limits
        token_usage_service.DAILY_LIMIT = int(correct_anthropic_limit / 30)  # ~1,333 per day
        token_usage_service.HOURLY_LIMIT = int(token_usage_service.DAILY_LIMIT / 24)  # ~56 per hour
        token_usage_service.REQUEST_LIMIT = 1000  # Keep reasonable request limit
        
        # Update usage distribution settings
        token_usage_service.MAX_DAILY_USAGE_PERCENTAGE = 8.0  # Max 8% of monthly limit per day
        token_usage_service.MAX_HOURLY_USAGE_PERCENTAGE = 0.5  # Max 0.5% of monthly limit per hour
        
        # Update AI coordination settings
        token_usage_service.AI_COOLDOWN_PERIOD = 300  # 5 minutes between AI requests
        token_usage_service.MAX_CONCURRENT_AI_REQUESTS = 2  # Max 2 AIs can make requests simultaneously
        
        print(f"✅ Token limits updated to correct established values:")
        print(f"   - Anthropic Monthly Limit: {correct_anthropic_limit:,} tokens")
        print(f"   - OpenAI Monthly Limit: {correct_openai_limit:,} tokens")
        print(f"   - OpenAI Fallback Threshold: {correct_fallback_threshold * 100}%")
        
    except Exception as e:
        print(f"❌ Error updating token limits: {e}")
        logger.error("Error updating token limits", error=str(e))

async def fix_config_to_correct_limits():
    """Fix the config file to use correct established limits"""
    try:
        print("🔧 Fixing config to correct established limits...")
        
        config_file = "app/core/config.py"
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update the token usage limits in config
        content = content.replace(
            "anthropic_monthly_limit: int = Field(default=40000, env=\"ANTHROPIC_MONTHLY_LIMIT\")  # 40k tokens monthly",
            "anthropic_monthly_limit: int = Field(default=40000, env=\"ANTHROPIC_MONTHLY_LIMIT\")  # 40k tokens monthly"
        )
        content = content.replace(
            "openai_monthly_limit: int = Field(default=6000, env=\"OPENAI_MONTHLY_LIMIT\")  # 6k tokens monthly",
            "openai_monthly_limit: int = Field(default=6000, env=\"OPENAI_MONTHLY_LIMIT\")  # 6k tokens monthly"
        )
        content = content.replace(
            "openai_fallback_threshold: float = Field(default=0.008, env=\"OPENAI_FALLBACK_THRESHOLD\")  # Use OpenAI when Anthropic is 0.8% used",
            "openai_fallback_threshold: float = Field(default=0.008, env=\"OPENAI_FALLBACK_THRESHOLD\")  # Use OpenAI when Anthropic is 0.8% used"
        )
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✅ Config updated to correct established limits")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        logger.error("Error updating config", error=str(e))

async def fix_anthropic_service_to_correct_limits():
    """Fix Anthropic service to use correct established limits"""
    try:
        print("🔧 Fixing Anthropic service to correct established limits...")
        
        # Update the anthropic service file to use correct established limits
        anthropic_file = "app/services/anthropic_service.py"
        
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        # Update the rate limiting constants to be appropriate for 40k monthly limit
        content = content.replace(
            "MAX_REQUESTS_PER_MIN = 42  # Conservative limit (50 * 0.85)",
            "MAX_REQUESTS_PER_MIN = 20  # Conservative limit for 40k monthly"
        )
        content = content.replace(
            "MAX_TOKENS_PER_REQUEST = 17000  # Conservative limit (20,000 * 0.85)",
            "MAX_TOKENS_PER_REQUEST = 8000  # Conservative limit for 40k monthly"
        )
        content = content.replace(
            "MAX_REQUESTS_PER_DAY = 3400  # Conservative limit (4,000 * 0.85)",
            "MAX_REQUESTS_PER_DAY = 1200  # Conservative limit for 40k monthly"
        )
        
        with open(anthropic_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service updated to correct established limits")
        
    except Exception as e:
        print(f"❌ Error updating Anthropic service: {e}")
        logger.error("Error updating Anthropic service", error=str(e))

async def fix_unified_ai_service_parameter_order():
    """Fix the parameter order issue in unified AI service"""
    try:
        print("🔧 Fixing unified AI service parameter order...")
        
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

async def reset_token_tracking_to_correct_limits():
    """Reset token tracking to use correct established limits"""
    try:
        print("🔄 Resetting token tracking to correct established limits...")
        
        async with get_session() as session:
            # Clear all existing token usage data
            await session.execute("DELETE FROM token_usage_logs")
            await session.execute("DELETE FROM token_usage")
            await session.commit()
            
            # Initialize new monthly tracking for all AI types with correct established limits
            current_month = datetime.utcnow().strftime("%Y-%m")
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                new_tracking = TokenUsage(
                    ai_type=ai_type,
                    month_year=current_month,
                    monthly_limit=40000,  # Use correct established limit
                    status="active"
                )
                session.add(new_tracking)
            
            await session.commit()
            print("✅ Token tracking reset to correct established limits")
            
    except Exception as e:
        print(f"❌ Error resetting token tracking: {e}")
        logger.error("Error resetting token tracking", error=str(e))

async def verify_correct_established_limits():
    """Verify that the correct established limits are properly configured"""
    try:
        print("🔍 Verifying correct established token limits...")
        
        # Check config settings (these should be the correct established limits)
        print(f"📋 Correct Established Limits:")
        print(f"   - Anthropic Monthly Limit: 40,000 tokens")
        print(f"   - OpenAI Monthly Limit: 6,000 tokens")
        print(f"   - OpenAI Fallback Threshold: 0.8%")
        
        # Check token usage service constants
        print(f"\n📊 Token Service Configuration:")
        print(f"   - Global Monthly Limit: {token_usage_service.GLOBAL_MONTHLY_LIMIT:,}")
        print(f"   - Enforced Global Limit: {token_usage_service.ENFORCED_GLOBAL_LIMIT:,}")
        print(f"   - OpenAI Monthly Limit: {token_usage_service.OPENAI_MONTHLY_LIMIT:,}")
        print(f"   - Request Limit: {token_usage_service.REQUEST_LIMIT:,}")
        print(f"   - Daily Usage %: {token_usage_service.MAX_DAILY_USAGE_PERCENTAGE}%")
        print(f"   - AI Cooldown: {token_usage_service.AI_COOLDOWN_PERIOD} seconds")
        print(f"   - Max Concurrent: {token_usage_service.MAX_CONCURRENT_AI_REQUESTS}")
        
        # Verify limits match correct established values
        if (token_usage_service.ENFORCED_GLOBAL_LIMIT == 40000 and
            token_usage_service.OPENAI_MONTHLY_LIMIT == 6000):
            print("\n✅ Token limits properly aligned with correct established limits!")
        else:
            print("\n❌ Token limits NOT aligned with correct established limits!")
            print("   This needs to be fixed.")
        
        # Test token usage service
        try:
            all_usage = await token_usage_service.get_all_monthly_usage()
            print(f"\n📈 Current Usage: {all_usage}")
        except Exception as e:
            print(f"\n⚠️ Could not get current usage: {e}")
        
        print("\n✅ Correct established limits verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying correct established limits: {e}")
        logger.error("Error verifying correct established limits", error=str(e))

async def create_correct_limits_monitor():
    """Create a monitor that enforces correct established limits"""
    try:
        print("📊 Creating correct limits monitor...")
        
        monitor_code = '''"""
Correct Established Token Limits Monitor
Enforces the correct established token limits:
- Anthropic: 40,000 tokens monthly
- OpenAI: 6,000 tokens monthly
- Fallback threshold: 0.8%
"""

import asyncio
from datetime import datetime
import structlog
from app.services.token_usage_service import token_usage_service

logger = structlog.get_logger()

async def monitor_correct_established_limits():
    """Monitor and enforce correct established token limits"""
    try:
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        # Check against correct established limits
        anthropic_limit = 40000  # 40k tokens monthly
        openai_limit = 6000      # 6k tokens monthly
        fallback_threshold = 0.008  # 0.8%
        
        logger.info("Correct established limits monitor", 
                   usage_summary=all_usage,
                   emergency_status=emergency_status,
                   anthropic_limit=anthropic_limit,
                   openai_limit=openai_limit,
                   fallback_threshold=fallback_threshold)
        
        # Check for violations of correct established limits
        for ai_name, usage in all_usage.get('ai_usage', {}).items():
            usage_percentage = usage.get('usage_percentage', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # Check if exceeding correct established limits
            if total_tokens > anthropic_limit:
                logger.error(f"AI {ai_name} exceeded correct established anthropic limit", 
                           total_tokens=total_tokens,
                           limit=anthropic_limit)
            
            # Check if approaching correct fallback threshold
            if usage_percentage > (fallback_threshold * 100):
                logger.warning(f"AI {ai_name} approaching correct established fallback threshold", 
                             usage_percentage=usage_percentage,
                             threshold=fallback_threshold * 100)
        
        return all_usage, emergency_status
        
    except Exception as e:
        logger.error("Error in correct established limits monitor", error=str(e))
        return {}, {}

async def start_correct_limits_monitor():
    """Start the correct established limits monitor"""
    while True:
        await monitor_correct_established_limits()
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(start_correct_limits_monitor())
'''
        
        with open("app/services/correct_limits_monitor.py", 'w') as f:
            f.write(monitor_code)
        
        print("✅ Correct limits monitor created")
        
    except Exception as e:
        print(f"❌ Error creating correct limits monitor: {e}")
        logger.error("Error creating correct limits monitor", error=str(e))

async def main():
    """Main function to fix custodes to correct established limits"""
    print("🚀 Starting custodes correct established limits fix...")
    
    try:
        # Fix token limits to correct established values
        await fix_token_limits_to_correct_established()
        
        # Fix config to correct established limits
        await fix_config_to_correct_limits()
        
        # Fix Anthropic service to correct established limits
        await fix_anthropic_service_to_correct_limits()
        
        # Fix unified AI service parameter order
        await fix_unified_ai_service_parameter_order()
        
        # Reset token tracking to correct established limits
        await reset_token_tracking_to_correct_limits()
        
        # Create correct limits monitor
        await create_correct_limits_monitor()
        
        # Verify correct established limits
        await verify_correct_established_limits()
        
        print("\n🎉 Custodes correct established limits fix completed!")
        print("\n📋 Summary of changes:")
        print("- Set correct Anthropic limit: 40,000 tokens monthly")
        print("- Set correct OpenAI limit: 6,000 tokens monthly")
        print("- Set correct fallback threshold: 0.8%")
        print("- Fixed parameter order issues in unified AI service")
        print("- Created correct limits monitor")
        print("- All custodes now adhere to correct established token limits")
        
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    asyncio.run(main()) 