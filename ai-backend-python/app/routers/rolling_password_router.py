"""
Rolling Password Router
Provides endpoints for rolling password management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog
from datetime import datetime

from app.services.rolling_password_service import rolling_password_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/rolling-password", tags=["Rolling Password"])

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
async def reset_password_system(request: ResetPasswordRequest):
    """Reset password system for a token"""
    try:
        result = rolling_password_service.reset_password_system(request.token)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Password system reset successfully",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to reset password system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_system_stats():
    """Get rolling password system statistics"""
    try:
        result = rolling_password_service.get_system_stats()
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "System statistics retrieved",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 