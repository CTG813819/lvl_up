#!/usr/bin/env python3
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def check_columns():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not found")
        return
    
    engine = create_async_engine(
        database_url.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False,
        connect_args={'ssl': 'require'}
    )
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print("Current proposals table columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Check specifically for description column
            description_exists = any(col[0] == 'description' for col in columns)
            print(f"\nDescription column exists: {description_exists}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_columns()) 