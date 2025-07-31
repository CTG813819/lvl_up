#!/usr/bin/env python3
"""
Simple script to fix the learning table by adding proposal_id column
"""

import asyncio
import asyncpg
import os

async def fix_learning_table():
    """Add proposal_id column to learning table"""
    
    # Database connection parameters
    DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    # Extract connection parameters from URL
    # postgresql+asyncpg://user:pass@host:port/db?params
    url_parts = DATABASE_URL.replace("postgresql+asyncpg://", "").split("/")
    auth_host = url_parts[0]
    db_name = url_parts[1].split("?")[0]
    
    auth, host = auth_host.split("@")
    user, password = auth.split(":")
    
    print(f"🔧 Connecting to database: {db_name}")
    print(f"👤 User: {user}")
    print(f"🌐 Host: {host}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host.split(":")[0],
            port=host.split(":")[1] if ":" in host else 5432,
            database=db_name,
            ssl='require'
        )
        
        print("✅ Connected to database successfully")
        
        # Check if learning table exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'learning'
            );
        """)
        
        if not result:
            print("❌ Learning table does not exist")
            return False
        
        print("✅ Learning table exists")
        
        # Define all the columns that should exist in the learning table
        expected_columns = [
            ('proposal_id', 'UUID REFERENCES proposals(id)'),
            ('ai_type', 'VARCHAR(50)'),
            ('learning_type', 'VARCHAR(50)'),
            ('learning_data', 'JSONB'),
            ('status', 'VARCHAR(20) DEFAULT \'pending\''),
            ('created_at', 'TIMESTAMP DEFAULT NOW()'),
            ('updated_at', 'TIMESTAMP DEFAULT NOW()')
        ]
        
        # Get existing columns
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'learning' 
            AND table_schema = 'public'
        """)
        existing_columns = {row['column_name'] for row in result}
        
        # Add missing columns
        for column_name, column_type in expected_columns:
            if column_name not in existing_columns:
                print(f"🔧 Adding {column_name} column to learning table...")
                await conn.execute(f"""
                    ALTER TABLE learning 
                    ADD COLUMN {column_name} {column_type}
                """)
                print(f"✅ {column_name} column added successfully")
            else:
                print(f"✅ {column_name} column already exists in learning table")
        
        # Create index if it doesn't exist
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'learning' 
                AND indexname = 'idx_learning_proposal_id'
            );
        """)
        
        if result:
            print("✅ Index for learning.proposal_id already exists")
        else:
            print("🔧 Creating index for learning.proposal_id...")
            await conn.execute("""
                CREATE INDEX idx_learning_proposal_id ON learning(proposal_id)
            """)
            print("✅ Index created successfully")
        
        await conn.close()
        print("✅ Learning table migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_learning_table()) 