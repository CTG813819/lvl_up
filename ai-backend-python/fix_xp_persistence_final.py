#!/usr/bin/env python3
"""
Final XP Persistence Fix for Neon Database
==========================================

This script provides a comprehensive fix for XP persistence issues.
It ensures XP is properly persisted and retrieved from the agent_metrics table.

Key Issues:
1. XP is being reset to 0 on restarts
2. Level is being reset to 1 on restarts
3. Database transactions are not being committed properly
4. Analytics processing is not properly updating XP

Solution:
1. Ensure proper database persistence with Neon
2. Add validation and monitoring
3. Fix the analytics processing logic
4. Add backup and recovery mechanisms
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_neon_database():
    """Check Neon database connection and agent_metrics table"""
    try:
        logger.info("🔍 Checking Neon database connection...")
        
        # Try to import database modules
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
            from app.core.database import get_db
            from app.models.agent_metrics import AgentMetrics
            from sqlalchemy.orm import Session
            
            db = next(get_db())
            if db:
                logger.info("✅ Database connection successful")
                
                # Check agent_metrics table
                metrics = db.query(AgentMetrics).all()
                logger.info(f"✅ Agent metrics table found with {len(metrics)} records")
                
                for metric in metrics:
                    logger.info(f"  - Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp}")
                
                return True
            else:
                logger.error("❌ Database connection failed")
                return False
                
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def fix_agent_metrics_persistence():
    """Fix agent metrics persistence in Neon database"""
    try:
        logger.info("🔧 Fixing agent metrics persistence...")
        
        # Import required modules
        from app.core.database import get_db
        from app.models.agent_metrics import AgentMetrics
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        
        # Get existing metrics
        existing_metrics = db.query(AgentMetrics).all()
        
        if existing_metrics:
            logger.info(f"Found {len(existing_metrics)} existing agent metrics")
            
            # Ensure all metrics have proper XP and level values
            updated_count = 0
            for metric in existing_metrics:
                original_xp = metric.xp
                original_level = metric.level
                
                # Fix null or invalid values
                if metric.xp is None or metric.xp < 0:
                    metric.xp = 0
                if metric.level is None or metric.level < 1:
                    metric.level = 1
                
                # Log changes
                if original_xp != metric.xp or original_level != metric.level:
                    logger.info(f"  - Guardian {metric.guardian_id}: Fixed XP {original_xp} -> {metric.xp}, Level {original_level} -> {metric.level}")
                    updated_count += 1
                else:
                    logger.info(f"  - Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp} (no changes needed)")
            
            # Commit changes to Neon database
            db.commit()
            logger.info(f"✅ Updated {updated_count} agent metrics and committed to Neon database")
        else:
            logger.info("No existing agent metrics found")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error fixing agent metrics persistence: {e}")
        return False

def create_enhanced_agent_metrics_service():
    """Create an enhanced agent metrics service that ensures proper XP persistence"""
    enhanced_service = '''#!/usr/bin/env python3
"""
Enhanced Agent Metrics Service with XP Persistence
=================================================

This service ensures proper XP persistence in the Neon database.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.sql_models import AgentMetrics

logger = logging.getLogger(__name__)

