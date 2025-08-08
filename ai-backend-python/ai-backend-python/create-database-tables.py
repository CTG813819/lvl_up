#!/usr/bin/env python3
"""
Script to create all database tables for the AI Backend
"""

import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.sql_models import Base
from app.core.config import settings

async def main():
    print("Creating database tables...")
    try:
        # Create async engine directly
        engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"ssl": "require"}
        )
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ All database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 