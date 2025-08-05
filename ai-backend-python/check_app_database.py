#!/usr/bin/env python3
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def check_app_database():
    # Check what DATABASE_URL the app is using
    database_url = os.getenv('DATABASE_URL')
    print(f"App DATABASE_URL: {database_url}")
    
    if not database_url:
        print("DATABASE_URL not found in environment")
        return
    
    engine = create_async_engine(
        database_url.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False,
        connect_args={'ssl': 'require'}
    )
    
    try:
        async with engine.begin() as conn:
            # Check current database name
            result = await conn.execute(text("SELECT current_database();"))
            db_name = result.scalar()
            print(f"Connected to database: {db_name}")
            
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
                # Check columns
                result = await conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    ORDER BY ordinal_position;
                """))
                
                columns = [row[0] for row in result.fetchall()]
                print(f"Columns: {columns}")
                
                # Check specifically for description
                description_exists = 'description' in columns
                print(f"Description column exists: {description_exists}")
                
                if not description_exists:
                    print("Adding description column...")
                    await conn.execute(text("ALTER TABLE proposals ADD COLUMN description TEXT;"))
                    print("Description column added!")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_app_database()) 