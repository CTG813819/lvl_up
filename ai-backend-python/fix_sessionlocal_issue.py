#!/usr/bin/env python3
"""
Fix SessionLocal issue in cleanup script
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database, SessionLocal
from app.models.sql_models import Proposal
from sqlalchemy import select, func, delete
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

async def fix_cleanup_issue():
    """Fix the SessionLocal issue and clean up pending proposals"""
    try:
        print("🔧 Initializing database...")
        await init_database()
        
        # Verify SessionLocal is properly initialized
        if SessionLocal is None:
            print("❌ SessionLocal is None after init_database")
            return False
            
        print("✅ Database initialized successfully")
        
        async with SessionLocal() as db:
            # Get current pending count
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar() or 0
            
            print(f"📊 Current pending proposals: {pending_count}")
            
            if pending_count > 0:
                print("🗑️ Cleaning up pending proposals...")
                
                # Delete all pending proposals
                delete_query = delete(Proposal).where(Proposal.status == "pending")
                result = await db.execute(delete_query)
                deleted_count = result.rowcount
                
                await db.commit()
                print(f"✅ Deleted {deleted_count} pending proposals")
                
                # Verify cleanup
                verify_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
                verify_result = await db.execute(verify_query)
                final_count = verify_result.scalar() or 0
                
                print(f"📊 Remaining pending proposals: {final_count}")
                
                if final_count == 0:
                    print("🎉 Cleanup completed successfully!")
                    return True
                else:
                    print("⚠️ Some proposals still remain")
                    return False
            else:
                print("✅ No pending proposals to clean up")
                return True
                
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🚀 Starting cleanup fix...")
    
    success = await fix_cleanup_issue()
    
    if success:
        print("✅ Cleanup fix completed successfully")
        sys.exit(0)
    else:
        print("❌ Cleanup fix failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 