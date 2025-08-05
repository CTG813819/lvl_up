#!/usr/bin/env python3
"""
Fix Custody Protocol Database Fields
====================================

This script fixes the issue where the Custody Protocol service is trying to set
custody test fields that don't exist in the AgentMetrics database model.

The problem is that the CustodyProtocolService is using setattr() to set fields
like 'total_tests_given', 'total_tests_passed', 'total_tests_failed', 'custody_xp',
'custody_level', etc., but these fields don't exist in the AgentMetrics model.

This script:
1. Creates a migration to add the missing custody test fields
2. Updates the AgentMetrics model to include these fields
3. Fixes the CustodyProtocolService to properly persist data
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog
from sqlalchemy import text
from alembic import op
import sqlalchemy as sa

logger = structlog.get_logger()

async def create_custody_fields_migration():
    """Create a migration to add custody test fields to agent_metrics table"""
    
    try:
        print("🔧 Creating migration for custody test fields...")
        
        migration_content = '''from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250115_add_custody_test_fields'
down_revision = '20250715_add_agentmetrics_leveling'
branch_labels = None
depends_on = None

def upgrade():
    """Add custody test fields to agent_metrics table"""
    
    # Add custody test tracking fields
    op.add_column('agent_metrics', sa.Column('total_tests_given', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('total_tests_passed', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('total_tests_failed', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('custody_level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('agent_metrics', sa.Column('custody_xp', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('consecutive_successes', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('consecutive_failures', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('last_test_date', sa.DateTime(), nullable=True))
    op.add_column('agent_metrics', sa.Column('test_history', sa.JSON(), nullable=True, server_default='[]'))
    op.add_column('agent_metrics', sa.Column('current_difficulty', sa.String(50), nullable=True, server_default='basic'))
    
    # Add indexes for better performance
    op.create_index('idx_agent_metrics_custody_level', 'agent_metrics', ['custody_level'])
    op.create_index('idx_agent_metrics_total_tests', 'agent_metrics', ['total_tests_given'])
    op.create_index('idx_agent_metrics_last_test_date', 'agent_metrics', ['last_test_date'])

def downgrade():
    """Remove custody test fields from agent_metrics table"""
    
    # Drop indexes
    op.drop_index('idx_agent_metrics_custody_level')
    op.drop_index('idx_agent_metrics_total_tests')
    op.drop_index('idx_agent_metrics_last_test_date')
    
    # Drop columns
    op.drop_column('agent_metrics', 'current_difficulty')
    op.drop_column('agent_metrics', 'test_history')
    op.drop_column('agent_metrics', 'last_test_date')
    op.drop_column('agent_metrics', 'consecutive_failures')
    op.drop_column('agent_metrics', 'consecutive_successes')
    op.drop_column('agent_metrics', 'custody_xp')
    op.drop_column('agent_metrics', 'custody_level')
    op.drop_column('agent_metrics', 'total_tests_failed')
    op.drop_column('agent_metrics', 'total_tests_passed')
    op.drop_column('agent_metrics', 'total_tests_given')
'''
        
        # Write migration file
        migration_path = "app/migrations/versions/20250115_add_custody_test_fields.py"
        with open(migration_path, 'w') as f:
            f.write(migration_content)
        
        print(f"✅ Created migration file: {migration_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating migration: {str(e)}")
        return False

async def update_agent_metrics_model():
    """Update the AgentMetrics model to include custody test fields"""
    
    try:
        print("🔧 Updating AgentMetrics model...")
        
        # Read the current model file
        model_path = "app/models/sql_models.py"
        with open(model_path, 'r') as f:
            content = f.read()
        
        # Find the AgentMetrics class
        agent_metrics_start = content.find("class AgentMetrics(Base):")
        if agent_metrics_start == -1:
            print("❌ Could not find AgentMetrics class")
            return False
        
        # Find the end of the AgentMetrics class
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

async def fix_custody_protocol_service():
    """Fix the CustodyProtocolService to properly persist custody metrics"""
    
    try:
        print("🔧 Fixing CustodyProtocolService...")
        
        # Read the current service file
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

async def apply_database_migration():
    """Apply the database migration to add custody test fields"""
    
    try:
        print("🔧 Applying database migration...")
        
        # Get database URL from environment or config
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/lvl_up')
        
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        # Add the custody test fields
        await conn.execute('''
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
            ADD COLUMN IF NOT EXISTS current_difficulty VARCHAR(50) DEFAULT 'basic'
        ''')
        
        # Create indexes
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_metrics_custody_level ON agent_metrics(custody_level);
            CREATE INDEX IF NOT EXISTS idx_agent_metrics_total_tests ON agent_metrics(total_tests_given);
            CREATE INDEX IF NOT EXISTS idx_agent_metrics_last_test_date ON agent_metrics(last_test_date);
        ''')
        
        await conn.close()
        print("✅ Database migration applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error applying database migration: {str(e)}")
        return False

async def test_custody_protocol_fix():
    """Test that the custody protocol fix is working"""
    
    try:
        print("🧪 Testing custody protocol fix...")
        
        # Import the fixed service
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Initialize the service
        custody_service = await CustodyProtocolService.initialize()
        
        # Test administering a custody test
        result = await custody_service.administer_custody_test("imperium")
        
        print(f"✅ Custody test result: {json.dumps(result, indent=2)}")
        
        # Check if metrics were persisted
        analytics = await custody_service.get_custody_analytics()
        imperium_metrics = analytics.get("ai_specific_metrics", {}).get("imperium", {})
        
        print(f"✅ Imperium metrics after test:")
        print(f"   Total tests given: {imperium_metrics.get('total_tests_given', 0)}")
        print(f"   Total tests passed: {imperium_metrics.get('total_tests_passed', 0)}")
        print(f"   Total tests failed: {imperium_metrics.get('total_tests_failed', 0)}")
        print(f"   Custody XP: {imperium_metrics.get('custody_xp', 0)}")
        print(f"   Custody level: {imperium_metrics.get('custody_level', 1)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing custody protocol fix: {str(e)}")
        return False

async def main():
    """Main function to fix the custody protocol database issue"""
    
    print("🚀 Starting custody protocol database fix...")
    
    # Step 1: Create migration file
    if not await create_custody_fields_migration():
        print("❌ Failed to create migration")
        return
    
    # Step 2: Update AgentMetrics model
    if not await update_agent_metrics_model():
        print("❌ Failed to update AgentMetrics model")
        return
    
    # Step 3: Fix CustodyProtocolService
    if not await fix_custody_protocol_service():
        print("❌ Failed to fix CustodyProtocolService")
        return
    
    # Step 4: Apply database migration
    if not await apply_database_migration():
        print("❌ Failed to apply database migration")
        return
    
    # Step 5: Test the fix
    if not await test_custody_protocol_fix():
        print("❌ Failed to test custody protocol fix")
        return
    
    print("✅ Custody protocol database fix completed successfully!")
    print("\n📋 Summary of changes:")
    print("1. Created migration to add custody test fields to agent_metrics table")
    print("2. Updated AgentMetrics model to include custody test fields")
    print("3. Fixed CustodyProtocolService to properly persist data")
    print("4. Applied database migration")
    print("5. Tested the fix with a sample custody test")
    print("\n🎯 The custody protocol should now properly track and persist test results!")

if __name__ == "__main__":
    asyncio.run(main()) 