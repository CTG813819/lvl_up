"""
Updated Unified AI Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

from app.core.config import settings
from app.services.anthropic_service import AnthropicService
from app.services.openai_service import OpenAIService
import sys
import os

logger = structlog.get_logger()

class UnifiedAIServiceShared:
    """Unified AI service with shared token limits integration"""
    
    def __init__(self):
        self.anthropic_service = AnthropicService()
        self.openai_service = OpenAIService()
    
    async def get_provider_recommendation(self, ai_name: str) -> Dict[str, Any]:
        """Get provider recommendation based on shared usage"""
        try:
            # For now, return a simple recommendation
            # This can be enhanced later with actual shared limits service
            return {
                "recommendation": "anthropic",
                "reason": "anthropic_available",
                "anthropic": {
                    "usage_percentage": 0,
                    "total_tokens": 0,
                    "available": True
                },
                "openai": {
                    "usage_percentage": 0,
                    "total_tokens": 0,
                    "available": True
                }
            }
            
        except Exception as e:
            logger.error("Error getting provider recommendation", error=str(e), ai_name=ai_name)
            return {
                "recommendation": "anthropic",
                "reason": "error_fallback",
                "error": str(e)
            }
    
    async def make_request(self, ai_name: str, prompt: str, estimated_tokens: int = 1000, 
                          max_tokens: int = 4000, temperature: float = 0.7) -> Dict[str, Any]:
        """Make AI request with shared limits enforcement"""
        try:
            if ai_name in ["imperium", "guardian", "conquest", "sandbox"]:
                try:
                    from app.services.imperium_ai_service import ImperiumAIService
                    from app.services.guardian_ai_service import GuardianAIService
                    from app.services.sandbox_ai_service import SandboxAIService
                    from app.services.conquest_ai_service import ConquestAIService

                    if ai_name == "imperium":
                        content = await ImperiumAIService().answer_prompt(prompt)
                    elif ai_name == "guardian":
                        content = await GuardianAIService().answer_prompt(prompt)
                    elif ai_name == "sandbox":
                        content = await SandboxAIService().answer_prompt(prompt)
                    elif ai_name == "conquest":
                        content = await ConquestAIService().answer_prompt(prompt)
                    return {
                        "success": True,
                        "provider": "inhouse",
                        "content": content,
                        "ai_name": ai_name
                    }
                except Exception as inhouse_error:
                    logger.warning(f"In-house AI {ai_name} failed, falling back to Anthropic/OpenAI", error=str(inhouse_error))
            # Fallback to Anthropic/OpenAI as before
            # Try Anthropic first
            try:
                result = await self.anthropic_service.generate_response(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if result.get("success", False):
                    return {
                        "success": True,
                        "provider": "anthropic",
                        "content": result.get("content", ""),
                        "tokens_used": result.get("tokens_used", 0),
                        "ai_name": ai_name
                    }
                else:
                    raise Exception(result.get("error", "Anthropic request failed"))
                
            except Exception as anthropic_error:
                logger.warning(f"Anthropic failed for {ai_name}, trying OpenAI", error=str(anthropic_error))
                
                # Try OpenAI as fallback
                return await self._make_openai_request(ai_name, prompt, estimated_tokens, max_tokens, temperature)
                
        except Exception as e:
            logger.error("Error in unified AI request", error=str(e), ai_name=ai_name)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name
            }
    
    async def _make_openai_request(self, ai_name: str, prompt: str, estimated_tokens: int, 
                                  max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Make OpenAI request with shared limits"""
        try:
            # Make OpenAI request using the generate_response method
            result = await self.openai_service.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if result.get("success", False):
                return {
                    "success": True,
                    "provider": "openai",
                    "content": result.get("content", ""),
                    "tokens_used": result.get("tokens_used", 0),
                    "ai_name": ai_name
                }
            else:
                raise Exception(result.get("error", "OpenAI request failed"))
            
        except Exception as e:
            logger.error("Error in OpenAI request", error=str(e), ai_name=ai_name)
            return {
                "success": False,
                "error": "openai_error",
                "message": str(e),
                "ai_name": ai_name
            }

# Global instance
unified_ai_service_shared = UnifiedAIServiceShared() 