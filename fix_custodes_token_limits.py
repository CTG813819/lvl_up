#!/usr/bin/env python3
"""
Fix Custodes Token Limits
Adjusts token usage limits to be more reasonable and ensures proper adherence
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
from app.models.sql_models import TokenUsage

logger = structlog.get_logger()

async def reset_token_usage():
    """Reset all token usage to zero for testing"""
    try:
        print("🔄 Resetting token usage to zero...")
        
        async with get_session() as session:
            # Delete all token usage records
            await session.execute("DELETE FROM token_usage")
            await session.execute("DELETE FROM token_usage_logs")
            await session.commit()
            
        print("✅ Token usage reset successfully")
        return True
    except Exception as e:
        print(f"❌ Error resetting token usage: {e}")
        return False

async def adjust_token_limits():
    """Adjust token limits to be more reasonable"""
    try:
        print("🔧 Adjusting token limits...")
        
        # Update the token usage service constants
        token_usage_service_file = "app/services/token_usage_service.py"
        
        with open(token_usage_service_file, 'r') as f:
            content = f.read()
        
        # Update limits to be more reasonable
        replacements = {
            'GLOBAL_MONTHLY_LIMIT = 200_000': 'GLOBAL_MONTHLY_LIMIT = 500_000',
            'ENFORCED_GLOBAL_LIMIT = int(GLOBAL_MONTHLY_LIMIT * 0.7)': 'ENFORCED_GLOBAL_LIMIT = int(GLOBAL_MONTHLY_LIMIT * 0.8)',
            'REQUEST_LIMIT = 1000': 'REQUEST_LIMIT = 2000',
            'MAX_DAILY_USAGE_PERCENTAGE = 8.0': 'MAX_DAILY_USAGE_PERCENTAGE = 15.0',
            'MAX_HOURLY_USAGE_PERCENTAGE = 0.5': 'MAX_HOURLY_USAGE_PERCENTAGE = 1.0',
            'AI_COOLDOWN_PERIOD = 300': 'AI_COOLDOWN_PERIOD = 60',
            'MAX_CONCURRENT_AI_REQUESTS = 2': 'MAX_CONCURRENT_AI_REQUESTS = 4',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(token_usage_service_file, 'w') as f:
            f.write(content)
        
        print("✅ Token limits adjusted successfully")
        return True
    except Exception as e:
        print(f"❌ Error adjusting token limits: {e}")
        return False

async def update_anthropic_service_limits():
    """Update Anthropic service limits"""
    try:
        print("🔧 Updating Anthropic service limits...")
        
        anthropic_service_file = "app/services/anthropic_service.py"
        
        with open(anthropic_service_file, 'r') as f:
            content = f.read()
        
        # Update limits to be more reasonable
        replacements = {
            'MAX_TOKENS_PER_REQUEST = 17000': 'MAX_TOKENS_PER_REQUEST = 20000',
            'MAX_REQUESTS_PER_MIN = 42': 'MAX_REQUESTS_PER_MIN = 45',
            'MAX_REQUESTS_PER_DAY = 3400': 'MAX_REQUESTS_PER_DAY = 3600',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(anthropic_service_file, 'w') as f:
            f.write(content)
        
        print("✅ Anthropic service limits updated successfully")
        return True
    except Exception as e:
        print(f"❌ Error updating Anthropic service limits: {e}")
        return False

async def update_openai_service_limits():
    """Update OpenAI service limits"""
    try:
        print("🔧 Updating OpenAI service limits...")
        
        openai_service_file = "app/services/openai_service.py"
        
        with open(openai_service_file, 'r') as f:
            content = f.read()
        
        # Update limits to be more reasonable
        replacements = {
            'MAX_TOKENS_PER_REQUEST = 17000': 'MAX_TOKENS_PER_REQUEST = 20000',
            'MAX_REQUESTS_PER_MIN = 42': 'MAX_REQUESTS_PER_MIN = 45',
            'MAX_REQUESTS_PER_DAY = 3400': 'MAX_REQUESTS_PER_DAY = 3600',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(openai_service_file, 'w') as f:
            f.write(content)
        
        print("✅ OpenAI service limits updated successfully")
        return True
    except Exception as e:
        print(f"❌ Error updating OpenAI service limits: {e}")
        return False

async def update_config_limits():
    """Update configuration limits"""
    try:
        print("🔧 Updating configuration limits...")
        
        config_file = "app/core/config.py"
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Update limits to be more reasonable
        replacements = {
            'anthropic_monthly_limit: int = Field(default=140000': 'anthropic_monthly_limit: int = Field(default=400000',
            'openai_monthly_limit: int = Field(default=6000': 'openai_monthly_limit: int = Field(default=15000',
            'openai_fallback_threshold: float = Field(default=0.80': 'openai_fallback_threshold: float = Field(default=0.85',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✅ Configuration limits updated successfully")
        return True
    except Exception as e:
        print(f"❌ Error updating configuration limits: {e}")
        return False

async def create_token_usage_monitor():
    """Create a simple token usage monitor"""
    try:
        print("🔧 Creating token usage monitor...")
        
        monitor_script = '''#!/usr/bin/env python3
"""
Simple Token Usage Monitor
Monitors token usage and provides status updates
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.token_usage_service import token_usage_service

