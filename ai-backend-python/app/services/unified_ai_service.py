"""
Unified AI Service - Load balancing between OpenAI and Anthropic
"""

import os
import asyncio
import time
import random
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import structlog
from collections import defaultdict
import json

from ..core.config import settings

logger = structlog.get_logger()


class UnifiedAIService:
    """Unified AI service with load balancing between OpenAI and Anthropic"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_providers()
            self._setup_rate_limiting()
            self._initialized = True
            logger.info("🤖 Unified AI Service initialized with load balancing")
    
    def _setup_providers(self):
        """Setup AI providers and their configurations"""
        self.providers = {}
        
        # Anthropic provider
        if settings.anthropic_api_key:
            self.providers['anthropic'] = {
                'api_key': settings.anthropic_api_key,
                'model': settings.anthropic_model,
                'max_tokens': settings.anthropic_max_tokens,
                'base_url': 'https://api.anthropic.com/v1/messages',
                'headers': {
                    'x-api-key': settings.anthropic_api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                'weight': settings.anthropic_weight,
                'enabled': True,
                'last_error': None,
                'error_count': 0,
                'success_count': 0
            }
            logger.info("✅ Anthropic provider configured")
        else:
            logger.warning("⚠️ Anthropic API key not configured")
        
        # OpenAI provider
        if settings.openai_api_key:
            self.providers['openai'] = {
                'api_key': settings.openai_api_key,
                'model': settings.openai_model,
                'max_tokens': settings.openai_max_tokens,
                'base_url': 'https://api.openai.com/v1/chat/completions',
                'headers': {
                    'Authorization': f'Bearer {settings.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                'weight': settings.openai_weight,
                'enabled': True,
                'last_error': None,
                'error_count': 0,
                'success_count': 0
            }
            logger.info("✅ OpenAI provider configured")
        else:
            logger.warning("⚠️ OpenAI API key not configured")
        
        if not self.providers:
            raise ValueError("No AI providers configured. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def _setup_rate_limiting(self):
        """Setup rate limiting for each provider"""
        self.rate_limits = {
            'anthropic': {
                'requests_per_min': 42,  # 50 * 0.85 buffer
                'requests_per_day': 3400,  # 4000 * 0.85 buffer
                'max_tokens_per_request': 17000,  # 20000 * 0.85 buffer
                'request_timestamps': defaultdict(list),
                'ai_request_counts': defaultdict(lambda: defaultdict(list))
            },
            'openai': {
                'requests_per_min': 3000,  # GPT-4o rate limit
                'requests_per_day': 100000,  # Daily limit
                'max_tokens_per_request': 4096,  # GPT-4o token limit
                'request_timestamps': defaultdict(list),
                'ai_request_counts': defaultdict(lambda: defaultdict(list))
            }
        }
        
        # AI names for tracking
        self.ai_names = ["imperium", "guardian", "sandbox", "conquest"]
        self._rate_limiter_lock = asyncio.Lock()
    
    async def call_ai(self, prompt: str, ai_name: str = "imperium", 
                     model: Optional[str] = None, max_tokens: Optional[int] = None,
                     provider: Optional[str] = None) -> str:
        """
        Call AI with intelligent provider selection and load balancing
        
        Args:
            prompt: The prompt to send to the AI
            ai_name: Name of the AI agent making the request
            model: Specific model to use (overrides provider default)
            max_tokens: Maximum tokens for response
            provider: Specific provider to use ('anthropic' or 'openai')
        
        Returns:
            AI response text
        """
        if ai_name not in self.ai_names:
            ai_name = "imperium"  # fallback
        
        # Select provider
        selected_provider = await self._select_provider(provider, ai_name)
        if not selected_provider:
            raise ValueError("No available AI providers")
        
        # Apply rate limiting
        await self._apply_rate_limiting(selected_provider, ai_name)
        
        # Call the selected provider
        try:
            response = await self._call_provider(selected_provider, prompt, ai_name, model, max_tokens)
            self.providers[selected_provider]['success_count'] += 1
            return response
        except Exception as e:
            self.providers[selected_provider]['error_count'] += 1
            self.providers[selected_provider]['last_error'] = str(e)
            logger.error(f"Provider {selected_provider} failed", error=str(e))
            
            # Try fallback provider
            fallback_provider = await self._get_fallback_provider(selected_provider)
            if fallback_provider:
                logger.info(f"Trying fallback provider: {fallback_provider}")
                return await self._call_provider(fallback_provider, prompt, ai_name, model, max_tokens)
            else:
                raise e
    
    async def _select_provider(self, requested_provider: Optional[str], ai_name: str) -> Optional[str]:
        """Select the best provider based on load balancing and availability"""
        available_providers = [p for p, config in self.providers.items() 
                             if config['enabled'] and config['api_key']]
        
        if not available_providers:
            return None
        
        # If specific provider requested and available
        if requested_provider and requested_provider in available_providers:
            return requested_provider
        
        # Load balancing based on weights
        if settings.enable_ai_load_balancing and len(available_providers) > 1:
            weights = [self.providers[p]['weight'] for p in available_providers]
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Weighted random selection
            selected = random.choices(available_providers, weights=normalized_weights)[0]
            logger.info(f"Load balancing selected {selected} for {ai_name}")
            return selected
        else:
            # Use first available provider
            return available_providers[0]
    
    async def _get_fallback_provider(self, failed_provider: str) -> Optional[str]:
        """Get fallback provider when primary fails"""
        available_providers = [p for p, config in self.providers.items() 
                             if config['enabled'] and config['api_key'] and p != failed_provider]
        return available_providers[0] if available_providers else None
    
    async def _apply_rate_limiting(self, provider: str, ai_name: str):
        """Apply rate limiting for the provider and AI agent"""
        now = time.time()
        limits = self.rate_limits[provider]
        
        async with self._rate_limiter_lock:
            # Clean up old timestamps
            limits['request_timestamps'] = {k: [t for t in v if now - t < 60] 
                                          for k, v in limits['request_timestamps'].items()}
            limits['ai_request_counts'][ai_name] = [t for t in limits['ai_request_counts'][ai_name] 
                                                   if now - t < 86400]
            
            # Check global rate limits
            while len(limits['request_timestamps']['global']) >= limits['requests_per_min']:
                await asyncio.sleep(1)
                now = time.time()
                limits['request_timestamps']['global'] = [t for t in limits['request_timestamps']['global'] 
                                                        if now - t < 60]
            
            # Check AI-specific daily limits
            while len(limits['ai_request_counts'][ai_name]) >= limits['requests_per_day']:
                await asyncio.sleep(1)
                now = time.time()
                limits['ai_request_counts'][ai_name] = [t for t in limits['ai_request_counts'][ai_name] 
                                                       if now - t < 86400]
            
            # Register this request
            limits['request_timestamps']['global'].append(now)
            limits['ai_request_counts'][ai_name].append(now)
    
    async def _call_provider(self, provider: str, prompt: str, ai_name: str, 
                           model: Optional[str], max_tokens: Optional[int]) -> str:
        """Call the specific AI provider"""
        config = self.providers[provider]
        
        # Use provider defaults if not specified
        model = model or config['model']
        max_tokens = max_tokens or config['max_tokens']
        
        # Enforce token limits
        max_tokens = min(max_tokens, self.rate_limits[provider]['max_tokens_per_request'])
        
        if provider == 'anthropic':
            return await self._call_anthropic(config, prompt, model, max_tokens)
        elif provider == 'openai':
            return await self._call_openai(config, prompt, model, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _call_anthropic(self, config: Dict, prompt: str, model: str, max_tokens: int) -> str:
        """Call Anthropic Claude API"""
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with asyncio.get_event_loop().run_in_executor(None, 
            lambda: requests.post(config['base_url'], headers=config['headers'], json=data)
        ) as response:
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
    
    async def _call_openai(self, config: Dict, prompt: str, model: str, max_tokens: int) -> str:
        """Call OpenAI API"""
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with asyncio.get_event_loop().run_in_executor(None,
            lambda: requests.post(config['base_url'], headers=config['headers'], json=data)
        ) as response:
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about provider usage and performance"""
        stats = {
            'providers': {},
            'total_requests': 0,
            'total_errors': 0,
            'load_balancing_enabled': settings.enable_ai_load_balancing
        }
        
        for provider, config in self.providers.items():
            total_requests = config['success_count'] + config['error_count']
            success_rate = (config['success_count'] / total_requests * 100) if total_requests > 0 else 0
            
            stats['providers'][provider] = {
                'enabled': config['enabled'],
                'success_count': config['success_count'],
                'error_count': config['error_count'],
                'total_requests': total_requests,
                'success_rate': success_rate,
                'last_error': config['last_error'],
                'weight': config['weight']
            }
            stats['total_requests'] += total_requests
            stats['total_errors'] += config['error_count']
        
        return stats
    
    def reset_provider_stats(self):
        """Reset provider statistics"""
        for provider in self.providers:
            self.providers[provider]['success_count'] = 0
            self.providers[provider]['error_count'] = 0
            self.providers[provider]['last_error'] = None
        logger.info("Provider statistics reset")


# Global instance
unified_ai_service = UnifiedAIService()


# Backward compatibility functions
async def call_ai(prompt: str, ai_name: str = "imperium", 
                 model: Optional[str] = None, max_tokens: Optional[int] = None,
                 provider: Optional[str] = None) -> str:
    """Backward compatibility function for existing code"""
    return await unified_ai_service.call_ai(prompt, ai_name, model, max_tokens, provider)


def get_ai_stats() -> Dict[str, Any]:
    """Get AI service statistics"""
    return unified_ai_service.get_provider_stats() 