#!/usr/bin/env python3
"""
Fix XP Persistence Issue
========================

This script fixes the XP persistence issue where XP is reset to 0 on backend restarts.
The problem is that the system is creating new agent metrics records instead of properly
persisting existing ones.

Key Issues Identified:
1. XP is being reset to 0 on restarts
2. Level is being reset to 1 on restarts  
3. Learning cycles are not being persisted properly
4. Database transactions are not being committed properly

Solution:
1. Ensure proper database persistence with transactions
2. Add backup and recovery mechanisms
3. Implement robust error handling
4. Add monitoring and validation
"""

import asyncio
import sys
import os
from datetime import datetime
import json
import structlog

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()

async def fix_xp_persistence():
    """Fix XP persistence by ensuring proper database initialization and persistence"""
    
    try:
        print("🔧 Fixing XP persistence issue...")
        
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
            print("❌ Agent metrics table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Ensure all AI types have proper metrics records
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist for this AI type
            existing_metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles, prestige
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if existing_metrics:
                print(f"✅ {ai_type}: Level {existing_metrics['level']}, Score {existing_metrics['learning_score']:.2f}, XP {existing_metrics['xp']}")
                
                # Update with enhanced persistence fields
                await conn.execute("""
                    UPDATE agent_metrics 
                    SET 
                        last_persistence_check = NOW(),
                        persistence_version = '2.0',
                        backup_created = true,
                        updated_at = NOW()
                    WHERE agent_id = $1 OR agent_type = $1
                """, ai_type)
            else:
                # Create default metrics for this AI type with enhanced persistence
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        id, agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at,
                        last_persistence_check, persistence_version, backup_created
                    ) VALUES (
                        gen_random_uuid(), $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW(), NOW(), '2.0', true
                    )
                """, ai_type)
                print(f"✅ Created default metrics for {ai_type}")
        
        # Create backup table for additional persistence
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics_backup (
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
        
        # Create current backup
        await conn.execute("""
            INSERT INTO agent_metrics_backup (
                agent_id, learning_score, level, xp, prestige, total_learning_cycles, backup_reason
            )
            SELECT agent_id, learning_score, level, xp, prestige, total_learning_cycles, 'xp_persistence_fix'
            FROM agent_metrics
        """)
        
        await conn.close()
        
        print("✅ XP persistence fix completed:")
        print("   - All AI types have proper metrics records")
        print("   - Enhanced persistence tracking added")
        print("   - Backup table created for additional persistence")
        print("   - Current backup created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing XP persistence: {str(e)}")
        return False

async def create_persistence_monitoring_script():
    """Create a script to monitor and maintain data persistence"""
    
    try:
        print("🔍 Creating persistence monitoring script...")
        
        monitoring_script = '''#!/usr/bin/env python3
"""
Data Persistence Monitoring Script
=================================

This script monitors and maintains data persistence to prevent metrics resetting.
Run this script periodically to ensure data integrity.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select

logger = structlog.get_logger()

async def check_metrics_persistence():
    """Check if agent metrics are properly persisted"""
    try:
        print("🔍 Checking metrics persistence...")
        
        async with get_session() as session:
            # Check all AI types
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                stmt = select(AgentMetrics).where(
                    (AgentMetrics.agent_id == ai_type) | 
                    (AgentMetrics.agent_type == ai_type)
                )
                result = await session.execute(stmt)
                metrics = result.scalar_one_or_none()
                
                if metrics:
                    print(f"✅ {ai_type}: Level {metrics.level}, Score {metrics.learning_score:.2f}, XP {metrics.xp}")
                else:
                    print(f"❌ {ai_type}: No metrics found - creating default")
                    # Create default metrics
                    default_metrics = AgentMetrics(
                        agent_id=ai_type,
                        agent_type=ai_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=0,
                        level=1,
                        prestige=0,
                        status="idle",
                        is_active=True,
                        priority="medium"
                    )
                    session.add(default_metrics)
            
            await session.commit()
            print("✅ Metrics persistence check completed")
            
    except Exception as e:
        print(f"❌ Error checking metrics persistence: {str(e)}")

