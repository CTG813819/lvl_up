#!/usr/bin/env python3
"""
Script to forcefully add the missing description column to the proposals table
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

async def force_add_description_column():
    """Forcefully add description column to proposals table"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return
        
        async with engine.begin() as conn:
            # Try to add the column - this will fail if it already exists, but that's okay
            try:
                logger.info("Adding description column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN description TEXT;
                """))
                logger.info("description column added successfully")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    logger.info("description column already exists")
                else:
                    logger.error(f"Error adding column: {e}")
                    raise
        
        # Verify the column exists by trying to select it
        async with engine.begin() as conn:
            try:
                result = await conn.execute(text("""
                    SELECT description FROM proposals LIMIT 1;
                """))
                logger.info("description column verified and accessible")
            except Exception as e:
                logger.error(f"Column verification failed: {e}")
                raise
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error("Error adding description column", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(force_add_description_column()) 