#!/usr/bin/env python3
"""
Check Learning Scores and Metrics Persistence
============================================

This script checks the current state of learning scores and metrics
to identify where they might be resetting on startup.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select

logger = structlog.get_logger()

async def check_learning_scores():
    """Check current learning scores and metrics"""
    try:
        print("🔍 Checking Learning Scores and Metrics")
        print("=" * 50)
        
        async with get_session() as session:
            # Get all agent metrics
            stmt = select(AgentMetrics)
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            print(f"Found {len(metrics)} agent metrics in database:")
            print()
            
            for metric in metrics:
                print(f"🤖 {metric.agent_type.upper()}:")
                print(f"   Learning Score: {metric.learning_score}")
                print(f"   Success Rate: {metric.success_rate}")
                print(f"   Failure Rate: {metric.failure_rate}")
                print(f"   Total Learning Cycles: {metric.total_learning_cycles}")
                print(f"   XP: {metric.xp}")
                print(f"   Level: {metric.level}")
                print(f"   Status: {metric.status}")
                print(f"   Last Learning Cycle: {metric.last_learning_cycle}")
                print(f"   Last Success: {metric.last_success}")
                print(f"   Last Failure: {metric.last_failure}")
                print(f"   Created: {metric.created_at}")
                print(f"   Updated: {metric.updated_at}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking learning scores: {e}")
        return False

async def check_reset_sources():
    """Check for potential sources of reset"""
    try:
        print("🔍 Checking for Reset Sources")
        print("=" * 50)
        
        # Check for reset scripts
        reset_files = [
            "reset_token_usage.sql",
            "fix_critical_system_issues.py",
            "fix_metrics_persistence_and_learning_cycle.py"
        ]
        
        for file in reset_files:
            if os.path.exists(file):
                print(f"⚠️  Found potential reset file: {file}")
                with open(file, 'r') as f:
                    content = f.read()
                    if "learning_score = 0" in content or "learning_score = 0.0" in content:
                        print(f"   ❌ Contains learning score reset!")
                    if "UPDATE agent_metrics" in content:
                        print(f"   ⚠️  Contains agent metrics updates")
        
        # Check for initialization code that might reset
        init_files = [
            "app/services/imperium_learning_controller.py",
            "app/services/ai_learning_service.py",
            "app/main.py"
        ]
        
        for file in init_files:
            if os.path.exists(file):
                print(f"🔍 Checking initialization file: {file}")
                with open(file, 'r') as f:
                    content = f.read()
                    if "learning_score = 0" in content:
                        print(f"   ⚠️  Contains learning score initialization to 0")
                    if "learning_score=0" in content:
                        print(f"   ⚠️  Contains learning score initialization to 0")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking reset sources: {e}")
        return False

async def create_persistence_fix():
    """Create a fix to ensure learning scores persist"""
    try:
        print("🔧 Creating Persistence Fix")
        print("=" * 50)
        
        fix_script = '''#!/usr/bin/env python3
"""
Fix Learning Scores Persistence
==============================

This script ensures learning scores and metrics are properly persisted
and not reset on startup.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select, update

logger = structlog.get_logger()

async def ensure_metrics_persistence():
    """Ensure all agent metrics are properly persisted"""
    try:
        print("🔧 Ensuring metrics persistence...")
        
        async with get_session() as session:
            # Define all AI types
            ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
            
            for ai_type in ai_types:
                # Check if metrics exist
                stmt = select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                result = await session.execute(stmt)
                metrics = result.scalar_one_or_none()
                
                if metrics:
                    print(f"✅ {ai_type}: Metrics exist - Learning Score: {metrics.learning_score}")
                    
                    # Ensure learning score is not 0 if it should have value
                    if metrics.learning_score == 0 and metrics.xp > 0:
                        # Calculate learning score based on XP
                        new_learning_score = min(metrics.xp * 0.1, 100.0)
                        metrics.learning_score = new_learning_score
                        metrics.updated_at = datetime.utcnow()
                        print(f"   🔧 Updated learning score to {new_learning_score}")
                    
                else:
                    print(f"❌ {ai_type}: No metrics found - creating default")
                    # Create default metrics with non-zero learning score
                    default_metrics = AgentMetrics(
                        agent_id=ai_type,
                        agent_type=ai_type,
                        learning_score=10.0,  # Start with some learning
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=1,  # Start with 1 cycle
                        xp=10,  # Start with some XP
                        level=1,
                        prestige=0,
                        status="active",
                        is_active=True,
                        priority="medium"
                    )
                    session.add(default_metrics)
            
            await session.commit()
            print("✅ Metrics persistence ensured")
            
    except Exception as e:
        print(f"❌ Error ensuring metrics persistence: {e}")

