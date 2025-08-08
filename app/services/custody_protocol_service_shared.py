"""
Updated Custody Protocol Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
import sys
import os

from app.services.unified_ai_service_shared import unified_ai_service_shared

logger = structlog.get_logger()

class CustodyProtocolServiceShared:
    """Custody protocol service with shared token limits integration"""
    
    async def evaluate_custody_protocol(self, ai_name: str, content: str, 
                                       evaluation_type: str = "comprehensive") -> Dict[str, Any]:
        """Evaluate custody protocol with shared limits"""
        try:
            # Estimate tokens for evaluation
            estimated_tokens = len(content.split()) * 2  # Rough estimate
            
            # Try Anthropic first
            try:
                result = await self._evaluate_with_anthropic(ai_name, content, evaluation_type, estimated_tokens)
                return result
            except Exception as anthropic_error:
                logger.warning(f"Anthropic failed for custody protocol, trying OpenAI", error=str(anthropic_error))
                return await self._evaluate_with_openai(ai_name, content, evaluation_type, estimated_tokens)
                
        except Exception as e:
            logger.error("Error in custody protocol evaluation", error=str(e), ai_name=ai_name)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name
            }
    
    async def _evaluate_with_anthropic(self, ai_name: str, content: str, 
                                      evaluation_type: str, estimated_tokens: int) -> Dict[str, Any]:
        """Evaluate with Anthropic"""
        # This would contain the actual custody protocol evaluation logic
        # For now, we'll use the unified service
        prompt = f"Evaluate the following content for custody protocol compliance ({evaluation_type}):\n\n{content}"
        
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 2000, 0.3
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "anthropic",
                "evaluation": result["content"],
                "evaluation_type": evaluation_type,
                "ai_name": ai_name
            }
        else:
            raise Exception(result.get("message", "Anthropic evaluation failed"))
    
    async def _evaluate_with_openai(self, ai_name: str, content: str, 
                                   evaluation_type: str, estimated_tokens: int) -> Dict[str, Any]:
        """Evaluate with OpenAI"""
        prompt = f"Evaluate the following content for custody protocol compliance ({evaluation_type}):\n\n{content}"
        
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 2000, 0.3
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "openai",
                "evaluation": result["content"],
                "evaluation_type": evaluation_type,
                "ai_name": ai_name
            }
        else:
            return {
                "success": False,
                "error": "openai_evaluation_failed",
                "message": result.get("message", "OpenAI evaluation failed"),
                "ai_name": ai_name
            }

# Global instance
custody_protocol_service_shared = CustodyProtocolServiceShared() 