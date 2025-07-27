#!/usr/bin/env python3
"""
Fix Custody XP Persistence
Ensures that all XP is properly stored as custody XP in the database
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import structlog

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database, get_session
from app.services.agent_metrics_service import AgentMetricsService
from sqlalchemy import select, update
from app.models.sql_models import AgentMetrics

logger = structlog.get_logger()

async def fix_custody_xp_persistence():
    """Fix custody XP persistence by merging regular XP into custody XP"""
    try:
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        print("🔧 Initializing agent metrics service...")
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        print("✅ Agent metrics service initialized")
        
        # Get all agent metrics
        print("📊 Fetching all agent metrics...")
        all_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        if not all_metrics:
            print("ℹ️ No agent metrics found")
            return
        
        print(f"📈 Found {len(all_metrics)} agent metrics")
        
        # Fix each agent's custody XP
        async with get_session() as session:
            for ai_type, metrics in all_metrics.items():
                try:
                    # Get the database record
                    result = await session.execute(
                        select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                    )
                    agent_metrics = result.scalar_one_or_none()
                    
                    if agent_metrics:
                        current_xp = agent_metrics.xp or 0
                        current_custody_xp = agent_metrics.custody_xp or 0
                        
                        # Merge regular XP into custody XP
                        new_custody_xp = current_custody_xp + current_xp
                        
                        # Update the database record
                        await session.execute(
                            update(AgentMetrics)
                            .where(AgentMetrics.agent_type == ai_type)
                            .values(
                                custody_xp=new_custody_xp,
                                xp=0,  # Reset regular XP since it's now merged into custody XP
                                updated_at=datetime.utcnow()
                            )
                        )
                        
                        print(f"✅ Updated {ai_type}: {current_xp} XP → {new_custody_xp} Custody XP")
                    else:
                        print(f"⚠️ No database record found for {ai_type}")
                        
                except Exception as e:
                    print(f"❌ Error updating {ai_type}: {str(e)}")
            
            # Commit all changes
            await session.commit()
            print("💾 All changes committed to database")
        
        # Verify the changes
        print("🔍 Verifying changes...")
        updated_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        for ai_type, metrics in updated_metrics.items():
            custody_xp = metrics.get('custody_xp', 0)
            regular_xp = metrics.get('xp', 0)
            print(f"📊 {ai_type}: Custody XP = {custody_xp}, Regular XP = {regular_xp}")
        
        print("✅ Custody XP persistence fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Error fixing custody XP persistence: {str(e)}")
        print(f"❌ Error: {str(e)}")
        raise

async def run_database_migrations():
    """Run any pending database migrations"""
    try:
        print("🔄 Running database migrations...")
        
        # Import and run migrations
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Database migrations completed")
        
    except Exception as e:
        print(f"⚠️ Migration warning: {str(e)}")
        # Continue even if migrations fail

async def main():
    """Main function"""
    print("🚀 Starting Custody XP Persistence Fix")
    print("=" * 50)
    
    try:
        # Run migrations first
        await run_database_migrations()
        
        # Fix custody XP persistence
        await fix_custody_xp_persistence()
        
        print("=" * 50)
        print("🎉 Custody XP persistence fix completed!")
        print("📝 All XP is now stored as custody XP for continuity")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 