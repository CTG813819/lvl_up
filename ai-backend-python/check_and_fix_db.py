#!/usr/bin/env python3
"""
Check and fix database schema issues
"""

import asyncio
from sqlalchemy import text
from app.core.database import get_session, init_database

async def check_and_fix_database():
    """Check if ai_learning_summary column exists and add it if needed"""
    
    # Initialize database first
    await init_database()
    
    async with get_session() as session:
        try:
            # Check if the column exists
            result = await session.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'proposals' AND column_name = 'ai_learning_summary'")
            )
            column_exists = result.scalar() is not None
            
            print(f"ai_learning_summary column exists: {column_exists}")
            
            if not column_exists:
                print("Adding ai_learning_summary column...")
                await session.execute(
                    text("ALTER TABLE proposals ADD COLUMN ai_learning_summary TEXT")
                )
                await session.commit()
                print("✅ ai_learning_summary column added successfully!")
            else:
                print("✅ ai_learning_summary column already exists")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(check_and_fix_database()) 