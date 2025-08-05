#!/usr/bin/env python3
"""
Script to check what tables exist in the NeonDB database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

async def check_tables():
    try:
        from app.core.database import init_database, get_session
        from sqlalchemy import text
        
        print("🔄 Initializing database...")
        await init_database()
        
        print("🔍 Checking for terra_extensions table...")
        async with get_session() as session:
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'terra_extensions'
            """))
            
            table_exists = result.fetchone() is not None
            print(f"✅ Terra extensions table exists: {table_exists}")
            
            if table_exists:
                # Check if there are any extensions
                result = await session.execute(text("SELECT COUNT(*) FROM terra_extensions"))
                count = result.scalar()
                print(f"📊 Number of extensions in table: {count}")
                
                # List all extensions
                result = await session.execute(text("SELECT id, feature_name, status FROM terra_extensions"))
                extensions = result.fetchall()
                print(f"📋 Extensions:")
                for ext in extensions:
                    print(f"  - {ext[0]}: {ext[1]} ({ext[2]})")
            else:
                print("❌ Terra extensions table does not exist!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_tables()) 