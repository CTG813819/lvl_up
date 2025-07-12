#!/usr/bin/env python3
"""
Database Schema Fix Script
Adds missing columns to the proposals table
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text
import structlog

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database, engine, SessionLocal
from app.models.sql_models import Base

logger = structlog.get_logger()

load_dotenv()


async def check_table_schema():
    """Check the current schema of the proposals table"""
    try:
        # Initialize database first
        await init_database()
        
        async with engine.begin() as conn:
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
                logger.info("Proposals table does not exist. Creating it...")
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Proposals table created successfully")
                return
            
            # Check current columns
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            logger.info(f"Current proposals table columns: {[col[0] for col in columns]}")
            
            return columns
            
    except Exception as e:
        logger.error(f"Error checking table schema: {e}")
        raise


async def add_missing_columns():
    """Add missing columns to the proposals table"""
    try:
        async with engine.begin() as conn:
            # Check if description column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'description'
                );
            """))
            description_exists = result.scalar()
            
            if not description_exists:
                logger.info("Adding description column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN description TEXT;
                """))
                logger.info("Description column added successfully")
            else:
                logger.info("Description column already exists")
            
            # Check if result column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'result'
                );
            """))
            result_exists = result.scalar()
            
            if not result_exists:
                logger.info("Adding result column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN result TEXT;
                """))
                logger.info("Result column added successfully")
            else:
                logger.info("Result column already exists")
            
            # Check if user_feedback_reason column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'user_feedback_reason'
                );
            """))
            feedback_reason_exists = result.scalar()
            
            if not feedback_reason_exists:
                logger.info("Adding user_feedback_reason column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN user_feedback_reason TEXT;
                """))
                logger.info("user_feedback_reason column added successfully")
            else:
                logger.info("user_feedback_reason column already exists")
            
            # Check if ai_learning_applied column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'ai_learning_applied'
                );
            """))
            learning_applied_exists = result.scalar()
            
            if not learning_applied_exists:
                logger.info("Adding ai_learning_applied column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN ai_learning_applied BOOLEAN DEFAULT FALSE;
                """))
                logger.info("ai_learning_applied column added successfully")
            else:
                logger.info("ai_learning_applied column already exists")
            
            # Check if previous_mistakes_avoided column exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = 'previous_mistakes_avoided'
                );
            """))
            mistakes_avoided_exists = result.scalar()
            
            if not mistakes_avoided_exists:
                logger.info("Adding previous_mistakes_avoided column to proposals table...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN previous_mistakes_avoided JSONB DEFAULT '[]';
                """))
                logger.info("previous_mistakes_avoided column added successfully")
            else:
                logger.info("previous_mistakes_avoided column already exists")
            
    except Exception as e:
        logger.error(f"Error adding missing columns: {e}")
        raise


async def create_indexes():
    """Create indexes for better performance"""
    try:
        async with engine.begin() as conn:
            # Create indexes if they don't exist
            indexes = [
                ("idx_proposals_ai_type_status", "proposals(ai_type, status)"),
                ("idx_proposals_file_path_ai_type", "proposals(file_path, ai_type)"),
                ("idx_proposals_created_at", "proposals(created_at DESC)"),
                ("idx_proposals_code_hash_ai_type", "proposals(code_hash, ai_type)"),
                ("idx_proposals_semantic_hash_ai_type", "proposals(semantic_hash, ai_type)")
            ]
            
            for index_name, index_def in indexes:
                try:
                    await conn.execute(text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def};"))
                    logger.info(f"Index {index_name} created or already exists")
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {e}")
            
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise


async def verify_fix():
    """Verify that the database schema is now correct"""
    try:
        async with engine.begin() as conn:
            # Test query to make sure all columns exist
            result = await conn.execute(text("""
                SELECT id, ai_type, file_path, code_before, code_after, description, 
                       status, user_feedback, test_status, test_output, result, 
                       code_hash, semantic_hash, diff_score, duplicate_of, 
                       ai_reasoning, learning_context, mistake_pattern, 
                       improvement_type, confidence, user_feedback_reason, 
                       ai_learning_applied, previous_mistakes_avoided, 
                       created_at, updated_at
                FROM proposals 
                LIMIT 1;
            """))
            
            logger.info("✅ Database schema verification successful - all columns exist")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database schema verification failed: {e}")
        return False


async def main():
    """Main function to fix the database schema"""
    logger.info("🔧 Starting database schema fix...")
    
    try:
        # Check current schema
        await check_table_schema()
        
        # Add missing columns
        await add_missing_columns()
        
        # Create indexes
        await create_indexes()
        
        # Verify the fix
        if await verify_fix():
            logger.info("🎉 Database schema fix completed successfully!")
        else:
            logger.error("❌ Database schema fix failed verification")
            
    except Exception as e:
        logger.error(f"❌ Error during database schema fix: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 