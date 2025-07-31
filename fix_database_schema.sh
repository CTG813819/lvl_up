#!/bin/bash

# Comprehensive Database Schema Fix Script
# This script fixes the learning table schema issues

set -e

echo "🔧 Fixing Database Schema Issues"
echo "================================"

cd /home/ubuntu/ai-backend-python

# Create a comprehensive database fix script
cat > fix_database_comprehensive.py << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive Database Schema Fix
Fixes the learning table pattern column issue
"""

import asyncio
import asyncpg
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

def convert_sqlalchemy_url_to_asyncpg(url):
    """Convert SQLAlchemy URL to asyncpg format"""
    # Remove the +asyncpg part
    url = url.replace('postgresql+asyncpg://', 'postgresql://')
    
    # Handle SSL parameters
    if '?sslmode=require' in url:
        url = url.replace('?sslmode=require', '')
        ssl_mode = 'require'
    elif '&sslmode=require' in url:
        url = url.replace('&sslmode=require', '')
        ssl_mode = 'require'
    else:
        ssl_mode = None
    
    # Handle channel_binding parameter
    url = url.replace('&channel_binding=require', '')
    
    return url, ssl_mode

async def fix_database_schema():
    """Comprehensive database schema fix"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        # Convert URL format for asyncpg
        print("🔧 Converting database URL format...")
        asyncpg_url, ssl_mode = convert_sqlalchemy_url_to_asyncpg(database_url)
        print(f"✅ Converted URL: {asyncpg_url}")
        
        # Connect to database
        print("🔌 Connecting to database...")
        if ssl_mode:
            conn = await asyncpg.connect(asyncpg_url, ssl=ssl_mode)
        else:
            conn = await asyncpg.connect(asyncpg_url)
        
        # Check current table structure
        print("🔍 Checking current learning table structure...")
        columns = await conn.fetch("""
            SELECT column_name, is_nullable, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'learning'
            ORDER BY ordinal_position
        """)
        
        print("📊 Current learning table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}, nullable={col['is_nullable']}, default={col['column_default']}")
        
        # Check if pattern column exists
        pattern_column = await conn.fetch("""
            SELECT column_name, is_nullable, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'learning' AND column_name = 'pattern'
        """)
        
        if not pattern_column:
            print("❌ Pattern column not found in learning table")
            print("🔧 Adding pattern column...")
            await conn.execute("""
                ALTER TABLE learning 
                ADD COLUMN pattern VARCHAR DEFAULT 'default_pattern'
            """)
            print("✅ Pattern column added")
        else:
            print("✅ Pattern column exists")
            col_info = pattern_column[0]
            print(f"📊 Pattern column: nullable={col_info['is_nullable']}, type={col_info['data_type']}, default={col_info['column_default']}")
            
            # Fix nullable constraint
            if col_info['is_nullable'] == 'NO':
                print("🔧 Making pattern column nullable...")
                await conn.execute("""
                    ALTER TABLE learning 
                    ALTER COLUMN pattern DROP NOT NULL
                """)
                print("✅ Pattern column is now nullable")
            
            # Add default value if not exists
            if not col_info['column_default']:
                print("🔧 Adding default value for pattern column...")
                await conn.execute("""
                    ALTER TABLE learning 
                    ALTER COLUMN pattern SET DEFAULT 'default_pattern'
                """)
                print("✅ Default value added for pattern column")
        
        # Update existing null values
        print("🔧 Updating existing null pattern values...")
        result = await conn.execute("""
            UPDATE learning 
            SET pattern = 'default_pattern' 
            WHERE pattern IS NULL
        """)
        print(f"✅ Updated {result} rows with null pattern values")
        
        # Check for any remaining null values
        null_count = await conn.fetchval("""
            SELECT COUNT(*) FROM learning WHERE pattern IS NULL
        """)
        print(f"📊 Remaining null pattern values: {null_count}")
        
        # Verify the fix
        print("🔍 Verifying the fix...")
        test_insert = await conn.fetchval("""
            INSERT INTO learning (id, ai_type, learning_type, learning_data, status, pattern)
            VALUES (gen_random_uuid(), 'test', 'test_type', '{"test": "data"}', 'active', 'test_pattern')
            RETURNING id
        """)
        print(f"✅ Test insert successful with ID: {test_insert}")
        
        # Clean up test data
        await conn.execute("DELETE FROM learning WHERE ai_type = 'test'")
        print("✅ Test data cleaned up")
        
        await conn.close()
        print("✅ Database schema fix completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database_schema())
    if success:
        print("🎉 Database schema fix successful")
    else:
        print("💥 Database schema fix failed")
        exit(1)
EOF

# Run the database fix using the virtual environment
echo "🔧 Running comprehensive database schema fix..."
source venv/bin/activate
python3 fix_database_comprehensive.py
deactivate

echo ""
echo "🎉 Database schema fix completed!"
echo "================================"
echo "✅ Pattern column issues resolved"
echo "✅ Default values set"
echo "✅ Nullable constraints fixed"
echo ""
echo "🚀 You can now run the port conflict fix:"
echo "   ./fix_port_conflict_final.sh" 