"""
Advanced Notification System for AI Backend
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_session
from app.models.sql_models import Notification, Proposal
from app.services.ai_agent_service import AIAgentService
from app.services.conquest_ai_service import ConquestAIService
from app.services.ai_learning_service import AILearningService

logger = structlog.get_logger()
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()


@router.get("/")
async def get_notifications(
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    unread_only: bool = False
):
    """Get notifications with filtering options"""
    try:
        query = select(Notification)
        
        if unread_only:
            query = query.where(Notification.read == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await session.execute(query)
        notifications = result.scalars().all()
        
        return {
            "notifications": [
                {
                    "id": str(n.id),
                    "title": n.title,
                    "message": n.message,
                    "type": n.type,
                    "priority": n.priority,
                    "read": n.read,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                    "metadata": n.notification_data
                }
                for n in notifications
            ],
            "total": len(notifications),
            "unread_count": len([n for n in notifications if not n.read]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notifications", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_notification(
    title: str,
    message: str,
    notification_type: str = "info",
    priority: str = "normal",
    metadata: Optional[Dict] = None,
    session: AsyncSession = Depends(get_session)
):
    """Create a new notification"""
    try:
        notification = Notification(
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            notification_data=metadata or {},
            created_at=datetime.utcnow(),
            read=False
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        
        # Broadcast to WebSocket connections
        await manager.broadcast(json.dumps({
            "type": "notification",
            "data": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "priority": notification.priority,
                "created_at": notification.created_at.isoformat()
            }
        }))
        
        return {
            "status": "success",
            "notification": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "priority": notification.priority,
                "created_at": notification.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error("Error creating notification", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Mark a notification as read"""
    try:
        result = await session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.read = True
        await session.commit()
        
        return {"status": "success", "message": "Notification marked as read"}
    except Exception as e:
        logger.error("Error marking notification as read", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_notifications_read(session: AsyncSession = Depends(get_session)):
    """Mark all notifications as read"""
    try:
        await session.execute(
            "UPDATE notifications SET read = true WHERE read = false"
        )
        await session.commit()
        
        return {"status": "success", "message": "All notifications marked as read"}
    except Exception as e:
        logger.error("Error marking all notifications as read", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_notification_stats(session: AsyncSession = Depends(get_session)):
    """Get notification statistics"""
    try:
        # Get total notifications
        total_result = await session.execute(select(Notification))
        total_notifications = len(total_result.scalars().all())
        
        # Get unread notifications
        unread_result = await session.execute(
            select(Notification).where(Notification.read == False)
        )
        unread_notifications = len(unread_result.scalars().all())
        
        # Get notifications by type
        types_result = await session.execute(
            "SELECT type, COUNT(*) as count FROM notifications GROUP BY type"
        )
        notifications_by_type = {row[0]: row[1] for row in types_result}
        
        # Get notifications by priority
        priority_result = await session.execute(
            "SELECT priority, COUNT(*) as count FROM notifications GROUP BY priority"
        )
        notifications_by_priority = {row[0]: row[1] for row in priority_result}
        
        return {
            "stats": {
                "total": total_notifications,
                "unread": unread_notifications,
                "read": total_notifications - unread_notifications,
                "by_type": notifications_by_type,
                "by_priority": notifications_by_priority
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting notification stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for testing
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Notification triggers for important events
async def notify_conquest_progress(operation_id: str, progress: Dict):
    """Notify about Conquest AI operation progress"""
    try:
        title = f"Conquest AI Progress: {progress.get('stage', 'Unknown')}"
        message = f"Operation {operation_id}: {progress.get('message', 'Progress update')}"
        
        # Create notification
        from app.core.database import get_session
        session = get_session()
        
        notification = Notification(
            title=title,
            message=message,
            type="conquest_progress",
            priority="high" if progress.get('stage') in ['building_apk', 'deploying'] else "normal",
            notification_data={
                "operation_id": operation_id,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            read=False
        )
        
        session.add(notification)
        await session.commit()
        
        # Broadcast to WebSocket
        await manager.broadcast(json.dumps({
            "type": "conquest_progress",
            "data": {
                "operation_id": operation_id,
                "progress": progress,
                "notification": {
                    "title": title,
                    "message": message,
                    "type": "conquest_progress"
                }
            }
        }))
        
    except Exception as e:
        logger.error("Error creating conquest progress notification", error=str(e))


async def notify_ai_learning_milestone(milestone: Dict):
    """Notify about AI learning milestones"""
    try:
        title = f"AI Learning Milestone: {milestone.get('type', 'Unknown')}"
        message = f"AI has learned: {milestone.get('description', 'New knowledge acquired')}"
        
        notification = Notification(
            title=title,
            message=message,
            type="ai_learning",
            priority="medium",
            notification_data=milestone,
            created_at=datetime.utcnow(),
            read=False
        )
        
        # Add to database and broadcast
        # (Implementation similar to above)
        
    except Exception as e:
        logger.error("Error creating AI learning notification", error=str(e))


async def notify_proposal_status_change(proposal_id: str, new_status: str):
    """Notify about proposal status changes"""
    try:
        title = f"Proposal Status Update: {new_status.title()}"
        message = f"Proposal {proposal_id} status changed to {new_status}"
        
        notification = Notification(
            title=title,
            message=message,
            type="proposal_update",
            priority="normal",
            notification_data={
                "proposal_id": proposal_id,
                "new_status": new_status,
                "timestamp": datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            read=False
        )
        
        # Add to database and broadcast
        # (Implementation similar to above)
        
    except Exception as e:
        logger.error("Error creating proposal notification", error=str(e))


@router.post("/test-broadcast")
async def test_broadcast():
    """Test WebSocket broadcast functionality"""
    try:
        test_message = {
            "type": "test",
            "data": {
                "message": "Test notification broadcast",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        await manager.broadcast(json.dumps(test_message))
        
        return {
            "status": "success",
            "message": "Test broadcast sent",
            "active_connections": len(manager.active_connections)
        }
    except Exception as e:
        logger.error("Error testing broadcast", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 