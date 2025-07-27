#!/usr/bin/env python3
"""
Migration script to add subject fields to oath_papers and training_data tables
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core.database import get_session, init_database

async def add_subject_fields():
    """Add subject fields to existing tables"""
    try:
        # Initialize database first
        await init_database()
        session = get_session()
        async with session as s:
            
            # Add subject field to oath_papers table if it doesn't exist
            check_oath_subject_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'oath_papers' AND column_name = 'subject';
            """
            
            result = await s.execute(text(check_oath_subject_sql))
            oath_subject_exists = result.fetchone()
            
            if not oath_subject_exists:
                add_oath_subject_sql = """
                ALTER TABLE oath_papers 
                ADD COLUMN subject VARCHAR(200);
                """
                await s.execute(text(add_oath_subject_sql))
                print("✅ Added subject field to oath_papers table")
            else:
                print("✅ Subject field already exists in oath_papers table")
            
            # Add subject field to training_data table if it doesn't exist
            check_training_subject_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'training_data' AND column_name = 'subject';
            """
            
            result = await s.execute(text(check_training_subject_sql))
            training_subject_exists = result.fetchone()
            
            if not training_subject_exists:
                add_training_subject_sql = """
                ALTER TABLE training_data 
                ADD COLUMN subject VARCHAR(200);
                """
                await s.execute(text(add_training_subject_sql))
                print("✅ Added subject field to training_data table")
            else:
                print("✅ Subject field already exists in training_data table")
            
            # Create indexes for better performance
            try:
                create_oath_subject_index_sql = """
                CREATE INDEX IF NOT EXISTS idx_oath_papers_subject 
                ON oath_papers(subject);
                """
                await s.execute(text(create_oath_subject_index_sql))
                print("✅ Created index on oath_papers.subject")
            except Exception as e:
                print(f"⚠️ Index on oath_papers.subject may already exist: {e}")
            
            try:
                create_training_subject_index_sql = """
                CREATE INDEX IF NOT EXISTS idx_training_data_subject 
                ON training_data(subject);
                """
                await s.execute(text(create_training_subject_index_sql))
                print("✅ Created index on training_data.subject")
            except Exception as e:
                print(f"⚠️ Index on training_data.subject may already exist: {e}")
            
            await s.commit()
            
            # Verify the changes
            verify_sql = """
            SELECT 
                table_name, 
                column_name, 
                data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('oath_papers', 'training_data') 
            AND column_name = 'subject'
            ORDER BY table_name;
            """
            
            result = await s.execute(text(verify_sql))
            columns = result.fetchall()
            
            print("\n📋 Verification Results:")
            for table_name, column_name, data_type in columns:
                print(f"  ✅ {table_name}.{column_name}: {data_type}")
            
            print("\n🎉 Subject fields migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Starting subject fields migration...")
    asyncio.run(add_subject_fields())
    print("✅ Migration completed!") 