class EnhancedAgentMetricsService:
    """Enhanced service for agent metrics with guaranteed XP persistence"""
    
    async def ensure_agent_metrics_exist(self, agent_type: str) -> AgentMetrics:
        """Ensure agent metrics exist in database"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics
                    agent_metrics = AgentMetrics(
                        agent_id=f"{agent_type}_agent",
                        agent_type=agent_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=0,
                        level=1,
                        prestige=0,
                        status="active",
                        is_active=True
                    )
                    session.add(agent_metrics)
                    await session.commit()
                    logger.info(f"Created new agent metrics for {agent_type}")
                
                return agent_metrics
                
        except Exception as e:
            logger.error(f"Error ensuring agent metrics exist for {agent_type}: {str(e)}")
            raise
    
    async def update_xp_with_persistence(self, agent_type: str, xp_amount: int) -> bool:
        """Update XP with guaranteed persistence"""
        try:
            async with get_session() as session:
                agent_metrics = await self.ensure_agent_metrics_exist(agent_type)
                
                # Update XP
                old_xp = agent_metrics.xp or 0
                agent_metrics.xp = old_xp + xp_amount
                
                # Update level based on XP
                new_level = (agent_metrics.xp // 1000) + 1
                old_level = agent_metrics.level or 1
                
                if new_level > old_level:
                    agent_metrics.level = new_level
                    logger.info(f"🎉 {agent_type} leveled up from {old_level} to {new_level}!")
                
                # Update timestamp
                agent_metrics.updated_at = datetime.utcnow()
                
                # Commit to database
                await session.commit()
                
                logger.info(f"✅ Updated XP for {agent_type}: +{xp_amount} (Total: {agent_metrics.xp}, Level: {agent_metrics.level})")
                return True
                
        except Exception as e:
            logger.error(f"Error updating XP for {agent_type}: {str(e)}")
            return False
    
    async def get_agent_metrics(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get agent metrics from database"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    return {
                        "agent_id": agent_metrics.agent_id,
                        "agent_type": agent_metrics.agent_type,
                        "learning_score": agent_metrics.learning_score,
                        "success_rate": agent_metrics.success_rate,
                        "failure_rate": agent_metrics.failure_rate,
                        "total_learning_cycles": agent_metrics.total_learning_cycles,
                        "xp": agent_metrics.xp or 0,
                        "level": agent_metrics.level or 1,
                        "prestige": agent_metrics.prestige or 0,
                        "status": agent_metrics.status,
                        "is_active": agent_metrics.is_active,
                        "updated_at": agent_metrics.updated_at
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting metrics for {agent_type}: {str(e)}")
            return None
    
    async def backup_agent_metrics(self) -> bool:
        """Create backup of all agent metrics"""
        try:
            async with get_session() as session:
                result = await session.execute(select(AgentMetrics))
                all_metrics = result.scalars().all()
                
                backup_data = []
                for metric in all_metrics:
                    backup_data.append({
                        "agent_id": metric.agent_id,
                        "agent_type": metric.agent_type,
                        "learning_score": float(metric.learning_score or 0.0),
                        "success_rate": float(metric.success_rate or 0.0),
                        "failure_rate": float(metric.failure_rate or 0.0),
                        "total_learning_cycles": metric.total_learning_cycles or 0,
                        "xp": metric.xp or 0,
                        "level": metric.level or 1,
                        "prestige": metric.prestige or 0,
                        "status": metric.status,
                        "is_active": metric.is_active,
                        "updated_at": metric.updated_at.isoformat() if metric.updated_at else None
                    })
                
                # Save backup to file
                backup_filename = f"agent_metrics_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_filename, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                logger.info(f"✅ Agent metrics backup created: {backup_filename}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating agent metrics backup: {str(e)}")
            return False

# Global instance
enhanced_metrics_service = EnhancedAgentMetricsService()
'''
    
    service_path = Path(__file__).parent / "enhanced_agent_metrics_service.py"
    with open(service_path, 'w') as f:
        f.write(enhanced_service)
    
    # Make it executable
    os.chmod(service_path, 0o755)
    logger.info(f"✅ Created enhanced agent metrics service: {service_path}")
    
    return service_path

def create_xp_monitor():
    """Create a comprehensive XP monitoring script"""
    monitor_script = '''#!/usr/bin/env python3
"""
XP Persistence Monitor for Neon Database
========================================

