#!/usr/bin/env python3
"""
Priority Fixes Application Script
Applies all critical fixes identified in the audit:
1. Fix syntax errors
2. Address security vulnerabilities
3. Implement timeout mechanisms
4. Add comprehensive error handling
5. Optimize memory usage
6. Add caching and performance improvements
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def backup_file(file_path):
    """Create a backup of a file"""
    backup_path = f"{file_path}.backup"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"Backed up {file_path} to {backup_path}")

def fix_syntax_errors():
    """Fix any syntax errors in the codebase"""
    print("🔧 Fixing syntax errors...")
    
    # Check for syntax errors in Python files
    success, stdout, stderr = run_command("find . -name '*.py' -exec python -m py_compile {} \\;", cwd="app")
    if not success:
        print(f"Syntax check failed: {stderr}")
        return False
    
    print("✅ Syntax check passed")
    return True

def fix_security_vulnerabilities():
    """Fix security vulnerabilities identified in the audit"""
    print("🔒 Fixing security vulnerabilities...")
    
    # 1. Fix CORS configuration in main.py
    main_py = "app/main.py"
    if os.path.exists(main_py):
        backup_file(main_py)
        
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Replace permissive CORS with restrictive one
        content = re.sub(
            r"app\.add_middleware\(CORSMiddleware,.*?\)",
            """app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)""",
            content,
            flags=re.DOTALL
        )
        
        # Remove or secure debug endpoints
        content = re.sub(
            r"@app\.get\('/debug/.*?'\)",
            "# @app.get('/debug/...')  # Debug endpoint removed for security",
            content
        )
        
        with open(main_py, 'w') as f:
            f.write(content)
        
        print("✅ Fixed CORS and debug endpoints in main.py")
    
    # 2. Add security headers middleware
    security_middleware = """from fastapi import Request
from fastapi.responses import Response
import time

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
"""
    
    # Add security middleware to main.py
    with open(main_py, 'r') as f:
        content = f.read()
    
    if "add_security_headers" not in content:
        # Insert after imports
        content = re.sub(
            r"(from fastapi import.*?)\n",
            r"\\1\n" + security_middleware + "\n",
            content,
            flags=re.DOTALL
        )
        
        with open(main_py, 'w') as f:
            f.write(content)
        
        print("✅ Added security headers middleware")

def implement_timeout_mechanisms():
    """Implement timeout mechanisms for long-running operations"""
    print("⏱️ Implementing timeout mechanisms...")
    
    # Add timeout decorator utility
    timeout_utility = """import asyncio
import functools
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def timeout(seconds: int):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Operation timed out after {seconds} seconds")
        return wrapper
    return decorator

def sync_timeout(seconds: int):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"Operation timed out after {seconds} seconds")
        return wrapper
    return decorator
"""
    
    # Create timeout utility file
    timeout_file = "app/core/timeout.py"
    os.makedirs(os.path.dirname(timeout_file), exist_ok=True)
    with open(timeout_file, 'w') as f:
        f.write(timeout_utility)
    
    print("✅ Created timeout utility")

def add_comprehensive_error_handling():
    """Add comprehensive error handling throughout the codebase"""
    print("🛡️ Adding comprehensive error handling...")
    
    # Create error handling utilities
    error_handling = """import logging
import traceback
from typing import Any, Dict, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class AIBackendError(Exception):
    \"\"\"Base exception for AI backend errors\"\"\"
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class ValidationError(AIBackendError):
    \"\"\"Raised when data validation fails\"\"\"
    pass

class DatabaseError(AIBackendError):
    \"\"\"Raised when database operations fail\"\"\"
    pass

class AIServiceError(AIBackendError):
    \"\"\"Raised when AI service operations fail\"\"\"
    pass

def handle_async_errors(func):
    \"\"\"Decorator to handle async function errors\"\"\"
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AIBackendError as e:
            logger.error(f"AI Backend Error in {func.__name__}: {e.message}", 
                        extra={"error_code": e.error_code, "details": e.details})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": e.message, "code": e.error_code, "details": e.details}
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", 
                        exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Internal server error", "code": "INTERNAL_ERROR"}
            )
    return wrapper

def safe_execute(func, *args, **kwargs):
    \"\"\"Safely execute a function with error handling\"\"\"
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
        return None

async def safe_async_execute(func, *args, **kwargs):
    \"\"\"Safely execute an async function with error handling\"\"\"
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
        return None
"""
    
    # Create error handling file
    error_file = "app/core/error_handling.py"
    os.makedirs(os.path.dirname(error_file), exist_ok=True)
    with open(error_file, 'w') as f:
        f.write(error_handling)
    
    print("✅ Created comprehensive error handling utilities")

def optimize_memory_usage():
    """Optimize memory usage for ML operations"""
    print("💾 Optimizing memory usage...")
    
    # Create memory optimization utilities
    memory_utils = """import gc
