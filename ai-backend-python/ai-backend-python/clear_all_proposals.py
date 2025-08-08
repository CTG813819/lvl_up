#!/usr/bin/env python3
"""
Simple script to clear all proposals from the database
"""

import asyncio
import asyncpg
import os

async def clear_proposals():
    """Clear all proposals from the database"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/ai_backend')
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Delete all proposals
        await conn.execute("DELETE FROM proposals")
        
        print("✅ All proposals cleared successfully")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error clearing proposals: {e}")

if __name__ == "__main__":
    asyncio.run(clear_proposals()) 