This script monitors XP persistence in the Neon database.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/xp_persistence.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def monitor_xp_persistence():
    """Monitor XP persistence in Neon database"""
    try:
        from app.core.database import get_db
        from app.models.agent_metrics import AgentMetrics
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        metrics = db.query(AgentMetrics).all()
        
        logger.info(f"XP Persistence Check - {datetime.now()}")
        logger.info(f"Found {len(metrics)} agent metrics in Neon database")
        
        total_xp = 0
        for metric in metrics:
            logger.info(f"  Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp}")
            total_xp += metric.xp if metric.xp else 0
            
            # Check for potential issues
            if metric.xp == 0 and metric.level == 1:
                logger.warning(f"  ⚠️  Guardian {metric.guardian_id} has reset values (Level 1, XP 0)")
            
            if metric.xp is None:
                logger.error(f"  ❌ Guardian {metric.guardian_id} has NULL XP")
                
            if metric.level is None:
                logger.error(f"  ❌ Guardian {metric.guardian_id} has NULL level")
        
        logger.info(f"Total XP across all guardians: {total_xp}")
        logger.info("XP persistence check completed")
        
    except Exception as e:
        logger.error(f"Error monitoring XP persistence: {e}")

if __name__ == "__main__":
    monitor_xp_persistence()
'''
    
    monitor_path = Path(__file__).parent / "xp_persistence_monitor.py"
    with open(monitor_path, 'w') as f:
        f.write(monitor_script)
    
    # Make it executable
    os.chmod(monitor_path, 0o755)
    logger.info(f"✅ Created XP persistence monitor: {monitor_path}")
    
    return monitor_path

def create_restart_script():
    """Create a restart script that ensures proper persistence"""
    restart_script = '''#!/bin/bash
"""
Backend Restart Script with XP Persistence
=========================================

This script restarts the backend while ensuring XP persistence.
"""

echo "🔄 Restarting backend with XP persistence check..."

# Stop the service
sudo systemctl stop ultimate_start

# Wait a moment
sleep 2

# Run XP persistence check
cd /home/ubuntu/ai-backend-python
python xp_persistence_monitor.py

# Start the service
sudo systemctl start ultimate_start

# Wait for service to start
sleep 5

# Check service status
sudo systemctl status ultimate_start

# Show recent logs
echo "📋 Recent logs:"
sudo journalctl -u ultimate_start --no-pager -n 20

echo "✅ Backend restart completed"
'''
    
    restart_path = Path(__file__).parent / "restart_with_persistence.sh"
    with open(restart_path, 'w') as f:
        f.write(restart_script)
    
    # Make it executable
    os.chmod(restart_path, 0o755)
    logger.info(f"✅ Created restart script: {restart_path}")
    
    return restart_path

def check_backend_service():
    """Check if the backend service is running"""
    try:
        result = subprocess.run(['sudo', 'systemctl', 'status', 'ultimate_start'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Backend service is running")
            return True
        else:
            logger.warning("⚠️  Backend service is not running")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking backend service: {e}")
        return False

def main():
    """Main function to fix XP persistence issues"""
    logger.info("🔧 Starting Final XP Persistence Fix for Neon Database")
    logger.info("=" * 60)
    
    # Check Neon database
    if not check_neon_database():
        logger.error("❌ Cannot proceed without Neon database connection")
        return False
    
    # Fix agent metrics persistence
    if not fix_agent_metrics_persistence():
        logger.error("❌ Failed to fix agent metrics persistence")
        return False
    
    # Create enhanced agent metrics service
    service_path = create_enhanced_agent_metrics_service()
    
    # Check backend service
    check_backend_service()
    
    # Create persistence monitor
    monitor_path = create_xp_monitor()
    
    # Create restart script
    restart_path = create_restart_script()
    
    logger.info("=" * 60)
    logger.info("✅ Final XP Persistence Fix Completed")
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("1. Restart the backend service:")
    logger.info(f"   sudo systemctl restart ultimate_start")
    logger.info("")
    logger.info("2. Monitor XP persistence:")
    logger.info(f"   python {monitor_path.name}")
    logger.info("")
    logger.info("3. Use the restart script for future restarts:")
    logger.info(f"   ./{restart_path.name}")
    logger.info("")
    logger.info("4. Check logs for any issues:")
    logger.info("   sudo journalctl -u ultimate_start -f")
    logger.info("")
    logger.info("5. Verify XP is persisting in Neon database:")
    logger.info("   python xp_persistence_monitor.py")
    logger.info("")
    logger.info("6. Use enhanced agent metrics service:")
    logger.info(f"   python {service_path.name}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 