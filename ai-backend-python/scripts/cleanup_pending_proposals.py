#!/usr/bin/env python3
"""
Script to clean up pending proposals backlog
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_database
from app.models.sql_models import Proposal
from sqlalchemy import select, update, func
import structlog

logger = structlog.get_logger()

async def cleanup_pending_proposals():
    """Clean up ALL pending proposals to clear the backlog"""
    try:
        await init_database()
        
        # Access SessionLocal directly through the module to avoid import scope issues
        import app.core.database as database_module
        
        async with database_module.SessionLocal() as db:
            # Get count of pending proposals
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar()
            
            logger.info(f"Found {pending_count} pending proposals to clean up")
            
            if pending_count == 0:
                logger.info("No pending proposals to clean up")
                return
            
            # Use direct SQL DELETE for more aggressive cleanup
            logger.info("Deleting ALL pending proposals using direct SQL")
            
            # Method 1: Direct SQL DELETE
            from sqlalchemy import text
            delete_sql = text("DELETE FROM proposals WHERE status = 'pending'")
            result = await db.execute(delete_sql)
            deleted_count = result.rowcount
            
            logger.info(f"Direct SQL DELETE affected {deleted_count} rows")
            
            # Commit the transaction
            await db.commit()
            
            # Verify the cleanup worked
            verify_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            verify_result = await db.execute(verify_query)
            final_pending_count = verify_result.scalar()
            
            logger.info(f"Cleanup completed. Remaining pending proposals: {final_pending_count}")
            
            if final_pending_count > 0:
                logger.warning(f"Still have {final_pending_count} pending proposals after cleanup!")
                
                # Method 2: Force update to expired status as backup
                logger.info("Trying backup method: updating remaining proposals to expired status")
                update_sql = text("UPDATE proposals SET status = 'expired', user_feedback = 'Force expired during cleanup' WHERE status = 'pending'")
                update_result = await db.execute(update_sql)
                updated_count = update_result.rowcount
                
                await db.commit()
                logger.info(f"Updated {updated_count} proposals to expired status")
                
                # Final verification
                final_verify_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
                final_verify_result = await db.execute(final_verify_query)
                final_count = final_verify_result.scalar()
                
                logger.info(f"Final pending count after backup cleanup: {final_count}")
            
    except Exception as e:
        logger.error("Error during cleanup", error=str(e), exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(cleanup_pending_proposals()) 