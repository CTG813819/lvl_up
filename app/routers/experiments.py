"""
Experiments router for experiment management and tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.sql_models import Proposal

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_experiments_overview():
    """Get experiments system overview"""
    try:
        return {
            "status": "success",
            "message": "Experiments management system is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "experiment_tracking",
                "hypothesis_testing",
                "data_collection",
                "result_analysis",
                "experiment_history"
            ]
        }
    except Exception as e:
        logger.error("Error getting experiments overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_experiments(session: AsyncSession = Depends(get_db)):
    """Get currently active experiments"""
    try:
        # Get active experiments (pending proposals)
        active_result = await session.execute(
            select(Proposal)
            .where(Proposal.status == "pending")
            .order_by(Proposal.created_at.desc())
            .limit(20)
        )
        active_experiments = active_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "active_count": len(active_experiments),
                "experiments": [
                    {
                        "id": str(p.id),
                        "name": f"Experiment {p.id[:8]}",
                        "ai_type": p.ai_type,
                        "status": p.status,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                        "progress": 65.0
                    }
                    for p in active_experiments
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting active experiments", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_experiment_history(session: AsyncSession = Depends(get_db)):
    """Get experiment history and results"""
    try:
        # Get completed experiments
        history_result = await session.execute(
            select(Proposal)
            .where(Proposal.status.in_(["approved", "rejected", "applied"]))
            .order_by(Proposal.created_at.desc())
            .limit(50)
        )
        experiment_history = history_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "total_experiments": len(experiment_history),
                "successful_experiments": len([e for e in experiment_history if e.status == "approved"]),
                "failed_experiments": len([e for e in experiment_history if e.status == "rejected"]),
                "applied_experiments": len([e for e in experiment_history if e.status == "applied"]),
                "history": [
                    {
                        "id": str(p.id),
                        "name": f"Experiment {p.id[:8]}",
                        "ai_type": p.ai_type,
                        "status": p.status,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                        "result": "success" if p.status == "approved" else "failure"
                    }
                    for p in experiment_history
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting experiment history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 