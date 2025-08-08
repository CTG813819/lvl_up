"""
Notification Service for Live Testing and Proposal Status Updates
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import get_session
from ..models.sql_models import Notification

logger = structlog.get_logger()


class NotificationService:
    """Service for sending notifications about live testing and proposal status"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the notification service"""
        instance = cls()
        logger.info("Notification Service initialized")
        return instance
    
    async def notify_live_test_started(self, proposal_id: str, ai_type: str, file_path: str) -> bool:
        """Send notification when live testing starts"""
        try:
            notification = Notification(
                title="Live Testing Started",
                message=f"AI {ai_type} proposal for {file_path} is now being live tested",
                type="live_testing",
                priority="normal",
                notification_data={
                    "proposal_id": proposal_id,
                    "ai_type": ai_type,
                    "file_path": file_path,
                    "event": "test_started",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async with get_session() as session:
                session.add(notification)
                await session.commit()
            
            logger.info("Live testing notification sent", 
                       proposal_id=proposal_id, 
                       ai_type=ai_type,
                       file_path=file_path)
            return True
            
        except Exception as e:
            logger.error("Error sending live test started notification", error=str(e))
            return False
    
    async def notify_live_test_completed(self, proposal_id: str, ai_type: str, file_path: str, 
                                       test_result: str, test_summary: str, detailed_results: list) -> bool:
        """Send notification when live testing completes"""
        try:
            # Determine notification type and priority based on result
            if test_result == "passed":
                title = "Live Testing Passed ✅"
                message = f"AI {ai_type} proposal for {file_path} passed live testing"
                notification_type = "live_testing_success"
                priority = "normal"
            elif test_result == "failed":
                title = "Live Testing Failed ❌"
                message = f"AI {ai_type} proposal for {file_path} failed live testing"
                notification_type = "live_testing_failure"
                priority = "high"
            else:
                title = "Live Testing Error ⚠️"
                message = f"AI {ai_type} proposal for {file_path} had errors during live testing"
                notification_type = "live_testing_error"
                priority = "high"
            
            notification = Notification(
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                notification_data={
                    "proposal_id": proposal_id,
                    "ai_type": ai_type,
                    "file_path": file_path,
                    "test_result": test_result,
                    "test_summary": test_summary,
                    "detailed_results": detailed_results,
                    "event": "test_completed",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async with get_session() as session:
                session.add(notification)
                await session.commit()
            
            logger.info("Live testing completion notification sent", 
                       proposal_id=proposal_id, 
                       ai_type=ai_type,
                       file_path=file_path,
                       test_result=test_result)
            return True
            
        except Exception as e:
            logger.error("Error sending live test completion notification", error=str(e))
            return False
    
    async def notify_proposal_ready_for_user(self, proposal_id: str, ai_type: str, file_path: str) -> bool:
        """Send notification when a proposal is ready to be shown to users"""
        try:
            notification = Notification(
                title="New Proposal Ready 🎉",
                message=f"AI {ai_type} proposal for {file_path} has passed live testing and is ready for review",
                type="proposal_ready",
                priority="normal",
                notification_data={
                    "proposal_id": proposal_id,
                    "ai_type": ai_type,
                    "file_path": file_path,
                    "event": "proposal_ready",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async with get_session() as session:
                session.add(notification)
                await session.commit()
            
            logger.info("Proposal ready notification sent", 
                       proposal_id=proposal_id, 
                       ai_type=ai_type,
                       file_path=file_path)
            return True
            
        except Exception as e:
            logger.error("Error sending proposal ready notification", error=str(e))
            return False
    
    async def notify_learning_triggered(self, proposal_id: str, ai_type: str, learning_reason: str) -> bool:
        """Send notification when learning is triggered from failed tests"""
        try:
            notification = Notification(
                title="AI Learning Triggered 🧠",
                message=f"AI {ai_type} is learning from failed test: {learning_reason}",
                type="ai_learning",
                priority="normal",
                notification_data={
                    "proposal_id": proposal_id,
                    "ai_type": ai_type,
                    "learning_reason": learning_reason,
                    "event": "learning_triggered",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            async with get_session() as session:
                session.add(notification)
                await session.commit()
            
            logger.info("Learning triggered notification sent", 
                       proposal_id=proposal_id, 
                       ai_type=ai_type,
                       learning_reason=learning_reason)
            return True
            
        except Exception as e:
            logger.error("Error sending learning triggered notification", error=str(e))
            return False
    
    async def get_notifications(self, limit: int = 50, unread_only: bool = False) -> list:
        """Get notifications"""
        try:
            async with get_session() as session:
                query = select(Notification).order_by(Notification.created_at.desc())
                
                if unread_only:
                    query = query.where(Notification.read == False)
                
                query = query.limit(limit)
                result = await session.execute(query)
                notifications = result.scalars().all()
                
                return [
                    {
                        "id": str(n.id),
                        "title": n.title,
                        "message": n.message,
                        "type": n.type,
                        "priority": n.priority,
                        "read": n.read,
                        "notification_data": n.notification_data,
                        "created_at": n.created_at.isoformat() if n.created_at else None
                    }
                    for n in notifications
                ]
                
        except Exception as e:
            logger.error("Error getting notifications", error=str(e))
            # Return empty list instead of raising exception
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(Notification).where(Notification.id == notification_id)
                )
                notification = result.scalar_one_or_none()
                
                if notification:
                    notification.read = True
                    await session.commit()
                    return True
                return False
                
        except Exception as e:
            logger.error("Error marking notification as read", error=str(e))
            return False


# Global instance
notification_service = NotificationService() 