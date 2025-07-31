#!/usr/bin/env python3
"""
Check current database schema in Neon database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def check_current_schema():
    """Check what tables exist in the database"""
    try:
        from app.core.database import init_database
        from sqlalchemy import text
        
        print("🔍 Checking current database schema...")
        
        # Initialize database
        await init_database()
        
        from app.core.database import engine
        
        async with engine.begin() as conn:
            # Get all tables in the database
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Found {len(tables)} tables in database:")
            
            for table in tables:
                print(f"  - {table}")
            
            # Check for specific tables we need
            required_tables = [
                'internet_knowledge',
                'test_scenarios', 
                'ai_communications',
                'ai_responses',
                'agent_metrics',
                'proposals',
                'learning_entries',
                'token_usage'
            ]
            
            print(f"\n🔍 Checking for required tables:")
            missing_tables = []
            for table in required_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - MISSING")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {missing_tables}")
                print("These tables need to be created for the enhanced test system to work properly.")
            else:
                print(f"\n✅ All required tables exist!")
                
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_current_schema()) 