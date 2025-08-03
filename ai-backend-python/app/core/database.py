"""
Database connection and management for PostgreSQL/NeonDB
"""

# Enhanced Database Configuration for Autonomy
ENABLE_LIVE_DATA_PERSISTENCE = True
ENABLE_REAL_TIME_METRICS = True
ENABLE_CROSS_AI_METRICS = True
ENABLE_EXPONENTIAL_LEARNING_STORAGE = True
ENABLE_INTELLIGENT_SCORING_HISTORY = True

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, text
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import structlog
import asyncio
import time
from functools import wraps
from .config import settings

logger = structlog.get_logger()

# Create async engine
engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None

# Base class for models
Base = declarative_base()

# Metadata for table management
metadata = MetaData()

# Circuit breaker state
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Global circuit breaker for database operations
db_circuit_breaker = CircuitBreaker()

# Connection retry decorator
def with_retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Database operation failed, retrying in {wait_time}s", 
                                     attempt=attempt + 1, error=str(e))
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Database operation failed after {max_retries} attempts", error=str(e))
                        raise last_exception
            return None
        return wrapper
    return decorator


async def init_database():
    """Initialize database connection with enhanced error handling"""
    global engine, SessionLocal
    
    try:
        logger.info("Initializing PostgreSQL database connection")
        
        # Parse database URL and handle SSL properly
        db_url = settings.database_url
        
        # Remove problematic SSL parameters from URL (asyncpg doesn't support them in URL)
        if "?" in db_url:
            base_url = db_url.split("?")[0]
            params = db_url.split("?")[1]
            if params:
                # Remove problematic parameters
                param_pairs = [
                    p for p in params.split("&") 
                    if not p.startswith("sslmode=") and 
                       not p.startswith("channel_binding=") and
                       not p.startswith("application_name=")
                ]
                if param_pairs:
                    db_url = f"{base_url}?{'&'.join(param_pairs)}"
                else:
                    db_url = base_url
        
        # Create async engine with asyncpg driver - Enhanced configuration
        engine = create_async_engine(
            db_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=1800,      # Recycle connections every 30 min
            pool_size=10,           # Lowered from 50 to 10 for safer FD usage
            max_overflow=5,         # Lowered from 100 to 5
            pool_timeout=30,        # Lowered from 120 to 30 seconds
            pool_reset_on_return='commit',
            # pool_use_lifo removed for simplicity and compatibility
            connect_args={
                "ssl": "require",
                "server_settings": {
                    "application_name": "ai_backend_python",
                    "statement_timeout": "120000",  # 120 seconds
                    "idle_in_transaction_session_timeout": "300000",  # 300 seconds
                }
            }
        )
        
        # Create session factory with enhanced configuration
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,      # Disable autoflush for better performance
            autocommit=False      # Explicitly disable autocommit
        )
        
        # Test connection with retry
        await _test_connection_with_retry()
        
        # Start connection pool monitoring
        asyncio.create_task(_monitor_connection_pool())
        
        # Start health check monitoring
        asyncio.create_task(_health_check_monitor())
        
        logger.info("PostgreSQL database connection established successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


@with_retry(max_retries=3, delay=2)
async def _test_connection_with_retry():
    """Test database connection with retry logic"""
    if not engine:
        raise RuntimeError("Engine not initialized")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
        # Test a more complex query to ensure full connectivity
        await conn.execute(text("SELECT version()"))


async def close_database():
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def _monitor_connection_pool():
    """Monitor connection pool health with reduced frequency"""
    while True:
        try:
            await _check_pool_health()
            # Reduced monitoring frequency from 30 seconds to 5 minutes
            await asyncio.sleep(300)  # Check every 5 minutes instead of 30 seconds
        except Exception as e:
            logger.error("Pool monitoring error", error=str(e))
            await asyncio.sleep(600)  # Wait 10 minutes on error instead of 60 seconds


async def _health_check_monitor():
    """Periodic health check of database connectivity"""
    while True:
        try:
            await _perform_health_check()
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            await asyncio.sleep(60)


async def _perform_health_check():
    """Perform a comprehensive health check"""
    if not engine:
        logger.error("Engine not initialized for health check")
        return
    try:
        async with engine.begin() as conn:
            # Test basic connectivity
            result = await conn.execute(text("SELECT 1"))
            if result:
                logger.info("Database health check passed")
            else:
                logger.warning("Database health check failed - no result")
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        # Could trigger circuit breaker here if needed


async def _check_pool_health():
    """Check for potential pool health issues"""
    if not engine:
        logger.error("Engine not initialized for pool health check")
        return
    try:
        # Test a simple query to ensure pool is working
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Pool health check failed", error=str(e))


async def get_pool_status() -> dict:
    """Get current connection pool status"""
    if not engine:
        return {"error": "Database not initialized"}
    
    try:
        # Get basic pool information
        pool_status = {
            "status": "active",
            "engine_initialized": engine is not None,
            "circuit_breaker_state": db_circuit_breaker.state,
            "circuit_breaker_failures": db_circuit_breaker.failure_count,
        }
        
        # Try to get detailed pool statistics if available
        try:
            pool = engine.pool
            if hasattr(pool, 'size'):
                pool_status.update({
                    "pool_size": getattr(pool, 'size', lambda: 0)(),
                    "pool_checked_in": getattr(pool, 'checkedin', lambda: 0)(),
                    "pool_checked_out": getattr(pool, 'checkedout', lambda: 0)(),
                    "pool_overflow": getattr(pool, 'overflow', lambda: 0)(),
                    "pool_invalid": getattr(pool, 'invalid', lambda: 0)(),
                })
                
                # Calculate derived statistics
                total_connections = pool_status.get("pool_size", 0) + pool_status.get("pool_overflow", 0)
                in_use_connections = pool_status.get("pool_checked_out", 0)
                
                pool_status.update({
                    "total_connections": total_connections,
                    "in_use_connections": in_use_connections,
                    "available_connections": total_connections - in_use_connections
                })
                
                # Log pool status if there are issues
                if total_connections > 0 and in_use_connections > total_connections * 0.8:
                    logger.warning("Connection pool usage high", 
                                 in_use=in_use_connections,
                                 total=total_connections,
                                 usage_percent=in_use_connections / total_connections * 100)
        except Exception as pool_error:
            logger.warning("Could not get detailed pool statistics", error=str(pool_error))
            pool_status["pool_info"] = "Basic pool monitoring only"
        
        return pool_status
    except Exception as e:
        return {"error": str(e)}


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as async context manager with enhanced error handling"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error("Database session error", error=str(e), error_type=type(e).__name__)
        try:
            await session.rollback()
        except Exception as rollback_error:
            logger.error("Failed to rollback session", error=str(rollback_error))
        # Increment circuit breaker failure count
        db_circuit_breaker.failure_count += 1
        raise
    finally:
        try:
            await session.close()
        except Exception as close_error:
            logger.error("Failed to close session", error=str(close_error))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as FastAPI dependency with enhanced error handling"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error("Database session error", error=str(e), error_type=type(e).__name__)
        try:
            await session.rollback()
        except Exception as rollback_error:
            logger.error("Failed to rollback session", error=str(rollback_error))
        # Increment circuit breaker failure count
        db_circuit_breaker.failure_count += 1
        raise
    finally:
        try:
            await session.close()
        except Exception as close_error:
            logger.error("Failed to close session", error=str(close_error))


# Enhanced database operations with retry logic
@with_retry(max_retries=3, delay=1)
async def execute_with_retry(query, params=None):
    """Execute a database query with retry logic"""
    if not engine:
        raise RuntimeError("Engine not initialized")
    async with engine.begin() as conn:
        result = await conn.execute(text(query), params or {})
        return result


@with_retry(max_retries=3, delay=1)
async def fetch_with_retry(query, params=None):
    """Fetch data with retry logic"""
    if not engine:
        raise RuntimeError("Engine not initialized")
    async with engine.begin() as conn:
        result = await conn.execute(text(query), params or {})
        return result.fetchall()


async def create_tables():
    """Create database tables with enhanced error handling"""
    try:
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


async def create_indexes():
    """Create database indexes for optimal performance with enhanced error handling"""
    try:
        if engine:
            async with engine.begin() as conn:
                # Create indexes for proposals table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_proposals_ai_type_status 
                    ON proposals(ai_type, status)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_proposals_file_path_ai_type 
                    ON proposals(file_path, ai_type)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_proposals_created_at 
                    ON proposals(created_at DESC)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_proposals_code_hash_ai_type 
                    ON proposals(code_hash, ai_type)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_proposals_semantic_hash_ai_type 
                    ON proposals(semantic_hash, ai_type)
                """))
                
                # Create indexes for learning table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_learning_ai_type_created_at 
                    ON learning(ai_type, created_at DESC)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_learning_learning_type 
                    ON learning(learning_type)
                """))
                
                # Create indexes for error_learning table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_error_learning_ai_type_created_at 
                    ON error_learning(ai_type, created_at DESC)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_error_learning_error_pattern 
                    ON error_learning(error_pattern)
                """))
                
                # Create indexes for experiments table
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_experiments_ai_type_status 
                    ON experiments(ai_type, status)
                """))
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_experiments_created_at 
                    ON experiments(created_at DESC)
                """))
            
            logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error("Failed to create database indexes", error=str(e))
        raise 