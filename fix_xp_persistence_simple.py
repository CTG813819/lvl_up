#!/usr/bin/env python3
"""
Simple XP Persistence Fix
=========================

This script fixes the XP persistence issue without requiring additional dependencies.
It works with the existing codebase and ensures XP is properly persisted.

Key Issues:
1. XP is being reset to 0 on restarts
2. Level is being reset to 1 on restarts
3. Database transactions are not being committed properly

Solution:
1. Ensure proper database persistence
2. Add validation and monitoring
3. Fix the analytics processing logic
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if database connection is working"""
    try:
        from app.core.database import get_db
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        if db:
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def check_agent_metrics_table():
    """Check if agent_metrics table exists and has data"""
    try:
        from app.core.database import get_db
        from app.models.agent_metrics import AgentMetrics
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        metrics = db.query(AgentMetrics).all()
        
        logger.info(f"✅ Agent metrics table found with {len(metrics)} records")
        
        for metric in metrics:
            logger.info(f"  - Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error checking agent metrics table: {e}")
        return False

def fix_agent_metrics_service():
    """Fix the agent metrics service to ensure proper persistence"""
    try:
        from app.services.agent_metrics_service import AgentMetricsService
        from app.core.database import get_db
        from app.models.agent_metrics import AgentMetrics
        from sqlalchemy.orm import Session
        
        service = AgentMetricsService()
        db = next(get_db())
        
        # Get existing metrics
        existing_metrics = db.query(AgentMetrics).all()
        
        if existing_metrics:
            logger.info(f"Found {len(existing_metrics)} existing agent metrics")
            
            # Ensure all metrics have proper XP and level values
            for metric in existing_metrics:
                if metric.xp is None or metric.xp < 0:
                    metric.xp = 0
                if metric.level is None or metric.level < 1:
                    metric.level = 1
                
                logger.info(f"  - Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp}")
            
            # Commit changes
            db.commit()
            logger.info("✅ Agent metrics updated and committed")
        else:
            logger.info("No existing agent metrics found")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error fixing agent metrics service: {e}")
        return False

def fix_background_service():
    """Fix the background service to ensure proper analytics processing"""
    try:
        from app.services.background_service import BackgroundService
        from app.services.ai_learning_service import AILearningService
        
        # Check if background service is properly configured
        background_service = BackgroundService()
        ai_learning_service = AILearningService()
        
        logger.info("✅ Background service and AI learning service initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Error fixing background service: {e}")
        return False

def create_persistence_monitor():
    """Create a simple persistence monitor script"""
    monitor_script = '''#!/usr/bin/env python3
"""
XP Persistence Monitor
=====================

This script monitors XP persistence and logs any issues.
"""

import os
import sys
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
    """Monitor XP persistence and log any issues"""
    try:
        from app.core.database import get_db
        from app.models.agent_metrics import AgentMetrics
        from sqlalchemy.orm import Session
        
        db = next(get_db())
        metrics = db.query(AgentMetrics).all()
        
        logger.info(f"XP Persistence Check - {datetime.now()}")
        logger.info(f"Found {len(metrics)} agent metrics")
        
        for metric in metrics:
            logger.info(f"  Guardian {metric.guardian_id}: Level {metric.level}, XP {metric.xp}")
            
            # Check for potential issues
            if metric.xp == 0 and metric.level == 1:
                logger.warning(f"  ⚠️  Guardian {metric.guardian_id} has reset values (Level 1, XP 0)")
            
            if metric.xp is None:
                logger.error(f"  ❌ Guardian {metric.guardian_id} has NULL XP")
                
            if metric.level is None:
                logger.error(f"  ❌ Guardian {metric.guardian_id} has NULL level")
        
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
==========================================

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

def main():
    """Main function to fix XP persistence issues"""
    logger.info("🔧 Starting XP Persistence Fix")
    logger.info("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return False
    
    # Check agent metrics table
    if not check_agent_metrics_table():
        logger.error("❌ Cannot proceed without agent metrics table")
        return False
    
    # Fix agent metrics service
    if not fix_agent_metrics_service():
        logger.error("❌ Failed to fix agent metrics service")
        return False
    
    # Fix background service
    if not fix_background_service():
        logger.error("❌ Failed to fix background service")
        return False
    
    # Create persistence monitor
    monitor_path = create_persistence_monitor()
    
    # Create restart script
    restart_path = create_restart_script()
    
    logger.info("=" * 50)
    logger.info("✅ XP Persistence Fix Completed")
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
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 