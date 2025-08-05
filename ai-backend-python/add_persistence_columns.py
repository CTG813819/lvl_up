#!/usr/bin/env python3
"""
Add Persistence Columns Migration
================================

This script adds the missing persistence columns to the agent_metrics table
to support enhanced metrics persistence.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()


async def add_persistence_columns():
    """Add persistence columns to agent_metrics table"""
    
    try:
        print("Adding persistence columns to agent_metrics table...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if columns already exist
        columns_exist = await conn.fetchval("""
            SELECT EXISTS (
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name = 'last_persistence_check'
            );
        """)
        
        if not columns_exist:
            # Add persistence columns
            await conn.execute("""
                ALTER TABLE agent_metrics 
                ADD COLUMN IF NOT EXISTS last_persistence_check TIMESTAMP,
                ADD COLUMN IF NOT EXISTS persistence_version VARCHAR(10) DEFAULT '1.0',
                ADD COLUMN IF NOT EXISTS backup_created BOOLEAN DEFAULT false
            """)
            
            # Update existing records
            await conn.execute("""
                UPDATE agent_metrics 
                SET 
                    last_persistence_check = NOW(),
                    persistence_version = '2.0',
                    backup_created = true
                WHERE last_persistence_check IS NULL
            """)
            
            print("Persistence columns added successfully")
        else:
            print("Persistence columns already exist")
        
        # Verify the columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'agent_metrics' 
            AND column_name IN ('last_persistence_check', 'persistence_version', 'backup_created')
            ORDER BY column_name
        """)
        
        print("Persistence columns in agent_metrics table:")
        for column in columns:
            print(f"  {column['column_name']}: {column['data_type']} (nullable: {column['is_nullable']})")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding persistence columns: {str(e)}")
        return False


async def create_backup_table():
    """Create backup table for additional persistence"""
    
    try:
        print("Creating backup table...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if backup table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'agent_metrics_backup'
            );
        """)
        
        if not table_exists:
            # Create backup table
            await conn.execute("""
                CREATE TABLE agent_metrics_backup (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    agent_id VARCHAR(100) NOT NULL,
                    learning_score FLOAT DEFAULT 0.0,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    prestige INTEGER DEFAULT 0,
                    total_learning_cycles INTEGER DEFAULT 0,
                    backup_timestamp TIMESTAMP DEFAULT NOW(),
                    backup_reason VARCHAR(100) DEFAULT 'scheduled'
                )
            """)
            
            print("Backup table created successfully")
        else:
            print("Backup table already exists")
        
        # Create initial backup
        await conn.execute("""
            INSERT INTO agent_metrics_backup (
                agent_id, learning_score, level, xp, prestige, total_learning_cycles, backup_reason
            )
            SELECT agent_id, learning_score, level, xp, prestige, total_learning_cycles, 'migration_backup'
            FROM agent_metrics
        """)
        
        # Check backup count
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics_backup")
        print(f"Backup records created: {backup_count}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating backup table: {str(e)}")
        return False


async def main():
    """Main function"""
    print("Starting persistence columns migration...")
    print("=" * 60)
    
    # Add persistence columns
    success1 = await add_persistence_columns()
    
    # Create backup table
    success2 = await create_backup_table()
    
    if success1 and success2:
        print("\nMigration completed successfully!")
        print("Persistence columns added to agent_metrics table")
        print("Backup table created with initial backup")
        print("\nYou can now run the enhanced monitoring script:")
        print("python enhanced_monitor_system.py")
    else:
        print("\nMigration failed. Please check the errors above.")
    
    return success1 and success2


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        sys.exit(1) 