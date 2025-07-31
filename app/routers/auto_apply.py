"""
Auto-Apply Router for Real-Time Proposal Application
==================================================

This router provides endpoints for controlling and monitoring the auto-apply service
that automatically applies proposals to the app after user approval.

ENDPOINTS:
- GET /api/auto-apply/stats - Get auto-apply statistics
- POST /api/auto-apply/start - Start auto-apply monitoring
- POST /api/auto-apply/stop - Stop auto-apply monitoring
- POST /api/auto-apply/manual/{proposal_id} - Manually trigger auto-apply
- GET /api/auto-apply/status - Get auto-apply service status
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import structlog

from ..services.auto_apply_service import auto_apply_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/auto-apply", tags=["Auto-Apply Service"])


@router.get("/stats")
async def get_auto_apply_stats():
    """Get auto-apply service statistics"""
    try:
        stats = await auto_apply_service.get_auto_apply_stats()
        return {
            "status": "success",
            "data": stats,
            "message": "Auto-apply statistics retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting auto-apply stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_auto_apply_monitoring():
    """Start auto-apply monitoring for approved proposals"""
    try:
        await auto_apply_service.start_monitoring()
        return {
            "status": "success",
            "message": "Auto-apply monitoring started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting auto-apply monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_auto_apply_monitoring():
    """Stop auto-apply monitoring"""
    try:
        await auto_apply_service.stop_monitoring()
        return {
            "status": "success",
            "message": "Auto-apply monitoring stopped successfully"
        }
    except Exception as e:
        logger.error(f"Error stopping auto-apply monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual/{proposal_id}")
async def manual_auto_apply_proposal(proposal_id: str):
    """Manually trigger auto-apply for a specific proposal"""
    try:
        result = await auto_apply_service.manual_auto_apply_proposal(proposal_id)
        
        if result.get("success"):
            return {
                "status": "success",
                "data": result,
                "message": "Proposal auto-applied successfully"
            }
        else:
            return {
                "status": "error",
                "data": result,
                "message": result.get("error", "Auto-apply failed")
            }
    except Exception as e:
        logger.error(f"Error in manual auto-apply: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_auto_apply_status():
    """Get auto-apply service status"""
    try:
        stats = await auto_apply_service.get_auto_apply_stats()
        
        return {
            "status": "success",
            "data": {
                "is_monitoring": stats.get("is_monitoring", False),
                "auto_applied_count": stats.get("auto_applied_count", 0),
                "auto_apply_failed_count": stats.get("auto_apply_failed_count", 0),
                "pending_auto_apply_count": stats.get("pending_auto_apply_count", 0),
                "last_check": stats.get("last_check"),
                "service_status": "running" if stats.get("is_monitoring") else "stopped"
            },
            "message": "Auto-apply service status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error getting auto-apply status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 