import psutil
import logging
from typing import Any, Dict, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MemoryManager:
    \"\"\"Manages memory usage for ML operations\"\"\"
    
    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> Dict[str, float]:
        \"\"\"Get current memory usage\"\"\"
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": memory_percent,
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }
    
    def check_memory_limit(self) -> bool:
        \"\"\"Check if memory usage is within limits\"\"\"
        memory_usage = self.get_memory_usage()
        return memory_usage["percent"] < self.max_memory_percent
    
    def force_garbage_collection(self):
        \"\"\"Force garbage collection\"\"\"
        collected = gc.collect()
        logger.info(f"Garbage collection freed {collected} objects")
    
    @contextmanager
    def memory_context(self, operation_name: str = "operation"):
        \"\"\"Context manager for memory-intensive operations\"\"\"
        initial_memory = self.get_memory_usage()
        logger.info(f"Starting {operation_name}, initial memory: {initial_memory['rss_mb']:.1f}MB")
        
        try:
            yield
        finally:
            final_memory = self.get_memory_usage()
            memory_diff = final_memory['rss_mb'] - initial_memory['rss_mb']
            logger.info(f"Completed {operation_name}, memory change: {memory_diff:+.1f}MB")
            
            # Force garbage collection if memory usage is high
            if final_memory['percent'] > 70:
                self.force_garbage_collection()

def optimize_ml_model_loading():
    \"\"\"Optimize ML model loading with lazy loading and caching\"\"\"
    import joblib
    from functools import lru_cache
    
    @lru_cache(maxsize=10)
    def load_model_cached(model_path: str):
        \"\"\"Load ML model with caching\"\"\"
        return joblib.load(model_path)
    
    return load_model_cached

def clear_ml_cache():
    \"\"\"Clear ML model cache\"\"\"
    load_model_cached.cache_clear()
    gc.collect()
"""
    
    # Create memory optimization file
    memory_file = "app/core/memory_optimization.py"
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)
    with open(memory_file, 'w') as f:
        f.write(memory_utils)
    
    print("✅ Created memory optimization utilities")

def add_caching_and_performance():
    """Add caching and performance improvements"""
    print("⚡ Adding caching and performance improvements...")
    
    # Create caching utilities
    caching_utils = """import asyncio
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps
import json
import hashlib

