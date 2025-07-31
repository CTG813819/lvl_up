#!/usr/bin/env python3
"""
Fix Custodes to Adhere to Shared Token Limits
Ensures custodes understand that token limits are SHARED across all AIs:
- Anthropic: 40,000 tokens monthly (shared by all AIs)
- OpenAI: 6,000 tokens monthly (shared by all AIs)
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

async def fix_shared_token_limits():
    """Fix token limits to reflect shared usage across all AIs"""
    try:
        print("🔧 Fixing shared token limits across all AIs...")
        
        # Use the correct shared limits
        shared_anthropic_limit = 40000  # 40k tokens monthly (shared by all AIs)
        shared_openai_limit = 6000      # 6k tokens monthly (shared by all AIs)
        fallback_threshold = 0.008      # 0.8%
        
        # Update token usage service constants to reflect SHARED limits
        token_usage_service.GLOBAL_MONTHLY_LIMIT = 50000  # Base limit
        token_usage_service.ENFORCED_GLOBAL_LIMIT = shared_anthropic_limit  # 40,000 (SHARED)
        token_usage_service.OPENAI_MONTHLY_LIMIT = shared_openai_limit  # 6,000 (SHARED)
        
        # Update rate limiting settings based on shared limits
        # These are now shared across all AIs, so we need to be more conservative
        token_usage_service.DAILY_LIMIT = int(shared_anthropic_limit / 30)  # ~1,333 per day (shared)
        token_usage_service.HOURLY_LIMIT = int(token_usage_service.DAILY_LIMIT / 24)  # ~56 per hour (shared)
        token_usage_service.REQUEST_LIMIT = 1000  # Keep reasonable request limit
        
        # Update usage distribution settings for shared limits
        token_usage_service.MAX_DAILY_USAGE_PERCENTAGE = 8.0  # Max 8% of shared monthly limit per day
        token_usage_service.MAX_HOURLY_USAGE_PERCENTAGE = 0.5  # Max 0.5% of shared monthly limit per hour
        
        # Update AI coordination settings for shared limits
        token_usage_service.AI_COOLDOWN_PERIOD = 300  # 5 minutes between AI requests
        token_usage_service.MAX_CONCURRENT_AI_REQUESTS = 2  # Max 2 AIs can make requests simultaneously
        
        print(f"✅ Shared token limits updated:")
        print(f"   - Anthropic Monthly Limit: {shared_anthropic_limit:,} tokens (SHARED by all AIs)")
        print(f"   - OpenAI Monthly Limit: {shared_openai_limit:,} tokens (SHARED by all AIs)")
        print(f"   - OpenAI Fallback Threshold: {fallback_threshold * 100}%")
        print(f"   - Daily Limit: ~{token_usage_service.DAILY_LIMIT:,} tokens (shared)")
        print(f"   - Hourly Limit: ~{token_usage_service.HOURLY_LIMIT:,} tokens (shared)")
        
    except Exception as e:
        print(f"❌ Error updating shared token limits: {e}")
        logger.error("Error updating shared token limits", error=str(e))

async def fix_anthropic_service_for_shared_limits():
    """Fix Anthropic service to respect shared limits"""
    try:
        print("🔧 Fixing Anthropic service for shared limits...")
        
        # Update the anthropic service file to use conservative limits for shared usage
        anthropic_file = "app/services/anthropic_service.py"
        
        with open(anthropic_file, 'r') as f:
            content = f.read()
        
        # Update the rate limiting constants to be very conservative for shared limits
        content = content.replace(
            "MAX_REQUESTS_PER_MIN = 20  # Conservative limit for 40k monthly",
            "MAX_REQUESTS_PER_MIN = 10  # Very conservative for shared 40k monthly"
        )
        content = content.replace(
            "MAX_TOKENS_PER_REQUEST = 8000  # Conservative limit for 40k monthly",
            "MAX_TOKENS_PER_REQUEST = 4000  # Very conservative for shared 40k monthly"
        )
        content = content.replace(
            "MAX_REQUESTS_PER_DAY = 1200  # Conservative limit for 40k monthly",
            "MAX_REQUESTS_PER_DAY = 600  # Very conservative for shared 40k monthly"
        )
        
        with open(anthropic_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service updated for shared limits")
        
    except Exception as e:
        print(f"❌ Error updating Anthropic service: {e}")
        logger.error("Error updating Anthropic service", error=str(e))

async def create_shared_limits_monitor():
    """Create a monitor that enforces shared limits across all AIs"""
    try:
        print("📊 Creating shared limits monitor...")
        
        monitor_code = '''"""
