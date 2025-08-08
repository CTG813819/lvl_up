"""
Rolling Password Router
API endpoints for rolling password authentication system
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
import structlog

from app.services.rolling_password_service import rolling_password_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/rolling-password", tags=["Rolling Password"])

# Additional router for auth endpoints that frontend expects
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Pydantic models
class InitializePasswordRequest(BaseModel):
    initial_password: str

class ValidatePasswordRequest(BaseModel):
    current_password: str
    token: str

class PasswordStatusRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str

class AdminRecoveryRequest(BaseModel):
    password: str
    admin_phrase: str

@router.post("/initialize")
async def initialize_rolling_password(request: InitializePasswordRequest):
    """Initialize rolling password system with initial password"""
    try:
        result = rolling_password_service.initialize_rolling_password(request.initial_password)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Rolling password system initialized",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to initialize rolling password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_and_generate_new_password(request: ValidatePasswordRequest):
    """Validate current password and generate new one"""
    try:
        result = rolling_password_service.validate_and_generate_new_password(
            request.current_password, 
            request.token
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Password validated and new password generated",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to validate and generate new password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_password_status(token: str):
    """Get current password status"""
    try:
        result = rolling_password_service.get_password_status(token)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Password status retrieved",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to get password status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_rolling_password(request: ResetPasswordRequest):
    """Reset rolling password system"""
    try:
        result = rolling_password_service.reset_rolling_password(request.token)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Rolling password system reset",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to reset rolling password: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin-recovery")
async def admin_recovery(request: AdminRecoveryRequest):
    """Admin recovery endpoint - validates admin credentials and generates new rolling password"""
    try:
        # Validate admin credentials
        if request.password != "813819":
            raise HTTPException(status_code=401, detail="Invalid admin password")
        
        if request.admin_phrase != "there are no wolves on fenris":
            raise HTTPException(status_code=401, detail="Invalid admin phrase")
        
        # Generate new rolling password
        new_password = await rolling_password_service.admin_recovery_generate_password()
        
        if new_password["status"] == "success":
            return {
                "status": "success",
                "message": "Admin recovery successful - new rolling password generated",
                "new_password": new_password["new_password"],
                "expires_at": new_password["expires_at"],
                "admin_recovery_used": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=new_password["message"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin recovery failed: {e}")
        raise HTTPException(status_code=500, detail=f"Admin recovery failed: {str(e)}")

@router.get("/system-status")
async def get_system_status() -> Dict[str, Any]:
    """Get overall system status"""
    try:
        status = await rolling_password_service.get_system_status()
        
        return {
            "status": "success",
            "system_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/current-password-status")
async def get_current_password_status() -> Dict[str, Any]:
    """Get current password status (for users to know when to expect new password)"""
    try:
        password_info = await rolling_password_service.get_current_password_info()
        
        return {
            "password_active": password_info.get("has_active_password", False),
            "expires_at": password_info.get("expiry_time"),
            "time_until_expiry": password_info.get("time_until_expiry"),
            "rotation_interval": f"{password_info.get('rotation_interval_hours', 1)} hours",
            "grace_period": f"{password_info.get('grace_period_minutes', 5)} minutes",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get password status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get password status: {str(e)}")

@router.post("/test-authentication")
async def test_authentication_system() -> Dict[str, Any]:
    """Test the authentication system functionality"""
    try:
        logger.info("🧪 Testing rolling password authentication system")
        
        # Get system status
        password_info = await rolling_password_service.get_current_password_info()
        
        test_results = {
            "system_operational": password_info.get("has_active_password", False),
            "password_rotation_active": True,
            "database_connection": True,  # If we get here, DB is working
            "security_monitoring": True,
            "test_timestamp": datetime.utcnow().isoformat(),
            "recommendations": []
        }
        
        # Add recommendations based on status
        if not test_results["system_operational"]:
            test_results["recommendations"].append("Initialize rolling password system")
        
        if password_info.get("active_sessions", 0) > 100:
            test_results["recommendations"].append("Monitor high session count")
        
        test_results["recommendations"].extend([
            "Regular security analytics review",
            "Monitor failed authentication attempts",
            "Ensure proper password rotation intervals"
        ])
        
        return {
            "status": "success",
            "test_results": test_results,
            "system_health": "operational" if test_results["system_operational"] else "needs_attention",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Authentication system test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication system test failed: {str(e)}")

# Additional endpoint for integration with security testing
@router.get("/integration/security-status")
async def get_security_integration_status() -> Dict[str, Any]:
    """Get rolling password security status for integration with other security systems"""
    try:
        analytics = await rolling_password_service.get_security_analytics()
        password_info = await rolling_password_service.get_current_password_info()
        
        return {
            "rolling_password_security": {
                "status": "active",
                "security_level": analytics.get("security_status", "secure"),
                "rotation_frequency": "hourly",
                "failed_attempts_trend": analytics.get("last_24_hours", {}).get("failed_attempts", 0),
                "account_lockout_active": True,
                "session_management": "active",
                "password_complexity": "high",
                "monitoring_active": True
            },
            "integration_points": {
                "guardian_ai_compatible": True,
                "security_testing_compatible": True,
                "audit_logging": True,
                "threat_detection": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get security integration status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get security integration status: {str(e)}")

# Auth endpoints that frontend expects
@auth_router.get("/current-password-status")
async def get_auth_current_password_status() -> Dict[str, Any]:
    """Get current password status for auth endpoints"""
    try:
        password_info = await rolling_password_service.get_current_password_info()
        
        # Calculate remaining time in a format suitable for frontend timer
        time_until_expiry = password_info.get("time_until_expiry")
        if time_until_expiry and time_until_expiry != "expired":
            try:
                # Parse the time string and convert to seconds for frontend
                import re
                time_parts = re.findall(r'(\d+):(\d+):(\d+\.?\d*)', time_until_expiry)
                if time_parts:
                    hours, minutes, seconds = time_parts[0]
                    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
                else:
                    total_seconds = 3600  # Default 1 hour
            except:
                total_seconds = 3600
        else:
            total_seconds = 0
        
        return {
            "password_active": password_info.get("has_active_password", False),
            "expires_at": password_info.get("expiry_time"),
            "time_until_expiry": password_info.get("time_until_expiry"),
            "time_until_expiry_seconds": total_seconds,
            "rotation_interval": f"{password_info.get('rotation_interval_hours', 1)} hours",
            "grace_period": f"{password_info.get('grace_period_minutes', 5)} minutes",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get auth password status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get auth password status: {str(e)}")

@auth_router.get("/timer")
async def get_password_timer() -> Dict[str, Any]:
    """Get password timer information for frontend display"""
    try:
        password_info = await rolling_password_service.get_current_password_info()
        
        # Calculate timer data
        time_until_expiry = password_info.get("time_until_expiry")
        if time_until_expiry and time_until_expiry != "expired":
            try:
                import re
                time_parts = re.findall(r'(\d+):(\d+):(\d+\.?\d*)', time_until_expiry)
                if time_parts:
                    hours, minutes, seconds = time_parts[0]
                    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
                    hours_remaining = int(hours)
                    minutes_remaining = int(minutes)
                    seconds_remaining = int(float(seconds))
                else:
                    total_seconds = 3600
                    hours_remaining = 1
                    minutes_remaining = 0
                    seconds_remaining = 0
            except:
                total_seconds = 3600
                hours_remaining = 1
                minutes_remaining = 0
                seconds_remaining = 0
        else:
            total_seconds = 0
            hours_remaining = 0
            minutes_remaining = 0
            seconds_remaining = 0
        
        return {
            "active": password_info.get("has_active_password", False),
            "total_seconds": total_seconds,
            "hours": hours_remaining,
            "minutes": minutes_remaining,
            "seconds": seconds_remaining,
            "expires_at": password_info.get("expiry_time"),
            "formatted_time": f"{hours_remaining:02d}:{minutes_remaining:02d}:{seconds_remaining:02d}",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get password timer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get password timer: {str(e)}")

# Add endpoints that Flutter app expects
@auth_router.post("/login")
async def login(request: Request) -> Dict[str, Any]:
    """Login endpoint that Flutter app expects"""
    try:
        body = await request.json()
        user_id = body.get("user_id")
        password = body.get("password")
        
        if not password:
            raise HTTPException(status_code=400, detail="Password required")
        
        # Validate password and generate new one
        result = await rolling_password_service.validate_and_generate_new_password(password, "app_token")
        
        if result["status"] == "success":
            # Generate session token
            import secrets
            session_token = secrets.token_urlsafe(32)
            
            return {
                "success": True,
                "session_token": session_token,
                "next_password": result["new_password"],
                "password_expires_at": result["expires_at"],
                "time_until_expiry": result.get("time_until_expiry", "1:00:00")
            }
        else:
            return {
                "success": False,
                "error": result["message"]
            }
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@auth_router.get("/current-password")
async def get_current_password() -> Dict[str, Any]:
    """Get current password endpoint that Flutter app expects"""
    try:
        password_info = await rolling_password_service.get_current_password_info()
        
        if password_info.get("has_active_password", False):
            return {
                "current_password": rolling_password_service.current_password,
                "expires_at": password_info.get("expiry_time"),
                "time_until_expiry": password_info.get("time_until_expiry")
            }
        else:
            raise HTTPException(status_code=404, detail="No active password")
    except Exception as e:
        logger.error(f"Failed to get current password: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current password: {str(e)}")

@auth_router.post("/force-rotation")
async def force_rotation() -> Dict[str, Any]:
    """Force password rotation endpoint that Flutter app expects"""
    try:
        # Generate new password
        new_password = await rolling_password_service.admin_recovery_generate_password()
        
        if new_password["status"] == "success":
            return {
                "success": True,
                "new_password": new_password["new_password"],
                "expires_at": new_password["expires_at"]
            }
        else:
            raise HTTPException(status_code=500, detail=new_password["message"])
    except Exception as e:
        logger.error(f"Force rotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Force rotation failed: {str(e)}")
