"""
Cache Service for API Optimization
Implements intelligent caching to reduce Claude API calls and improve performance
"""

import asyncio
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
from collections import OrderedDict
import pickle
import os
from pathlib import Path

logger = structlog.get_logger()

class CacheService:
    """Intelligent caching service to reduce API calls and improve performance"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cache_dir = Path("./cache")
            self._cache_dir.mkdir(exist_ok=True)
            
            # In-memory cache for fast access
            self._memory_cache: OrderedDict = OrderedDict()
            self._max_memory_items = 1000
            
            # Cache configuration
            self._cache_ttl = {
                "github_data": 3600,  # 1 hour
                "stackoverflow_data": 1800,  # 30 minutes
                "claude_analysis": 7200,  # 2 hours
                "ml_predictions": 3600,  # 1 hour
                "internet_search": 900,  # 15 minutes
                "code_analysis": 1800,  # 30 minutes
            }
            
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the cache service"""
        instance = cls()
        logger.info("Cache service initialized")
        return instance
    
    def _generate_cache_key(self, data_type: str, content: str, **kwargs) -> str:
        """Generate a unique cache key"""
        # Create a hash of the content and parameters
        key_data = {
            "type": data_type,
            "content": content,
            **kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache entry"""
        return self._cache_dir / f"{cache_key}.cache"
    
    async def get(self, data_type: str, content: str, **kwargs) -> Optional[Any]:
        """Get cached data if available and not expired"""
        cache_key = self._generate_cache_key(data_type, content, **kwargs)
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            cached_item = self._memory_cache[cache_key]
            if self._is_valid(cached_item, data_type):
                # Move to end (LRU)
                self._memory_cache.move_to_end(cache_key)
                logger.debug(f"Cache hit (memory): {data_type}")
                return cached_item["data"]
            else:
                # Remove expired item
                del self._memory_cache[cache_key]
        
        # Check file cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    cached_item = pickle.load(f)
                
                if self._is_valid(cached_item, data_type):
                    # Add to memory cache
                    self._add_to_memory_cache(cache_key, cached_item)
                    logger.debug(f"Cache hit (file): {data_type}")
                    return cached_item["data"]
                else:
                    # Remove expired file
                    cache_path.unlink()
            except Exception as e:
                logger.warning(f"Error reading cache file: {e}")
                if cache_path.exists():
                    cache_path.unlink()
        
        logger.debug(f"Cache miss: {data_type}")
        return None
    
    async def set(self, data_type: str, content: str, data: Any, **kwargs) -> None:
        """Cache data with appropriate TTL"""
        cache_key = self._generate_cache_key(data_type, content, **kwargs)
        
        cached_item = {
            "data": data,
            "timestamp": time.time(),
            "type": data_type,
            "ttl": self._cache_ttl.get(data_type, 3600)
        }
        
        # Add to memory cache
        self._add_to_memory_cache(cache_key, cached_item)
        
        # Save to file cache
        try:
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_item, f)
        except Exception as e:
            logger.warning(f"Error writing cache file: {e}")
    
    def _add_to_memory_cache(self, key: str, item: Dict[str, Any]) -> None:
        """Add item to memory cache with LRU eviction"""
        if key in self._memory_cache:
            self._memory_cache.move_to_end(key)
        else:
            self._memory_cache[key] = item
            
            # Evict oldest if cache is full
            if len(self._memory_cache) > self._max_memory_items:
                self._memory_cache.popitem(last=False)
    
    def _is_valid(self, cached_item: Dict[str, Any], data_type: str) -> bool:
        """Check if cached item is still valid"""
        if not cached_item or "timestamp" not in cached_item:
            return False
        
        ttl = cached_item.get("ttl", self._cache_ttl.get(data_type, 3600))
        age = time.time() - cached_item["timestamp"]
        return age < ttl
    
    async def invalidate(self, data_type: str, content: str, **kwargs) -> None:
        """Invalidate a specific cache entry"""
        cache_key = self._generate_cache_key(data_type, content, **kwargs)
        
        # Remove from memory cache
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]
        
        # Remove from file cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()
    
    async def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        cleared_count = 0
        
        # Clear expired memory cache entries
        expired_keys = []
        for key, item in self._memory_cache.items():
            if not self._is_valid(item, item.get("type", "unknown")):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_cache[key]
            cleared_count += 1
        
        # Clear expired file cache entries
        for cache_file in self._cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    cached_item = pickle.load(f)
                
                if not self._is_valid(cached_item, cached_item.get("type", "unknown")):
                    cache_file.unlink()
                    cleared_count += 1
            except Exception:
                # Remove corrupted cache files
                cache_file.unlink()
                cleared_count += 1
        
        if cleared_count > 0:
            logger.info(f"Cleared {cleared_count} expired cache entries")
        
        return cleared_count
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_size = len(self._memory_cache)
        file_count = len(list(self._cache_dir.glob("*.cache")))
        
        return {
            "memory_cache_size": memory_size,
            "file_cache_count": file_count,
            "cache_ttl_config": self._cache_ttl,
            "max_memory_items": self._max_memory_items
        }
    
    async def clear_all(self) -> None:
        """Clear all cache entries"""
        self._memory_cache.clear()
        
        for cache_file in self._cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        logger.info("All cache entries cleared") 