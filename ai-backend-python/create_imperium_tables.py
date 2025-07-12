#!/usr/bin/env python3
"""
Database migration script for Imperium master orchestration tables
Creates the new tables for agent metrics, learning cycles, learning logs, and internet learning results
"""

import asyncio
import sys
import os

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, create_tables, engine
from app.models.sql_models import (
    AgentMetrics, LearningCycle, LearningLog, InternetLearningResult,
    Base
)
from sqlalchemy import text
import structlog

logger = structlog.get_logger()


async def create_imperium_tables():
    """Create the new Imperium master orchestration tables"""
    try:
        logger.info("Initializing database connection...")
        await init_database()
        
        logger.info("Creating Imperium master orchestration tables...")
        
        # Get the engine after initialization
        from app.core.database import engine
        
        # Create tables
        async with engine.begin() as conn:
            # Create agent_metrics table
            await conn.run_sync(lambda sync_conn: AgentMetrics.__table__.create(sync_conn, checkfirst=True))
            logger.info("Created agent_metrics table")
            
            # Create learning_cycles table
            await conn.run_sync(lambda sync_conn: LearningCycle.__table__.create(sync_conn, checkfirst=True))
            logger.info("Created learning_cycles table")
            
            # Create learning_logs table
            await conn.run_sync(lambda sync_conn: LearningLog.__table__.create(sync_conn, checkfirst=True))
            logger.info("Created learning_logs table")
            
            # Create internet_learning_results table
            await conn.run_sync(lambda sync_conn: InternetLearningResult.__table__.create(sync_conn, checkfirst=True))
            logger.info("Created internet_learning_results table")
        
        logger.info("All Imperium master orchestration tables created successfully!")
        
        # Create indexes for better performance
        logger.info("Creating indexes...")
        async with engine.begin() as conn:
            # Agent metrics indexes
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_id 
                ON agent_metrics(agent_id)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent_type 
                ON agent_metrics(agent_type)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_metrics_status 
                ON agent_metrics(status)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_metrics_is_active 
                ON agent_metrics(is_active)
            """))
            
            # Learning cycles indexes
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_cycles_cycle_id 
                ON learning_cycles(cycle_id)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_cycles_start_time 
                ON learning_cycles(start_time DESC)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_cycles_status 
                ON learning_cycles(status)
            """))
            
            # Learning logs indexes
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_logs_event_type 
                ON learning_logs(event_type)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_logs_agent_id 
                ON learning_logs(agent_id)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_logs_created_at 
                ON learning_logs(created_at DESC)
            """))
            
            # Internet learning results indexes
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_internet_learning_results_agent_id 
                ON internet_learning_results(agent_id)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_internet_learning_results_topic 
                ON internet_learning_results(topic)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_internet_learning_results_source 
                ON internet_learning_results(source)
            """))
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_internet_learning_results_created_at 
                ON internet_learning_results(created_at DESC)
            """))
        
        logger.info("All indexes created successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating Imperium tables: {str(e)}")
        return False


async def verify_tables():
    """Verify that all tables were created successfully"""
    try:
        # Get the engine after initialization
        from app.core.database import engine
        
        async with engine.begin() as conn:
            # Check if tables exist
            tables_to_check = [
                'agent_metrics',
                'learning_cycles', 
                'learning_logs',
                'internet_learning_results'
            ]
            
            for table_name in tables_to_check:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}'
                    )
                """))
                exists = result.scalar()
                if exists:
                    logger.info(f"✓ Table {table_name} exists")
                else:
                    logger.error(f"✗ Table {table_name} does not exist")
                    return False
            
            logger.info("All Imperium tables verified successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying tables: {str(e)}")
        return False


async def main():
    """Main function to run the migration"""
    logger.info("Starting Imperium master orchestration table migration...")
    
    # Create tables
    success = await create_imperium_tables()
    if not success:
        logger.error("Failed to create tables")
        sys.exit(1)
    
    # Verify tables
    success = await verify_tables()
    if not success:
        logger.error("Failed to verify tables")
        sys.exit(1)
    
    logger.info("Imperium master orchestration migration completed successfully!")
    logger.info("Tables created:")
    logger.info("  - agent_metrics")
    logger.info("  - learning_cycles")
    logger.info("  - learning_logs")
    logger.info("  - internet_learning_results")


if __name__ == "__main__":
    asyncio.run(main()) 