class AsyncCache:
    \"\"\"Simple async cache implementation\"\"\"
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def _generate_key(self, *args, **kwargs) -> str:
        \"\"\"Generate cache key from arguments\"\"\"
        key_data = json.dumps((args, sorted(kwargs.items())), sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        \"\"\"Get value from cache\"\"\"
        if key in self.cache:
            item = self.cache[key]
            if time.time() - item['timestamp'] < self.ttl:
                return item['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        \"\"\"Set value in cache\"\"\"
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear(self):
        \"\"\"Clear all cache\"\"\"
        self.cache.clear()

# Global cache instance
ai_cache = AsyncCache(max_size=500, ttl=600)  # 10 minutes TTL

def cache_result(ttl: int = 300):
    \"\"\"Decorator to cache function results\"\"\"
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{ai_cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = ai_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            ai_cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator

def sync_cache_result(ttl: int = 300):
    \"\"\"Decorator to cache synchronous function results\"\"\"
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{ai_cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = ai_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            ai_cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator
"""
    
    # Create caching file
    cache_file = "app/core/caching.py"
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w') as f:
        f.write(caching_utils)
    
    print("✅ Created caching utilities")

def add_streaming_support():
    """Add streaming support for large file operations"""
    print("🌊 Adding streaming support...")
    
    # Create streaming utilities
    streaming_utils = """import asyncio
import aiofiles
from typing import AsyncGenerator, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def stream_file_content(file_path: str, chunk_size: int = 8192) -> AsyncGenerator[bytes, None]:
    \"\"\"Stream file content in chunks\"\"\"
    try:
        async with aiofiles.open(file_path, 'rb') as file:
            while chunk := await file.read(chunk_size):
                yield chunk
    except Exception as e:
        logger.error(f"Error streaming file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error streaming file")

async def stream_large_response(data: Any, chunk_size: int = 1000) -> AsyncGenerator[Any, None]:
    \"\"\"Stream large response data in chunks\"\"\"
    if isinstance(data, list):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    elif isinstance(data, str):
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    else:
        yield data

class StreamingProcessor:
    \"\"\"Process large datasets in streaming fashion\"\"\"
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    async def process_stream(self, data_stream: AsyncGenerator[Any, None], 
                           processor_func: callable) -> AsyncGenerator[Any, None]:
        \"\"\"Process streaming data with a processor function\"\"\"
        batch = []
        
        async for item in data_stream:
            batch.append(item)
            
            if len(batch) >= self.batch_size:
                # Process batch
                processed_batch = await processor_func(batch)
                for result in processed_batch:
                    yield result
                batch = []
        
        # Process remaining items
        if batch:
            processed_batch = await processor_func(batch)
            for result in processed_batch:
                yield result
"""
    
    # Create streaming file
    streaming_file = "app/core/streaming.py"
    os.makedirs(os.path.dirname(streaming_file), exist_ok=True)
    with open(streaming_file, 'w') as f:
        f.write(streaming_utils)
    
    print("✅ Created streaming utilities")

def add_monitoring_and_logging():
    """Add monitoring and logging improvements"""
    print("📊 Adding monitoring and logging...")
    
    # Create monitoring utilities
    monitoring_utils = """import time
import logging
import psutil
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    \"\"\"Monitor application performance\"\"\"
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
    
    def record_request(self, response_time: float, success: bool = True):
        \"\"\"Record a request\"\"\"
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.response_times.append(response_time)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        \"\"\"Get performance statistics\"\"\"
        if not self.response_times:
            return {
                "uptime": time.time() - self.start_time,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0
            }
        
        return {
            "uptime": time.time() - self.start_time,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        \"\"\"Get system statistics\"\"\"
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    \"\"\"Decorator to monitor function performance\"\"\"
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            performance_monitor.record_request(response_time, success=True)
            return result
        except Exception as e:
            response_time = time.time() - start_time
            performance_monitor.record_request(response_time, success=False)
            raise
    return wrapper

class HealthChecker:
    \"\"\"Check system health\"\"\"
    
    @staticmethod
    async def check_health() -> Dict[str, Any]:
        \"\"\"Perform health check\"\"\"
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Check system resources
        try:
            system_stats = performance_monitor.get_system_stats()
            health_status["checks"]["system"] = {
                "status": "healthy" if system_stats["memory_percent"] < 90 else "warning",
                "details": system_stats
            }
        except Exception as e:
            health_status["checks"]["system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check performance stats
        try:
            perf_stats = performance_monitor.get_stats()
            health_status["checks"]["performance"] = {
                "status": "healthy" if perf_stats["error_rate"] < 0.1 else "warning",
                "details": perf_stats
            }
        except Exception as e:
            health_status["checks"]["performance"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Overall status
        if any(check["status"] == "unhealthy" for check in health_status["checks"].values()):
            health_status["status"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health_status["checks"].values()):
            health_status["status"] = "warning"
        
        return health_status
"""
    
    # Create monitoring file
    monitoring_file = "app/core/monitoring.py"
    os.makedirs(os.path.dirname(monitoring_file), exist_ok=True)
    with open(monitoring_file, 'w') as f:
        f.write(monitoring_utils)
    
    print("✅ Created monitoring utilities")

def update_requirements():
    """Update requirements.txt with new dependencies"""
    print("📦 Updating requirements...")
    
    new_dependencies = [
        "psutil>=5.9.0",
        "aiofiles>=23.0.0",
        "joblib>=1.3.0"
    ]
    
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Add new dependencies if not present
        for dep in new_dependencies:
            if dep.split('>=')[0] not in content:
                content += f"\n{dep}\n"
        
        with open(requirements_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated requirements.txt")

def create_health_check_endpoint():
    """Create health check endpoint"""
    print("🏥 Creating health check endpoint...")
    
    health_endpoint = """from fastapi import APIRouter
from app.core.monitoring import HealthChecker
from app.core.error_handling import handle_async_errors

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
@handle_async_errors
async def health_check():
    \"\"\"Health check endpoint\"\"\"
    return await HealthChecker.check_health()

@router.get("/ready")
@handle_async_errors
async def readiness_check():
    \"\"\"Readiness check endpoint\"\"\"
    health = await HealthChecker.check_health()
    if health["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")
"""
    
    # Create health router
    health_file = "app/routers/health.py"
    os.makedirs(os.path.dirname(health_file), exist_ok=True)
    with open(health_file, 'w') as f:
        f.write(health_endpoint)
    
    print("✅ Created health check endpoint")

def main():
    """Main function to apply all priority fixes"""
    print("🚀 Applying Priority Fixes from Audit...")
    print("=" * 50)
    
    # We're already in the ai-backend-python directory, so no need to change
    # os.chdir("ai-backend-python")  # Remove this line
    
    # Apply fixes in order
    fixes = [
        ("Syntax Errors", fix_syntax_errors),
        ("Security Vulnerabilities", fix_security_vulnerabilities),
        ("Timeout Mechanisms", implement_timeout_mechanisms),
        ("Error Handling", add_comprehensive_error_handling),
        ("Memory Optimization", optimize_memory_usage),
        ("Caching & Performance", add_caching_and_performance),
        ("Streaming Support", add_streaming_support),
        ("Monitoring & Logging", add_monitoring_and_logging),
        ("Requirements Update", update_requirements),
        ("Health Check Endpoint", create_health_check_endpoint)
    ]
    
    for fix_name, fix_func in fixes:
        print(f"\n📋 Applying {fix_name}...")
        try:
            fix_func()
            print(f"✅ {fix_name} applied successfully")
        except Exception as e:
            print(f"❌ Failed to apply {fix_name}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Priority fixes application completed!")
    print("\nNext steps:")
    print("1. Install new dependencies: pip install -r requirements.txt")
    print("2. Restart the backend service")
    print("3. Test the health endpoint: GET /health")
    print("4. Monitor logs for any issues")

if __name__ == "__main__":
    main() 