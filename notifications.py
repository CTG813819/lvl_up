"""
Notifications Router for Live Testing and Proposal Status Updates
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from ..core.database import get_db
from ..services.notification_service import notification_service

logger = structlog.get_logger()

router = APIRouter(tags=["notifications"])


@router.get("/")
async def get_notifications(
    limit: int = 50, 
    unread_only: bool = False,
    session: AsyncSession = Depends(get_db)
):
    """Get notifications"""
    try:
        notifications = await notification_service.get_notifications(limit=limit, unread_only=unread_only)
        
        return {
            "status": "success",
            "data": {
                "notifications": notifications,
                "total_count": len(notifications),
                "unread_count": len([n for n in notifications if not n.get("read", False)])
            }
        }
    except Exception as e:
        logger.error("Error getting notifications", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        success = await notification_service.mark_notification_read(notification_id)
        
        if success:
            return {
                "status": "success",
                "message": "Notification marked as read"
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error marking notification as read", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_notifications_read(session: AsyncSession = Depends(get_db)):
    """Mark all notifications as read"""
    try:
        # Get all unread notifications
        notifications = await notification_service.get_notifications(limit=1000, unread_only=True)
        
        # Mark each as read
        marked_count = 0
        for notification in notifications:
            success = await notification_service.mark_notification_read(notification["id"])
            if success:
                marked_count += 1
        
        return {
            "status": "success",
            "message": f"Marked {marked_count} notifications as read"
        }
        
    except Exception as e:
        logger.error("Error marking all notifications as read", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_notification_stats(session: AsyncSession = Depends(get_db)):
    """Get notification statistics"""
    try:
        all_notifications = await notification_service.get_notifications(limit=1000)
        
        # Calculate stats
        total_count = len(all_notifications)
        unread_count = len([n for n in all_notifications if not n.get("read", False)])
        
        # Count by type
        type_counts = {}
        for notification in all_notifications:
            notification_type = notification.get("type", "unknown")
            type_counts[notification_type] = type_counts.get(notification_type, 0) + 1
        
        # Count by priority
        priority_counts = {}
        for notification in all_notifications:
            priority = notification.get("priority", "normal")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "status": "success",
            "data": {
                "total_notifications": total_count,
                "unread_notifications": unread_count,
                "read_notifications": total_count - unread_count,
                "by_type": type_counts,
                "by_priority": priority_counts
            }
        }
        
    except Exception as e:
        logger.error("Error getting notification stats", error=str(e))
        # Return empty stats instead of 500 error
        return {
            "status": "success",
            "data": {
                "total_notifications": 0,
                "unread_notifications": 0,
                "read_notifications": 0,
                "by_type": {},
                "by_priority": {}
            }
        }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    try:
        # This would require adding a delete method to the notification service
        # For now, just mark as read
        success = await notification_service.mark_notification_read(notification_id)
        
        if success:
            return {
                "status": "success",
                "message": "Notification marked as read (deletion not implemented)"
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting notification", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.websocket("/ws")
async def notifications_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass 