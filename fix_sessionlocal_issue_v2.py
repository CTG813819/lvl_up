#!/usr/bin/env python3
"""
Fix SessionLocal issue in cleanup script - Version 2
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database
from app.models.sql_models import Proposal
from sqlalchemy import select, func, delete, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
import structlog
import asyncpg

logger = structlog.get_logger()

async def create_session_local():
    """Create SessionLocal manually if it's None"""
    try:
        from app.core.config import settings
        
        # Create async engine manually
        db_url = settings.database_url
        
        # Remove problematic SSL parameters from URL
        if "?" in db_url:
            base_url = db_url.split("?")[0]
            params = db_url.split("?")[1]
            if params:
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
        
        # Create async engine
        engine = create_async_engine(
            db_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            pool_timeout=60,
            connect_args={
                "ssl": "require",
                "server_settings": {
                    "application_name": "ai_backend_python_fix",
                    "statement_timeout": "120000",
                    "idle_in_transaction_session_timeout": "300000",
                }
            }
        )
        
        # Create session factory
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        
        return SessionLocal, engine
        
    except Exception as e:
        print(f"❌ Error creating SessionLocal: {e}")
        return None, None

async def cleanup_with_direct_sql():
    """Clean up pending proposals using direct SQL connection"""
    try:
        from app.core.config import settings
        
        print("🔧 Connecting directly to database...")
        
        # Connect directly using asyncpg
        conn = await asyncpg.connect(settings.database_url)
        
        # Get current pending count
        count_result = await conn.fetchval("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
        pending_count = count_result or 0
        
        print(f"📊 Current pending proposals: {pending_count}")
        
        if pending_count > 0:
            print("🗑️ Cleaning up pending proposals using direct SQL...")
            
            # Delete all pending proposals
            deleted_count = await conn.execute("DELETE FROM proposals WHERE status = 'pending'")
            
            print(f"✅ Deleted {pending_count} pending proposals")
            
            # Verify cleanup
            final_count = await conn.fetchval("SELECT COUNT(*) FROM proposals WHERE status = 'pending'")
            final_count = final_count or 0
            
            print(f"📊 Remaining pending proposals: {final_count}")
            
            await conn.close()
            
            if final_count == 0:
                print("🎉 Cleanup completed successfully!")
                return True
            else:
                print("⚠️ Some proposals still remain")
                return False
        else:
            print("✅ No pending proposals to clean up")
            await conn.close()
            return True
            
    except Exception as e:
        print(f"❌ Error during direct SQL cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False

async def fix_cleanup_issue():
    """Fix the SessionLocal issue and clean up pending proposals"""
    try:
        print("🔧 Initializing database...")
        await init_database()
        
        # Try to import SessionLocal
        try:
            from app.core.database import SessionLocal
        except ImportError:
            print("❌ Could not import SessionLocal from app.core.database")
            SessionLocal = None
        
        # Verify SessionLocal is properly initialized
        if SessionLocal is None:
            print("❌ SessionLocal is None after init_database")
            print("🔄 Trying to create SessionLocal manually...")
            
            SessionLocal, engine = await create_session_local()
            
            if SessionLocal is None:
                print("❌ Failed to create SessionLocal manually")
                print("🔄 Trying direct SQL cleanup...")
                return await cleanup_with_direct_sql()
        
        print("✅ Database initialized successfully")
        
        async with SessionLocal() as db:
            # Get current pending count
            pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
            pending_result = await db.execute(pending_query)
            pending_count = pending_result.scalar() or 0
            
            print(f"📊 Current pending proposals: {pending_count}")
            
            if pending_count > 0:
                print("🗑️ Cleaning up pending proposals...")
                
                # Delete all pending proposals
                delete_query = delete(Proposal).where(Proposal.status == "pending")
                result = await db.execute(delete_query)
                deleted_count = result.rowcount
                
                await db.commit()
                print(f"✅ Deleted {deleted_count} pending proposals")
                
                # Verify cleanup
                verify_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
                verify_result = await db.execute(verify_query)
                final_count = verify_result.scalar() or 0
                
                print(f"📊 Remaining pending proposals: {final_count}")
                
                if final_count == 0:
                    print("🎉 Cleanup completed successfully!")
                    return True
                else:
                    print("⚠️ Some proposals still remain")
                    return False
            else:
                print("✅ No pending proposals to clean up")
                return True
                
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        
        # Try direct SQL as fallback
        print("🔄 Trying direct SQL cleanup as fallback...")
        return await cleanup_with_direct_sql()

async def main():
    """Main function"""
    print("🚀 Starting cleanup fix (Version 2)...")
    
    success = await fix_cleanup_issue()
    
    if success:
        print("✅ Cleanup fix completed successfully")
        sys.exit(0)
    else:
        print("❌ Cleanup fix failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 