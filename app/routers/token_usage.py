"""
Token Usage Router - Monitor and manage AI token usage
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from ..services.token_usage_service import token_usage_service
from ..services.unified_ai_service import unified_ai_service_shared
from ..core.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/api/token-usage", tags=["Token Usage"])


@router.get("/summary")
async def get_token_usage_summary():
    """Get summary of token usage for all AIs"""
    try:
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "usage_summary": all_usage,
            "emergency_status": emergency_status,
            "limits": {
                "anthropic_monthly": settings.anthropic_monthly_limit,
                "openai_monthly": settings.openai_monthly_limit,
                "anthropic_threshold": settings.openai_fallback_threshold * 100
            }
        }
    except Exception as e:
        logger.error("Error getting token usage summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting token usage summary: {str(e)}")


@router.get("/ai/{ai_name}")
async def get_ai_token_usage(ai_name: str):
    """Get token usage for a specific AI"""
    try:
        usage = await token_usage_service.get_monthly_usage(ai_name)
        if not usage:
            raise HTTPException(status_code=404, detail=f"No usage data found for {ai_name}")
        
        return {
            "ai_name": ai_name,
            "usage": usage,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting AI token usage", error=str(e), ai_name=ai_name)
        raise HTTPException(status_code=500, detail=f"Error getting token usage for {ai_name}: {str(e)}")


@router.get("/provider-status/{ai_name}")
async def get_provider_status(ai_name: str):
    """Get provider status for a specific AI"""
    try:
        status = await unified_ai_service_shared.get_provider_status(ai_name)
        return status
    except Exception as e:
        logger.error("Error getting provider status", error=str(e), ai_name=ai_name)
        raise HTTPException(status_code=500, detail=f"Error getting provider status for {ai_name}: {str(e)}")


@router.get("/provider-status")
async def get_all_provider_status():
    """Get provider status for all AIs"""
    try:
        status = await unified_ai_service_shared.get_all_provider_status()
        return status
    except Exception as e:
        logger.error("Error getting all provider status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting provider status: {str(e)}")


@router.get("/alerts")
async def get_token_usage_alerts():
    """Get token usage alerts"""
    try:
        alerts = await token_usage_service.get_usage_alerts()
        return {
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting token usage alerts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting token usage alerts: {str(e)}")


@router.get("/emergency-status")
async def get_emergency_status():
    """Get emergency status for token usage"""
    try:
        status = await token_usage_service.get_emergency_status()
        return status
    except Exception as e:
        logger.error("Error getting emergency status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting emergency status: {str(e)}")


@router.post("/test-ai-call")
async def test_ai_call(ai_name: str, prompt: str, preferred_provider: Optional[str] = None):
    """Test AI call with provider selection"""
    try:
        response, provider_info = await unified_ai_service_shared.call_ai(
            prompt=prompt,
            ai_name=ai_name,
            preferred_provider=preferred_provider
        )
        
        return {
            "ai_name": ai_name,
            "response": response,
            "provider_info": provider_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error testing AI call", error=str(e), ai_name=ai_name)
        raise HTTPException(status_code=500, detail=f"Error testing AI call for {ai_name}: {str(e)}")


@router.post("/reset/{ai_name}")
async def reset_ai_token_usage(ai_name: str):
    """Reset token usage for a specific AI"""
    try:
        success = await token_usage_service.reset_monthly_usage(ai_name)
        if success:
            return {
                "message": f"Token usage reset for {ai_name}",
                "ai_name": ai_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to reset token usage for {ai_name}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error resetting token usage", error=str(e), ai_name=ai_name)
        raise HTTPException(status_code=500, detail=f"Error resetting token usage for {ai_name}: {str(e)}")


@router.post("/reset-all")
async def reset_all_token_usage():
    """Reset token usage for all AIs"""
    try:
        # Get all AI names from the usage data
        all_usage = await token_usage_service.get_all_monthly_usage()
        ai_names = list(all_usage.keys())
        
        reset_results = {}
        for ai_name in ai_names:
            success = await token_usage_service.reset_monthly_usage(ai_name)
            reset_results[ai_name] = "success" if success else "failed"
        
        success_count = sum(1 for result in reset_results.values() if result == "success")
        
        return {
            "message": f"Token usage reset for {success_count}/{len(ai_names)} AIs",
            "reset_results": reset_results,
            "total_ais": len(ai_names),
            "successful_resets": success_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error resetting all token usage", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error resetting all token usage: {str(e)}")


@router.get("/history/{ai_name}")
async def get_ai_token_history(ai_name: str, months: int = 6):
    """Get token usage history for a specific AI"""
    try:
        history = await token_usage_service.get_usage_history(ai_name, months)
        return {
            "ai_name": ai_name,
            "history": history,
            "months": months,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting token history", error=str(e), ai_name=ai_name)
        raise HTTPException(status_code=500, detail=f"Error getting token history for {ai_name}: {str(e)}")


@router.get("/distribution")
async def get_usage_distribution():
    """Get detailed usage distribution statistics"""
    try:
        distribution_stats = await token_usage_service.get_usage_distribution_stats()
        return {
            "distribution_stats": distribution_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting usage distribution", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting usage distribution: {str(e)}") 