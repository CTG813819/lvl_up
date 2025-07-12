#!/usr/bin/env python3
"""
Script to create Mission and MissionSubtask tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, engine
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def create_mission_tables():
    """Create Mission and MissionSubtask tables"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        # Create missions table if it doesn't exist
        async with engine.begin() as conn:
            # Check if missions table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'missions'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.info("Creating missions table...")
                await conn.execute(text("""
                    CREATE TABLE missions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        mission_id VARCHAR(100),
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        mission_type VARCHAR(50) NOT NULL,
                        is_completed BOOLEAN DEFAULT FALSE,
                        has_failed BOOLEAN DEFAULT FALSE,
                        mastery_id VARCHAR(100),
                        value FLOAT,
                        is_counter_based BOOLEAN DEFAULT FALSE,
                        current_count INTEGER DEFAULT 0,
                        target_count INTEGER DEFAULT 0,
                        mastery_value FLOAT DEFAULT 0.0,
                        linked_mastery_id VARCHAR(100),
                        notification_id INTEGER NOT NULL,
                        scheduled_notification_id INTEGER,
                        image_url VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_completed TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        subtasks_data JSONB,
                        subtask_mastery_values JSONB,
                        bolt_color VARCHAR(20),
                        timelapse_color VARCHAR(20),
                        last_health_check TIMESTAMP,
                        health_status VARCHAR(20) DEFAULT 'unknown',
                        data_integrity_score FLOAT DEFAULT 1.0
                    );
                """))
                # Create indexes for missions (one at a time)
                await conn.execute(text("CREATE INDEX idx_missions_mission_id ON missions(mission_id);"))
                await conn.execute(text("CREATE INDEX idx_missions_title ON missions(title);"))
                await conn.execute(text("CREATE INDEX idx_missions_type ON missions(mission_type);"))
                await conn.execute(text("CREATE INDEX idx_missions_completed ON missions(is_completed);"))
                await conn.execute(text("CREATE INDEX idx_missions_health_status ON missions(health_status);"))
                await conn.execute(text("CREATE INDEX idx_missions_created_at ON missions(created_at DESC);"))
                logger.info("missions table created successfully")
            else:
                logger.info("missions table already exists")
            
            # Check if mission_subtasks table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'mission_subtasks'
                );
            """))
            subtasks_table_exists = result.scalar()
            
            if not subtasks_table_exists:
                logger.info("Creating mission_subtasks table...")
                await conn.execute(text("""
                    CREATE TABLE mission_subtasks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
                        name VARCHAR(200) NOT NULL,
                        required_completions INTEGER DEFAULT 0,
                        current_completions INTEGER DEFAULT 0,
                        linked_mastery_id VARCHAR(100),
                        mastery_value FLOAT DEFAULT 0.0,
                        is_counter_based BOOLEAN DEFAULT FALSE,
                        current_count INTEGER DEFAULT 0,
                        bolt_color VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # Create indexes for mission_subtasks (one at a time)
                await conn.execute(text("CREATE INDEX idx_mission_subtasks_mission_id ON mission_subtasks(mission_id);"))
                await conn.execute(text("CREATE INDEX idx_mission_subtasks_linked_mastery ON mission_subtasks(linked_mastery_id);"))
                logger.info("mission_subtasks table created successfully")
            else:
                logger.info("mission_subtasks table already exists")
        
        logger.info("Mission tables migration completed successfully")
        
    except Exception as e:
        logger.error("Error creating mission tables", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(create_mission_tables()) 