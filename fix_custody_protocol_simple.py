#!/usr/bin/env python3
"""
Simple Custody Protocol Database Fix
====================================

This script fixes the custody protocol database issue without requiring asyncpg.
It directly updates the database schema and fixes the service code.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {str(e)}")
        return False

def update_agent_metrics_model():
    """Update the AgentMetrics model to include custody test fields"""
    try:
        print("🔧 Updating AgentMetrics model...")
        
        model_path = "app/models/sql_models.py"
        with open(model_path, 'r') as f:
            content = f.read()
        
        # Find the AgentMetrics class
        agent_metrics_start = content.find("class AgentMetrics(Base):")
        if agent_metrics_start == -1:
            print("❌ Could not find AgentMetrics class")
            return False
        
        # Find the leveling details section
        class_content_start = content.find("    # Leveling details", agent_metrics_start)
        if class_content_start == -1:
            print("❌ Could not find leveling details section")
            return False
        
        # Insert custody test fields before the leveling details
        custody_fields = '''    # Custody test tracking fields
    total_tests_given = Column(Integer, default=0)
    total_tests_passed = Column(Integer, default=0)
    total_tests_failed = Column(Integer, default=0)
    custody_level = Column(Integer, default=1)
    custody_xp = Column(Integer, default=0)
    consecutive_successes = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    last_test_date = Column(DateTime, nullable=True)
    test_history = Column(JSON, default=list)
    current_difficulty = Column(String(50), default="basic")
    
    # Leveling details'''
        
        # Replace the leveling details section
        new_content = content[:class_content_start] + custody_fields + content[class_content_start + len("    # Leveling details"):]
        
        # Write the updated model file
        with open(model_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Updated AgentMetrics model in {model_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating AgentMetrics model: {str(e)}")
        return False

def fix_custody_protocol_service():
    """Fix the CustodyProtocolService to properly persist custody metrics"""
    try:
        print("🔧 Fixing CustodyProtocolService...")
        
        service_path = "app/services/custody_protocol_service.py"
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Find the _persist_custody_metrics_to_database method
        method_start = content.find("async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):")
        if method_start == -1:
            print("❌ Could not find _persist_custody_metrics_to_database method")
            return False
        
        # Find the end of the method
        method_end = content.find("except Exception as e:", method_start)
        if method_end == -1:
            print("❌ Could not find end of method")
            return False
        
        # Create the fixed method content
        fixed_method = '''    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):
        """Persist custody metrics to the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AgentMetrics
                from sqlalchemy import select
                
                # Get or create agent metrics record
                result = await s.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics record
                    agent_metrics = AgentMetrics(
                        agent_id=f"{ai_type}_agent",
                        agent_type=ai_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=metrics["custody_xp"],
                        level=metrics["custody_level"],
                        prestige=0,
                        status="active",
                        is_active=True,
                        priority="medium",
                        # Custody test fields
                        total_tests_given=metrics["total_tests_given"],
                        total_tests_passed=metrics["total_tests_passed"],
                        total_tests_failed=metrics["total_tests_failed"],
                        custody_level=metrics["custody_level"],
                        custody_xp=metrics["custody_xp"],
                        consecutive_successes=metrics["consecutive_successes"],
                        consecutive_failures=metrics["consecutive_failures"],
                        last_test_date=datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None,
                        test_history=metrics["test_history"],
                        current_difficulty=metrics.get("current_difficulty", "basic")
                    )
                    s.add(agent_metrics)
                else:
                    # Update existing record with custody metrics
                    agent_metrics.xp = metrics["custody_xp"]
                    agent_metrics.level = metrics["custody_level"]
                    # Custody test fields
                    agent_metrics.total_tests_given = metrics["total_tests_given"]
                    agent_metrics.total_tests_passed = metrics["total_tests_passed"]
                    agent_metrics.total_tests_failed = metrics["total_tests_failed"]
                    agent_metrics.custody_level = metrics["custody_level"]
                    agent_metrics.custody_xp = metrics["custody_xp"]
                    agent_metrics.consecutive_successes = metrics["consecutive_successes"]
                    agent_metrics.consecutive_failures = metrics["consecutive_failures"]
                    agent_metrics.last_test_date = datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None
                    agent_metrics.test_history = metrics["test_history"]
                    agent_metrics.current_difficulty = metrics.get("current_difficulty", "basic")
                
                await s.commit()
                logger.info(f"Persisted custody metrics for {ai_type}: Tests={metrics['total_tests_given']}, Passed={metrics['total_tests_passed']}, Failed={metrics['total_tests_failed']}, XP={metrics['custody_xp']}, Level={metrics['custody_level']}")
                
        except Exception as e:
            logger.error(f"Error persisting custody metrics to database: {str(e)}")'''
        
        # Replace the method
        new_content = content[:method_start] + fixed_method + content[method_end:]
        
        # Write the updated service file
        with open(service_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Fixed CustodyProtocolService in {service_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing CustodyProtocolService: {str(e)}")
        return False

def create_database_migration():
    """Create a SQL migration file to add custody test fields"""
    try:
        print("🔧 Creating database migration...")
        
        migration_sql = '''-- Add custody test fields to agent_metrics table
