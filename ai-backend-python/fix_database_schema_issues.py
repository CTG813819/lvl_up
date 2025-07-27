#!/usr/bin/env python3
"""
Fix Database Schema Issues
Adds missing columns to agent_metrics and experiments tables
"""

import asyncio
import logging
from sqlalchemy import text
from app.core.database import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_database_schema_issues():
    """Fix database schema issues by adding missing columns"""
    try:
        # Initialize database if not already done
        from app.core.database import init_database
        await init_database()
        
        # Get the engine
        from app.core.database import engine
        
        if not engine:
            raise RuntimeError("Database engine not initialized")
        
        async with engine.begin() as conn:
            logger.info("🔧 Starting database schema fixes...")
            
            # Fix 1: Add missing columns to agent_metrics table
            logger.info("📊 Fixing agent_metrics table...")
            
            # Check if xp column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name = 'xp'
            """))
            xp_exists = result.fetchone()
            
            if not xp_exists:
                logger.info("Adding xp column to agent_metrics...")
                await conn.execute(text("""
                    ALTER TABLE agent_metrics 
                    ADD COLUMN xp INTEGER DEFAULT 0
                """))
            
            # Check if level column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name = 'level'
            """))
            level_exists = result.fetchone()
            
            if not level_exists:
                logger.info("Adding level column to agent_metrics...")
                await conn.execute(text("""
                    ALTER TABLE agent_metrics 
                    ADD COLUMN level INTEGER DEFAULT 1
                """))
            
            # Check if prestige column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name = 'prestige'
            """))
            prestige_exists = result.fetchone()
            
            if not prestige_exists:
                logger.info("Adding prestige column to agent_metrics...")
                await conn.execute(text("""
                    ALTER TABLE agent_metrics 
                    ADD COLUMN prestige INTEGER DEFAULT 0
                """))
            
            # Fix 2: Add missing columns to experiments table
            logger.info("🧪 Fixing experiments table...")
            
            # Check if experiment_data column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'experiments' 
                AND column_name = 'experiment_data'
            """))
            experiment_data_exists = result.fetchone()
            
            if not experiment_data_exists:
                logger.info("Adding experiment_data column to experiments...")
                await conn.execute(text("""
                    ALTER TABLE experiments 
                    ADD COLUMN experiment_data JSONB
                """))
            
            # Check if updated_at column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'experiments' 
                AND column_name = 'updated_at'
            """))
            updated_at_exists = result.fetchone()
            
            if not updated_at_exists:
                logger.info("Adding updated_at column to experiments...")
                await conn.execute(text("""
                    ALTER TABLE experiments 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
            
            # Fix 3: Create agent_metrics table if it doesn't exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'agent_metrics'
                )
            """))
            agent_metrics_exists = result.scalar()
            
            if not agent_metrics_exists:
                logger.info("Creating agent_metrics table...")
                await conn.execute(text("""
                    CREATE TABLE agent_metrics (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        agent_id VARCHAR(100) UNIQUE NOT NULL,
                        agent_type VARCHAR(50) NOT NULL,
                        learning_score FLOAT DEFAULT 0.0,
                        success_rate FLOAT DEFAULT 0.0,
                        failure_rate FLOAT DEFAULT 0.0,
                        total_learning_cycles INTEGER DEFAULT 0,
                        last_learning_cycle TIMESTAMP,
                        last_success TIMESTAMP,
                        last_failure TIMESTAMP,
                        learning_patterns JSONB DEFAULT '[]',
                        improvement_suggestions JSONB DEFAULT '[]',
                        status VARCHAR(20) DEFAULT 'idle',
                        is_active BOOLEAN DEFAULT TRUE,
                        priority VARCHAR(20) DEFAULT 'medium',
                        capabilities JSONB,
                        config JSONB,
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        prestige INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes for agent_metrics
                await conn.execute(text("""
                    CREATE INDEX idx_agent_metrics_agent_id ON agent_metrics(agent_id)
                """))
                await conn.execute(text("""
                    CREATE INDEX idx_agent_metrics_agent_type ON agent_metrics(agent_type)
                """))
                await conn.execute(text("""
                    CREATE INDEX idx_agent_metrics_status ON agent_metrics(status)
                """))
                await conn.execute(text("""
                    CREATE INDEX idx_agent_metrics_is_active ON agent_metrics(is_active)
                """))
                
                # Insert default agent metrics
                logger.info("Creating default agent metrics...")
                default_agents = [
                    ('imperium', 'imperium', 1000.0, 0.8, 0.2, 5, 0, 1, 0),
                    ('guardian', 'guardian', 800.0, 0.85, 0.15, 4, 0, 1, 0),
                    ('sandbox', 'sandbox', 1200.0, 0.75, 0.25, 6, 0, 1, 0),
                    ('conquest', 'conquest', 1500.0, 0.9, 0.1, 8, 0, 1, 0),
                ]
                
                for agent_id, agent_type, learning_score, success_rate, failure_rate, cycles, xp, level, prestige in default_agents:
                    await conn.execute(text("""
                        INSERT INTO agent_metrics (
                            agent_id, agent_type, learning_score, success_rate, failure_rate,
                            total_learning_cycles, xp, level, prestige, status, is_active, created_at, updated_at
                        ) VALUES (:agent_id, :agent_type, :learning_score, :success_rate, :failure_rate, 
                                 :cycles, :xp, :level, :prestige, :status, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "learning_score": learning_score,
                        "success_rate": success_rate,
                        "failure_rate": failure_rate,
                        "cycles": cycles,
                        "xp": xp,
                        "level": level,
                        "prestige": prestige,
                        "status": 'idle',
                        "is_active": True
                    })
            
            # Fix 4: Create experiments table if it doesn't exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'experiments'
                )
            """))
            experiments_exists = result.scalar()
            
            if not experiments_exists:
                logger.info("Creating experiments table...")
                await conn.execute(text("""
                    CREATE TABLE experiments (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        experiment_type VARCHAR(50) NOT NULL,
                        experiment_data JSONB,
                        status VARCHAR(20) DEFAULT 'running',
                        results JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes for experiments
                await conn.execute(text("""
                    CREATE INDEX idx_experiments_ai_type_status ON experiments(ai_type, status)
                """))
                await conn.execute(text("""
                    CREATE INDEX idx_experiments_created_at ON experiments(created_at DESC)
                """))
            
            logger.info("✅ Database schema fixes completed successfully!")
            
            # Verify the fixes
            logger.info("🔍 Verifying fixes...")
            
            # Check agent_metrics columns
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'agent_metrics' 
                AND column_name IN ('xp', 'level', 'prestige')
                ORDER BY column_name
            """))
            agent_metrics_columns = [row[0] for row in result.fetchall()]
            logger.info(f"Agent metrics columns: {agent_metrics_columns}")
            
            # Check experiments columns
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'experiments' 
                AND column_name IN ('experiment_data', 'updated_at')
                ORDER BY column_name
            """))
            experiments_columns = [row[0] for row in result.fetchall()]
            logger.info(f"Experiments columns: {experiments_columns}")
            
            # Check agent metrics count
            result = await conn.execute(text("SELECT COUNT(*) FROM agent_metrics"))
            agent_count = result.scalar()
            logger.info(f"Agent metrics count: {agent_count}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error fixing database schema: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🚀 Starting database schema fix...")
    success = await fix_database_schema_issues()
    
    if success:
        logger.info("✅ Database schema fix completed successfully!")
    else:
        logger.error("❌ Database schema fix failed!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 