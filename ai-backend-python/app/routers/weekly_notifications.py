"""
Weekly Notifications Router - API endpoints for weekly token usage notifications
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import structlog

from ..core.database import get_session
from ..services.scheduled_notification_service import scheduled_notification_service
from ..services.weekly_usage_notification_service import weekly_notification_service

router = APIRouter(prefix="/api/weekly-notifications", tags=["Weekly Notifications"])
logger = structlog.get_logger()


@router.post("/send")
async def send_weekly_notification(db: AsyncSession = Depends(get_session)):
    """Manually trigger weekly token usage notifications"""
    try:
        result = await scheduled_notification_service.send_manual_weekly_notification()
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "message": "Weekly notifications sent successfully",
                "report": result.get("report", {}),
                "notifications": result.get("notifications", {})
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))
            
    except Exception as e:
        logger.error("Error sending weekly notification", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schedule")
async def get_schedule_info(db: AsyncSession = Depends(get_session)):
    """Get information about the next scheduled weekly notification"""
    try:
        schedule_info = await scheduled_notification_service.get_next_scheduled_time()
        
        if "error" in schedule_info:
            raise HTTPException(status_code=500, detail=schedule_info["error"])
        
        return {
            "status": "success",
            "schedule": schedule_info
        }
        
    except Exception as e:
        logger.error("Error getting schedule info", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-scheduler")
async def start_weekly_scheduler(db: AsyncSession = Depends(get_session)):
    """Start the weekly notification scheduler"""
    try:
        await scheduled_notification_service.start_weekly_scheduler()
        
        return {
            "status": "success",
            "message": "Weekly notification scheduler started"
        }
        
    except Exception as e:
        logger.error("Error starting weekly scheduler", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-scheduler")
async def stop_weekly_scheduler(db: AsyncSession = Depends(get_session)):
    """Stop the weekly notification scheduler"""
    try:
        await scheduled_notification_service.stop_weekly_scheduler()
        
        return {
            "status": "success",
            "message": "Weekly notification scheduler stopped"
        }
        
    except Exception as e:
        logger.error("Error stopping weekly scheduler", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def get_weekly_report(db: AsyncSession = Depends(get_session)):
    """Generate a weekly usage report without sending notifications"""
    try:
        report = await weekly_notification_service.generate_weekly_usage_report()
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return {
            "status": "success",
            "report": report
        }
        
    except Exception as e:
        logger.error("Error generating weekly report", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_notification_status(db: AsyncSession = Depends(get_session)):
    """Get the current status of weekly notifications"""
    try:
        schedule_info = await scheduled_notification_service.get_next_scheduled_time()
        
        # Get recent notifications
        from sqlalchemy import select, desc
        from ..models.sql_models import Notification
        
        async with get_session() as session:
            stmt = select(Notification).where(
                Notification.type == "weekly_token_usage"
            ).order_by(desc(Notification.created_at)).limit(5)
            
            result = await session.execute(stmt)
            recent_notifications = result.scalars().all()
            
            notifications = []
            for notif in recent_notifications:
                notifications.append({
                    "id": str(notif.id),
                    "title": notif.title,
                    "message": notif.message,
                    "priority": notif.priority,
                    "created_at": notif.created_at.isoformat(),
                    "read": notif.read
                })
        
        return {
            "status": "success",
            "scheduler_running": schedule_info.get("scheduler_running", False),
            "next_scheduled": schedule_info.get("next_scheduled"),
            "recent_notifications": notifications
        }
        
    except Exception as e:
        logger.error("Error getting notification status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 