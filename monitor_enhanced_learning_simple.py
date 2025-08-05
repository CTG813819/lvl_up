#!/usr/bin/env python3
"""
Simplified monitoring script for enhanced subject learning on EC2
"""

import asyncio
import json
from datetime import datetime, timedelta
from app.core.database import get_session
from app.models.sql_models import OathPaper, AgentMetrics
from sqlalchemy import select

async def monitor_enhanced_learning():
    """Monitor enhanced learning activities"""
    try:
        session = get_session()
        async with session as s:
            # Get recent oath papers
            recent_oath_papers = await s.execute(
                select(OathPaper)
                .where(OathPaper.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(OathPaper.created_at.desc())
                .limit(10)
            )
            oath_papers = recent_oath_papers.scalars().all()
            
            # Get AI metrics
            ai_metrics = await s.execute(select(AgentMetrics))
            metrics = ai_metrics.scalars().all()
            
            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "oath_papers_last_24h": len(oath_papers),
                "ai_metrics": [
                    {
                        "agent_type": m.agent_type,
                        "learning_score": m.learning_score,
                        "level": m.level,
                        "prestige": m.prestige,
                        "total_learning_cycles": m.total_learning_cycles
                    }
                    for m in metrics
                ],
                "recent_subjects": [
                    {
                        "subject": p.subject,
                        "title": p.title,
                        "learning_value": p.learning_value,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in oath_papers if p.subject
                ]
            }
            
            print(json.dumps(report, indent=2))
            
    except Exception as e:
        print(f"Error monitoring enhanced learning: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_enhanced_learning()) 