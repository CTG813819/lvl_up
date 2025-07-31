#!/usr/bin/env python3
"""
Reset Custody XP Levels Script
=============================

This script resets custody XP levels to zero for all AIs in the database.
This ensures the strict leveling system starts fresh.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import asyncpg

async def reset_custody_xp_levels():
    """Reset custody XP levels to zero for all AIs"""
    
    try:
        print("Resetting custody XP levels to zero...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if agent_metrics table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'agent_metrics'
            );
        """)
        
        if not table_exists:
            print("Agent metrics table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Reset custody XP for all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check current custody metrics
            current_metrics = await conn.fetchrow("""
                SELECT agent_id, agent_type, xp, level, test_history
                FROM agent_metrics 
                WHERE agent_type = $1
            """, ai_type)
            
            if current_metrics:
                print(f"Current {ai_type}: XP={current_metrics['xp']}, Level={current_metrics['level']}")
                
                # Reset custody XP and level
                await conn.execute("""
                    UPDATE agent_metrics 
                    SET xp = 0, level = 1, test_history = '[]'::jsonb
                    WHERE agent_type = $1
                """, ai_type)
                
                print(f"✅ Reset {ai_type}: XP=0, Level=1")
            else:
                print(f"⚠️ No metrics found for {ai_type}")
        
        # Also reset custody metrics in the custody protocol service file
        custody_metrics_file = "/home/ubuntu/ai-backend-python/custody_metrics.json"
        if os.path.exists(custody_metrics_file):
            import json
            with open(custody_metrics_file, 'w') as f:
                reset_metrics = {
                    "imperium": {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": "basic",
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    },
                    "guardian": {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": "basic",
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    },
                    "sandbox": {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": "basic",
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    },
                    "conquest": {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": "basic",
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    }
                }
                json.dump(reset_metrics, f, indent=2)
            print(f"✅ Reset custody metrics file: {custody_metrics_file}")
        
        await conn.close()
        print("Custody XP reset completed successfully")
        return True
        
    except Exception as e:
        print(f"Error resetting custody XP: {str(e)}")
        return False

async def verify_custody_token_system():
    """Verify that the custody system adheres to the token system"""
    
    try:
        print("\nVerifying custody token system compliance...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if token usage tracking exists
        token_table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'token_usage'
            );
        """)
        
        if token_table_exists:
            print("✅ Token usage tracking table exists")
            
            # Check recent token usage
            recent_usage = await conn.fetch("""
                SELECT ai_type, total_tokens, last_used, created_at
                FROM token_usage 
                ORDER BY last_used DESC 
                LIMIT 10
            """)
            
            print(f"Recent token usage records: {len(recent_usage)}")
            for usage in recent_usage:
                print(f"  {usage['ai_type']}: {usage['total_tokens']} tokens, last used: {usage['last_used']}")
        else:
            print("⚠️ Token usage tracking table does not exist")
            print("Creating token usage tracking table...")
            
            # Create token usage table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    ai_type VARCHAR(50) NOT NULL,
                    total_tokens INTEGER DEFAULT 0,
                    tokens_used_today INTEGER DEFAULT 0,
                    daily_limit INTEGER DEFAULT 1000,
                    last_used TIMESTAMP DEFAULT NOW(),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Initialize token usage for all AIs
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            for ai_type in ai_types:
                await conn.execute("""
                    INSERT INTO token_usage (ai_type, total_tokens, tokens_used_today, daily_limit)
                    VALUES ($1, 0, 0, 1000)
                    ON CONFLICT (ai_type) DO NOTHING
                """, ai_type)
            
            print("✅ Token usage tracking table created and initialized")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Error verifying token system: {str(e)}")
        return False

async def main():
    """Main function"""
    print("Starting custody XP reset and token system verification...")
    
    # Reset custody XP levels
    success = await reset_custody_xp_levels()
    
    if success:
        # Verify token system
        await verify_custody_token_system()
        
        print("\n🎯 Custody XP reset and token system verification completed!")
        print("All AIs now start with XP=0, Level=1")
        print("Token usage tracking is properly configured")
    else:
        print("\n❌ Custody XP reset failed")

if __name__ == "__main__":
    asyncio.run(main()) 