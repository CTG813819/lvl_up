"""
OpenAI Service - Fallback AI service when Anthropic tokens are exhausted
"""

import os
import asyncio
import time
import json
from collections import defaultdict
from typing import Optional, Dict, Any, Tuple
import requests
import structlog
from datetime import datetime

from ..core.config import settings
from .token_usage_service import token_usage_service

logger = structlog.get_logger()

# OpenAI rate limits (with 15% buffer for safety)
MAX_REQUESTS_PER_MIN = 42  # 50 * 0.85
MAX_TOKENS_PER_REQUEST = 17000  # 20,000 * 0.85
MAX_REQUESTS_PER_DAY = 3400  # 4,000 * 0.85
AI_NAMES = ["imperium", "guardian", "sandbox", "conquest"]

# Track requests per AI
_request_counts_minute = defaultdict(list)  # {ai_name: [timestamps]}
_request_counts_day = defaultdict(list)     # {ai_name: [timestamps]}
_rate_limiter_lock = asyncio.Lock()


class OpenAIService:
    """OpenAI service for AI agents with token usage tracking and fallback logic"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.api_key = settings.openai_api_key
            self.base_url = settings.openai_base_url
            self.model = settings.openai_model
            self.max_tokens = settings.openai_max_tokens
            self.temperature = settings.openai_temperature
            self._initialized = True
    
    async def should_use_openai(self, ai_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if OpenAI should be used as fallback for this AI"""
        try:
            # Get current Anthropic usage
            anthropic_usage = await token_usage_service.get_monthly_usage(ai_name)
            
            if not anthropic_usage:
                # No usage data, default to Anthropic
                return False, {"reason": "no_usage_data", "anthropic_usage": 0}
            
            # Check if Anthropic usage is above threshold
            anthropic_percentage = anthropic_usage.get("usage_percentage", 0)
            threshold = settings.openai_fallback_threshold * 100  # Convert to percentage
            
            # Check if we should use OpenAI based on monthly usage
            should_use_monthly = anthropic_percentage >= threshold
            
            # Also check if any rate limits are exceeded (hourly/daily)
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
            
            # Get daily and hourly usage
            daily_usage = await token_usage_service._get_daily_usage(current_date)
            hourly_usage = await token_usage_service._get_hourly_usage(current_hour)
            
            # Calculate limits
            daily_limit = int(settings.anthropic_monthly_limit * (8.0 / 100))  # 8% of monthly limit
            hourly_limit = int(settings.anthropic_monthly_limit * (0.5 / 100))  # 0.5% of monthly limit
            
            # Check if any limits are exceeded
            daily_exceeded = daily_usage >= daily_limit
            hourly_exceeded = hourly_usage >= hourly_limit
            
            should_use_rate_limit = daily_exceeded or hourly_exceeded
            
            # Use OpenAI if either monthly threshold is reached OR any rate limit is exceeded
            if should_use_monthly or should_use_rate_limit:
                # Check if OpenAI usage is within limits
                openai_usage = await self._get_openai_usage(ai_name)
                openai_percentage = (openai_usage.get("total_tokens", 0) / settings.openai_monthly_limit) * 100
                
                if openai_percentage < 100:  # OpenAI not exhausted
                    reason = "anthropic_exhausted" if should_use_monthly else "rate_limit_exceeded"
                    return True, {
                        "reason": reason,
                        "anthropic_percentage": anthropic_percentage,
                        "openai_percentage": openai_percentage,
                        "threshold": threshold,
                        "daily_exceeded": daily_exceeded,
                        "hourly_exceeded": hourly_exceeded,
                        "daily_usage": daily_usage,
                        "hourly_usage": hourly_usage,
                        "daily_limit": daily_limit,
                        "hourly_limit": hourly_limit
                    }
                else:
                    return False, {
                        "reason": "both_exhausted",
                        "anthropic_percentage": anthropic_percentage,
                        "openai_percentage": openai_percentage,
                        "daily_exceeded": daily_exceeded,
                        "hourly_exceeded": hourly_exceeded
                    }
            else:
                return False, {
                    "reason": "anthropic_available",
                    "anthropic_percentage": anthropic_percentage,
                    "threshold": threshold,
                    "daily_exceeded": daily_exceeded,
                    "hourly_exceeded": hourly_exceeded
                }
                
        except Exception as e:
            logger.error("Error checking OpenAI fallback", error=str(e), ai_name=ai_name)
            return False, {"reason": "error", "error": str(e)}
    
    async def _get_openai_usage(self, ai_name: str) -> Dict[str, Any]:
        """Get OpenAI usage for an AI agent"""
        try:
            # Use the same token usage service but with OpenAI provider
            usage = await token_usage_service.get_monthly_usage(f"{ai_name}_openai")
            if usage:
                return usage
            else:
                return {"total_tokens": 0, "usage_percentage": 0}
        except Exception as e:
            logger.error("Error getting OpenAI usage", error=str(e), ai_name=ai_name)
            return {"total_tokens": 0, "usage_percentage": 0}
    
    async def call_openai(
        self, 
        prompt: str, 
        ai_name: str, 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Call OpenAI with token usage tracking and rate limiting"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        
        if ai_name not in AI_NAMES:
            ai_name = "imperium"  # fallback
        
        # Use provided parameters or defaults
        model = model or self.model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        # Estimate tokens for this request
        estimated_input_tokens = len(prompt.split()) * 1.3  # Rough estimate with 30% buffer
        estimated_total_tokens = estimated_input_tokens + max_tokens
        
        # Check if we should use OpenAI
        should_use, reason = await self.should_use_openai(ai_name)
        if not should_use:
            raise Exception(f"OpenAI not available for {ai_name}: {reason.get('reason', 'unknown')}")
        
        # Check OpenAI usage limits
        can_make_request, usage_info = await self._enforce_openai_limits(ai_name, int(estimated_total_tokens))
        if not can_make_request:
            error_msg = f"OpenAI token limit reached for {ai_name}. Usage: {usage_info.get('usage_percentage', 0):.1f}%"
            if 'error' in usage_info:
                error_msg += f" - {usage_info['error']}"
            raise Exception(error_msg)
        
        # Apply rate limiting
        now = time.time()
        async with _rate_limiter_lock:
            # Clean up old timestamps
            _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
            _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
            
            # Enforce per-minute and per-day limits
            while (len(_request_counts_minute[ai_name]) >= MAX_REQUESTS_PER_MIN or
                   len(_request_counts_day[ai_name]) >= MAX_REQUESTS_PER_DAY):
                await asyncio.sleep(1)
                now = time.time()
                _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
                _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
            
            # Register this request
            _request_counts_minute[ai_name].append(now)
            _request_counts_day[ai_name].append(now)
        
        # Enforce token limit
        if max_tokens > MAX_TOKENS_PER_REQUEST:
            max_tokens = MAX_TOKENS_PER_REQUEST
        
        try:
            # Call OpenAI and capture response
            response = await self._call_openai_with_tracking(prompt, model, max_tokens, temperature, ai_name)
            return response
        except Exception as e:
            # Record failed request
            await self._record_openai_usage(
                ai_name=ai_name,
                tokens_in=int(estimated_input_tokens),
                tokens_out=0,
                model_used=model,
                success=False,
                error_message=str(e)
            )
            raise e
    
    async def _enforce_openai_limits(self, ai_name: str, estimated_tokens: int) -> Tuple[bool, Dict[str, Any]]:
        """Enforce OpenAI usage limits using token usage service"""
        try:
            # Use token usage service with OpenAI provider
            can_make_request, usage_info = await token_usage_service.enforce_strict_limits(ai_name, estimated_tokens, "openai")
            
            if not can_make_request:
                return False, usage_info
            
            # Get current OpenAI usage for additional info
            openai_usage = await self._get_openai_usage(ai_name)
            current_tokens = openai_usage.get("total_tokens", 0)
            
            return True, {
                "current_tokens": current_tokens,
                "estimated_tokens": estimated_tokens,
                "usage_percentage": (current_tokens / settings.openai_monthly_limit) * 100,
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error("Error enforcing OpenAI limits", error=str(e), ai_name=ai_name)
            return False, {"error": str(e)}
    
    async def _call_openai_with_tracking(
        self, 
        prompt: str, 
        model: str, 
        max_tokens: int, 
        temperature: float, 
        ai_name: str
    ) -> str:
        """Call OpenAI with token usage tracking"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            response_text = response_data["choices"][0]["message"]["content"]
            
            # Extract token usage from response
            tokens_in = 0
            tokens_out = 0
            request_id = None
            
            # Try to get token usage from response
            if "usage" in response_data:
                usage = response_data["usage"]
                tokens_in = usage.get("prompt_tokens", 0)
                tokens_out = usage.get("completion_tokens", 0)
            else:
                # Estimate token usage if not provided
                tokens_in = len(prompt.split())  # Rough estimate
                tokens_out = len(response_text.split())  # Rough estimate
            
            # Record token usage
            await self._record_openai_usage(
                ai_name=ai_name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model_used=model,
                success=True
            )
            
            return response_text
            
        except requests.exceptions.RequestException as e:
            # Record failed request
            await self._record_openai_usage(
                ai_name=ai_name,
                tokens_in=len(prompt.split()),  # Approximate input tokens
                tokens_out=0,
                model_used=model,
                success=False,
                error_message=str(e)
            )
            raise e
    
    async def _record_openai_usage(
        self,
        ai_name: str,
        tokens_in: int,
        tokens_out: int,
        model_used: str,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """Record OpenAI token usage for an AI agent"""
        try:
            # Use the token usage service with OpenAI provider identifier
            openai_ai_name = f"{ai_name}_openai"
            
            return await token_usage_service.record_token_usage(
                ai_type=openai_ai_name,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                model_used=model_used,
                request_type="OpenAI",
                success=success,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error("Error recording OpenAI token usage", error=str(e), ai_name=ai_name)
            return False

    async def generate_response(self, prompt: str, max_tokens: int = 4000, 
                               temperature: float = 0.7, model: str = None) -> Dict[str, Any]:
        """
        Generate response using OpenAI API - compatibility method for unified service
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            model: Model to use (optional, will use default if not provided)
            
        Returns:
            Dict containing the response content
        """
        try:
            # Use the existing call_openai method
            # Note: We'll use "imperium" as default ai_name since it's not provided
            response_text = await self.call_openai(
                prompt=prompt,
                ai_name="imperium",  # Default AI name
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response_text,
                "model": model or self.model,
                "tokens_used": len(prompt.split()) + len(response_text.split()),
                "success": True
            }
            
        except Exception as e:
            return {
                "content": "",
                "error": str(e),
                "success": False
            }


# Create singleton instance
openai_service = OpenAIService() 