"""
Scheduled Notification Service - Runs weekly token usage notifications
"""

import asyncio
from datetime import datetime, timedelta
import structlog
from typing import Dict, Any

from .weekly_usage_notification_service import weekly_notification_service

logger = structlog.get_logger()


class ScheduledNotificationService:
    """Service to handle scheduled weekly notifications"""
    
    _instance = None
    _initialized = False
    _task = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScheduledNotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._running = False
    
    @classmethod
    async def initialize(cls):
        """Initialize the scheduled notification service"""
        instance = cls()
        logger.info("Scheduled Notification Service initialized")
        return instance
    
    async def start_weekly_scheduler(self):
        """Start the weekly notification scheduler"""
        if self._running:
            logger.warning("Weekly scheduler already running")
            return
        
        self._running = True
        logger.info("Starting weekly notification scheduler")
        
        # Start the background task
        self._task = asyncio.create_task(self._weekly_scheduler_loop())
    
    async def stop_weekly_scheduler(self):
        """Stop the weekly notification scheduler"""
        if not self._running:
            logger.warning("Weekly scheduler not running")
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Weekly notification scheduler stopped")
    
    async def _weekly_scheduler_loop(self):
        """Main scheduler loop for weekly notifications"""
        while self._running:
            try:
                # Calculate next Monday at 9:00 AM UTC
                now = datetime.utcnow()
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0 and now.hour >= 9:
                    # If it's Monday and past 9 AM, schedule for next Monday
                    days_until_monday = 7
                
                next_monday = now.replace(hour=9, minute=0, second=0, microsecond=0)
                next_monday += timedelta(days=days_until_monday)
                
                # Calculate sleep time
                sleep_seconds = (next_monday - now).total_seconds()
                
                logger.info(f"Next weekly notification scheduled for {next_monday.isoformat()} (in {sleep_seconds/3600:.1f} hours)")
                
                # Sleep until next Monday
                await asyncio.sleep(sleep_seconds)
                
                if self._running:
                    # Send weekly notifications
                    logger.info("Sending weekly token usage notifications")
                    result = await weekly_notification_service.send_weekly_notifications()
                    
                    if result.get("status") == "success":
                        logger.info("Weekly notifications sent successfully", 
                                   report=result.get("report", {}),
                                   notifications=result.get("notifications", {}))
                    else:
                        logger.error("Failed to send weekly notifications", 
                                   error=result.get("message", "Unknown error"))
                
            except asyncio.CancelledError:
                logger.info("Weekly scheduler cancelled")
                break
            except Exception as e:
                logger.error("Error in weekly scheduler loop", error=str(e))
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)
    
    async def send_manual_weekly_notification(self) -> Dict[str, Any]:
        """Manually trigger weekly notifications (for testing)"""
        try:
            logger.info("Manually triggering weekly notifications")
            result = await weekly_notification_service.send_weekly_notifications()
            return result
        except Exception as e:
            logger.error("Error sending manual weekly notification", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def get_next_scheduled_time(self) -> Dict[str, Any]:
        """Get information about the next scheduled notification"""
        try:
            now = datetime.utcnow()
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0 and now.hour >= 9:
                days_until_monday = 7
            
            next_monday = now.replace(hour=9, minute=0, second=0, microsecond=0)
            next_monday += timedelta(days=days_until_monday)
            
            return {
                "next_scheduled": next_monday.isoformat(),
                "days_until_next": days_until_monday,
                "hours_until_next": (next_monday - now).total_seconds() / 3600,
                "scheduler_running": self._running
            }
        except Exception as e:
            logger.error("Error getting next scheduled time", error=str(e))
            return {"error": str(e)}


# Global instance
scheduled_notification_service = ScheduledNotificationService() 