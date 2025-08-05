#!/usr/bin/env python3
"""
Add custody test count fields to AgentMetrics table
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, get_session
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def add_custody_test_fields():
    """Add custody test count fields to AgentMetrics table"""
    try:
        print("🔧 Adding custody test count fields to AgentMetrics table...")
        
        # Initialize database
        await init_database()
        
        async with get_session() as session:
            # Check if custody test fields already exist
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name IN ('total_tests_given', 'total_tests_passed', 'total_tests_failed', 'custody_level', 'custody_xp')
                ORDER BY column_name
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            print(f"Existing custody columns: {existing_columns}")
            
            # Add missing columns
            columns_to_add = [
                ('total_tests_given', 'INTEGER DEFAULT 0'),
                ('total_tests_passed', 'INTEGER DEFAULT 0'),
                ('total_tests_failed', 'INTEGER DEFAULT 0'),
                ('custody_level', 'INTEGER DEFAULT 1'),
                ('custody_xp', 'INTEGER DEFAULT 0'),
                ('consecutive_successes', 'INTEGER DEFAULT 0'),
                ('consecutive_failures', 'INTEGER DEFAULT 0'),
                ('last_test_date', 'TIMESTAMP'),
                ('test_history', 'JSONB DEFAULT \'[]\'')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"Adding column: {column_name}")
                    await session.execute(text(f"""
                        ALTER TABLE agent_metrics 
                        ADD COLUMN {column_name} {column_type}
                    """))
                else:
                    print(f"Column {column_name} already exists")
            
            await session.commit()
            
            # Verify the columns were added
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name IN ('total_tests_given', 'total_tests_passed', 'total_tests_failed', 'custody_level', 'custody_xp', 'consecutive_successes', 'consecutive_failures', 'last_test_date', 'test_history')
                ORDER BY column_name
            """))
            final_columns = [row[0] for row in result.fetchall()]
            
            print(f"✅ Final custody columns: {final_columns}")
            
            # Update existing records with default values
            print("📝 Updating existing records with default custody values...")
            
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            for ai_type in ai_types:
                # Check if record exists
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM agent_metrics 
                    WHERE agent_id = :ai_type OR agent_type = :ai_type
                """), {"ai_type": ai_type})
                exists = result.scalar()
                
                if exists:
                    # Update existing record
                    await session.execute(text("""
                        UPDATE agent_metrics 
                        SET 
                            total_tests_given = COALESCE(total_tests_given, 0),
                            total_tests_passed = COALESCE(total_tests_passed, 0),
                            total_tests_failed = COALESCE(total_tests_failed, 0),
                            custody_level = COALESCE(custody_level, 1),
                            custody_xp = COALESCE(custody_xp, 0),
                            consecutive_successes = COALESCE(consecutive_successes, 0),
                            consecutive_failures = COALESCE(consecutive_failures, 0),
                            test_history = COALESCE(test_history, '[]'),
                            updated_at = NOW()
                        WHERE agent_id = :ai_type OR agent_type = :ai_type
                    """), {"ai_type": ai_type})
                    print(f"Updated custody fields for {ai_type}")
                else:
                    # Create new record
                    await session.execute(text("""
                        INSERT INTO agent_metrics (
                            id, agent_id, agent_type, learning_score, success_rate, 
                            failure_rate, total_learning_cycles, xp, level, prestige,
                            total_tests_given, total_tests_passed, total_tests_failed,
                            custody_level, custody_xp, consecutive_successes, consecutive_failures,
                            test_history, status, is_active, priority, created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), :ai_type, :ai_type, 0.0, 0.0, 0.0, 0, 0, 1, 0,
                            0, 0, 0, 1, 0, 0, 0, '[]', 'idle', true, 'medium', NOW(), NOW()
                        )
                    """), {"ai_type": ai_type})
                    print(f"Created new record for {ai_type}")
            
            await session.commit()
            
            # Verify the updates
            print("🔍 Verifying custody test fields...")
            result = await session.execute(text("""
                SELECT agent_id, agent_type, total_tests_given, total_tests_passed, 
                       total_tests_failed, custody_level, custody_xp
                FROM agent_metrics 
                WHERE agent_type IN ('imperium', 'guardian', 'sandbox', 'conquest')
                ORDER BY agent_type
            """))
            
            for row in result.fetchall():
                print(f"  {row.agent_type}: Tests={row.total_tests_given}, Passed={row.total_tests_passed}, Failed={row.total_tests_failed}, Level={row.custody_level}, XP={row.custody_xp}")
            
            print("✅ Custody test fields added successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error adding custody test fields: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(add_custody_test_fields())
    sys.exit(0 if success else 1) 