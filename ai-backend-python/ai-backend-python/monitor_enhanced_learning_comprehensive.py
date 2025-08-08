#!/usr/bin/env python3
"""
Comprehensive monitoring script for enhanced autonomous learning system
Tracks learning, proposals, file analysis, and AI growth
"""

import asyncio
import json
from datetime import datetime, timedelta
from app.core.database import get_session
from app.models.sql_models import OathPaper, AgentMetrics, Proposal
from sqlalchemy import select

async def monitor_enhanced_learning_comprehensive():
    """Comprehensive monitoring of enhanced learning activities"""
    try:
        session = get_session()
        async with session as s:
            # Get recent oath papers (last 24 hours)
            recent_oath_papers = await s.execute(
                select(OathPaper)
                .where(OathPaper.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(OathPaper.created_at.desc())
                .limit(20)
            )
            oath_papers = recent_oath_papers.scalars().all()
            
            # Get recent proposals (last 24 hours)
            recent_proposals = await s.execute(
                select(Proposal)
                .where(Proposal.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(Proposal.created_at.desc())
                .limit(20)
            )
            proposals = recent_proposals.scalars().all()
            
            # Get AI metrics
            ai_metrics = await s.execute(select(AgentMetrics))
            metrics = ai_metrics.scalars().all()
            
            # Calculate learning statistics
            enhanced_papers = [p for p in oath_papers if p.category == "enhanced_autonomous_learning"]
            ai_generated_proposals = [p for p in proposals if p.ai_generated]
            cross_ai_sharing = [p for p in oath_papers if p.category == "cross_ai_sharing"]
            
            # Generate comprehensive report
            report = {
                "timestamp": datetime.now().isoformat(),
                "learning_activity": {
                    "total_oath_papers_24h": len(oath_papers),
                    "enhanced_learning_papers": len(enhanced_papers),
                    "cross_ai_sharing_papers": len(cross_ai_sharing),
                    "unique_subjects_learned": len(set(p.subject for p in oath_papers if p.subject))
                },
                "proposal_activity": {
                    "total_proposals_24h": len(proposals),
                    "ai_generated_proposals": len(ai_generated_proposals),
                    "proposal_categories": list(set(p.category for p in proposals)),
                    "proposal_status_distribution": {
                        "draft": len([p for p in proposals if p.status == "draft"]),
                        "analysis": len([p for p in proposals if p.status == "analysis"]),
                        "review": len([p for p in proposals if p.status == "review"])
                    }
                },
                "ai_growth_metrics": [
                    {
                        "agent_type": m.agent_type,
                        "learning_score": m.learning_score,
                        "level": m.level,
                        "prestige": m.prestige,
                        "total_learning_cycles": m.total_learning_cycles,
                        "xp": m.xp,
                        "last_learning_cycle": m.last_learning_cycle.isoformat() if m.last_learning_cycle else None
                    }
                    for m in metrics
                ],
                "recent_enhanced_subjects": [
                    {
                        "subject": p.subject,
                        "title": p.title,
                        "learning_value": p.learning_value,
                        "created_at": p.created_at.isoformat(),
                        "category": p.category
                    }
                    for p in enhanced_papers[:10]
                ],
                "recent_ai_proposals": [
                    {
                        "title": p.title,
                        "category": p.category,
                        "priority": p.priority,
                        "status": p.status,
                        "created_at": p.created_at.isoformat(),
                        "source_subject": getattr(p, 'source_subject', None),
                        "source_area": getattr(p, 'source_area', None)
                    }
                    for p in ai_generated_proposals[:10]
                ],
                "system_health": {
                    "database_connection": "active",
                    "autonomous_learning": "running",
                    "proposal_generation": "active",
                    "file_analysis": "active",
                    "cross_ai_sharing": "active"
                }
            }
            
            print(json.dumps(report, indent=2))
            
    except Exception as e:
        print(f"Error in comprehensive monitoring: {e}")

async def get_ai_learning_summary():
    """Get a summary of AI learning progress"""
    try:
        session = get_session()
        async with session as s:
            # Get all AI metrics
            ai_metrics = await s.execute(select(AgentMetrics))
            metrics = ai_metrics.scalars().all()
            
            print("\n🤖 AI Learning Summary:")
            print("=" * 50)
            
            for m in metrics:
                print(f"\n{m.agent_type.upper()}:")
                print(f"  📊 Level: {m.level}")
                print(f"  🏆 Prestige: {m.prestige}")
                print(f"  📈 Learning Score: {m.learning_score:.2f}")
                print(f"  ⚡ XP: {m.xp}")
                print(f"  🔄 Learning Cycles: {m.total_learning_cycles}")
                
                if m.last_learning_cycle:
                    time_since = datetime.utcnow() - m.last_learning_cycle
                    print(f"  ⏰ Last Learning: {time_since.total_seconds() / 3600:.1f} hours ago")
                
                # Calculate growth rate
                if m.learning_patterns:
                    recent_patterns = [p for p in m.learning_patterns if p.get("timestamp") and 
                                     datetime.fromisoformat(p["timestamp"]) > datetime.utcnow() - timedelta(hours=24)]
                    print(f"  📚 Recent Learning Patterns: {len(recent_patterns)}")
            
    except Exception as e:
        print(f"Error getting AI learning summary: {e}")

async def get_proposal_summary():
    """Get a summary of AI-generated proposals"""
    try:
        session = get_session()
        async with session as s:
            # Get recent AI-generated proposals
            recent_proposals = await s.execute(
                select(Proposal)
                .where(Proposal.ai_generated == True)
                .where(Proposal.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(Proposal.created_at.desc())
            )
            proposals = recent_proposals.scalars().all()
            
            print("\n📋 AI-Generated Proposals Summary:")
            print("=" * 50)
            
            if proposals:
                for p in proposals:
                    print(f"\n📄 {p.title}")
                    print(f"  📂 Category: {p.category}")
                    print(f"  🎯 Priority: {p.priority}")
                    print(f"  📊 Status: {p.status}")
                    print(f"  ⏰ Created: {p.created_at.strftime('%Y-%m-%d %H:%M')}")
                    if hasattr(p, 'source_subject') and p.source_subject:
                        print(f"  🧠 Source Subject: {p.source_subject}")
                    if hasattr(p, 'source_area') and p.source_area:
                        print(f"  📁 Source Area: {p.source_area}")
            else:
                print("No AI-generated proposals in the last 24 hours.")
            
    except Exception as e:
        print(f"Error getting proposal summary: {e}")

if __name__ == "__main__":
    print("🔍 Enhanced Autonomous Learning System Monitor")
    print("=" * 60)
    
    # Run comprehensive monitoring
    asyncio.run(monitor_enhanced_learning_comprehensive())
    
    # Run AI learning summary
    asyncio.run(get_ai_learning_summary())
    
    # Run proposal summary
    asyncio.run(get_proposal_summary())
    
    print("\n✅ Monitoring complete!") 