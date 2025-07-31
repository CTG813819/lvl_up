#!/usr/bin/env python3
"""
Direct database cleanup script using raw SQL
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_database
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def direct_db_cleanup():
    """Clean up pending proposals using direct SQL"""
    try:
        await init_database()
        
        # Access SessionLocal directly through the module
        import app.core.database as database_module
        
        async with database_module.SessionLocal() as db:
            # Check current count
            count_sql = text("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
            count_result = await db.execute(count_sql)
            current_count = count_result.scalar()
            
            logger.info(f"Current pending proposals: {current_count}")
            
            if current_count == 0:
                logger.info("No pending proposals to clean up")
                return
            
            # Method 1: Direct DELETE
            logger.info("Executing direct DELETE...")
            delete_sql = text("DELETE FROM proposals WHERE status = 'pending'")
            delete_result = await db.execute(delete_sql)
            deleted_rows = delete_result.rowcount
            
            logger.info(f"DELETE affected {deleted_rows} rows")
            
            # Commit immediately
            await db.commit()
            logger.info("Transaction committed")
            
            # Verify deletion
            verify_sql = text("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
            verify_result = await db.execute(verify_sql)
            final_count = verify_result.scalar()
            
            logger.info(f"Final pending count: {final_count}")
            
            if final_count > 0:
                logger.warning(f"Still have {final_count} pending proposals!")
                
                # Method 2: UPDATE to expired
                logger.info("Trying UPDATE to expired status...")
                update_sql = text("UPDATE proposals SET status = 'expired', user_feedback = 'Direct cleanup' WHERE status = 'pending'")
                update_result = await db.execute(update_sql)
                updated_rows = update_result.rowcount
                
                await db.commit()
                logger.info(f"UPDATE affected {updated_rows} rows")
                
                # Final verification
                final_verify_sql = text("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
                final_verify_result = await db.execute(final_verify_sql)
                final_final_count = final_verify_result.scalar()
                
                logger.info(f"Final count after UPDATE: {final_final_count}")
            
    except Exception as e:
        logger.error("Error in direct cleanup", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(direct_db_cleanup()) 