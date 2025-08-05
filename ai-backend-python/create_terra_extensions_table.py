#!/usr/bin/env python3
"""
Migration script to create the Terra extensions table.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database, create_tables, engine
from app.models.terra_extension import TerraExtension

async def create_terra_extensions_table():
    """Create the Terra extensions table"""
    print("🔧 Creating Terra extensions table...")
    
    try:
        # Initialize database
        await init_database()
        
        # Create tables
        await create_tables()
        
        print("✅ Terra extensions table created successfully!")
        print("📋 Table structure:")
        print("   - id: Primary key")
        print("   - feature_name: Unique feature identifier")
        print("   - menu_title: Display name in menu")
        print("   - icon_name: Flutter icon name")
        print("   - description: Extension description")
        print("   - dart_code: The actual Dart code")
        print("   - status: pending/testing/ready_for_approval/approved/failed")
        print("   - test_results: JSON test results")
        print("   - ai_analysis: AI analysis results")
        print("   - created_at: Creation timestamp")
        print("   - updated_at: Last update timestamp")
        print("   - approved_at: Approval timestamp")
        
    except Exception as e:
        print(f"❌ Error creating Terra extensions table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(create_terra_extensions_table())
        if success:
            print("\n🎉 Terra extensions table migration completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 