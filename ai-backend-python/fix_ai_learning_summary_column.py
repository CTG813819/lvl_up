#!/usr/bin/env python3
"""
Quick fix for missing ai_learning_summary column
Run this on the EC2 instance to add the missing column
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

async def fix_ai_learning_summary_column():
    """Add the missing ai_learning_summary column to proposals table"""
    try:
        # Initialize database connection
        await init_database()
        
        # Import engine after initialization
        from app.core.database import engine
        
        if not engine:
            logger.error("Database engine is None after initialization")
            return False
        
        async with engine.begin() as conn:
            logger.info("🔧 Checking for missing ai_learning_summary column...")
            
            # Check if the column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND column_name = 'ai_learning_summary'
            """))
            column_exists = result.scalar() is not None
            
            if not column_exists:
                logger.info("📝 Adding ai_learning_summary column...")
                await conn.execute(text("""
                    ALTER TABLE proposals 
                    ADD COLUMN ai_learning_summary TEXT
                """))
                logger.info("✅ ai_learning_summary column added successfully!")
            else:
                logger.info("✅ ai_learning_summary column already exists")
            
            # Verify the column was added
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'proposals' 
                AND column_name = 'ai_learning_summary'
            """))
            column_exists_after = result.scalar() is not None
            
            if column_exists_after:
                logger.info("🎉 Verification successful - ai_learning_summary column is now available!")
                return True
            else:
                logger.error("❌ Column was not added successfully")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error fixing ai_learning_summary column: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🚀 Starting ai_learning_summary column fix...")
    
    success = await fix_ai_learning_summary_column()
    
    if success:
        logger.info("🎉 ai_learning_summary column fix completed successfully!")
        return 0
    else:
        logger.error("❌ ai_learning_summary column fix failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 