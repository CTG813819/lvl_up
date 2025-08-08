"""
Weekly Token Usage Notification Service
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog
from sqlalchemy import select, func

from ..core.database import get_session
from ..models.sql_models import TokenUsage, Notification
from ..services.token_usage_service import token_usage_service
from ..core.config import settings

logger = structlog.get_logger()

# Twilio configuration (you'll need to add these to your .env file)
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
ADMIN_PHONE_NUMBER = "your_admin_phone_number"  # Where to send SMS notifications


class WeeklyUsageNotificationService:
    """Service to send weekly token usage notifications"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WeeklyUsageNotificationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the weekly notification service"""
        instance = cls()
        logger.info("Weekly Usage Notification Service initialized")
        return instance
    
    async def generate_weekly_usage_report(self) -> Dict[str, Any]:
        """Generate a comprehensive weekly usage report"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            # Get all AI usage for current month
            all_usage = await token_usage_service.get_all_monthly_usage(current_month)
            
            # Calculate summary statistics
            total_tokens = all_usage.get("summary", {}).get("total_tokens", 0)
            total_requests = all_usage.get("summary", {}).get("total_requests", 0)
            ai_count = all_usage.get("summary", {}).get("ai_count", 0)
            
            # Calculate usage percentage
            usage_percentage = (total_tokens / 140000) * 100  # 140K is the enforced limit
            
            # Get alerts
            alerts = await token_usage_service.get_usage_alerts()
            
            # Generate AI-specific breakdown
            ai_breakdown = []
            for ai_type, usage in all_usage.get("ai_usage", {}).items():
                ai_breakdown.append({
                    "ai_type": ai_type,
                    "tokens_used": usage.get("total_tokens", 0),
                    "requests": usage.get("request_count", 0),
                    "percentage": usage.get("usage_percentage", 0)
                })
            
            # Determine status and recommendations
            status = "normal"
            if usage_percentage >= 95:
                status = "critical"
            elif usage_percentage >= 80:
                status = "warning"
            
            recommendations = []
            if usage_percentage >= 80:
                recommendations.append("Consider reducing AI activity to stay within limits")
            if usage_percentage >= 90:
                recommendations.append("Critical: Token usage approaching monthly limit")
            
            return {
                "week_ending": datetime.utcnow().strftime("%Y-%m-%d"),
                "total_tokens_used": total_tokens,
                "total_requests": total_requests,
                "usage_percentage": round(usage_percentage, 2),
                "status": status,
                "ai_count": ai_count,
                "ai_breakdown": ai_breakdown,
                "alerts": alerts,
                "recommendations": recommendations,
                "monthly_limit": 140000,
                "remaining_tokens": 140000 - total_tokens
            }
            
        except Exception as e:
            logger.error("Error generating weekly usage report", error=str(e))
            return {"error": str(e)}
    
    async def send_in_app_notification(self, report: Dict[str, Any]) -> bool:
        """Send in-app notification with weekly usage report"""
        try:
            # Create notification message
            status_emoji = {
                "normal": "✅",
                "warning": "⚠️", 
                "critical": "🚨"
            }.get(report.get("status", "normal"), "ℹ️")
            
            title = f"{status_emoji} Weekly Token Usage Report"
            
            # Create detailed message
            message_parts = [
                f"Week ending: {report.get('week_ending', 'N/A')}",
                f"Total tokens used: {report.get('total_tokens_used', 0):,}",
                f"Usage percentage: {report.get('usage_percentage', 0):.1f}%",
                f"Remaining tokens: {report.get('remaining_tokens', 0):,}",
                f"Total requests: {report.get('total_requests', 0)}"
            ]
            
            # Add AI breakdown
            if report.get("ai_breakdown"):
                message_parts.append("\nAI Breakdown:")
                for ai in report["ai_breakdown"]:
                    message_parts.append(f"• {ai['ai_type']}: {ai['tokens_used']:,} tokens ({ai['percentage']:.1f}%)")
            
            # Add recommendations
            if report.get("recommendations"):
                message_parts.append("\nRecommendations:")
                for rec in report["recommendations"]:
                    message_parts.append(f"• {rec}")
            
            message = "\n".join(message_parts)
            
            # Create notification in database
            async with get_session() as session:
                notification = Notification(
                    title=title,
                    message=message,
                    type="weekly_token_usage",
                    priority="high" if report.get("status") in ["warning", "critical"] else "normal",
                    notification_data={
                        "report": report,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                session.add(notification)
                await session.commit()
                
                logger.info("In-app weekly usage notification created", 
                           notification_id=str(notification.id),
                           status=report.get("status"))
                
                return True
                
        except Exception as e:
            logger.error("Error sending in-app notification", error=str(e))
            return False
    
    async def send_sms_notification(self, report: Dict[str, Any]) -> bool:
        """Send SMS notification with weekly usage summary"""
        try:
            # Create concise SMS message
            status_emoji = {
                "normal": "✅",
                "warning": "⚠️",
                "critical": "🚨"
            }.get(report.get("status", "normal"), "ℹ️")
            
            usage_percentage = report.get("usage_percentage", 0)
            total_tokens = report.get("total_tokens_used", 0)
            remaining = report.get("remaining_tokens", 0)
            
            sms_message = (
                f"{status_emoji} Weekly Token Usage Report\n"
                f"Usage: {usage_percentage:.1f}% ({total_tokens:,} tokens)\n"
                f"Remaining: {remaining:,} tokens\n"
                f"Status: {report.get('status', 'normal').upper()}"
            )
            
            # Add critical warning if needed
            if report.get("status") == "critical":
                sms_message += "\n🚨 CRITICAL: Approaching monthly limit!"
            
            # Send SMS via Twilio (you'll need to configure this)
            if hasattr(settings, 'twilio_account_sid') and settings.twilio_account_sid:
                await self._send_twilio_sms(sms_message)
            else:
                # Log the message for now (you can configure Twilio later)
                logger.info("SMS notification (Twilio not configured)", message=sms_message)
            
            return True
            
        except Exception as e:
            logger.error("Error sending SMS notification", error=str(e))
            return False
    
    async def _send_twilio_sms(self, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            # You'll need to add Twilio credentials to your .env file
            # TWILIO_ACCOUNT_SID=your_account_sid
            # TWILIO_AUTH_TOKEN=your_auth_token
            # TWILIO_PHONE_NUMBER=your_twilio_number
            # ADMIN_PHONE_NUMBER=your_admin_number
            
            if not all([settings.twilio_account_sid, settings.twilio_auth_token, 
                       settings.twilio_phone_number, settings.admin_phone_number]):
                logger.warning("Twilio credentials not fully configured")
                return False
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
            
            data = {
                "From": settings.twilio_phone_number,
                "To": settings.admin_phone_number,
                "Body": message
            }
            
            auth = (settings.twilio_account_sid, settings.twilio_auth_token)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, auth=auth) as response:
                    if response.status == 201:
                        logger.info("SMS notification sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send SMS: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error("Error sending Twilio SMS", error=str(e))
            return False
    
    async def send_weekly_notifications(self) -> Dict[str, Any]:
        """Send both in-app and SMS weekly notifications"""
        try:
            logger.info("Starting weekly token usage notifications")
            
            # Generate report
            report = await self.generate_weekly_usage_report()
            
            if "error" in report:
                return {"status": "error", "message": report["error"]}
            
            # Send notifications
            in_app_success = await self.send_in_app_notification(report)
            sms_success = await self.send_sms_notification(report)
            
            return {
                "status": "success",
                "report": report,
                "notifications": {
                    "in_app": in_app_success,
                    "sms": sms_success
                }
            }
            
        except Exception as e:
            logger.error("Error sending weekly notifications", error=str(e))
            return {"status": "error", "message": str(e)}


# Global instance
weekly_notification_service = WeeklyUsageNotificationService() 