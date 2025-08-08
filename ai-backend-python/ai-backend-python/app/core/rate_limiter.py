"""
Rate limiting and throttling mechanisms for API protection
"""

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Optional, Callable
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """Rate limiter with sliding window and per-endpoint limits"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 requests per minute
            'growth_analytics': {'requests': 30, 'window': 60},  # 30 requests per minute
            'oath_papers': {'requests': 20, 'window': 60},  # 20 requests per minute
            'proposals': {'requests': 50, 'window': 60},  # 50 requests per minute
            'learning': {'requests': 40, 'window': 60},  # 40 requests per minute
        }
    
    def is_allowed(self, endpoint: str, client_id: str = 'default') -> bool:
        """Check if request is allowed based on rate limits"""
        key = f"{endpoint}:{client_id}"
        now = time.time()
        
        # Get limits for endpoint
        limit_config = self.limits.get(endpoint, self.limits['default'])
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < now - window:
            self.requests[key].popleft()
        
        # Check if under limit
        if len(self.requests[key]) < max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining(self, endpoint: str, client_id: str = 'default') -> int:
        """Get remaining requests for endpoint"""
        key = f"{endpoint}:{client_id}"
        now = time.time()
        
        limit_config = self.limits.get(endpoint, self.limits['default'])
        max_requests = limit_config['requests']
        window = limit_config['window']
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < now - window:
            self.requests[key].popleft()
        
        return max(0, max_requests - len(self.requests[key]))


class ConnectionThrottler:
    """Throttle database connections to prevent overload"""
    
    def __init__(self, max_concurrent: int = 50, window: int = 60):
        self.max_concurrent = max_concurrent
        self.window = window
        self.active_connections = 0
        self.connection_history = deque()
        self.lock = asyncio.Lock()
    
    async def acquire_connection(self) -> bool:
        """Try to acquire a database connection"""
        async with self.lock:
            now = time.time()
            
            # Clean old history
            while self.connection_history and self.connection_history[0] < now - self.window:
                self.connection_history.popleft()
            
            # Check if we can allow more connections
            if self.active_connections < self.max_concurrent:
                self.active_connections += 1
                self.connection_history.append(now)
                return True
            
            return False
    
    async def release_connection(self):
        """Release a database connection"""
        async with self.lock:
            self.active_connections = max(0, self.active_connections - 1)
    
    def get_stats(self) -> dict:
        """Get connection throttling stats"""
        return {
            'active_connections': self.active_connections,
            'max_concurrent': self.max_concurrent,
            'connections_in_window': len(self.connection_history)
        }


class AdaptiveThrottler:
    """Adaptive throttling based on system performance"""
    
    def __init__(self):
        self.response_times = deque(maxlen=100)
        self.error_rates = deque(maxlen=100)
        self.base_limit = 100
        self.current_limit = self.base_limit
        self.min_limit = 10
        self.max_limit = 200
    
    def record_response_time(self, response_time: float):
        """Record response time for adaptive throttling"""
        self.response_times.append(response_time)
        
        # Adjust limits based on performance
        if len(self.response_times) >= 10:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            
            if avg_response_time > 2.0:  # Slow response times
                self.current_limit = max(self.min_limit, self.current_limit * 0.8)
            elif avg_response_time < 0.5:  # Fast response times
                self.current_limit = min(self.max_limit, self.current_limit * 1.2)
    
    def record_error(self, error: bool):
        """Record error for adaptive throttling"""
        self.error_rates.append(error)
        
        # Adjust limits based on error rate
        if len(self.error_rates) >= 10:
            error_rate = sum(self.error_rates) / len(self.error_rates)
            
            if error_rate > 0.1:  # High error rate
                self.current_limit = max(self.min_limit, self.current_limit * 0.7)
            elif error_rate < 0.01:  # Low error rate
                self.current_limit = min(self.max_limit, self.current_limit * 1.1)
    
    def get_current_limit(self) -> int:
        """Get current adaptive limit"""
        return int(self.current_limit)


# Global instances
rate_limiter = RateLimiter()
connection_throttler = ConnectionThrottler()
adaptive_throttler = AdaptiveThrottler()


def rate_limit_decorator(endpoint: str):
    """Decorator for rate limiting endpoints"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            client_id = kwargs.get('client_id', 'default')
            
            if not rate_limiter.is_allowed(endpoint, client_id):
                remaining = rate_limiter.get_remaining(endpoint, client_id)
                logger.warning(f"Rate limit exceeded for {endpoint}", 
                             client_id=client_id, remaining=remaining)
                raise Exception(f"Rate limit exceeded. Try again later.")
            
            # Record response time for adaptive throttling
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                adaptive_throttler.record_response_time(response_time)
                adaptive_throttler.record_error(False)
                return result
            except Exception as e:
                adaptive_throttler.record_error(True)
                raise e
        
        return wrapper
    return decorator


async def with_connection_throttling(func: Callable, *args, **kwargs):
    """Execute function with connection throttling"""
    if not await connection_throttler.acquire_connection():
        logger.warning("Connection limit reached, request throttled")
        raise Exception("Too many concurrent requests. Try again later.")
    
    try:
        return await func(*args, **kwargs)
    finally:
        await connection_throttler.release_connection()


def get_throttling_stats() -> dict:
    """Get comprehensive throttling statistics"""
    return {
        'rate_limiter': {
            'endpoints': list(rate_limiter.limits.keys()),
            'limits': rate_limiter.limits
        },
        'connection_throttler': connection_throttler.get_stats(),
        'adaptive_throttler': {
            'current_limit': adaptive_throttler.get_current_limit(),
            'base_limit': adaptive_throttler.base_limit,
            'response_times_count': len(adaptive_throttler.response_times),
            'error_rates_count': len(adaptive_throttler.error_rates)
        }
    } 