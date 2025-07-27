#!/usr/bin/env python3
"""
Script to create token usage tables in the database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import init_database, create_tables
from app.models.sql_models import TokenUsage, TokenUsageLog, Base


async def create_token_usage_tables():
    """Create token usage tables in the database"""
    try:
        print("🔄 Creating token usage tables...")
        
        # Initialize database
        await init_database()
        
        # Create all tables (this will include the new token usage tables)
        await create_tables()
        
        print("✅ Token usage tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating token usage tables: {e}")
        raise


async def verify_tables():
    """Verify that the tables were created correctly"""
    try:
        print("🔍 Verifying token usage tables...")
        
        await init_database()
        
        # Use the session to check tables
        from app.core.database import get_session
        from sqlalchemy import text
        
        async with get_session() as session:
            # Check if tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('token_usage', 'token_usage_logs')
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            table_names = [row[0] for row in tables]
            
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
        print(f"❌ Error verifying tables: {e}")


async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        await verify_tables()
    else:
        await create_token_usage_tables()


if __name__ == "__main__":
    asyncio.run(main()) 