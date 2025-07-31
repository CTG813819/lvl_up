#!/usr/bin/env python3
"""
Check Token Usage Status
=======================
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def check_token_status():
    """Check current token usage status"""
    try:
        from app.core.database import get_session, init_database
        from app.models.sql_models import TokenUsage
        from sqlalchemy import select
        
        # Initialize database first
        await init_database()
        
        async with get_session() as session:
            result = await session.execute(select(TokenUsage))
            records = result.scalars().all()
            
            print(f"Token Usage Records: {len(records)}")
            print("=" * 50)
            
            for record in records:
                print(f"{record.ai_type}: {record.total_tokens} tokens ({record.usage_percentage:.1f}%)")
                print(f"  - Monthly Limit: {record.monthly_limit:,}")
                print(f"  - Status: {record.status}")
                print(f"  - Last Request: {record.last_request_at}")
                print()
                
    except Exception as e:
        print(f"Error checking token status: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_token_status()) 