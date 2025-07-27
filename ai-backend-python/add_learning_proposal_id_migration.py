#!/usr/bin/env python3
"""
Migration script to add proposal_id column to the learning table

This script adds the missing proposal_id column to the learning table
to fix the UndefinedColumnError.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import text
from app.core.database import engine
import structlog

logger = structlog.get_logger()


async def add_learning_proposal_id():
    """Add proposal_id column to the learning table"""
    
    try:
        # Initialize database connection
        from app.core.database import init_database
        await init_database()
        
        async with engine.begin() as conn:
            logger.info("🔧 Starting learning table proposal_id migration...")
            
            # Check if learning table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'learning'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.error("Learning table does not exist. Please run the main migration first.")
                return False
            
            # Check if proposal_id column already exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'learning' 
                AND table_schema = 'public'
                AND column_name = 'proposal_id'
            """))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                logger.info("Adding proposal_id column to learning table")
                await conn.execute(text("""
                    ALTER TABLE learning 
                    ADD COLUMN proposal_id UUID REFERENCES proposals(id)
                """))
                logger.info("✅ proposal_id column added successfully")
            else:
                logger.info("proposal_id column already exists in learning table")
            
            # Create index for proposal_id if it doesn't exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE tablename = 'learning' 
                    AND indexname = 'idx_learning_proposal_id'
                );
            """))
            index_exists = result.scalar()
            
            if not index_exists:
                logger.info("Creating index for learning.proposal_id")
                await conn.execute(text("""
                    CREATE INDEX idx_learning_proposal_id ON learning(proposal_id)
                """))
            else:
                logger.info("Index for learning.proposal_id already exists")
            
            logger.info("✅ Learning table proposal_id migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during learning table proposal_id migration: {e}")
        return False


async def main():
    """Main migration function"""
    logger.info("🚀 Starting learning table proposal_id migration...")
    
    success = await add_learning_proposal_id()
    
    if success:
        logger.info("✅ Migration completed successfully")
        print("✅ Learning table proposal_id migration completed successfully")
    else:
        logger.error("❌ Migration failed")
        print("❌ Learning table proposal_id migration failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 