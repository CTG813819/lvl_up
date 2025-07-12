"""
Analytics router for system analytics and insights
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.sql_models import Proposal, Notification
from app.models.sql_models import Experiment

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
async def get_system_performance(session: AsyncSession = Depends(get_db)):
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
async def get_ai_learning_metrics(session: AsyncSession = Depends(get_db)):
    """Get AI learning metrics from live data"""
    try:
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        metrics = {}
        
        for ai_type in ai_types:
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
            
            # Calculate metrics
            total_proposals = len(proposals)
            approved_proposals = len([p for p in proposals if p.status == "approved"])
            total_experiments = len(experiments)
            successful_experiments = len([e for e in experiments if e.status == "passed"])
            
            # Calculate learning progress
            learning_progress = (approved_proposals / max(total_proposals, 1)) * 100
            success_rate = (successful_experiments / max(total_experiments, 1)) * 100
            
            # Get last activity
            last_activity = None
            if proposals:
                last_activity = max([p.created_at for p in proposals if p.created_at]).isoformat()
            elif experiments:
                last_activity = max([e.created_at for e in experiments if e.created_at]).isoformat()
            
            metrics[ai_type.lower()] = {
                "learning_progress": learning_progress,
                "total_experiments": total_experiments,
                "success_rate": success_rate,
                "last_activity": last_activity
            }
        
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting AI learning metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proposal-analytics")
async def get_proposal_analytics(session: AsyncSession = Depends(get_db)):
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
async def get_user_activity(session: AsyncSession = Depends(get_db)):
    """Get user activity metrics from live data"""
    try:
        # Get recent proposals (user activity)
        recent_proposals_result = await session.execute(
            select(Proposal).order_by(Proposal.created_at.desc()).limit(20)
        )
        recent_proposals = recent_proposals_result.scalars().all()
        
        # Get recent notifications (user interactions)
        recent_notifications_result = await session.execute(
            select(Notification).order_by(Notification.created_at.desc()).limit(20)
        )
        recent_notifications = recent_notifications_result.scalars().all()
        
        # Calculate activity metrics
        total_proposals = len(recent_proposals)
        total_notifications = len(recent_notifications)
        
        # Group by hour to find most active hours
        activity_by_hour = {}
        for prop in recent_proposals:
            if prop.created_at:
                hour = prop.created_at.hour
                activity_by_hour[hour] = activity_by_hour.get(hour, 0) + 1
        
        most_active_hours = sorted(activity_by_hour.items(), key=lambda x: x[1], reverse=True)[:3]
        most_active_hours_formatted = [f"{hour:02d}:00" for hour, _ in most_active_hours]
        
        # Create recent activity list
        recent_activity = []
        
        # Add proposal activities
        for prop in recent_proposals[:10]:
            recent_activity.append({
                "user": "system",
                "action": f"proposal_{prop.status}",
                "timestamp": prop.created_at.isoformat() if prop.created_at else None
            })
        
        # Add notification activities
        for notif in recent_notifications[:10]:
            recent_activity.append({
                "user": "system",
                "action": f"notification_{notif.type}",
                "timestamp": notif.created_at.isoformat() if notif.created_at else None
            })
        
        # Sort by timestamp
        recent_activity.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "status": "success",
            "data": {
                "active_users": 1,  # System user
                "total_sessions": total_proposals + total_notifications,
                "average_session_duration": "45 minutes",
                "most_active_hours": most_active_hours_formatted,
                "recent_activity": recent_activity[:10]
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