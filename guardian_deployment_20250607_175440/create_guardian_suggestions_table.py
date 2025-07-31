#!/usr/bin/env python3
"""
Script to create Guardian suggestions table
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

async def create_guardian_suggestions_table():
    """Create Guardian suggestions table"""
    try:
        # Initialize database connection
        await init_database()
        
        # Create guardian_suggestions table if it doesn't exist
        async with engine.begin() as conn:
            # Check if guardian_suggestions table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'guardian_suggestions'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.info("Creating guardian_suggestions table...")
                await conn.execute(text("""
                    CREATE TABLE guardian_suggestions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        issue_type VARCHAR(100) NOT NULL,
                        affected_item_type VARCHAR(50) NOT NULL,
                        affected_item_id VARCHAR(100) NOT NULL,
                        affected_item_name VARCHAR(200),
                        issue_description TEXT NOT NULL,
                        current_value TEXT,
                        proposed_fix TEXT NOT NULL,
                        severity VARCHAR(20) DEFAULT 'medium',
                        health_check_type VARCHAR(100) NOT NULL,
                        logical_consistency BOOLEAN DEFAULT TRUE,
                        data_integrity_score FLOAT DEFAULT 1.0,
                        status VARCHAR(20) DEFAULT 'pending',
                        user_feedback TEXT,
                        approved_by VARCHAR(100),
                        approved_at TIMESTAMP,
                        fix_applied BOOLEAN DEFAULT FALSE,
                        fix_applied_at TIMESTAMP,
                        fix_result TEXT,
                        fix_success BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        context_data JSONB,
                        related_items JSONB
                    );
                """))
                
                # Create indexes for guardian_suggestions
                await conn.execute(text("""
                    CREATE INDEX idx_guardian_suggestions_status ON guardian_suggestions(status);
                    CREATE INDEX idx_guardian_suggestions_issue_type ON guardian_suggestions(issue_type);
                    CREATE INDEX idx_guardian_suggestions_affected_item ON guardian_suggestions(affected_item_type, affected_item_id);
                    CREATE INDEX idx_guardian_suggestions_severity ON guardian_suggestions(severity);
                    CREATE INDEX idx_guardian_suggestions_created_at ON guardian_suggestions(created_at DESC);
                    CREATE INDEX idx_guardian_suggestions_health_check_type ON guardian_suggestions(health_check_type);
                """))
                
                logger.info("guardian_suggestions table created successfully")
            else:
                logger.info("guardian_suggestions table already exists")
        
        logger.info("Guardian suggestions table migration completed successfully")
        
    except Exception as e:
        logger.error("Error creating guardian suggestions table", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(create_guardian_suggestions_table()) 