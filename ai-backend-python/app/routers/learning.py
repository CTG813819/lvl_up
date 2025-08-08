# pyright: reportGeneralTypeIssues=false
"""
Learning router for AI learning endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import json

from app.services.ml_service import MLService
ml_service = MLService()

from app.services.ai_learning_service import AILearningService
ai_learning_service = AILearningService()

from app.models.sql_models import Proposal, Experiment
from app.core.database import get_db
from app.models.sql_models import Learning
from app.core.database import get_session
from sqlalchemy import select
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()
router = APIRouter()


def only_datetimes(values):
    from datetime import datetime
    return [v for v in values if isinstance(v, datetime)]


@router.get("/stats/{ai_type}")
async def get_learning_stats(ai_type: str, session: AsyncSession = Depends(get_db)):
    """Get learning statistics for an AI type from live data"""
    try:
        # Get proposals for this AI type
        proposals_result = await session.execute(
            select(Proposal).where(Proposal.ai_type == ai_type)
        )
        proposals = proposals_result.scalars().all()
        
        # Get experiments for this AI type
        experiments_result = await session.execute(
            select(Experiment).where(Experiment.ai_type == ai_type)
        )
        experiments = experiments_result.scalars().all()
        
        # Calculate statistics
        total_proposals = len(proposals)
        approved_proposals = len([p for p in proposals if p.status == "approved"])
        total_experiments = len(experiments)
        successful_experiments = len([e for e in experiments if e.status == "passed"])
        
        created_ats = only_datetimes([p.created_at for p in proposals])
        last_activity = max(created_ats).isoformat() if created_ats else None

        return {
            "status": "success",
            "data": {
                "ai_type": ai_type,
                "total_proposals": total_proposals,
                "approved_proposals": approved_proposals,
                "approval_rate": (approved_proposals / total_proposals * 100) if total_proposals > 0 else 0,
                "total_experiments": total_experiments,
                "successful_experiments": successful_experiments,
                "success_rate": (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0,
                "last_activity": last_activity,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error("Error getting learning stats", error=str(e), ai_type=ai_type)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{ai_type}")
async def get_learning_insights(ai_type: str, session: AsyncSession = Depends(get_db)):
    """Get learning insights for a specific AI type"""
    try:
        from ..models.sql_models import Learning, Proposal
        from sqlalchemy import select, func
        from datetime import datetime, timedelta
        
        # Get recent learning data for the AI type
        recent_query = select(Learning).where(
            Learning.ai_type == ai_type
        ).order_by(Learning.updated_at.desc()).limit(10)
        
        result = await session.execute(recent_query)
        recent_learning = result.scalars().all()
        
        # Generate recommendations based on learning patterns
        recommendations = []
        
        if recent_learning:
            # Analyze learning patterns based on learning_type and status
            successful_learning = [l for l in recent_learning if l.status == "active"]
            failed_learning = [l for l in recent_learning if l.status == "failed"]
            
            if successful_learning:
                recommendations.append(f"Continue focusing on {successful_learning[0].learning_type} - successful learning")
            
            if failed_learning:
                recommendations.append(f"Improve {failed_learning[0].learning_type} - needs refinement")
            
            # General recommendations based on learning types
            learning_types = [l.learning_type for l in recent_learning]
            if "proposal_feedback" in learning_types:
                recommendations.append("Focus on improving proposal quality")
            elif "user_feedback" in learning_types:
                recommendations.append("Enhance user interaction patterns")
            elif "system_analysis" in learning_types:
                recommendations.append("Strengthen system analysis capabilities")
            
            # Pattern-specific recommendations
            for learning in recent_learning[:3]:
                if learning.learning_type:
                    if "error" in learning.learning_type.lower():
                        recommendations.append("Enhance error handling capabilities")
                    elif "security" in learning.learning_type.lower():
                        recommendations.append("Strengthen security validation")
                    elif "performance" in learning.learning_type.lower():
                        recommendations.append("Optimize performance patterns")
        
        # Calculate learning metrics
        total_learning = len(recent_learning)
        successful_learning = len([l for l in recent_learning if l.status == "active"])
        avg_success_rate = successful_learning / total_learning if total_learning > 0 else 0.0
        applied_learning = successful_learning / total_learning if total_learning > 0 else 0.0
        
        return {
            "recommendations": recommendations,
            "learning_score": avg_success_rate,
            "success_rate": avg_success_rate * 100,
            "applied_learning": applied_learning * 100,
            "backend_test_success_rate": avg_success_rate * 100,
            "total_patterns": total_learning,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning insights for {ai_type}", error=str(e))
        # Return empty recommendations and zeroed metrics
        return {
            "recommendations": [],
            "learning_score": 0.0,
            "success_rate": 0.0,
            "applied_learning": 0.0,
            "backend_test_success_rate": 0.0,
            "total_patterns": 0,
            "last_updated": datetime.utcnow().isoformat()
        }


@router.post("/train")
async def train_models():
    """Train ML models"""
    try:
        await ml_service.train_models()
        return {"message": "Models trained successfully"}
    except Exception as e:
        logger.error("Error training models", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml-insights")
async def get_ml_insights():
    """Get ML insights"""
    try:
        insights = await ml_service.get_ml_insights()
        return insights
    except Exception as e:
        logger.error("Error getting ML insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data")
async def get_learning_data(session: AsyncSession = Depends(get_db)):
    """Get learning data for all AI types from live data"""
    try:
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        data = {}
        
        for ai_type in ai_types:
            # Get experiments for this AI type
            experiments_result = await session.execute(
                select(Experiment).where(Experiment.ai_type == ai_type)
            )
            experiments = experiments_result.scalars().all()
            
            # Get proposals for this AI type
            proposals_result = await session.execute(
                select(Proposal).where(Proposal.ai_type == ai_type)
            )
            proposals = proposals_result.scalars().all()
            
            data[ai_type] = {
                "experiments": [
                    {
                        "id": str(e.id),
                        "description": e.description or f"Experiment {str(e.id)[:8]}",
                        "timestamp": e.created_at.isoformat() if e.created_at is not None else None,
                        "success": e.status == "passed"
                    }
                    for e in experiments[:5]  # Limit to 5 most recent
                ],
                "insights": [
                    f"AI {ai_type} has processed {len(proposals)} proposals",
                    f"Success rate: {(len([p for p in proposals if p.status == 'approved']) / len(proposals) * 100) if proposals else 0:.1f}%"
                ]
            }
        
        return data
    except Exception as e:
        logger.error("Error getting learning data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_learning_metrics(session: AsyncSession = Depends(get_db)):
    """Get learning metrics for all AI types from live data"""
    try:
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        metrics = {}
        
        for ai_type in ai_types:
            # Get experiments for this AI type
            experiments_result = await session.execute(
                select(Experiment).where(Experiment.ai_type == ai_type)
            )
            experiments = experiments_result.scalars().all()
            
            # Get proposals for this AI type
            proposals_result = await session.execute(
                select(Proposal).where(Proposal.ai_type == ai_type)
            )
            proposals = proposals_result.scalars().all()
            
            total_experiments = len(experiments)
            successful_experiments = len([e for e in experiments if e.status == "passed"])
            success_rate = (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0
            
            # Calculate learning progress based on approved proposals
            approved_proposals = len([p for p in proposals if p.status == "approved"])
            learning_progress = min((approved_proposals / max(len(proposals), 1)) * 100, 100)
            
            # Get last activity
            last_activity = None
            exp_created_ats = only_datetimes([e.created_at for e in experiments])
            prop_created_ats = only_datetimes([p.created_at for p in proposals])
            if exp_created_ats:
                last_activity = max(exp_created_ats).isoformat()
            elif prop_created_ats:
                last_activity = max(prop_created_ats).isoformat()
            
            metrics[ai_type] = {
                "totalExperiments": total_experiments,
                "successRate": success_rate,
                "lastExperiment": last_activity,
                "learningProgress": learning_progress
            }
        
        return metrics
    except Exception as e:
        logger.error("Error getting learning metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_learning_status(session: AsyncSession = Depends(get_db)):
    """Get learning system status from live data"""
    try:
        # Get total experiments
        total_experiments_result = await session.execute(select(Experiment))
        total_experiments = len(total_experiments_result.scalars().all())
        
        # Get total proposals
        total_proposals_result = await session.execute(select(Proposal))
        total_proposals = len(total_proposals_result.scalars().all())
        
        # Calculate success rate
        successful_experiments_result = await session.execute(
            select(Experiment).where(Experiment.status == "passed")
        )
        successful_experiments = len(successful_experiments_result.scalars().all())
        success_rate = (successful_experiments / total_experiments * 100) if total_experiments > 0 else 0
        
        # Get last activity
        last_activity = None
        if total_experiments > 0:
            last_exp_result = await session.execute(
                select(Experiment).order_by(Experiment.created_at.desc()).limit(1)
            )
            last_exp = last_exp_result.scalar_one_or_none()
            if last_exp and last_exp.created_at is not None:
                last_activity = last_exp.created_at.isoformat()
        
        return {
            "status": "active",
            "message": "AI Learning system is running",
            "timestamp": datetime.utcnow().isoformat(),
            "ai_types": ["Imperium", "Guardian", "Sandbox", "Conquest"],
            "active_learning": True,
            "last_activity": last_activity,
            "total_experiments": total_experiments,
            "total_proposals": total_proposals,
            "success_rate": success_rate
        }
    except Exception as e:
        logger.error("Error getting learning status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-log")
async def get_debug_log(session: AsyncSession = Depends(get_db)):
    """Get debug log for learning system from live data"""
    try:
        # Get recent experiments
        recent_experiments_result = await session.execute(
            select(Experiment).order_by(Experiment.created_at.desc()).limit(10)
        )
        recent_experiments = recent_experiments_result.scalars().all()
        
        # Get recent proposals
        recent_proposals_result = await session.execute(
            select(Proposal).order_by(Proposal.created_at.desc()).limit(10)
        )
        recent_proposals = recent_proposals_result.scalars().all()
        
        log_entries = []
        
        # Add experiment entries
        for exp in recent_experiments:
            log_entries.append({
                "timestamp": exp.created_at.isoformat() if exp.created_at is not None else None,
                "level": "INFO",
                "message": f"Experiment {str(exp.id)[:8]} {'completed successfully' if exp.status == 'passed' else 'failed'}",
                "ai_type": exp.ai_type or "unknown"
            })
        
        # Add proposal entries
        for prop in recent_proposals:
            log_entries.append({
                "timestamp": prop.created_at.isoformat() if prop.created_at is not None else None,
                "level": "INFO",
                "message": f"Proposal {str(prop.id)[:8]} {prop.status}",
                "ai_type": prop.ai_type
            })
        
        # Sort by timestamp
        log_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "entries": log_entries[:20],  # Limit to 20 most recent
            "total_entries": len(log_entries),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting debug log", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/all")
async def get_all_logs():
    """
    Return recent learning, audit, and agent logs (from codex_log.json and debug-log).
    """
    logs = []
    codex_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../codex_log.json'))
    if os.path.exists(codex_log_path):
        with open(codex_log_path, 'r', encoding='utf-8') as f:
            logs.extend(json.load(f))
    logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
    return {"logs": logs[:100], "last_updated": datetime.utcnow().isoformat()}


@router.get("/periodic-learning-status")
async def get_periodic_learning_status(session: AsyncSession = Depends(get_db)):
    """Get status of periodic internet learning for all AIs from live data"""
    try:
        # Get periodic learning information from the service
        learning_info = await ai_learning_service.get_last_periodic_learning_info()
        
        # Get recent learning activities from database
        recent_activities_result = await session.execute(
            select(Proposal)
            .where(Proposal.ai_type.in_(["Imperium", "Guardian", "Sandbox", "Conquest"]))
            .order_by(Proposal.created_at.desc())
            .limit(10)
        )
        recent_activities = recent_activities_result.scalars().all()
        
        status = {
            "status": "active" if learning_info["is_periodic_learning_active"] else "inactive",
            "message": "Periodic internet learning system status",
            "timestamp": datetime.utcnow().isoformat(),
            "periodic_learning": {
                "is_active": learning_info["is_periodic_learning_active"],
                "last_learning_time": learning_info["last_learning_time"],
                "next_learning_in_minutes": learning_info["next_learning_in_minutes"],
                "cycle_interval_minutes": 60,
                "ai_types": ["Imperium", "Guardian", "Sandbox", "Conquest"],
                "features": [
                    "internet_search",
                    "knowledge_extraction",
                    "pattern_learning",
                    "adaptive_improvement"
                ]
            },
            "recent_activities": [
                {
                    "ai_type": p.ai_type,
                    "action": f"Proposal {p.status}",
                    "timestamp": p.created_at.isoformat() if p.created_at is not None else None
                }
                for p in recent_activities
            ]
        }
        return status
    except Exception as e:
        logger.error("Error getting periodic learning status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-periodic-learning")
async def trigger_periodic_learning():
    """Manually trigger a periodic learning cycle"""
    try:
        # Trigger the periodic learning manually
        learning_results = await ai_learning_service._perform_periodic_internet_learning()
        
        return {
            "message": "Periodic learning cycle triggered successfully",
            "results": learning_results,
            "timestamp": "2025-07-05T12:00:00Z"
        }
    except Exception as e:
        logger.error("Error triggering periodic learning", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/codex/chapters")
def get_codex_chapters() -> Dict[str, Any]:
    # Placeholder: In a real implementation, fetch from DB or logs
    # Group entries by day, each day is a chapter
    # Each entry: {ai_type, content, timestamp}
    now = datetime.utcnow()
    chapters = []
    for i in range(3):
        day = (now - timedelta(days=i)).strftime('%Y-%m-%d')
        entries = [
            {
                "ai_type": "Imperium",
                "content": f"Learned about ML topic {i+1}.",
                "timestamp": (now - timedelta(days=i, hours=2)).strftime('%H:%M')
            },
            {
                "ai_type": "Guardian",
                "content": f"Discussed system architecture {i+1}.",
                "timestamp": (now - timedelta(days=i, hours=1)).strftime('%H:%M')
            },
        ]
        chapters.append({"day": day, "entries": entries})
    chapters.reverse()  # Oldest first
    return {"chapters": chapters}


@router.get("/insights")
async def get_all_learning_insights():
    """Get all learning insights for all AI types"""
    try:
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        all_insights = {}
        for ai_type in ai_types:
            try:
                insights = await ai_learning_service.get_learning_insights(ai_type)
                all_insights[ai_type] = insights
            except Exception as e:
                all_insights[ai_type] = {"error": str(e)}
        return all_insights
    except Exception as e:
        logger.error("Error getting all learning insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/nodes/{ai_type}")
async def get_learning_nodes(ai_type: str, session: AsyncSession = Depends(get_session)):
    """
    Return a list of learning nodes for the given AI type from the live Neon database.
    """
    result = await session.execute(
        select(Learning).where(Learning.ai_type == ai_type)
    )
    nodes = []
    for row in result.scalars().all():
        nodes.append({
            "id": row.id,
            "name": getattr(row, "learning_type", "Unknown"),
            "unlocked": True,  # You can add logic to determine this
            "timestamp": row.created_at.isoformat() if hasattr(row, "created_at") and row.created_at else None,
            "learning_data": getattr(row, "learning_data", None),
        })
    return {"nodes": nodes, "ai_type": ai_type} 