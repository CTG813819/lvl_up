#!/usr/bin/env python3
"""
Script to clear all proposals from the database
"""
import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, SessionLocal
from app.models.sql_models import Proposal
from sqlalchemy import delete

async def clear_proposals():
    """Clear all proposals from the database"""
    try:
        await init_database()
        
        # Use SessionLocal to create a session
        async with SessionLocal() as session:
            # Delete all proposals
            await session.execute(delete(Proposal))
            await session.commit()
            print("✅ All proposals cleared successfully")
            
    except Exception as e:
        print(f"❌ Error clearing proposals: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(clear_proposals()) 