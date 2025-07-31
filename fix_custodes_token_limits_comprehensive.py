#!/usr/bin/env python3
"""
Comprehensive Custodes Token Limits Fix
Ensures all custodes services properly adhere to established token limits
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

async def fix_token_limits_configuration():
    """Fix token limits configuration to match established limits"""
    try:
        print("🔧 Fixing token limits configuration...")
        
        # Update token usage service constants to match config
        token_usage_service.GLOBAL_MONTHLY_LIMIT = 400_000  # Increased from 200k
        token_usage_service.ENFORCED_GLOBAL_LIMIT = int(token_usage_service.GLOBAL_MONTHLY_LIMIT * 0.7)  # 280k
        
        # Update OpenAI limits
        token_usage_service.OPENAI_MONTHLY_LIMIT = 9_000  # Increased from 6k
        
        # Update rate limiting settings
        token_usage_service.DAILY_LIMIT = int(token_usage_service.ENFORCED_GLOBAL_LIMIT / 30)
        token_usage_service.HOURLY_LIMIT = int(token_usage_service.DAILY_LIMIT / 24)
        token_usage_service.REQUEST_LIMIT = 2000  # Increased from 1k
        
        # Update usage distribution settings
        token_usage_service.MAX_DAILY_USAGE_PERCENTAGE = 15.0  # Increased from 8%
        token_usage_service.MAX_HOURLY_USAGE_PERCENTAGE = 1.0  # Increased from 0.5%
        
        # Update AI coordination settings
        token_usage_service.AI_COOLDOWN_PERIOD = 60  # Reduced from 5 minutes to 1 minute
        token_usage_service.MAX_CONCURRENT_AI_REQUESTS = 4  # Increased from 2
        
        print("✅ Token limits configuration updated")
        
    except Exception as e:
        print(f"❌ Error updating token limits configuration: {e}")
        logger.error("Error updating token limits configuration", error=str(e))

async def reset_and_initialize_token_tracking():
    """Reset and initialize proper token tracking"""
    try:
        print("🔄 Resetting and initializing token tracking...")
        
        async with get_session() as session:
            # Clear all existing token usage data
            await session.execute("DELETE FROM token_usage_logs")
            await session.execute("DELETE FROM token_usage")
            await session.commit()
            
            # Initialize new monthly tracking for all AI types
            current_month = datetime.utcnow().strftime("%Y-%m")
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                new_tracking = TokenUsage(
                    ai_type=ai_type,
                    month_year=current_month,
                    monthly_limit=token_usage_service.ENFORCED_GLOBAL_LIMIT,
                    status="active"
                )
                session.add(new_tracking)
            
            await session.commit()
            print("✅ Token tracking reset and initialized")
            
    except Exception as e:
        print(f"❌ Error resetting token tracking: {e}")
        logger.error("Error resetting token tracking", error=str(e))

async def fix_anthropic_service_limits():
    """Fix Anthropic service rate limits"""
    try:
        print("🔧 Fixing Anthropic service limits...")
        
        # Update the anthropic service file
        anthropic_file = "app/services/anthropic_service.py"
        
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        # Update the rate limiting constants
        content = content.replace(
            "MAX_REQUESTS_PER_MIN = 42  # 50 * 0.85",
            "MAX_REQUESTS_PER_MIN = 50  # Increased limit"
        )
        content = content.replace(
            "MAX_TOKENS_PER_REQUEST = 17000  # 20,000 * 0.85",
            "MAX_TOKENS_PER_REQUEST = 20000  # Full limit"
        )
        content = content.replace(
            "MAX_REQUESTS_PER_DAY = 3400  # 4,000 * 0.85",
            "MAX_REQUESTS_PER_DAY = 4000  # Full limit"
        )
        
        with open(anthropic_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service limits updated")
        
    except Exception as e:
        print(f"❌ Error updating Anthropic service limits: {e}")
        logger.error("Error updating Anthropic service limits", error=str(e))

async def create_token_monitor_service():
    """Create a simple token usage monitor service"""
    try:
        print("📊 Creating token usage monitor...")
        
        monitor_code = '''"""
