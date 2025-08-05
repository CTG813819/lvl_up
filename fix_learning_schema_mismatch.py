#!/usr/bin/env python3
"""
Fix Learning Schema Mismatch
============================
This script fixes the database schema mismatch between the old and new Learning table schemas.
The issue is that the database has the old schema with a 'pattern' column, but the code uses the new schema.
"""

import os
import sys
import asyncio
import asyncpg
from datetime import datetime
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def fix_learning_schema():
    """Fix the learning table schema to match the current model"""
    
    # Get database connection details from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Parse database URL
    if database_url.startswith("postgresql://"):
        # Remove postgresql:// prefix
        db_url = database_url.replace("postgresql://", "")
        
        # Extract credentials and connection info
        if "@" in db_url:
            credentials, rest = db_url.split("@", 1)
            user, password = credentials.split(":", 1)
            
            if "/" in rest:
                host_port, db_name = rest.split("/", 1)
                if ":" in host_port:
                    host, port = host_port.split(":", 1)
                else:
                    host, port = host_port, "5432"
            else:
                print("❌ Invalid database URL format")
                return False
        else:
            print("❌ Invalid database URL format")
            return False
    else:
        print("❌ Unsupported database URL format")
        return False
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=int(port),
            database=db_name,
            ssl='require'
        )
        
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
            await conn.execute("""
                ALTER TABLE learning 
                ADD COLUMN learning_data JSONB
            """)
            print("  ✅ learning_data column added")
            
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
            
            # Step 3: Drop old columns (optional - we'll keep them for now to be safe)
            print("  ⚠️  Keeping old columns for safety. You can drop them later if needed.")
            
            # Step 4: Update column constraints
            print("  📝 Updating column constraints...")
            
            # Make pattern column nullable (since it's now in learning_data)
            await conn.execute("""
                ALTER TABLE learning 
                ALTER COLUMN pattern DROP NOT NULL
            """)
            print("  ✅ Made pattern column nullable")
            
            # Make context column nullable
            await conn.execute("""
                ALTER TABLE learning 
                ALTER COLUMN context DROP NOT NULL
            """)
            print("  ✅ Made context column nullable")
            
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
    print("🔧 Fixing Learning Schema Mismatch")
    print("==================================")
    
    success = await fix_learning_schema()
    
    if success:
        print("\n✅ Schema mismatch fixed successfully!")
        print("🔄 Please restart your application to apply the changes.")
    else:
        print("\n❌ Failed to fix schema mismatch")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 