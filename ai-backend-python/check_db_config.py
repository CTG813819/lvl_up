#!/usr/bin/env python3
"""
Check database configuration and connection
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Database Configuration Check ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT_SET')}")

# Check if we can connect to the database
try:
    import asyncio
    from app.core.database import init_database
    from sqlalchemy import text
    
    async def check_db():
        await init_database()
        from app.core.database import engine
        
        async with engine.begin() as conn:
            # Check current database
            result = await conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"Connected to database: {db_info[0]}")
            print(f"Current user: {db_info[1]}")
            
            # Check if proposals table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'proposals'
                );
            """))
            table_exists = result.scalar()
            print(f"Proposals table exists: {table_exists}")
            
            if table_exists:
                # Check for ai_learning_summary column
                result = await conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'ai_learning_summary'
                """))
                column_exists = result.scalar() is not None
                print(f"ai_learning_summary column exists: {column_exists}")
                
                if not column_exists:
                    print("❌ ai_learning_summary column is missing!")
                else:
                    print("✅ ai_learning_summary column exists")
    
    asyncio.run(check_db())
    
except Exception as e:
    print(f"❌ Error checking database: {e}")

print("=== End Database Check ===") 