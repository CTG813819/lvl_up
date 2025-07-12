#!/usr/bin/env python3
"""
Script to create the oath_papers table
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_session, init_database

async def create_oath_papers_table():
    """Create the oath_papers table if it doesn't exist"""
    try:
        # Initialize database first
        await init_database()
        session = get_session()
        async with session as s:
            # Create oath_papers table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS oath_papers (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(100) DEFAULT 'general',
                ai_insights JSONB,
                learning_value FLOAT DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'pending',
                ai_responses JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            await s.execute(text(create_table_sql))
            await s.commit()
            
            print("✅ Oath papers table created successfully!")
            
            # Check if table exists
            check_sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'oath_papers'
            );
            """
            
            result = await s.execute(text(check_sql))
            exists = result.scalar()
            
            if exists:
                print("✅ Oath papers table verified!")
            else:
                print("❌ Oath papers table not found!")
                
    except Exception as e:
        print(f"❌ Error creating oath_papers table: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_oath_papers_table()) 