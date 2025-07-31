#!/usr/bin/env python3
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix_service_database():
    # Use the exact same DATABASE_URL as the service
    database_url = "postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb"
    print(f"Using service DATABASE_URL: {database_url}")
    
    engine = create_async_engine(
        database_url,
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
                print(f"Current columns: {columns}")
                
                # Check specifically for description
                description_exists = 'description' in columns
                print(f"Description column exists: {description_exists}")
                
                if not description_exists:
                    print("Adding description column...")
                    await conn.execute(text("ALTER TABLE proposals ADD COLUMN description TEXT;"))
                    print("Description column added!")
                    
                    # Check again
                    result = await conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'proposals' 
                        ORDER BY ordinal_position;
                    """))
                    
                    columns = [row[0] for row in result.fetchall()]
                    print(f"Updated columns: {columns}")
                    print(f"Description column now exists: {'description' in columns}")
                else:
                    print("Description column already exists!")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_service_database()) 