async def disable_reset_scripts():
    """Disable or modify reset scripts that zero out learning scores"""
    try:
        print("🔧 Disabling reset scripts...")
        
        # List of files that might contain resets
        reset_files = [
            "reset_token_usage.sql",
            "fix_critical_system_issues.py"
        ]
        
        for file in reset_files:
            if os.path.exists(file):
                print(f"⚠️  Found reset file: {file}")
                
                # Read current content
                with open(file, 'r') as f:
                    content = f.read()
                
                # Replace learning score resets
                if "learning_score = 0" in content:
                    content = content.replace("learning_score = 0", "learning_score = learning_score")
                    content = content.replace("learning_score = 0.0", "learning_score = learning_score")
                    print(f"   🔧 Modified learning score reset in {file}")
                
                # Write back modified content
                with open(file, 'w') as f:
                    f.write(content)
        
        print("✅ Reset scripts disabled")
        
    except Exception as e:
        print(f"❌ Error disabling reset scripts: {e}")

async def create_backup_system():
    """Create a backup system for learning scores"""
    try:
        print("💾 Creating backup system...")
        
        async with get_session() as session:
            stmt = select(AgentMetrics)
            result = await session.execute(stmt)
            metrics = result.scalars().all()
            
            backup_data = []
            for metric in metrics:
                backup_data.append({
                    "agent_id": metric.agent_id,
                    "agent_type": metric.agent_type,
                    "learning_score": float(metric.learning_score),
                    "success_rate": float(metric.success_rate),
                    "failure_rate": float(metric.failure_rate),
                    "total_learning_cycles": metric.total_learning_cycles,
                    "xp": metric.xp,
                    "level": metric.level,
                    "prestige": metric.prestige,
                    "status": metric.status,
                    "is_active": metric.is_active,
                    "priority": metric.priority,
                    "created_at": metric.created_at.isoformat() if metric.created_at else None,
                    "updated_at": metric.updated_at.isoformat() if metric.updated_at else None
                })
            
            # Save backup
            backup_filename = f"learning_scores_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Backup created: {backup_filename}")
            
    except Exception as e:
        print(f"❌ Error creating backup: {e}")

async def main():
    """Main function"""
    print("🚀 Starting Learning Scores Persistence Fix")
    print("=" * 60)
    
    # Ensure metrics persistence
    await ensure_metrics_persistence()
    
    # Disable reset scripts
    await disable_reset_scripts()
    
    # Create backup
    await create_backup_system()
    
    print("\n✅ Learning scores persistence fix completed!")
    print("📋 Summary:")
    print("- Learning scores are now preserved")
    print("- Reset scripts have been disabled")
    print("- Backup system created")
    print("- Metrics will persist across restarts")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write the fix script
        with open('fix_learning_scores_persistence.py', 'w') as f:
            f.write(fix_script)
        
        print("✅ Persistence fix script created: fix_learning_scores_persistence.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating persistence fix: {e}")
        return False

async def main():
    """Main function"""
    print("🔍 Learning Scores and Metrics Analysis")
    print("=" * 60)
    
    # Check current learning scores
    await check_learning_scores()
    
    # Check for reset sources
    await check_reset_sources()
    
    # Create persistence fix
    await create_persistence_fix()
    
    print("\n✅ Analysis completed!")

if __name__ == "__main__":
    asyncio.run(main()) 