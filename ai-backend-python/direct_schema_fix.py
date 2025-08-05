#!/usr/bin/env python3
"""
Direct Schema Fix
================
This script directly fixes the learning table schema by connecting to the database
and updating the schema to match the current model.
"""

import asyncio
import asyncpg
import json
from datetime import datetime

async def fix_schema_direct():
    """Fix the learning table schema directly"""
    
    # Database connection details (you may need to update these)
    DB_CONFIG = {
        'user': 'postgres',
        'password': 'your_password_here',  # Update this
        'host': 'your_host_here',          # Update this
        'port': 5432,
        'database': 'your_database_here',  # Update this
        'ssl': 'require'
    }
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected to database successfully")
        
        # Check current table structure
        print("🔍 Checking current learning table structure...")
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'learning' 
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        
        print("Current columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check if we have the old schema (with pattern column)
        has_pattern_column = any(col['column_name'] == 'pattern' for col in columns)
        has_learning_data_column = any(col['column_name'] == 'learning_data' for col in columns)
        
        if has_pattern_column and not has_learning_data_column:
            print("🔧 Detected old schema. Migrating to new schema...")
            
            # Step 1: Add learning_data column
            print("  📝 Adding learning_data column...")
            try:
                await conn.execute("""
                    ALTER TABLE learning 
                    ADD COLUMN learning_data JSONB
                """)
                print("  ✅ learning_data column added")
            except Exception as e:
                if "already exists" in str(e):
                    print("  ✅ learning_data column already exists")
                else:
                    raise e
            
            # Step 2: Migrate existing data to learning_data
            print("  📝 Migrating existing data to learning_data...")
            
            # Get all existing records
            records = await conn.fetch("""
                SELECT id, ai_type, learning_type, pattern, context, feedback, 
                       confidence, applied_count, success_rate, status, created_at, updated_at
                FROM learning
            """)
            
            print(f"  📊 Found {len(records)} records to migrate")
            
            for record in records:
                # Create learning_data JSON from old columns
                learning_data = {
                    "pattern": record['pattern'],
                    "context": record['context'],
                    "feedback": record['feedback'],
                    "confidence": float(record['confidence']) if record['confidence'] else 0.5,
                    "applied_count": record['applied_count'] or 0,
                    "success_rate": float(record['success_rate']) if record['success_rate'] else 0.0,
                    "migrated_from_old_schema": True,
                    "migration_timestamp": datetime.utcnow().isoformat()
                }
                
                # Update the record with learning_data
                await conn.execute("""
                    UPDATE learning 
                    SET learning_data = $1
                    WHERE id = $2
                """, json.dumps(learning_data), record['id'])
            
            print("  ✅ Data migration completed")
            
            # Step 3: Update column constraints
            print("  📝 Updating column constraints...")
            
            # Make pattern column nullable (since it's now in learning_data)
            try:
                await conn.execute("""
                    ALTER TABLE learning 
                    ALTER COLUMN pattern DROP NOT NULL
                """)
                print("  ✅ Made pattern column nullable")
            except Exception as e:
                print(f"  ⚠️  Could not make pattern column nullable: {e}")
            
            # Make context column nullable
            try:
                await conn.execute("""
                    ALTER TABLE learning 
                    ALTER COLUMN context DROP NOT NULL
                """)
                print("  ✅ Made context column nullable")
            except Exception as e:
                print(f"  ⚠️  Could not make context column nullable: {e}")
            
            print("✅ Schema migration completed successfully!")
            
        elif has_learning_data_column:
            print("✅ Database already has the new schema")
            
        else:
            print("❌ Unexpected table structure")
            return False
        
        # Verify the migration
        print("🔍 Verifying migration...")
        
        # Test inserting a record with the new schema
        test_data = {
            "pattern": "test_pattern",
            "context": "test_context",
            "feedback": "test_feedback",
            "confidence": 0.8,
            "applied_count": 1,
            "success_rate": 1.0
        }
        
        await conn.execute("""
            INSERT INTO learning (ai_type, learning_type, learning_data, status)
            VALUES ($1, $2, $3, $4)
        """, "test", "test_type", json.dumps(test_data), "active")
        
        print("✅ Test insert successful")
        
        # Clean up test record
        await conn.execute("""
            DELETE FROM learning WHERE ai_type = 'test'
        """)
        
        await conn.close()
        print("✅ Database connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Main function"""
    print("🔧 Direct Schema Fix")
    print("===================")
    print("⚠️  Please update the DB_CONFIG in this script with your database credentials")
    print("   before running it.")
    
    # Uncomment the line below after updating DB_CONFIG
    # success = await fix_schema_direct()
    
    print("\n📝 To run this script:")
    print("1. Update the DB_CONFIG dictionary with your database credentials")
    print("2. Uncomment the 'success = await fix_schema_direct()' line")
    print("3. Run: python3 direct_schema_fix.py")

if __name__ == "__main__":
    asyncio.run(main()) 