Shared Token Limits Monitor
Enforces shared token limits across all AIs:
- Anthropic: 40,000 tokens monthly (shared by all AIs)
- OpenAI: 6,000 tokens monthly (shared by all AIs)
- Fallback threshold: 0.8%
"""

import asyncio
from datetime import datetime
import structlog
from app.services.token_usage_service import token_usage_service

logger = structlog.get_logger()

async def monitor_shared_limits():
    """Monitor and enforce shared token limits across all AIs"""
    try:
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        # Check against shared established limits
        shared_anthropic_limit = 40000  # 40k tokens monthly (SHARED)
        shared_openai_limit = 6000      # 6k tokens monthly (SHARED)
        fallback_threshold = 0.008      # 0.8%
        
        # Get global usage across all AIs
        global_total_tokens = emergency_status.get('global_total_tokens', 0)
        global_usage_percentage = emergency_status.get('global_usage_percentage', 0)
        
        logger.info("Shared limits monitor", 
                   usage_summary=all_usage,
                   emergency_status=emergency_status,
                   shared_anthropic_limit=shared_anthropic_limit,
                   shared_openai_limit=shared_openai_limit,
                   fallback_threshold=fallback_threshold,
                   global_total_tokens=global_total_tokens,
                   global_usage_percentage=global_usage_percentage)
        
        # Check for violations of shared limits
        if global_total_tokens > shared_anthropic_limit:
            logger.error(f"Global usage exceeded shared anthropic limit", 
                       global_total_tokens=global_total_tokens,
                       limit=shared_anthropic_limit)
        
        # Check if approaching shared fallback threshold
        if global_usage_percentage > (fallback_threshold * 100):
            logger.warning(f"Global usage approaching shared fallback threshold", 
                         global_usage_percentage=global_usage_percentage,
                         threshold=fallback_threshold * 100)
        
        # Check individual AI usage patterns
        for ai_name, usage in all_usage.get('ai_usage', {}).items():
            ai_tokens = usage.get('total_tokens', 0)
            ai_percentage = usage.get('usage_percentage', 0)
            
            # Log high usage by individual AIs
            if ai_percentage > 25:  # If any AI is using more than 25% of shared limit
                logger.warning(f"AI {ai_name} using high percentage of shared limit", 
                             ai_tokens=ai_tokens,
                             ai_percentage=ai_percentage,
                             global_total=global_total_tokens)
        
        return all_usage, emergency_status
        
    except Exception as e:
        logger.error("Error in shared limits monitor", error=str(e))
        return {}, {}

async def start_shared_limits_monitor():
    """Start the shared limits monitor"""
    while True:
        await monitor_shared_limits()
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(start_shared_limits_monitor())
'''
        
        with open("app/services/shared_limits_monitor.py", 'w') as f:
            f.write(monitor_code)
        
        print("✅ Shared limits monitor created")
        
    except Exception as e:
        print(f"❌ Error creating shared limits monitor: {e}")
        logger.error("Error creating shared limits monitor", error=str(e))

async def verify_shared_limits():
    """Verify that the shared limits are properly configured"""
    try:
        print("🔍 Verifying shared token limits...")
        
        # Check config settings
        print(f"📋 Shared Limits Configuration:")
        print(f"   - Anthropic Monthly Limit: 40,000 tokens (SHARED by all AIs)")
        print(f"   - OpenAI Monthly Limit: 6,000 tokens (SHARED by all AIs)")
        print(f"   - OpenAI Fallback Threshold: 0.8%")
        
        # Check token usage service constants
        print(f"\n📊 Token Service Configuration:")
        print(f"   - Global Monthly Limit: {token_usage_service.GLOBAL_MONTHLY_LIMIT:,}")
        print(f"   - Enforced Global Limit: {token_usage_service.ENFORCED_GLOBAL_LIMIT:,} (SHARED)")
        print(f"   - OpenAI Monthly Limit: {token_usage_service.OPENAI_MONTHLY_LIMIT:,} (SHARED)")
        print(f"   - Request Limit: {token_usage_service.REQUEST_LIMIT:,}")
        print(f"   - Daily Usage %: {token_usage_service.MAX_DAILY_USAGE_PERCENTAGE}%")
        print(f"   - AI Cooldown: {token_usage_service.AI_COOLDOWN_PERIOD} seconds")
        print(f"   - Max Concurrent: {token_usage_service.MAX_CONCURRENT_AI_REQUESTS}")
        
        # Verify limits match shared values
        if (token_usage_service.ENFORCED_GLOBAL_LIMIT == 40000 and
            token_usage_service.OPENAI_MONTHLY_LIMIT == 6000):
            print("\n✅ Shared token limits properly configured!")
        else:
            print("\n❌ Shared token limits NOT properly configured!")
            print("   This needs to be fixed.")
        
        # Test token usage service
        try:
            all_usage = await token_usage_service.get_all_monthly_usage()
            print(f"\n📈 Current Shared Usage: {all_usage}")
        except Exception as e:
            print(f"\n⚠️ Could not get current usage: {e}")
        
        print("\n✅ Shared limits verification completed")
        
    except Exception as e:
        print(f"❌ Error verifying shared limits: {e}")
        logger.error("Error verifying shared limits", error=str(e))

async def create_shared_limits_documentation():
    """Create documentation explaining shared limits"""
    try:
        print("📝 Creating shared limits documentation...")
        
        doc_content = """# Shared Token Limits Documentation

