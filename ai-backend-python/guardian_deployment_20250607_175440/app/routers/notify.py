"""
Notify router for notification management and delivery
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_session
from app.models.sql_models import Notification

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_notify_overview():
    """Get notification system overview"""
    try:
        return {
            "status": "success",
            "message": "Notification system is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "notification_delivery",
                "notification_templates",
                "notification_channels",
                "notification_scheduling",
                "notification_tracking"
            ]
        }
    except Exception as e:
        logger.error("Error getting notify overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_notification(
    title: str,
    message: str,
    channel: str = "system",
    priority: str = "normal",
    session: AsyncSession = Depends(get_session)
):
    """Send a notification"""
    try:
        # Create notification
        notification = Notification(
            title=title,
            message=message,
            type=channel,
            priority=priority,
            notification_data={
                "channel": channel,
                "sent_at": datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            read=False
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        return {
            "status": "success",
            "data": {
                "notification_id": str(notification.id),
                "title": title,
                "message": message,
                "channel": channel,
                "priority": priority,
                "sent_at": notification.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error("Error sending notification", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_notification_templates():
    """Get available notification templates"""
    try:
        return {
            "status": "success",
            "data": {
                "templates": [
                    {
                        "id": "proposal_approved",
                        "name": "Proposal Approved",
                        "title": "Proposal {proposal_id} has been approved",
                        "message": "Your proposal has been approved and will be applied.",
                        "variables": ["proposal_id"]
                    },
                    {
                        "id": "system_alert",
                        "name": "System Alert",
                        "title": "System Alert: {alert_type}",
                        "message": "System alert: {alert_message}",
                        "variables": ["alert_type", "alert_message"]
                    },
                    {
                        "id": "ai_learning",
                        "name": "AI Learning Update",
                        "title": "AI Learning Progress: {ai_type}",
                        "message": "AI {ai_type} has learned new patterns: {learning_summary}",
                        "variables": ["ai_type", "learning_summary"]
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notification templates", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels")
async def get_notification_channels():
    """Get available notification channels"""
    try:
        return {
            "status": "success",
            "data": {
                "channels": [
                    {
                        "id": "system",
                        "name": "System Notifications",
                        "description": "Internal system notifications",
                        "status": "active"
                    },
                    {
                        "id": "email",
                        "name": "Email Notifications",
                        "description": "Email delivery",
                        "status": "configured"
                    },
                    {
                        "id": "webhook",
                        "name": "Webhook Notifications",
                        "description": "HTTP webhook delivery",
                        "status": "active"
                    },
                    {
                        "id": "websocket",
                        "name": "WebSocket Notifications",
                        "description": "Real-time WebSocket delivery",
                        "status": "active"
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notification channels", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_notification_stats(session: AsyncSession = Depends(get_session)):
    """Get notification statistics"""
    try:
        # Get total notifications
        total_result = await session.execute(select(Notification))
        total_notifications = len(total_result.scalars().all())
        
        # Get notifications by type
        types_result = await session.execute(
            select(Notification.type, func.count(Notification.id))
            .group_by(Notification.type)
        )
        notifications_by_type = types_result.all()
        
        # Get recent notifications
        recent_result = await session.execute(
            select(Notification)
            .order_by(Notification.created_at.desc())
            .limit(10)
        )
        recent_notifications = recent_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "total_notifications": total_notifications,
                "by_type": [
                    {"type": n_type, "count": count}
                    for n_type, count in notifications_by_type
                ],
                "recent_notifications": [
                    {
                        "id": str(n.id),
                        "title": n.title,
                        "type": n.type,
                        "priority": n.priority,
                        "created_at": n.created_at.isoformat() if n.created_at else None
                    }
                    for n in recent_notifications
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notification stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 