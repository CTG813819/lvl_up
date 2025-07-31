#!/usr/bin/env python3
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def debug_schema_issue():
    database_url = os.getenv('DATABASE_URL')
    print(f"Database URL: {database_url}")
    
    engine = create_async_engine(
        database_url.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False,
        connect_args={'ssl': 'require'}
    )
    
    try:
        async with engine.begin() as conn:
            # Check current schema
            result = await conn.execute(text("SELECT current_schema();"))
            current_schema = result.scalar()
            print(f"Current schema: {current_schema}")
            
            # Check all schemas
            result = await conn.execute(text("SELECT schema_name FROM information_schema.schemata;"))
            schemas = [row[0] for row in result.fetchall()]
            print(f"Available schemas: {schemas}")
            
            # Check if proposals table exists in current schema
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = current_schema()
                    AND table_name = 'proposals'
                );
            """))
            table_in_current_schema = result.scalar()
            print(f"Proposals table in current schema: {table_in_current_schema}")
            
            # Check all proposals tables across all schemas
            result = await conn.execute(text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name = 'proposals';
            """))
            all_proposals_tables = result.fetchall()
            print(f"All proposals tables: {all_proposals_tables}")
            
            # If table exists in current schema, check its columns
            if table_in_current_schema:
                result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = current_schema()
                    AND table_name = 'proposals' 
                    ORDER BY ordinal_position;
                """))
                columns = result.fetchall()
                print(f"Columns in current schema proposals table:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Check specifically for description
                description_exists = any(col[0] == 'description' for col in columns)
                print(f"Description column exists: {description_exists}")
                
                if not description_exists:
                    print("Adding description column to current schema...")
                    await conn.execute(text("ALTER TABLE proposals ADD COLUMN description TEXT;"))
                    print("Description column added!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(debug_schema_issue()) 