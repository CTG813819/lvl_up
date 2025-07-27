#!/usr/bin/env python3
"""
Fix Database Schema Issues
Adds missing columns to the proposals table
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, '/home/ubuntu/ai-backend-python/app')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

async def fix_database_schema():
    """Fix database schema issues"""
    try:
        from app.core.database import init_database, get_session
        from sqlalchemy import text
        
        logger.info("🔧 Starting database schema fix...")
        
        # Initialize database first
        logger.info("🔧 Initializing database...")
        await init_database()
        logger.info("✅ Database initialized")
        
        async with get_session() as session:
            # Check if ai_learning_summary column exists
            logger.info("🔍 Checking if ai_learning_summary column exists...")
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND column_name = 'ai_learning_summary'
            """))
            
            if result.fetchone():
                logger.info("✅ ai_learning_summary column already exists")
            else:
                logger.info("📝 Adding ai_learning_summary column...")
                await session.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN ai_learning_summary TEXT
                """))
                await session.commit()
                logger.info("✅ ai_learning_summary column added successfully")
            
            # Check for other missing columns and add them
            missing_columns = [
                ('change_type', 'VARCHAR(50)'),
                ('change_scope', 'VARCHAR(100)'),
                ('affected_components', 'TEXT'),
                ('learning_sources', 'TEXT'),
                ('expected_impact', 'TEXT'),
                ('risk_assessment', 'TEXT'),
                ('application_response', 'TEXT'),
                ('application_timestamp', 'TIMESTAMP'),
                ('application_result', 'TEXT'),
                ('post_application_analysis', 'TEXT'),
                ('files_analyzed', 'TEXT')
            ]
            
            for column_name, column_type in missing_columns:
                logger.info(f"🔍 Checking if {column_name} column exists...")
                result = await session.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'proposals' 
                    AND column_name = '{column_name}'
                """))
                
                if result.fetchone():
                    logger.info(f"✅ {column_name} column already exists")
                else:
                    logger.info(f"📝 Adding {column_name} column...")
                    await session.execute(text(f"""
                        ALTER TABLE proposals 
                        ADD COLUMN {column_name} {column_type}
                    """))
                    await session.commit()
                    logger.info(f"✅ {column_name} column added successfully")
            
            # Check if learning table exists and has required columns
            logger.info("🔍 Checking learning table...")
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'learning'
            """))
            
            if result.fetchone():
                logger.info("✅ Learning table exists")
                
                # Check for success_rate and confidence columns
                learning_columns = [
                    ('success_rate', 'FLOAT'),
                    ('confidence', 'FLOAT')
                ]
                
                for column_name, column_type in learning_columns:
                    result = await session.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'learning' 
                        AND column_name = '{column_name}'
                    """))
                    
                    if result.fetchone():
                        logger.info(f"✅ {column_name} column already exists in learning table")
                    else:
                        logger.info(f"📝 Adding {column_name} column to learning table...")
                        await session.execute(text(f"""
                            ALTER TABLE learning 
                            ADD COLUMN {column_name} {column_type}
                        """))
                        await session.commit()
                        logger.info(f"✅ {column_name} column added to learning table")
            else:
                logger.info("⚠️ Learning table does not exist - this is normal if not using learning features")
            
            # Create indexes for better performance
            logger.info("📝 Creating indexes for better performance...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status)",
                "CREATE INDEX IF NOT EXISTS idx_proposals_user_feedback ON proposals(user_feedback)",
                "CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_proposals_ai_type ON proposals(ai_type)"
            ]
            
            for index_sql in indexes:
                try:
                    await session.execute(text(index_sql))
                    await session.commit()
                    logger.info(f"✅ Index created: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
                except Exception as e:
                    logger.warning(f"⚠️ Index creation warning: {str(e)}")
            
            logger.info("🎉 Database schema fix completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Error fixing database schema: {str(e)}")
        raise

async def main():
    """Main function"""
    logger.info("🔧 Database Schema Fixer Starting...")
    
    try:
        await fix_database_schema()
        logger.info("✅ Database schema fix completed!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 