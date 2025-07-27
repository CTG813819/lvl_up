#!/usr/bin/env python3
"""
Complete Custody Protocol Fix
=============================

This script completely fixes the custody protocol service by:
1. Restoring the file to a working state
2. Adding the custody test fields to the AgentMetrics model
3. Properly implementing the persistence method
"""

import os
import re

def restore_custody_protocol_service():
    """Restore the custody protocol service to a working state"""
    try:
        print("🔧 Restoring custody protocol service...")
        
        # First, let's backup the current file
        service_path = "app/services/custody_protocol_service.py"
        backup_path = "app/services/custody_protocol_service.py.backup"
        
        if os.path.exists(service_path):
            os.system(f"cp {service_path} {backup_path}")
            print(f"✅ Created backup: {backup_path}")
        
        # Read the original file content (before our changes)
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Find and remove the problematic duplicate method
        # Look for the _persist_custody_metrics_to_database method
        method_pattern = r'async def _persist_custody_metrics_to_database\(self, ai_type: str, metrics: Dict\):'
        matches = list(re.finditer(method_pattern, content))
        
        if len(matches) > 1:
            print(f"Found {len(matches)} duplicate method definitions")
            
            # Find the first occurrence and keep it, remove the second
            first_match = matches[0]
            second_match = matches[1]
            
            # Get the content before the first method
            before_first = content[:first_match.start()]
            
            # Find the end of the first method
            first_method_end = second_match.start()
            
            # Find the end of the second method by looking for the next method or class
            after_second_start = second_match.start()
            next_method_match = re.search(r'\n    async def ', content[after_second_start:])
            if next_method_match:
                after_second_end = after_second_start + next_method_match.start()
            else:
                # If no next method, go to end of file
                after_second_end = len(content)
            
            after_second = content[after_second_end:]
            
            # Reconstruct the file content without the duplicate
            new_content = before_first + content[first_match.start():first_method_end] + after_second
            
            # Write the fixed file
            with open(service_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Removed duplicate method definition")
        
        # Now fix the _persist_custody_metrics_to_database method
        fix_persistence_method(service_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring custody protocol service: {str(e)}")
        return False

def fix_persistence_method(service_path):
    """Fix the _persist_custody_metrics_to_database method"""
    try:
        print("🔧 Fixing persistence method...")
        
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Find the _persist_custody_metrics_to_database method
        method_pattern = r'async def _persist_custody_metrics_to_database\(self, ai_type: str, metrics: Dict\):'
        match = re.search(method_pattern, content)
        
        if match:
            method_start = match.start()
            
            # Find the end of the method
            next_method_match = re.search(r'\n    async def ', content[method_start + 1:])
            if next_method_match:
                method_end = method_start + 1 + next_method_match.start()
            else:
                method_end = len(content)
            
            # Create the correct method implementation
            correct_method = '''    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):
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
            logger.error(f"Error persisting custody metrics to database: {str(e)}")
'''
            
            # Replace the method
            new_content = content[:method_start] + correct_method + content[method_end:]
            
            # Write the fixed file
            with open(service_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Fixed persistence method")
        
    except Exception as e:
        print(f"❌ Error fixing persistence method: {str(e)}")

def update_agent_metrics_model():
    """Update the AgentMetrics model to include custody test fields"""
    try:
        print("🔧 Updating AgentMetrics model...")
        
        model_path = "app/models/sql_models.py"
        with open(model_path, 'r') as f:
            content = f.read()
        
        # Check if custody fields already exist
        if 'total_tests_given' in content:
            print("✅ Custody fields already exist in AgentMetrics model")
            return True
        
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
        result = os.system(command)
        
        if result == 0:
            print("✅ Database migration applied successfully")
            return True
        else:
            print("❌ Database migration failed")
            return False
        
    except Exception as e:
        print(f"❌ Error applying database migration: {str(e)}")
        return False

def test_syntax():
    """Test that the file has correct syntax"""
    try:
        print("🧪 Testing syntax...")
        
        result = os.system("python -m py_compile app/services/custody_protocol_service.py")
        
        if result == 0:
            print("✅ Syntax check passed")
            return True
        else:
            print("❌ Syntax check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing syntax: {str(e)}")
        return False

def main():
    """Main function to fix the custody protocol database issue"""
    
    print("🚀 Starting complete custody protocol fix...")
    
    # Step 1: Restore custody protocol service
    if not restore_custody_protocol_service():
        print("❌ Failed to restore custody protocol service")
        return
    
    # Step 2: Update AgentMetrics model
    if not update_agent_metrics_model():
        print("❌ Failed to update AgentMetrics model")
        return
    
    # Step 3: Create database migration
    if not create_database_migration():
        print("❌ Failed to create database migration")
        return
    
    # Step 4: Test syntax
    if not test_syntax():
        print("❌ Syntax test failed")
        return
    
    # Step 5: Apply database migration
    if not apply_database_migration():
        print("❌ Failed to apply database migration")
        return
    
    print("✅ Complete custody protocol fix completed successfully!")
    print("\n📋 Summary of changes:")
    print("1. Restored custody protocol service to working state")
    print("2. Updated AgentMetrics model to include custody test fields")
    print("3. Created and applied database migration")
    print("4. Verified syntax is correct")
    print("\n🎯 The custody protocol should now properly track and persist test results!")

if __name__ == "__main__":
    main() 