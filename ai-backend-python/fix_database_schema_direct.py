#!/usr/bin/env python3
"""
Direct Database Schema Fix Script
Adds missing columns to the proposals table using direct SQL
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

load_dotenv()


async def fix_database_schema():
    """Fix the database schema by adding missing columns"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        return False
    
    # Create engine directly
    engine = create_async_engine(
        database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
        pool_pre_ping=True,
        connect_args={"ssl": "require"}
    )
    
    try:
        async with engine.begin() as conn:
            logger.info("🔧 Starting database schema fix...")
            
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
                # Create the table with all required columns
                await conn.execute(text("""
                    CREATE TABLE proposals (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        ai_type VARCHAR(50) NOT NULL,
                        file_path VARCHAR(500) NOT NULL,
                        code_before TEXT NOT NULL,
                        code_after TEXT NOT NULL,
                        description TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        user_feedback VARCHAR(20),
                        test_status VARCHAR(20) DEFAULT 'not-run',
                        test_output TEXT,
                        result TEXT,
                        code_hash VARCHAR(64),
                        semantic_hash VARCHAR(64),
                        diff_score FLOAT,
                        duplicate_of UUID REFERENCES proposals(id),
                        ai_reasoning TEXT,
                        learning_context TEXT,
                        mistake_pattern VARCHAR(200),
                        improvement_type VARCHAR(20),
                        confidence FLOAT DEFAULT 0.5,
                        user_feedback_reason TEXT,
                        ai_learning_applied BOOLEAN DEFAULT FALSE,
                        previous_mistakes_avoided JSONB DEFAULT '[]',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                logger.info("✅ Proposals table created successfully")
            else:
                logger.info("Proposals table exists, checking for missing columns...")
                
                # Check and add missing columns
                columns_to_add = [
                    ("description", "TEXT"),
                    ("result", "TEXT"),
                    ("user_feedback_reason", "TEXT"),
                    ("ai_learning_applied", "BOOLEAN DEFAULT FALSE"),
                    ("previous_mistakes_avoided", "JSONB DEFAULT '[]'")
                ]
                
                for column_name, column_type in columns_to_add:
                    # Check if column exists
                    result = await conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns 
                            WHERE table_name = 'proposals' 
                            AND column_name = :column_name
                        );
                    """), {"column_name": column_name})
                    
                    column_exists = result.scalar()
                    
                    if not column_exists:
                        logger.info(f"Adding {column_name} column to proposals table...")
                        await conn.execute(text(f"""
                            ALTER TABLE proposals 
                            ADD COLUMN {column_name} {column_type};
                        """))
                        logger.info(f"✅ {column_name} column added successfully")
                    else:
                        logger.info(f"✅ {column_name} column already exists")
                
                # Create indexes
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
                        logger.info(f"✅ Index {index_name} created or already exists")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not create index {index_name}: {e}")
            
            # Verify the fix
            try:
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
                
    except Exception as e:
        logger.error(f"❌ Error during database schema fix: {e}")
        return False
    finally:
        await engine.dispose()


async def main():
    """Main function"""
    success = await fix_database_schema()
    if success:
        logger.info("🎉 Database schema fix completed successfully!")
    else:
        logger.error("❌ Database schema fix failed")


if __name__ == "__main__":
    asyncio.run(main()) 