#!/usr/bin/env python3
"""
Analyze Learning Data Extraction
See what's being extracted vs what's available
"""

import asyncio
import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database, get_session
from app.models.sql_models import Learning, Proposal, OathPaper
from sqlalchemy import select, func

async def analyze_learning_extraction():
    """Analyze what learning data is being extracted vs available"""
    print("🔍 Analyzing learning data extraction...")
    
    # Initialize database
    await init_database()
    
    async with get_session() as session:
        for ai_type in ["imperium", "guardian", "conquest", "sandbox"]:
            print(f"\n{'='*60}")
            print(f"📊 ANALYSIS FOR {ai_type.upper()}")
            print(f"{'='*60}")
            
            # Count total records
            learning_count = await session.execute(
                select(func.count(Learning.id)).where(Learning.ai_type == ai_type)
            )
            learning_count = learning_count.scalar()
            
            proposal_count = await session.execute(
                select(func.count(Proposal.id)).where(Proposal.ai_type == ai_type)
            )
            proposal_count = proposal_count.scalar()
            
            print(f"📚 Total Learning Records: {learning_count}")
            print(f"📝 Total Proposal Records: {proposal_count}")
            
            # Analyze learning types
            learning_types = await session.execute(
                select(Learning.learning_type, func.count(Learning.id))
                .where(Learning.ai_type == ai_type)
                .group_by(Learning.learning_type)
                .order_by(func.count(Learning.id).desc())
                .limit(10)
            )
            learning_types = learning_types.all()
            
            print(f"\n🎓 Learning Types (Top 10):")
            for ltype, count in learning_types:
                print(f"   {ltype}: {count} records")
            
            # Analyze learning data content
            print(f"\n📖 Learning Data Content Analysis:")
            sample_learnings = await session.execute(
                select(Learning.learning_data, Learning.learning_type)
                .where(Learning.ai_type == ai_type)
                .order_by(Learning.created_at.desc())
                .limit(5)
            )
            sample_learnings = sample_learnings.all()
            
            for learning_data, learning_type in sample_learnings:
                print(f"   Type: {learning_type}")
                if learning_data:
                    try:
                        if isinstance(learning_data, str):
                            data = json.loads(learning_data)
                        else:
                            data = learning_data
                        
                        if isinstance(data, dict):
                            print(f"     Keys: {list(data.keys())}")
                            if 'subject' in data:
                                print(f"     Subject: {data['subject']}")
                            if 'topics' in data:
                                print(f"     Topics: {data['topics'][:3]}...")  # First 3
                        else:
                            print(f"     Data type: {type(data)}")
                    except:
                        print(f"     Raw data: {str(learning_data)[:100]}...")
                else:
                    print(f"     No learning data")
            
            # Analyze proposal improvement types
            improvement_types = await session.execute(
                select(Proposal.improvement_type, func.count(Proposal.id))
                .where(Proposal.ai_type == ai_type)
                .group_by(Proposal.improvement_type)
                .order_by(func.count(Proposal.id).desc())
                .limit(10)
            )
            improvement_types = improvement_types.all()
            
            print(f"\n🔧 Improvement Types (Top 10):")
            for itype, count in improvement_types:
                if itype:
                    print(f"   {itype}: {count} proposals")
            
            # Analyze file types
            file_types = await session.execute(
                select(Proposal.file_path, func.count(Proposal.id))
                .where(Proposal.ai_type == ai_type, Proposal.file_path.isnot(None))
                .group_by(Proposal.file_path)
                .order_by(func.count(Proposal.id).desc())
                .limit(10)
            )
            file_types = file_types.all()
            
            print(f"\n📁 File Types (Top 10):")
            for file_path, count in file_types:
                if file_path:
                    ext = file_path.split('.')[-1] if '.' in file_path else 'no_ext'
                    print(f"   .{ext}: {count} proposals")
            
            # Analyze proposal statuses
            statuses = await session.execute(
                select(Proposal.status, func.count(Proposal.id))
                .where(Proposal.ai_type == ai_type)
                .group_by(Proposal.status)
                .order_by(func.count(Proposal.id).desc())
            )
            statuses = statuses.all()
            
            print(f"\n📊 Proposal Statuses:")
            for status, count in statuses:
                print(f"   {status}: {count} proposals")

if __name__ == "__main__":
    asyncio.run(analyze_learning_extraction()) 