"""
Unified AI Service - Intelligent provider selection between Anthropic and OpenAI
"""

import asyncio
from typing import Optional, Dict, Any, Tuple
import structlog

from ..core.config import settings
from .token_usage_service import token_usage_service
from .anthropic_service import anthropic_rate_limited_call
from .openai_service import openai_service

logger = structlog.get_logger()


class UnifiedAIService:
    """Unified AI service that intelligently chooses between Anthropic and OpenAI"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    async def call_ai(
        self,
        prompt: str,
        ai_name: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        preferred_provider: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Call AI with intelligent provider selection
        
        Returns:
            Tuple of (response_text, provider_info)
        """
        try:
            # Get provider recommendation
            provider_info = await token_usage_service.get_provider_recommendation(ai_name)
            recommendation = provider_info.get("recommendation", "anthropic")
            
            # Override with preferred provider if specified and available
            if preferred_provider:
                is_available, availability_info = await token_usage_service.check_provider_availability(ai_name, preferred_provider)
                if is_available:
                    recommendation = preferred_provider
                    provider_info["reason"] = f"preferred_provider_{preferred_provider}"
                else:
                    logger.warning(f"Preferred provider {preferred_provider} not available for {ai_name}, using recommendation: {recommendation}")
            
            # Call the appropriate provider
            if recommendation == "anthropic":
                try:
                    response = await anthropic_rate_limited_call(prompt, ai_name, model or "claude-3-5-sonnet-20241022", max_tokens or 1024)
                    return response, {
                        "provider": "anthropic",
                        "model": model or "claude-3-5-sonnet-20241022",
                        "reason": provider_info.get("reason", "anthropic_available"),
                        "usage_info": provider_info.get("anthropic", {})
                    }
                except Exception as e:
                    # Try OpenAI as fallback if Anthropic fails
                    logger.warning(f"Anthropic call failed for {ai_name}, trying OpenAI fallback: {str(e)}")
                    try:
                        response = await openai_service.call_openai(prompt, ai_name, model, max_tokens, temperature)
                        return response, {
                            "provider": "openai",
                            "model": model or "gpt-4.1",
                            "reason": "anthropic_failed_openai_fallback",
                            "anthropic_error": str(e),
                            "usage_info": provider_info.get("openai", {})
                        }
                    except Exception as openai_error:
                        raise Exception(f"Both Anthropic and OpenAI failed for {ai_name}. Anthropic error: {str(e)}. OpenAI error: {str(openai_error)}")
            
            elif recommendation == "openai":
                try:
                    response = await openai_service.call_openai(prompt, ai_name, model, max_tokens, temperature)
                    return response, {
                        "provider": "openai",
                        "model": model or "gpt-4.1",
                        "reason": provider_info.get("reason", "anthropic_exhausted_openai_available"),
                        "usage_info": provider_info.get("openai", {})
                    }
                except Exception as e:
                    raise Exception(f"OpenAI call failed for {ai_name}: {str(e)}")
            
            else:
                raise Exception(f"No AI provider available for {ai_name}. Anthropic: {provider_info.get('anthropic', {}).get('available', False)}, OpenAI: {provider_info.get('openai', {}).get('available', False)}")
                
        except Exception as e:
            logger.error(f"Error in unified AI call for {ai_name}: {str(e)}")
            raise e
    
    async def get_provider_status(self, ai_name: str) -> Dict[str, Any]:
        """Get detailed status of all providers for an AI"""
        try:
            provider_info = await token_usage_service.get_provider_recommendation(ai_name)
            
            # Get additional details
            anthropic_available, anthropic_details = await token_usage_service.check_provider_availability(ai_name, "anthropic")
            openai_available, openai_details = await token_usage_service.check_provider_availability(ai_name, "openai")
            
            return {
                "ai_name": ai_name,
                "recommendation": provider_info.get("recommendation", "anthropic"),
                "reason": provider_info.get("reason", "unknown"),
                "anthropic": {
                    "available": anthropic_available,
                    "usage_percentage": provider_info.get("anthropic", {}).get("usage_percentage", 0),
                    "total_tokens": provider_info.get("anthropic", {}).get("total_tokens", 0),
                    "details": anthropic_details
                },
                "openai": {
                    "available": openai_available,
                    "usage_percentage": provider_info.get("openai", {}).get("usage_percentage", 0),
                    "total_tokens": provider_info.get("openai", {}).get("total_tokens", 0),
                    "details": openai_details
                },
                "limits": {
                    "anthropic_monthly": settings.anthropic_monthly_limit,
                    "openai_monthly": settings.openai_monthly_limit,
                    "anthropic_threshold": settings.openai_fallback_threshold * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting provider status for {ai_name}: {str(e)}")
            return {
                "ai_name": ai_name,
                "error": str(e),
                "recommendation": "anthropic",
                "reason": "error"
            }
    
    async def get_all_provider_status(self) -> Dict[str, Any]:
        """Get provider status for all AIs"""
        try:
            ai_names = ["imperium", "guardian", "sandbox", "conquest"]
            statuses = {}
            
            for ai_name in ai_names:
                statuses[ai_name] = await self.get_provider_status(ai_name)
            
            return {
                "timestamp": asyncio.get_event_loop().time(),
                "ai_statuses": statuses
            }
            
        except Exception as e:
            logger.error(f"Error getting all provider status: {str(e)}")
            return {
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }


# Global instance
unified_ai_service_shared = UnifiedAIService() 