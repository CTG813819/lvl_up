#!/usr/bin/env python3
"""
Check Learning Data in Database
See what learning data exists for the AIs
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database, get_session
from app.models.sql_models import Learning, Proposal, OathPaper, AgentMetrics
from sqlalchemy import select

async def check_learning_data():
    """Check what learning data exists in the database"""
    print("🔍 Checking learning data in database...")
    
    # Initialize database
    await init_database()
    
    async with get_session() as session:
        # Check Learning records
        result = await session.execute(select(Learning))
        learnings = result.scalars().all()
        print(f"📚 Learning records: {len(learnings)}")
        
        for learning in learnings[:5]:  # Show first 5
            print(f"   - {learning.ai_type}: {learning.learning_type} - {learning.created_at}")
        
        # Check Proposal records
        result = await session.execute(select(Proposal))
        proposals = result.scalars().all()
        print(f"📝 Proposal records: {len(proposals)}")
        
        for proposal in proposals[:5]:  # Show first 5
            print(f"   - {proposal.ai_type}: {proposal.status} - {proposal.created_at}")
        
        # Check OathPaper records
        result = await session.execute(select(OathPaper))
        oaths = result.scalars().all()
        print(f"📜 OathPaper records: {len(oaths)}")
        
        for oath in oaths[:5]:  # Show first 5
            print(f"   - {oath.title}: {oath.category} - {oath.created_at}")
        
        # Check AgentMetrics records
        result = await session.execute(select(AgentMetrics))
        metrics = result.scalars().all()
        print(f"📊 AgentMetrics records: {len(metrics)}")
        
        for metric in metrics:
            print(f"   - {metric.agent_type}: Level {metric.level}, XP {metric.xp}, Learning Score {metric.learning_score}")
        
        # Check learning data by AI type
        print(f"\n📊 Learning data by AI type:")
        for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
            # Learning records
            result = await session.execute(select(Learning).where(Learning.ai_type == ai_type))
            ai_learnings = result.scalars().all()
            
            # Proposal records
            result = await session.execute(select(Proposal).where(Proposal.ai_type == ai_type))
            ai_proposals = result.scalars().all()
            
            # OathPaper records (where AI has learned)
            result = await session.execute(select(OathPaper).where(OathPaper.ai_responses.contains({ai_type: "learned"})))
            ai_oaths = result.scalars().all()
            
            print(f"   {ai_type}: {len(ai_learnings)} learnings, {len(ai_proposals)} proposals, {len(ai_oaths)} oath papers learned")

if __name__ == "__main__":
    asyncio.run(check_learning_data()) 