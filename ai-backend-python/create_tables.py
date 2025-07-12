#!/usr/bin/env python3
"""
Script to create all database tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, create_tables, create_indexes
from app.models.sql_models import Base
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def create_all_tables():
    """Create all database tables"""
    try:
        # Initialize database connection
        await init_database()
        
        # Create tables
        await create_tables()
        
        # Create indexes
        await create_indexes()
        
        # Create oath_papers table if it doesn't exist
        from app.core.database import engine
        async with engine.begin() as conn:
            # Check if oath_papers table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'oath_papers'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.info("Creating oath_papers table...")
                await conn.execute(text("""
                    CREATE TABLE oath_papers (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title VARCHAR(200) NOT NULL,
                        content TEXT NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        ai_insights JSONB,
                        learning_value FLOAT DEFAULT 0.0,
                        status VARCHAR(20) DEFAULT 'pending',
                        ai_responses JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # Create indexes for oath_papers
                await conn.execute(text("""
                    CREATE INDEX idx_oath_papers_category ON oath_papers(category);
                    CREATE INDEX idx_oath_papers_created_at ON oath_papers(created_at DESC);
                    CREATE INDEX idx_oath_papers_status ON oath_papers(status);
                """))
                
                logger.info("oath_papers table created successfully")
            else:
                logger.info("oath_papers table already exists")
        
        logger.info("All database tables created successfully")
        
    except Exception as e:
        logger.error("Error creating tables", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(create_all_tables()) 