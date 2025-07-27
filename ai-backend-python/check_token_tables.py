#!/usr/bin/env python3
"""
Script to check if token usage tables exist
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from sqlalchemy import text

async def check_token_tables():
    """Check if token usage tables exist"""
    try:
        # Initialize database
        await init_database()
        
        from app.core.database import engine
        async with engine.begin() as conn:
            # Check for token usage tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('token_usage', 'token_usage_logs')
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            
            print("🔍 Checking token usage tables...")
            
            if 'token_usage' in table_names:
                print("✅ token_usage table exists")
            else:
                print("❌ token_usage table missing")
                
            if 'token_usage_logs' in table_names:
                print("✅ token_usage_logs table exists")
            else:
                print("❌ token_usage_logs table missing")
            
            if len(table_names) == 2:
                print("✅ All token usage tables verified!")
            else:
                print("❌ Some tables are missing")
                
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    asyncio.run(check_token_tables()) 