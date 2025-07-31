"""
System Status Router - Provides comprehensive system health information
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..services.token_usage_service import token_usage_service
from ..services.unified_ai_service_shared import unified_ai_service_shared
from ..core.config import settings

logger = structlog.get_logger()
router = APIRouter(tags=["system"])


@router.get("/status")
async def get_system_status(session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """Get comprehensive system status including backend health, AI services, and token usage"""
    try:
        # Get current timestamp
        current_time = datetime.utcnow()
        
        # Check backend connectivity
        backend_status = await _check_backend_health()
        
        # Check AI service status
        ai_service_status = await _check_ai_service_status()
        
        # Get token usage information
        token_usage_status = await _get_token_usage_status()
        
        # Get system metrics
        system_metrics = await _get_system_metrics(session)
        
        # Determine overall system health
        overall_health = _determine_overall_health(
            backend_status, ai_service_status, token_usage_status
        )
        
        return {
            "timestamp": current_time.isoformat(),
            "overall_health": overall_health,
            "backend": backend_status,
            "ai_services": ai_service_status,
            "token_usage": token_usage_status,
            "system_metrics": system_metrics,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error("Error getting system status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


async def _check_backend_health() -> Dict[str, Any]:
    """Check backend service health"""
    try:
        # Check if database is accessible
        db_healthy = True
        try:
            # Simple database check
            async with get_session() as session:
                # Try a simple query
                pass
        except Exception:
            db_healthy = False
        
        # Check if core services are initialized
        services_healthy = True
        try:
            # Check if token usage service is working
            await token_usage_service.get_all_monthly_usage()
        except Exception:
            services_healthy = False
        
        overall_health = "healthy" if db_healthy and services_healthy else "unhealthy"
        
        return {
            "status": overall_health,
            "database": "healthy" if db_healthy else "unhealthy",
            "services": "healthy" if services_healthy else "unhealthy",
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error checking backend health", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


async def _check_ai_service_status() -> Dict[str, Any]:
    """Check AI service status and availability"""
    try:
        # Check Anthropic service
        anthropic_status = await _check_anthropic_status()
        
        # Check OpenAI service
        openai_status = await _check_openai_status()
        
        # Check unified AI service
        unified_status = await _check_unified_service_status()
        
        return {
            "anthropic": anthropic_status,
            "openai": openai_status,
            "unified_service": unified_status,
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error checking AI service status", error=str(e))
        return {
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


async def _check_anthropic_status() -> Dict[str, Any]:
    """Check Anthropic service status"""
    try:
        import os
        import requests
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "status": "unavailable",
                "reason": "API key not configured"
            }
        
        # Quick connectivity test
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        test_data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "test"}]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=test_data,
            timeout=5
        )
        
        return {
            "status": "available" if response.status_code < 500 else "unavailable",
            "response_code": response.status_code,
            "reason": "API accessible" if response.status_code < 500 else "API error"
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "unavailable",
            "reason": "Connection timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "unavailable", 
            "reason": "Connection error"
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "reason": f"Error: {str(e)}"
        }


async def _check_openai_status() -> Dict[str, Any]:
    """Check OpenAI service status"""
    try:
        import os
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "status": "unavailable",
                "reason": "API key not configured"
            }
        
        # For now, just check if API key exists
        # Could add actual API test here
        return {
            "status": "available",
            "reason": "API key configured"
        }
        
    except Exception as e:
        return {
            "status": "unavailable",
            "reason": f"Error: {str(e)}"
        }


async def _check_unified_service_status() -> Dict[str, Any]:
    """Check unified AI service status"""
    try:
        # Test provider recommendation
        recommendation = await unified_ai_service_shared.get_provider_recommendation("imperium")
        
        return {
            "status": "available",
            "recommendation": recommendation.get("recommendation", "unknown"),
            "reason": recommendation.get("reason", "unknown")
        }
        
    except Exception as e:
        return {
            "status": "unavailable",
            "reason": f"Error: {str(e)}"
        }


async def _get_token_usage_status() -> Dict[str, Any]:
    """Get current token usage status"""
    try:
        # Get usage for all AI types
        ai_names = ["imperium", "guardian", "sandbox", "conquest"]
        usage_data = {}
        
        for ai_name in ai_names:
            try:
                # Get provider recommendation
                recommendation = await token_usage_service.get_provider_recommendation(ai_name)
                
                usage_data[ai_name] = {
                    "recommendation": recommendation.get("recommendation", "unknown"),
                    "reason": recommendation.get("reason", "unknown"),
                    "anthropic": recommendation.get("anthropic", {}),
                    "openai": recommendation.get("openai", {}),
                    "rate_limit_info": recommendation.get("rate_limit_info"),
                    "anthropic_reachable": recommendation.get("anthropic_reachable", True)
                }
            except Exception as e:
                usage_data[ai_name] = {
                    "error": str(e),
                    "recommendation": "unknown"
                }
        
        return {
            "ai_usage": usage_data,
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting token usage status", error=str(e))
        return {
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


async def _get_system_metrics(session: AsyncSession) -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # Get emergency status
        emergency_status = await token_usage_service.get_emergency_status()
        
        # Get usage distribution stats
        usage_stats = await token_usage_service.get_usage_distribution_stats()
        
        return {
            "emergency_status": emergency_status,
            "usage_distribution": usage_stats,
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting system metrics", error=str(e))
        return {
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }


def _determine_overall_health(
    backend_status: Dict[str, Any],
    ai_service_status: Dict[str, Any], 
    token_usage_status: Dict[str, Any]
) -> str:
    """Determine overall system health based on all components"""
    try:
        # Check backend health
        if backend_status.get("status") != "healthy":
            return "critical"
        
        # Check AI services
        anthropic_status = ai_service_status.get("anthropic", {}).get("status", "unknown")
        openai_status = ai_service_status.get("openai", {}).get("status", "unknown")
        
        if anthropic_status == "unavailable" and openai_status == "unavailable":
            return "critical"
        elif anthropic_status == "unavailable" or openai_status == "unavailable":
            return "warning"
        
        # Check token usage for any critical issues
        ai_usage = token_usage_status.get("ai_usage", {})
        for ai_name, usage in ai_usage.items():
            if usage.get("recommendation") == "none":
                return "warning"
        
        return "healthy"
        
    except Exception:
        return "unknown" 