"""
Database connection and management for PostgreSQL/NeonDB
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, text
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import structlog
from .config import settings

logger = structlog.get_logger()

# Create async engine
engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None

# Base class for models
Base = declarative_base()

# Metadata for table management
metadata = MetaData()


async def init_database():
    """Initialize database connection"""
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
        
        # Create async engine with asyncpg driver
        engine = create_async_engine(
            db_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=2,          # Lowered for NeonDB's low connection limits
            max_overflow=4,       # Lowered for NeonDB's low connection limits
            connect_args={
                "ssl": "require"
            }
        )
        
        # Create session factory
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("PostgreSQL database connection established successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


async def close_database():
    """Close database connection"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as async context manager"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    async with SessionLocal() as session:
        yield session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as FastAPI dependency"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    async with SessionLocal() as session:
        yield session


async def create_tables():
    """Create database tables"""
    try:
        if engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


async def create_indexes():
    """Create database indexes for optimal performance"""
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