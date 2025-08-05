#!/usr/bin/env python3
"""
Create Analytics Cache Table
===========================

This script creates the missing analytics_cache table needed for:
- Analytics growth score storage
- Black library data storage
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def create_analytics_cache_table():
    """Create the analytics_cache table"""
    print("🔧 Creating analytics_cache table...")
    
    try:
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if database_url and 'postgresql+asyncpg://' in database_url:
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        conn = await asyncpg.connect(database_url)
        
        # Create analytics_cache table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics_cache (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        print("✅ analytics_cache table created successfully")
        
        # Create index for better performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_analytics_cache_key 
            ON analytics_cache(key);
        """)
        
        print("✅ Index created for analytics_cache table")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating analytics_cache table: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Creating missing database table...")
    print("=" * 50)
    
    success = await create_analytics_cache_table()
    
    if success:
        print("\n✅ Table creation completed successfully!")
        print("You can now run the comprehensive fix script again.")
    else:
        print("\n❌ Table creation failed. Check the error above.")

if __name__ == "__main__":
    asyncio.run(main()) 