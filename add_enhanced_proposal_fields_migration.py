#!/usr/bin/env python3
"""
Migration script to add enhanced proposal fields to the database

This script adds the new fields for enhanced proposal descriptions:
- ai_learning_summary
- change_type
- change_scope
- affected_components
- learning_sources
- expected_impact
- risk_assessment
- application_response
- application_timestamp
- application_result
- post_application_analysis
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


async def add_enhanced_proposal_fields():
    """Add enhanced proposal fields to the database"""
    
    try:
        # Initialize database connection
        from app.core.database import init_database
        await init_database()
        
        async with engine.begin() as conn:
            logger.info("🔧 Starting enhanced proposal fields migration...")
            
            # Check if proposals table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'proposals'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                logger.error("Proposals table does not exist. Please run the main migration first.")
                return False
            
            # Check which columns already exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND table_schema = 'public'
            """))
            existing_columns = {row[0] for row in result.fetchall()}
            
            # Define the new columns to add
            new_columns = [
                ('ai_learning_summary', 'TEXT'),
                ('change_type', 'VARCHAR(20)'),
                ('change_scope', 'VARCHAR(20)'),
                ('affected_components', 'JSONB DEFAULT \'[]\''),
                ('learning_sources', 'JSONB DEFAULT \'[]\''),
                ('expected_impact', 'TEXT'),
                ('risk_assessment', 'TEXT'),
                ('application_response', 'TEXT'),
                ('application_timestamp', 'TIMESTAMP'),
                ('application_result', 'TEXT'),
                ('post_application_analysis', 'TEXT'),
            ]
            
            # Add each column if it doesn't exist
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    logger.info(f"Adding column: {column_name}")
                    await conn.execute(text(f"""
                        ALTER TABLE proposals 
                        ADD COLUMN {column_name} {column_type}
                    """))
                else:
                    logger.info(f"Column {column_name} already exists, skipping")
            
            # Create index for change_type if it doesn't exist
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes 
                    WHERE tablename = 'proposals' 
                    AND indexname = 'idx_proposals_change_type'
                );
            """))
            index_exists = result.scalar()
            
            if not index_exists:
                logger.info("Creating index for change_type")
                await conn.execute(text("""
                    CREATE INDEX idx_proposals_change_type ON proposals(change_type)
                """))
            else:
                logger.info("Index for change_type already exists")
            
            logger.info("✅ Enhanced proposal fields migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during enhanced proposal fields migration: {e}")
        return False


async def main():
    """Main migration function"""
    logger.info("🚀 Starting enhanced proposal fields migration...")
    
    success = await add_enhanced_proposal_fields()
    
    if success:
        logger.info("✅ Migration completed successfully")
        print("✅ Enhanced proposal fields migration completed successfully")
    else:
        logger.error("❌ Migration failed")
        print("❌ Enhanced proposal fields migration failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 