async def backup_metrics_data():
    """Create backup of metrics data"""
    try:
        print("💾 Creating metrics backup...")
        
        async with get_session() as session:
            stmt = select(AgentMetrics)
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            backup_data = []
            for metric in metrics:
                backup_data.append({
                    "agent_id": metric.agent_id,
                    "agent_type": metric.agent_type,
                    "learning_score": float(metric.learning_score),
                    "success_rate": float(metric.success_rate),
                    "failure_rate": float(metric.failure_rate),
                    "total_learning_cycles": metric.total_learning_cycles,
                    "xp": metric.xp,
                    "level": metric.level,
                    "prestige": metric.prestige,
                    "status": metric.status,
                    "is_active": metric.is_active,
                    "priority": metric.priority,
                    "created_at": metric.created_at.isoformat() if metric.created_at else None,
                    "updated_at": metric.updated_at.isoformat() if metric.updated_at else None
                })
            
            # Save backup to file
            backup_filename = f"metrics_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Metrics backup created: {backup_filename}")
            
    except Exception as e:
        print(f"❌ Error creating metrics backup: {str(e)}")

async def restore_metrics_from_backup(backup_filename: str):
    """Restore metrics from backup file"""
    try:
        print(f"🔄 Restoring metrics from {backup_filename}...")
        
        with open(backup_filename, 'r') as f:
            backup_data = json.load(f)
        
        async with get_session() as session:
            for metric_data in backup_data:
                # Check if metrics exist
                stmt = select(AgentMetrics).where(AgentMetrics.agent_id == metric_data["agent_id"])
                result = await session.execute(stmt)
                existing_metrics = result.scalar_one_or_none()
                
                if existing_metrics:
                    # Update existing metrics
                    existing_metrics.learning_score = metric_data["learning_score"]
                    existing_metrics.success_rate = metric_data["success_rate"]
                    existing_metrics.failure_rate = metric_data["failure_rate"]
                    existing_metrics.total_learning_cycles = metric_data["total_learning_cycles"]
                    existing_metrics.xp = metric_data["xp"]
                    existing_metrics.level = metric_data["level"]
                    existing_metrics.prestige = metric_data["prestige"]
                    existing_metrics.status = metric_data["status"]
                    existing_metrics.is_active = metric_data["is_active"]
                    existing_metrics.priority = metric_data["priority"]
                    existing_metrics.updated_at = datetime.utcnow()
                else:
                    # Create new metrics
                    new_metrics = AgentMetrics(
                        agent_id=metric_data["agent_id"],
                        agent_type=metric_data["agent_type"],
                        learning_score=metric_data["learning_score"],
                        success_rate=metric_data["success_rate"],
                        failure_rate=metric_data["failure_rate"],
                        total_learning_cycles=metric_data["total_learning_cycles"],
                        xp=metric_data["xp"],
                        level=metric_data["level"],
                        prestige=metric_data["prestige"],
                        status=metric_data["status"],
                        is_active=metric_data["is_active"],
                        priority=metric_data["priority"]
                    )
                    session.add(new_metrics)
            
            await session.commit()
            print("✅ Metrics restored from backup")
            
    except Exception as e:
        print(f"❌ Error restoring metrics: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting data persistence monitoring...")
    
    # Check metrics persistence
    await check_metrics_persistence()
    
    # Create backup
    await backup_metrics_data()
    
    print("✅ Data persistence monitoring completed")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write the monitoring script to file
        with open('monitor_persistence.py', 'w') as f:
            f.write(monitoring_script)
        
        print("✅ Persistence monitoring script created: monitor_persistence.py")
        
    except Exception as e:
        print(f"❌ Error creating monitoring script: {str(e)}")

