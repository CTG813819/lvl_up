#!/usr/bin/env python3
"""
Script to add the missing result column to the proposals table
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from app.core.database import init_database, engine
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def add_result_column():
    """Add result column to proposals table if it doesn't exist"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return
        
        async with engine.begin() as conn:
            # Check if result column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'result'
                );
            """))
            column_exists = result.scalar()
            
            if not column_exists:
                logger.info("Adding result column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN result TEXT;
                """))
                logger.info("result column added successfully")
            else:
                logger.info("result column already exists")
        
        # Verify the column exists by trying to select it
        async with engine.begin() as conn:
            try:
                result = await conn.execute(text("""
                    SELECT result FROM proposals LIMIT 1;
                """))
                logger.info("result column verified and accessible")
            except Exception as e:
                logger.error(f"Column verification failed: {e}")
                raise
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error("Error adding result column", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(add_result_column()) 