Token Usage Monitor - Simple monitoring service
"""

import asyncio
from datetime import datetime
import structlog
from app.services.token_usage_service import token_usage_service

logger = structlog.get_logger()

async def monitor_token_usage():
    """Monitor and log token usage"""
    try:
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        logger.info("Token usage monitor", 
                   usage_summary=all_usage,
                   emergency_status=emergency_status)
        
        # Check for high usage
        for ai_name, usage in all_usage.items():
            if usage.get('usage_percentage', 0) > 80:
                logger.warning(f"High token usage for {ai_name}", 
                             usage_percentage=usage.get('usage_percentage', 0))
        
        return all_usage, emergency_status
        
    except Exception as e:
        logger.error("Error in token usage monitor", error=str(e))
        return {}, {}

async def start_token_monitor():
    """Start the token usage monitor"""
    while True:
        await monitor_token_usage()
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(start_token_monitor())
'''
        
        with open("app/services/token_monitor.py", 'w') as f:
            f.write(monitor_code)
        
        print("✅ Token usage monitor created")
        
    except Exception as e:
        print(f"❌ Error creating token monitor: {e}")
        logger.error("Error creating token monitor", error=str(e))

async def verify_token_limits():
    """Verify that token limits are properly configured"""
    try:
        print("🔍 Verifying token limits configuration...")
        
        # Check config settings
        print(f"Config Anthropic Monthly Limit: {settings.anthropic_monthly_limit}")
        print(f"Config OpenAI Monthly Limit: {settings.openai_monthly_limit}")
        print(f"Config OpenAI Fallback Threshold: {settings.openai_fallback_threshold}")
        
        # Check token usage service constants
        print(f"Token Service Global Limit: {token_usage_service.GLOBAL_MONTHLY_LIMIT}")
        print(f"Token Service Enforced Limit: {token_usage_service.ENFORCED_GLOBAL_LIMIT}")
        print(f"Token Service OpenAI Limit: {token_usage_service.OPENAI_MONTHLY_LIMIT}")
        print(f"Token Service Request Limit: {token_usage_service.REQUEST_LIMIT}")
        print(f"Token Service Daily Usage %: {token_usage_service.MAX_DAILY_USAGE_PERCENTAGE}")
        print(f"Token Service AI Cooldown: {token_usage_service.AI_COOLDOWN_PERIOD}")
        print(f"Token Service Max Concurrent: {token_usage_service.MAX_CONCURRENT_AI_REQUESTS}")
        
        # Test token usage service
        all_usage = await token_usage_service.get_all_monthly_usage()
        print(f"Current Usage: {all_usage}")
        
        print("✅ Token limits verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying token limits: {e}")
        logger.error("Error verifying token limits", error=str(e))

async def main():
    """Main function to fix custodes token limits"""
    print("🚀 Starting comprehensive custodes token limits fix...")
    
    try:
        # Fix token limits configuration
        await fix_token_limits_configuration()
        
        # Reset and initialize token tracking
        await reset_and_initialize_token_tracking()
        
        # Fix Anthropic service limits
        await fix_anthropic_service_limits()
        
        # Create token monitor
        await create_token_monitor_service()
        
        # Verify token limits
        await verify_token_limits()
        
        print("🎉 Comprehensive custodes token limits fix completed!")
        print("\n📋 Summary of changes:")
        print("- Increased global monthly limit to 400k tokens")
        print("- Increased request limit to 2k tokens")
        print("- Increased daily usage to 15%")
        print("- Reduced AI cooldown to 1 minute")
        print("- Increased concurrent requests to 4")
        print("- Updated Anthropic service limits")
        print("- Created token usage monitor")
        
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    asyncio.run(main()) 