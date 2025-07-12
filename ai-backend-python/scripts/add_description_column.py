#!/usr/bin/env python3
"""
Script to add description column to proposals table.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.core import database

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

async def add_description_column():
    """Add description column to proposals table if it doesn't exist"""
    try:
        await database.init_database()
        
        async with database.engine.begin() as conn:
            # Check if description column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' AND column_name = 'description'
            """))
            
            column_exists = result.fetchone()
            
            if not column_exists:
                print("Adding description column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN description TEXT
                """))
                print("Description column added successfully!")
            else:
                print("Description column already exists in proposals table.")
                
    except Exception as e:
        print(f"Error adding description column: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(add_description_column()) 