#!/usr/bin/env python3
"""
Script to add the missing description column to the proposals table
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

async def add_description_column():
    """Add description column to proposals table if it doesn't exist"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return
        
        async with engine.begin() as conn:
            # Check if description column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'description'
                );
            """))
            column_exists = result.scalar()
            
            if not column_exists:
                logger.info("Adding description column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN description TEXT;
                """))
                logger.info("description column added successfully")
            else:
                logger.info("description column already exists")
        
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error("Error adding description column", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(add_description_column()) 