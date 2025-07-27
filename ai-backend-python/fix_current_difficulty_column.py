#!/usr/bin/env python3
"""
Fix Current Difficulty Column Migration
======================================

This script adds the missing current_difficulty column to the agent_metrics table
to resolve the database error that's causing system failures.
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


async def fix_current_difficulty_column():
    """Add current_difficulty column to agent_metrics table"""
    
    try:
        print("🔧 Adding current_difficulty column to agent_metrics table...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if current_difficulty column already exists
        column_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name = 'current_difficulty'
            );
        """)
        
        if not column_exists:
            # Add current_difficulty column
            await conn.execute("""
                ALTER TABLE agent_metrics 
                ADD COLUMN current_difficulty VARCHAR(50) DEFAULT 'basic'
            """)
            
            print("✅ current_difficulty column added successfully")
        else:
            print("ℹ️  current_difficulty column already exists")
        
        # Update existing records to have a default current_difficulty value
        await conn.execute("""
            UPDATE agent_metrics 
            SET current_difficulty = 'basic'
            WHERE current_difficulty IS NULL
        """)
        
        # Verify the column was added correctly
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'agent_metrics' 
            AND column_name = 'current_difficulty'
        """)
        
        print("📋 current_difficulty column details:")
        for column in columns:
            print(f"  Column: {column['column_name']}")
            print(f"  Type: {column['data_type']}")
            print(f"  Nullable: {column['is_nullable']}")
            print(f"  Default: {column['column_default']}")
        
        # Test query to ensure the column works
        test_result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM agent_metrics 
            WHERE current_difficulty = 'basic'
        """)
        
        print(f"✅ Test query successful: {test_result} records with current_difficulty = 'basic'")
        
        # Check all agent_metrics records
        all_metrics = await conn.fetch("""
            SELECT agent_id, agent_type, current_difficulty, level, xp
            FROM agent_metrics
            ORDER BY agent_id
        """)
        
        print("📊 Current agent_metrics records:")
        for metric in all_metrics:
            print(f"  {metric['agent_id']} ({metric['agent_type']}): difficulty={metric['current_difficulty']}, level={metric['level']}, xp={metric['xp']}")
        
        await conn.close()
        print("✅ current_difficulty column fix completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing current_difficulty column: {str(e)}")
        return False


async def verify_fix():
    """Verify that the fix resolved the database error"""
    
    try:
        print("🔍 Verifying the fix...")
        
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Test the exact query that was failing
        test_query = """
            SELECT agent_metrics.id, agent_metrics.agent_id, agent_metrics.agent_type, 
                   agent_metrics.learning_score, agent_metrics.success_rate, agent_metrics.failure_rate, 
                   agent_metrics.total_learning_cycles, agent_metrics.last_learning_cycle, 
                   agent_metrics.last_success, agent_metrics.last_failure, agent_metrics.learning_patterns, 
                   agent_metrics.improvement_suggestions, agent_metrics.status, agent_metrics.is_active, 
                   agent_metrics.priority, agent_metrics.capabilities, agent_metrics.config, 
                   agent_metrics.total_tests_given, agent_metrics.total_tests_passed, agent_metrics.total_tests_failed, 
                   agent_metrics.custody_level, agent_metrics.custody_xp, agent_metrics.consecutive_successes, 
                   agent_metrics.consecutive_failures, agent_metrics.last_test_date, agent_metrics.test_history, 
                   agent_metrics.current_difficulty, agent_metrics.xp, agent_metrics.level, agent_metrics.prestige, 
                   agent_metrics.created_at, agent_metrics.updated_at 
            FROM agent_metrics 
            WHERE agent_metrics.agent_type = $1
        """
        
        # Test with 'conquest' agent type (from the error log)
        result = await conn.execute(test_query, 'conquest')
        print("✅ The failing query now works successfully!")
        
        # Test with 'imperium' agent type (also from the error log)
        result = await conn.execute(test_query, 'imperium')
        print("✅ Query works for imperium agent type as well!")
        
        await conn.close()
        print("✅ Verification completed - the fix is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


async def main():
    """Main function"""
    print("🚀 Starting current_difficulty column fix...")
    
    # Fix the column
    success = await fix_current_difficulty_column()
    
    if success:
        # Verify the fix
        await verify_fix()
        print("🎉 current_difficulty column fix completed successfully!")
        print("📝 The database error should now be resolved.")
        print("🔄 You may need to restart your backend services for the changes to take effect.")
    else:
        print("❌ Fix failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main()) 