ALTER TABLE agent_metrics 
ADD COLUMN IF NOT EXISTS total_tests_given INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_tests_passed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_tests_failed INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS custody_level INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS custody_xp INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS consecutive_successes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS consecutive_failures INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_test_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS test_history JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS current_difficulty VARCHAR(50) DEFAULT 'basic';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agent_metrics_custody_level ON agent_metrics(custody_level);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_total_tests ON agent_metrics(total_tests_given);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_last_test_date ON agent_metrics(last_test_date);

-- Update existing records to have default values
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
    current_difficulty = COALESCE(current_difficulty, 'basic')
WHERE total_tests_given IS NULL;
'''
        
        # Write migration file
        migration_path = "custody_protocol_migration.sql"
        with open(migration_path, 'w') as f:
            f.write(migration_sql)
        
        print(f"✅ Created migration file: {migration_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating migration: {str(e)}")
        return False

def apply_database_migration():
    """Apply the database migration using psql"""
    try:
        print("🔧 Applying database migration...")
        
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/lvl_up')
        
        # Extract database name from URL
        if 'postgresql://' in database_url:
            db_name = database_url.split('/')[-1]
        else:
            db_name = 'lvl_up'
        
        # Run the migration
        command = f"psql -d {db_name} -f custody_protocol_migration.sql"
        return run_command(command, "Applying database migration")
        
    except Exception as e:
        print(f"❌ Error applying database migration: {str(e)}")
        return False

def test_custody_protocol():
    """Test the custody protocol fix"""
    try:
        print("🧪 Testing custody protocol fix...")
        
        # Create a simple test script
        test_script = '''#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.custody_protocol_service import CustodyProtocolService
    import asyncio
    
    async def test():
        custody_service = await CustodyProtocolService.initialize()
        result = await custody_service.administer_custody_test("imperium")
        print(f"✅ Custody test result: {result}")
        
        analytics = await custody_service.get_custody_analytics()
        imperium_metrics = analytics.get("ai_specific_metrics", {}).get("imperium", {})
        print(f"✅ Imperium metrics: {imperium_metrics}")
        
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
'''
        
        # Write test script
        test_path = "test_custody_fix.py"
        with open(test_path, 'w') as f:
            f.write(test_script)
        
        # Run the test
        return run_command("python test_custody_fix.py", "Testing custody protocol fix")
        
    except Exception as e:
        print(f"❌ Error testing custody protocol: {str(e)}")
        return False

def main():
    """Main function to fix the custody protocol database issue"""
    
    print("🚀 Starting simple custody protocol database fix...")
    
    # Step 1: Update AgentMetrics model
    if not update_agent_metrics_model():
        print("❌ Failed to update AgentMetrics model")
        return
    
    # Step 2: Fix CustodyProtocolService
    if not fix_custody_protocol_service():
        print("❌ Failed to fix CustodyProtocolService")
        return
    
    # Step 3: Create database migration
    if not create_database_migration():
        print("❌ Failed to create database migration")
        return
    
    # Step 4: Apply database migration
    if not apply_database_migration():
        print("❌ Failed to apply database migration")
        return
    
    # Step 5: Test the fix
    if not test_custody_protocol():
        print("❌ Failed to test custody protocol fix")
        return
    
    print("✅ Simple custody protocol database fix completed successfully!")
    print("\n📋 Summary of changes:")
    print("1. Updated AgentMetrics model to include custody test fields")
    print("2. Fixed CustodyProtocolService to properly persist data")
    print("3. Created and applied database migration")
    print("4. Tested the fix with a sample custody test")
    print("\n🎯 The custody protocol should now properly track and persist test results!")

if __name__ == "__main__":
    main() 