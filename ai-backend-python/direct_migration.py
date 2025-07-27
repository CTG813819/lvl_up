#!/usr/bin/env python3
"""
Direct migration script to add enhanced proposal fields to the database
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Database connection details
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require')

async def add_enhanced_proposal_fields():
    """Add enhanced proposal fields to the database"""
    
    try:
        print("🔧 Starting enhanced proposal fields migration...")
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if proposals table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'proposals'
            );
        """)
        
        if not table_exists:
            print("❌ Proposals table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Check which columns already exist
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'proposals' 
            AND table_schema = 'public'
        """)
        existing_columns = {row['column_name'] for row in result}
        
        # Define the new columns to add
        new_columns = [
            ('ai_learning_summary', 'TEXT'),
            ('change_type', 'VARCHAR(20)'),
            ('change_scope', 'VARCHAR(20)'),
            ('affected_components', 'JSONB DEFAULT \'[]\''),
            ('learning_sources', 'JSONB DEFAULT \'[]\''),
            ('expected_impact', 'TEXT'),
            ('risk_assessment', 'TEXT'),
            ('application_response', 'TEXT'),
            ('application_timestamp', 'TIMESTAMP'),
            ('application_result', 'TEXT'),
            ('post_application_analysis', 'TEXT'),
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"Adding column: {column_name}")
                await conn.execute(f"""
                    ALTER TABLE proposals 
                    ADD COLUMN {column_name} {column_type}
                """)
            else:
                print(f"Column {column_name} already exists, skipping")
        
        # Create index for change_type if it doesn't exist
        index_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_indexes 
                WHERE tablename = 'proposals' 
                AND indexname = 'idx_proposals_change_type'
            );
        """)
        
        if not index_exists:
            print("Creating index for change_type")
            await conn.execute("""
                CREATE INDEX idx_proposals_change_type ON proposals(change_type)
            """)
        else:
            print("Index for change_type already exists")
        
        await conn.close()
        
        print("✅ Enhanced proposal fields migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during enhanced proposal fields migration: {e}")
        return False


async def main():
    """Main migration function"""
    print("🚀 Starting enhanced proposal fields migration...")
    
    success = await add_enhanced_proposal_fields()
    
    if success:
        print("✅ Migration completed successfully")
    else:
        print("❌ Migration failed")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 