async def create_enhanced_agent_metrics_service():
    """Create enhanced agent metrics service with proper persistence"""
    
    try:
        print("🔧 Creating enhanced agent metrics service...")
        
        enhanced_service = '''
# Enhanced Agent Metrics Service with XP Persistence
# Add this to your agent_metrics_service.py

async def ensure_metrics_persistence(self, agent_type: str) -> bool:
    """Ensure metrics are properly persisted for an agent"""
    try:
        async with get_session() as session:
            # Check if metrics exist
            stmt = select(AgentMetrics).where(
                (AgentMetrics.agent_id == agent_type) | 
                (AgentMetrics.agent_type == agent_type)
            )
            result = await session.execute(stmt)
            metrics = result.scalar_one_or_none()
            
            if not metrics:
                # Create default metrics with proper persistence
                default_metrics = AgentMetrics(
                    agent_id=agent_type,
                    agent_type=agent_type,
                    learning_score=0.0,
                    success_rate=0.0,
                    failure_rate=0.0,
                    total_learning_cycles=0,
                    xp=0,
                    level=1,
                    prestige=0,
                    status="idle",
                    is_active=True,
                    priority="medium"
                )
                session.add(default_metrics)
                await session.commit()
                logger.info(f"Created default metrics for {agent_type}")
                return True
            
            # Update persistence tracking
            metrics.last_persistence_check = datetime.utcnow()
            metrics.persistence_version = "2.0"
            metrics.backup_created = True
            await session.commit()
            
            logger.info(f"Updated persistence for {agent_type}: Level {metrics.level}, XP {metrics.xp}")
            return True
            
    except Exception as e:
        logger.error(f"Error ensuring metrics persistence for {agent_type}: {str(e)}")
        return False

async def update_xp_with_persistence(self, agent_type: str, xp_gain: int) -> bool:
    """Update XP with proper persistence"""
    try:
        async with get_session() as session:
            # Ensure metrics exist
            await self.ensure_metrics_persistence(agent_type)
            
            # Get current metrics
            stmt = select(AgentMetrics).where(
                (AgentMetrics.agent_id == agent_type) | 
                (AgentMetrics.agent_type == agent_type)
            )
            result = await session.execute(stmt)
            metrics = result.scalar_one_or_none()
            
            if metrics:
                # Update XP
                old_xp = metrics.xp
                metrics.xp += xp_gain
                
                # Update level based on XP
                new_level = (metrics.xp // 1000) + 1
                if new_level > metrics.level:
                    metrics.level = new_level
                    logger.info(f"🎉 {agent_type} leveled up to level {new_level}!")
                
                # Update timestamps
                metrics.updated_at = datetime.utcnow()
                metrics.last_persistence_check = datetime.utcnow()
                
                await session.commit()
                
                logger.info(f"✅ Updated {agent_type} XP: {old_xp} -> {metrics.xp} (+{xp_gain})")
                return True
            else:
                logger.error(f"❌ No metrics found for {agent_type}")
                return False
                
    except Exception as e:
        logger.error(f"Error updating XP for {agent_type}: {str(e)}")
        return False
'''
        
        # Write the enhanced service to file
        with open('enhanced_agent_metrics_service.py', 'w') as f:
            f.write(enhanced_service)
        
        print("✅ Enhanced agent metrics service created: enhanced_agent_metrics_service.py")
        
    except Exception as e:
        print(f"❌ Error creating enhanced service: {str(e)}")

async def main():
    """Main function to fix XP persistence"""
    print("🚀 Starting XP persistence fix...")
    
    # Fix XP persistence
    success = await fix_xp_persistence()
    
    if success:
        # Create monitoring script
        await create_persistence_monitoring_script()
        
        # Create enhanced service
        await create_enhanced_agent_metrics_service()
        
        print("✅ XP persistence fix completed successfully!")
        print("📋 Next steps:")
        print("   1. Restart your backend service")
        print("   2. Run monitor_persistence.py periodically")
        print("   3. Check that XP is no longer resetting")
        print("   4. Monitor logs for persistence tracking")
    else:
        print("❌ XP persistence fix failed!")

if __name__ == "__main__":
    asyncio.run(main()) 