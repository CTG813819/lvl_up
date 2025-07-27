#!/usr/bin/env python3
"""
Script to reset token usage for the current month
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import init_database, get_session
from app.services.token_usage_service import TokenUsageService
from app.models.sql_models import TokenUsage, TokenUsageLog
from sqlalchemy import select, and_


async def reset_current_month_usage():
    """Reset token usage for all AI agents for the current month"""
    try:
        # Initialize database
        await init_database()
        
        # Initialize token usage service
        token_service = await TokenUsageService.initialize()
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"🔄 Resetting token usage for {current_month}...")
        
        async with get_session() as session:
            for ai_type in ai_types:
                # Reset monthly tracking
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year == current_month
                    )
                )
                result = await session.execute(stmt)
                tracking = result.scalar_one_or_none()
                
                if tracking:
                    tracking.tokens_in = 0
                    tracking.tokens_out = 0
                    tracking.total_tokens = 0
                    tracking.request_count = 0
                    tracking.usage_percentage = 0.0
                    tracking.status = "active"
                    tracking.last_request_at = None
                    
                    print(f"✅ Reset {ai_type}: 0 tokens, 0 requests")
                else:
                    # Create new tracking if it doesn't exist
                    new_tracking = TokenUsage(
                        ai_type=ai_type,
                        month_year=current_month,
                        monthly_limit=500000,
                        status="active"
                    )
                    session.add(new_tracking)
                    print(f"✅ Created new tracking for {ai_type}")
            
            await session.commit()
            print(f"✅ Successfully reset token usage for {current_month}")
            
            # Show current status
            print("\n📊 Current Usage Status:")
            for ai_type in ai_types:
                usage = await token_service.get_monthly_usage(ai_type, current_month)
                if usage:
                    print(f"  {ai_type}: {usage['total_tokens']} tokens ({usage['usage_percentage']:.1f}%)")
                else:
                    print(f"  {ai_type}: 0 tokens (0.0%)")
                    
    except Exception as e:
        print(f"❌ Error resetting token usage: {e}")
        raise


async def show_current_usage():
    """Show current usage for all AI agents"""
    try:
        await init_database()
        token_service = await TokenUsageService.initialize()
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        print(f"\n📊 Current Usage for {current_month}:")
        
        all_usage = await token_service.get_all_monthly_usage(current_month)
        
        for ai_type, usage in all_usage.get("ai_usage", {}).items():
            print(f"  {ai_type}:")
            print(f"    Tokens In: {usage['tokens_in']:,}")
            print(f"    Tokens Out: {usage['tokens_out']:,}")
            print(f"    Total: {usage['total_tokens']:,}")
            print(f"    Requests: {usage['request_count']}")
            print(f"    Usage: {usage['usage_percentage']:.1f}%")
            print(f"    Status: {usage['status']}")
            print()
            
    except Exception as e:
        print(f"❌ Error showing current usage: {e}")


async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        await show_current_usage()
    else:
        await reset_current_month_usage()


if __name__ == "__main__":
    asyncio.run(main()) 