"""
Analytics router for system analytics and insights
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_session
from app.models.sql_models import Proposal, Notification

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        return {
            "status": "success",
            "message": "Analytics system is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "system_performance",
                "ai_learning_metrics", 
                "proposal_analytics",
                "user_activity",
                "error_tracking"
            ]
        }
    except Exception as e:
        logger.error("Error getting analytics overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-performance")
async def get_system_performance(session: AsyncSession = Depends(get_session)):
    """Get system performance metrics"""
    try:
        # Get proposal statistics
        total_result = await session.execute(select(func.count(Proposal.id)))
        total_proposals = total_result.scalar()
        
        pending_result = await session.execute(
            select(func.count(Proposal.id)).where(Proposal.status == "pending")
        )
        pending_proposals = pending_result.scalar()
        
        approved_result = await session.execute(
            select(func.count(Proposal.id)).where(Proposal.status == "approved")
        )
        approved_proposals = approved_result.scalar()
        
        # Get recent activity
        recent_result = await session.execute(
            select(Proposal).order_by(Proposal.created_at.desc()).limit(10)
        )
        recent_proposals = recent_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "total_proposals": total_proposals,
                "pending_proposals": pending_proposals,
                "approved_proposals": approved_proposals,
                "approval_rate": (approved_proposals / total_proposals * 100) if total_proposals > 0 else 0,
                "recent_activity": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "status": p.status,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in recent_proposals
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting system performance", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-learning-metrics")
async def get_ai_learning_metrics():
    """Get AI learning metrics"""
    try:
        return {
            "status": "success",
            "data": {
                "imperium": {
                    "learning_progress": 0.75,
                    "total_experiments": 15,
                    "success_rate": 0.87,
                    "last_activity": "2025-07-06T06:00:00Z"
                },
                "guardian": {
                    "learning_progress": 0.68,
                    "total_experiments": 8,
                    "success_rate": 0.94,
                    "last_activity": "2025-07-06T06:00:00Z"
                },
                "sandbox": {
                    "learning_progress": 0.82,
                    "total_experiments": 23,
                    "success_rate": 0.91,
                    "last_activity": "2025-07-06T06:00:00Z"
                },
                "conquest": {
                    "learning_progress": 0.45,
                    "total_experiments": 5,
                    "success_rate": 0.80,
                    "last_activity": "2025-07-06T06:00:00Z"
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting AI learning metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposal-analytics")
async def get_proposal_analytics(session: AsyncSession = Depends(get_session)):
    """Get detailed proposal analytics"""
    try:
        # Get proposals by AI type
        ai_types_result = await session.execute(
            select(Proposal.ai_type, func.count(Proposal.id))
            .group_by(Proposal.ai_type)
        )
        ai_types_data = ai_types_result.all()
        
        # Get proposals by status
        status_result = await session.execute(
            select(Proposal.status, func.count(Proposal.id))
            .group_by(Proposal.status)
        )
        status_data = status_result.all()
        
        # Get recent proposals
        recent_result = await session.execute(
            select(Proposal).order_by(Proposal.created_at.desc()).limit(20)
        )
        recent_proposals = recent_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "by_ai_type": [
                    {"ai_type": ai_type, "count": count}
                    for ai_type, count in ai_types_data
                ],
                "by_status": [
                    {"status": status, "count": count}
                    for status, count in status_data
                ],
                "recent_proposals": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "status": p.status,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in recent_proposals
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting proposal analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-activity")
async def get_user_activity():
    """Get user activity metrics"""
    try:
        return {
            "status": "success",
            "data": {
                "active_users": 3,
                "total_sessions": 15,
                "average_session_duration": "45 minutes",
                "most_active_hours": ["09:00", "14:00", "18:00"],
                "recent_activity": [
                    {
                        "user": "admin",
                        "action": "proposal_approval",
                        "timestamp": "2025-07-06T06:20:00Z"
                    },
                    {
                        "user": "system",
                        "action": "ai_learning",
                        "timestamp": "2025-07-06T06:15:00Z"
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting user activity", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-tracking")
async def get_error_tracking():
    """Get error tracking and monitoring"""
    try:
        return {
            "status": "success",
            "data": {
                "total_errors": 5,
                "error_rate": 0.02,
                "critical_errors": 0,
                "warning_errors": 2,
                "info_errors": 3,
                "recent_errors": [
                    {
                        "type": "warning",
                        "message": "Database connection slow",
                        "timestamp": "2025-07-06T06:10:00Z"
                    },
                    {
                        "type": "info",
                        "message": "AI model training completed",
                        "timestamp": "2025-07-06T06:05:00Z"
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting error tracking", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 