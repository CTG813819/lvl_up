from dotenv import load_dotenv
load_dotenv()
import os
import requests
import asyncio
import time
import json
import logging
from collections import defaultdict
from typing import Optional, Dict, Any

# Set up logger
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Import token usage service
from .token_usage_service import token_usage_service
from .openai_service import openai_service


def call_claude(prompt, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

# Anthropic Opus 4 limits (with 15% buffer)
MAX_REQUESTS_PER_MIN = 42  # 50 * 0.85
MAX_TOKENS_PER_REQUEST = 17000  # 20,000 * 0.85
MAX_REQUESTS_PER_DAY = 3400  # 4,000 * 0.85
AI_NAMES = ["imperium", "guardian", "sandbox", "conquest"]

# Track requests per AI
_request_counts_minute = defaultdict(list)  # {ai_name: [timestamps]}
_request_counts_day = defaultdict(list)     # {ai_name: [timestamps]}
_rate_limiter_lock = asyncio.Lock()

async def anthropic_rate_limited_call(prompt, ai_name, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    """Async wrapper for call_claude with per-AI and global rate limiting, with OpenAI fallback."""
    if ai_name not in AI_NAMES:
        ai_name = "imperium"  # fallback
    
    # Estimate tokens for this request
    estimated_input_tokens = len(prompt.split()) * 1.3  # Rough estimate with 30% buffer
    estimated_total_tokens = estimated_input_tokens + max_tokens
    
    # Check monthly usage limits first with strict enforcement
    can_make_request, usage_info = await token_usage_service.enforce_strict_limits(ai_name, int(estimated_total_tokens), "anthropic")
    if not can_make_request:
        # Enhanced logging for which limit is hit
        logger.warning(f"Anthropic request blocked for {ai_name}", error=usage_info.get('error'), details=usage_info)
        # Try OpenAI as fallback for ANY Anthropic block (hourly, daily, monthly, cooldown, etc.)
        try:
            from .openai_service import openai_service
            should_use_openai, openai_reason = await openai_service.should_use_openai(ai_name)
            if should_use_openai:
                logger.info(f"🔄 Anthropic blocked ({usage_info.get('error', 'unknown')}) for {ai_name}, switching to OpenAI fallback")
                logger.info(f"   Anthropic usage: {usage_info.get('usage_percentage', 0):.1f}%")
                logger.info(f"   OpenAI reason: {openai_reason.get('reason', 'unknown')}")
                if openai_reason.get('daily_exceeded'):
                    logger.info(f"   OpenAI daily limit exceeded: {openai_reason.get('daily_usage', 0)}/{openai_reason.get('daily_limit', 0)}")
                if openai_reason.get('hourly_exceeded'):
                    logger.info(f"   OpenAI hourly limit exceeded: {openai_reason.get('hourly_usage', 0)}/{openai_reason.get('hourly_limit', 0)}")
                # Call OpenAI with the same prompt
                openai_response = await openai_service.call_openai(prompt, ai_name, max_tokens=max_tokens)
                logger.info(f"✅ Successfully used OpenAI fallback for {ai_name}")
                return openai_response
            else:
                error_msg = f"Anthropic blocked for {ai_name} ({usage_info.get('error', 'unknown')}). OpenAI fallback not available: {openai_reason.get('reason', 'unknown')}"
                if 'error' in usage_info:
                    error_msg += f" - {usage_info['error']}"
                if 'error' in openai_reason:
                    error_msg += f" | OpenAI: {openai_reason['error']}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Anthropic blocked for {ai_name} ({usage_info.get('error', 'unknown')}). OpenAI fallback failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
    
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
        # Call Claude and capture response
        response = await _call_claude_with_tracking(prompt, model, max_tokens, ai_name)
        return response
    except Exception as e:
        # Record failed request
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=int(estimated_input_tokens),
            tokens_out=0,
            model_used=model,
            request_type="HTTP",
            success=False,
            error_message=str(e)
        )
        raise e

async def _call_claude_with_tracking(prompt, model, max_tokens, ai_name):
    """Call Claude with token usage tracking"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        response_text = response_data["content"][0]["text"]
        
        # Extract token usage from response headers or estimate
        tokens_in = 0
        tokens_out = 0
        request_id = None
        
        # Try to get token usage from response headers
        if "x-request-id" in response.headers:
            request_id = response.headers["x-request-id"]
        
        # Try to get usage from response body if available
        if "usage" in response_data:
            usage = response_data["usage"]
            tokens_in = usage.get("input_tokens", 0)
            tokens_out = usage.get("output_tokens", 0)
        else:
            # Estimate token usage if not provided
            tokens_in = len(prompt.split())  # Rough estimate
            tokens_out = len(response_text.split())  # Rough estimate
        
        # Record token usage
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=request_id,
            model_used=model,
            request_type="HTTP",
            success=True
        )
        
        return response_text
        
    except requests.exceptions.RequestException as e:
        # Record failed request
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=len(prompt.split()),  # Approximate input tokens
            tokens_out=0,
            model_used=model,
            request_type="HTTP",
            success=False,
            error_message=str(e)
        )
        raise e


class AnthropicService:
    """AnthropicService class for compatibility with unified_ai_service_shared"""
    
    def __init__(self):
        pass
    
    async def generate_response(self, prompt: str, max_tokens: int = 4000, 
                               temperature: float = 0.7, model: str = "claude-3-5-sonnet-20241022") -> Dict[str, Any]:
        """
        Generate response using Anthropic Claude API
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation
            model: Model to use
            
        Returns:
            Dict containing the response content
        """
        try:
            # Use the existing anthropic_rate_limited_call function
            # Note: We'll use "imperium" as default ai_name since it's not provided
            response_text = await anthropic_rate_limited_call(
                prompt=prompt,
                ai_name="imperium",  # Default AI name
                model=model,
                max_tokens=max_tokens
            )
            
            return {
                "content": response_text,
                "model": model,
                "tokens_used": len(prompt.split()) + len(response_text.split()),
                "success": True
            }
            
        except Exception as e:
            return {
                "content": "",
                "error": str(e),
                "success": False
            } 