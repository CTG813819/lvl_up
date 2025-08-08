"""
Rolling Password Service
Provides rolling password authentication with automatic rotation
"""

import asyncio
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class RollingPasswordService:
    """Service for managing rolling password authentication"""
    
    def __init__(self):
        self.current_password = None
        self.password_expiry = None
        self.rotation_interval_hours = 1
        self.grace_period_minutes = 5
        self.failed_attempts = {}
        self.active_sessions = {}
        self.security_analytics = {
            "last_24_hours": {
                "successful_logins": 0,
                "failed_attempts": 0,
                "password_rotations": 0
            },
            "current_active_sessions": 0,
            "security_status": "secure"
        }
        self.initialized = False
    
    async def initialize_rolling_password(self, initial_password: str) -> Dict[str, Any]:
        """Initialize the rolling password system"""
        try:
            self.current_password = initial_password
            self.password_expiry = datetime.utcnow() + timedelta(hours=self.rotation_interval_hours)
            self.initialized = True
            
            logger.info("🔐 Rolling password system initialized")
            
            return {
                "status": "success",
                "message": "Rolling password system initialized",
                "expires_at": self.password_expiry.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to initialize rolling password: {e}")
            return {"status": "error", "message": str(e)}
    
    async def validate_and_generate_new_password(self, current_password: str, token: str) -> Dict[str, Any]:
        """Validate current password and generate new one"""
        try:
            if not self.initialized:
                return {"status": "error", "message": "System not initialized"}
            
            if current_password != self.current_password:
                return {"status": "error", "message": "Invalid password"}
            
            # Generate new password
            new_password = secrets.token_urlsafe(16)
            self.current_password = new_password
            self.password_expiry = datetime.utcnow() + timedelta(hours=self.rotation_interval_hours)
            
            logger.info("🔄 Password rotated successfully")
            
            return {
                "status": "success",
                "message": "Password validated and new password generated",
                "new_password": new_password,
                "expires_at": self.password_expiry.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to validate and generate new password: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_password_status(self, token: str) -> Dict[str, Any]:
        """Get current password status"""
        try:
            if not self.initialized:
                return {"status": "error", "message": "System not initialized"}
            
            return {
                "status": "success",
                "has_active_password": self.current_password is not None,
                "expires_at": self.password_expiry.isoformat() if self.password_expiry else None,
                "time_until_expiry": self._get_time_until_expiry()
            }
        except Exception as e:
            logger.error(f"Failed to get password status: {e}")
            return {"status": "error", "message": str(e)}
    
    async def reset_rolling_password(self, token: str) -> Dict[str, Any]:
        """Reset the rolling password system"""
        try:
            self.current_password = None
            self.password_expiry = None
            self.failed_attempts = {}
            self.active_sessions = {}
            self.initialized = False
            
            logger.info("🔄 Rolling password system reset")
            
            return {
                "status": "success",
                "message": "Rolling password system reset"
            }
        except Exception as e:
            logger.error(f"Failed to reset rolling password: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            return {
                "initialized": self.initialized,
                "has_active_password": self.current_password is not None,
                "active_sessions": len(self.active_sessions),
                "failed_attempts_24h": self.security_analytics["last_24_hours"]["failed_attempts"],
                "successful_logins_24h": self.security_analytics["last_24_hours"]["successful_logins"],
                "security_status": self.security_analytics["security_status"]
            }
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    async def get_current_password_info(self) -> Dict[str, Any]:
        """Get current password information"""
        try:
            return {
                "has_active_password": self.current_password is not None,
                "expiry_time": self.password_expiry.isoformat() if self.password_expiry else None,
                "time_until_expiry": self._get_time_until_expiry(),
                "rotation_interval_hours": self.rotation_interval_hours,
                "grace_period_minutes": self.grace_period_minutes,
                "active_sessions": len(self.active_sessions)
            }
        except Exception as e:
            logger.error(f"Failed to get current password info: {e}")
            return {"error": str(e)}
    
    async def get_security_analytics(self) -> Dict[str, Any]:
        """Get security analytics"""
        try:
            return self.security_analytics
        except Exception as e:
            logger.error(f"Failed to get security analytics: {e}")
            return {"error": str(e)}
    
    def _get_time_until_expiry(self) -> Optional[str]:
        """Get time until password expires"""
        if not self.password_expiry:
            return None
        
        time_remaining = self.password_expiry - datetime.utcnow()
        if time_remaining.total_seconds() <= 0:
            return "expired"
        
        return str(time_remaining)


# Global service instance
rolling_password_service = RollingPasswordService()