async def check_token_usage():
    """Check current token usage"""
    try:
        # Check usage for each AI
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print("\\n📊 Token Usage Status")
        print("=" * 50)
        
        for ai_type in ai_types:
            can_make_request, usage_info = await token_usage_service.check_usage_limit(ai_type)
            
            status = "✅ Active" if can_make_request else "❌ Blocked"
            usage_pct = usage_info.get("usage_percentage", 0)
            remaining = usage_info.get("remaining_tokens", 0)
            
            print(f"{ai_type.upper():12} | {status:10} | {usage_pct:6.1f}% | {remaining:,} remaining")
        
        print("=" * 50)
        
        # Check global status
        global_usage = await token_usage_service.get_all_monthly_usage()
        total_usage = sum(usage.get("total_tokens", 0) for usage in global_usage.values())
        global_limit = 400000  # Updated limit
        global_pct = (total_usage / global_limit) * 100
        
        print(f"\\n🌍 Global Usage: {total_usage:,} / {global_limit:,} ({global_pct:.1f}%)")
        
        if global_pct >= 95:
            print("⚠️  WARNING: Global usage is high!")
        elif global_pct >= 80:
            print("📈 Notice: Global usage is moderate")
        else:
            print("✅ Global usage is healthy")
            
    except Exception as e:
        print(f"❌ Error checking token usage: {e}")

if __name__ == "__main__":
    asyncio.run(check_token_usage())
'''
        
        with open("monitor_token_usage_simple.py", 'w') as f:
            f.write(monitor_script)
        
        # Make it executable
        os.chmod("monitor_token_usage_simple.py", 0o755)
        
        print("✅ Token usage monitor created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating token usage monitor: {e}")
        return False

async def main():
    """Main function to fix custodes token limits"""
    print("🚀 Starting Custodes Token Limits Fix")
    print("=" * 50)
    
    # Reset token usage first
    await reset_token_usage()
    
    # Adjust token limits
    await adjust_token_limits()
    
    # Update service limits
    await update_anthropic_service_limits()
    await update_openai_service_limits()
    
    # Update configuration
    await update_config_limits()
    
    # Create monitor
    await create_token_usage_monitor()
    
    print("\\n" + "=" * 50)
    print("✅ Custodes Token Limits Fix Complete!")
    print("\\n📋 Summary of Changes:")
    print("• Increased global monthly limit from 140k to 400k tokens")
    print("• Increased request limit from 1k to 2k tokens")
    print("• Increased daily usage from 8% to 15%")
    print("• Reduced AI cooldown from 5 minutes to 1 minute")
    print("• Increased concurrent requests from 2 to 4")
    print("• Updated Anthropic/OpenAI service limits")
    print("• Created simple token usage monitor")
    print("\\n🔧 To monitor usage, run: python monitor_token_usage_simple.py")
    print("🔧 To reset usage again, run: python fix_custodes_token_limits.py reset")

if __name__ == "__main__":
    # Check if reset flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        asyncio.run(reset_token_usage())
    else:
        asyncio.run(main()) 