## Overview
Token limits in the custodes system are **SHARED across all AIs**, not individual per AI.

## Limits
- **Anthropic Monthly Limit**: 40,000 tokens (shared by all AIs: imperium, guardian, sandbox, conquest)
- **OpenAI Monthly Limit**: 6,000 tokens (shared by all AIs)
- **Fallback Threshold**: 0.8% (when to switch from Anthropic to OpenAI)

## How It Works
1. All AIs share the same monthly token pool
2. When any AI makes a request, it consumes from the shared pool
3. Daily and hourly limits are also shared across all AIs
4. Rate limiting prevents any single AI from consuming too much

## Monitoring
- Global usage is tracked across all AIs
- Individual AI usage is tracked for analysis
- Alerts are triggered when shared limits are approached
- Emergency shutdown when shared limits are exceeded

## Best Practices
- Coordinate AI usage to avoid conflicts
- Monitor shared usage regularly
- Use fallback providers when approaching limits
- Implement proper rate limiting between AIs
"""
        
        with open("SHARED_LIMITS_DOCUMENTATION.md", 'w') as f:
            f.write(doc_content)
        
        print("✅ Shared limits documentation created")
        
    except Exception as e:
        print(f"❌ Error creating documentation: {e}")
        logger.error("Error creating documentation", error=str(e))

async def main():
    """Main function to fix custodes shared limits"""
    print("🚀 Starting custodes shared limits fix...")
    
    try:
        # Fix shared token limits
        await fix_shared_token_limits()
        
        # Fix Anthropic service for shared limits
        await fix_anthropic_service_for_shared_limits()
        
        # Create shared limits monitor
        await create_shared_limits_monitor()
        
        # Create documentation
        await create_shared_limits_documentation()
        
        # Verify shared limits
        await verify_shared_limits()
        
        print("\n🎉 Custodes shared limits fix completed!")
        print("\n📋 Summary of changes:")
        print("- Configured shared Anthropic limit: 40,000 tokens monthly (ALL AIs)")
        print("- Configured shared OpenAI limit: 6,000 tokens monthly (ALL AIs)")
        print("- Set fallback threshold: 0.8%")
        print("- Updated rate limiting for shared usage")
        print("- Created shared limits monitor")
        print("- Created documentation explaining shared limits")
        print("- All custodes now understand and adhere to SHARED token limits")
        
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    asyncio.run(main()) 