#!/usr/bin/env python3
"""
Migration script to add missing columns to proposals table
Specifically adds ai_learning_summary and other missing columns
"""

import asyncio
import sys
import os
from sqlalchemy import text
import structlog

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from app.core.database import init_database

logger = structlog.get_logger()

async def add_missing_columns():
    """Add missing columns to proposals table"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return False
        
        async with engine.begin() as conn:
            logger.info("🔧 Starting migration to add missing columns...")
            
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
                logger.error("Proposals table does not exist. Please create it first.")
                return False
            
            # Get existing columns
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND table_schema = 'public'
            """))
            existing_columns = {row[0] for row in result.fetchall()}
            
            logger.info(f"Existing columns: {sorted(existing_columns)}")
            
            # Define missing columns to add
            missing_columns = [
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
            
            # Add each missing column
            for column_name, column_type in missing_columns:
                if column_name not in existing_columns:
                    logger.info(f"Adding column: {column_name}")
                    try:
                        await conn.execute(text(f"""
                            ALTER TABLE proposals 
                            ADD COLUMN {column_name} {column_type}
                        """))
                        logger.info(f"✅ {column_name} column added successfully")
                    except Exception as e:
                        logger.error(f"❌ Error adding {column_name}: {e}")
                        # Continue with other columns even if one fails
                else:
                    logger.info(f"✅ {column_name} column already exists")
            
            # Create indexes for better performance
            indexes_to_create = [
                ('idx_proposals_change_type', 'proposals(change_type)'),
                ('idx_proposals_change_scope', 'proposals(change_scope)'),
            ]
            
            for index_name, index_def in indexes_to_create:
                try:
                    # Check if index exists
                    result = await conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM pg_indexes 
                            WHERE tablename = 'proposals' 
                            AND indexname = :index_name
                        );
                    """), {"index_name": index_name})
                    index_exists = result.scalar()
                    
                    if not index_exists:
                        logger.info(f"Creating index: {index_name}")
                        await conn.execute(text(f"CREATE INDEX {index_name} ON {index_def}"))
                        logger.info(f"✅ {index_name} created successfully")
                    else:
                        logger.info(f"✅ {index_name} already exists")
                except Exception as e:
                    logger.error(f"❌ Error creating index {index_name}: {e}")
            
            logger.info("🎉 Migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

async def verify_migration():
    """Verify that all required columns exist"""
    try:
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return False
        
        async with engine.begin() as conn:
            # Get all columns
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND table_schema = 'public'
                ORDER BY column_name
            """))
            columns = [row[0] for row in result.fetchall()]
            
            logger.info(f"Current columns in proposals table: {columns}")
            
            # Check for critical columns
            critical_columns = [
                'ai_learning_summary',
                'change_type', 
                'change_scope',
                'affected_components',
                'learning_sources',
                'expected_impact',
                'risk_assessment',
                'application_response',
                'application_timestamp',
                'application_result',
                'post_application_analysis'
            ]
            
            missing_critical = [col for col in critical_columns if col not in columns]
            
            if missing_critical:
                logger.error(f"❌ Missing critical columns: {missing_critical}")
                return False
            else:
                logger.info("✅ All critical columns are present")
                return True
                
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

async def main():
    """Main migration function"""
    logger.info("🚀 Starting proposals table migration...")
    
    # Run the migration
    success = await add_missing_columns()
    
    if success:
        # Verify the migration
        verification_success = await verify_migration()
        
        if verification_success:
            logger.info("🎉 Migration and verification completed successfully!")
        else:
            logger.error("❌ Migration verification failed!")
            return 1
    else:
        logger.error("❌ Migration failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 