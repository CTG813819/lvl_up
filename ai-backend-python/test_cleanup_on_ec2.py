#!/usr/bin/env python3
"""
Test script to verify the cleanup fix works on EC2
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
import app.core.database as database_module
from app.models.sql_models import Proposal
from sqlalchemy import select, func
from datetime import datetime, timedelta

async def test_cleanup_on_ec2():
    """Test the cleanup function on EC2 with the fixed user_feedback length"""
    try:
        print("Testing cleanup function on EC2 with fixed user_feedback length...")
        
        # Initialize database
        await init_database()
        
        # Access SessionLocal through the module
        async with database_module.SessionLocal() as db:
            # Check current pending count
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar()
            
            print(f"Current pending proposals: {pending_count}")
            
            if pending_count > 30:
                print("Testing cleanup function...")
                
                # Simulate the cleanup logic
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                
                # Find old pending proposals
                old_pending_query = select(Proposal).where(
                    Proposal.status == "pending",
                    Proposal.created_at < cutoff_time
                )
                old_pending_result = await db.execute(old_pending_query)
                old_pending_proposals = old_pending_result.scalars().all()
                
                if old_pending_proposals:
                    print(f"Found {len(old_pending_proposals)} old pending proposals to clean up")
                    
                    for proposal in old_pending_proposals:
                        proposal.status = "expired"
                        proposal.user_feedback = "expired"  # This should now work (7 chars vs 20 limit)
                    
                    await db.commit()
                    print("✅ Cleanup completed successfully!")
                    
                    # Verify cleanup
                    remaining_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
                    remaining_result = await db.execute(remaining_query)
                    remaining_count = remaining_result.scalar()
                    
                    print(f"Remaining pending proposals: {remaining_count}")
                else:
                    print("No old pending proposals found to clean up")
            else:
                print(f"Pending count ({pending_count}) is below threshold (30), no cleanup needed")
                
    except Exception as e:
        print(f"❌ Error during cleanup test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cleanup_on_ec2()) 