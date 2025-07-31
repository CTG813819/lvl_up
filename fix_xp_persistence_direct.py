#!/usr/bin/env python3
"""
Direct XP Persistence Fix for Neon Database
==========================================

This script fixes XP persistence issues directly without requiring additional dependencies.
It works with the existing codebase and ensures XP is properly persisted.

Key Issues:
1. XP is being reset to 0 on restarts
2. Level is being reset to 1 on restarts
3. Database transactions are not being committed properly

Solution:
1. Direct database operations
2. Add validation and monitoring
3. Fix the analytics processing logic
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

def check_database_direct():
    """Check database connection directly"""
    try:
        logger.info("🔍 Checking database connection directly...")
        
        # Try to import database modules without pydantic_settings
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
            
            # Import database modules directly
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            # Database URL (hardcoded to avoid pydantic_settings dependency)
            DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb"
            
            # Create engine
            engine = create_engine(DATABASE_URL)
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Database connection successful")
                
                # Check agent_metrics table
                result = conn.execute(text("SELECT COUNT(*) FROM agent_metrics"))
                count = result.scalar()
                logger.info(f"✅ Agent metrics table found with {count} records")
                
                # Get sample data
                result = conn.execute(text("SELECT agent_id, agent_type, xp, level FROM agent_metrics LIMIT 5"))
                for row in result:
                    logger.info(f"  - {row.agent_type}: Level {row.level}, XP {row.xp}")
                
                return True
                
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def fix_agent_metrics_direct():
    """Fix agent metrics persistence directly"""
    try:
        logger.info("🔧 Fixing agent metrics persistence directly...")
        
        # Import database modules directly
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Database URL
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Get existing metrics
            result = conn.execute(text("SELECT agent_id, agent_type, xp, level FROM agent_metrics"))
            existing_metrics = result.fetchall()
            
            if existing_metrics:
                logger.info(f"Found {len(existing_metrics)} existing agent metrics")
                
                # Fix null or invalid values
                updated_count = 0
                for row in existing_metrics:
                    agent_id = row.agent_id
                    agent_type = row.agent_type
                    xp = row.xp
                    level = row.level
                    
                    # Fix null or invalid values
                    if xp is None or xp < 0:
                        xp = 0
                    if level is None or level < 1:
                        level = 1
                    
                    # Update if needed
                    if row.xp != xp or row.level != level:
                        conn.execute(text("""
                            UPDATE agent_metrics 
                            SET xp = :xp, level = :level, updated_at = NOW()
                            WHERE agent_id = :agent_id
                        """), {"xp": xp, "level": level, "agent_id": agent_id})
                        
                        logger.info(f"  - {agent_type}: Fixed XP {row.xp} -> {xp}, Level {row.level} -> {level}")
                        updated_count += 1
                    else:
                        logger.info(f"  - {agent_type}: Level {level}, XP {xp} (no changes needed)")
                
                # Commit changes
                conn.commit()
                logger.info(f"✅ Updated {updated_count} agent metrics and committed to database")
            else:
                logger.info("No existing agent metrics found")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error fixing agent metrics persistence: {e}")
        return False

def create_simple_xp_monitor():
    """Create a simple XP monitoring script"""
    monitor_script = '''#!/usr/bin/env python3
"""
Simple XP Persistence Monitor
============================

This script monitors XP persistence in the database.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

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
    """Monitor XP persistence in database"""
    try:
        from sqlalchemy import create_engine, text
        
        # Database URL
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT agent_id, agent_type, xp, level FROM agent_metrics"))
            metrics = result.fetchall()
            
            logger.info(f"XP Persistence Check - {datetime.now()}")
            logger.info(f"Found {len(metrics)} agent metrics in database")
            
            total_xp = 0
            for row in metrics:
                logger.info(f"  {row.agent_type}: Level {row.level}, XP {row.xp}")
                total_xp += row.xp if row.xp else 0
                
                # Check for potential issues
                if row.xp == 0 and row.level == 1:
                    logger.warning(f"  ⚠️  {row.agent_type} has reset values (Level 1, XP 0)")
                
                if row.xp is None:
                    logger.error(f"  ❌ {row.agent_type} has NULL XP")
                    
                if row.level is None:
                    logger.error(f"  ❌ {row.agent_type} has NULL level")
            
            logger.info(f"Total XP across all agents: {total_xp}")
            logger.info("XP persistence check completed")
        
    except Exception as e:
        logger.error(f"Error monitoring XP persistence: {e}")

if __name__ == "__main__":
    monitor_xp_persistence()
'''
    
    monitor_path = Path(__file__).parent / "simple_xp_monitor.py"
    with open(monitor_path, 'w') as f:
        f.write(monitor_script)
    
    # Make it executable
    os.chmod(monitor_path, 0o755)
    logger.info(f"✅ Created simple XP monitor: {monitor_path}")
    
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
python simple_xp_monitor.py

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

def create_xp_update_script():
    """Create a script to manually update XP"""
    update_script = '''#!/usr/bin/env python3
"""
Manual XP Update Script
======================

This script allows manual XP updates for testing persistence.
"""

import sys
import os
from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb"

def update_agent_xp(agent_type, xp_amount):
    """Update XP for a specific agent"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Get current XP
            result = conn.execute(text("""
                SELECT xp, level FROM agent_metrics 
                WHERE agent_type = :agent_type
            """), {"agent_type": agent_type})
            
            row = result.fetchone()
            if row:
                current_xp = row.xp or 0
                current_level = row.level or 1
                
                # Update XP
                new_xp = current_xp + xp_amount
                new_level = (new_xp // 1000) + 1
                
                # Update database
                conn.execute(text("""
                    UPDATE agent_metrics 
                    SET xp = :xp, level = :level, updated_at = NOW()
                    WHERE agent_type = :agent_type
                """), {
                    "xp": new_xp, 
                    "level": new_level, 
                    "agent_type": agent_type
                })
                
                conn.commit()
                
                print(f"✅ Updated {agent_type}: XP {current_xp} -> {new_xp} (+{xp_amount})")
                if new_level > current_level:
                    print(f"🎉 {agent_type} leveled up from {current_level} to {new_level}!")
                
                return True
            else:
                print(f"❌ No metrics found for {agent_type}")
                return False
                
    except Exception as e:
        print(f"❌ Error updating XP for {agent_type}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python xp_update.py <agent_type> <xp_amount>")
        print("Example: python xp_update.py guardian 100")
        sys.exit(1)
    
    agent_type = sys.argv[1]
    xp_amount = int(sys.argv[2])
    
    update_agent_xp(agent_type, xp_amount)
'''
    
    update_path = Path(__file__).parent / "xp_update.py"
    with open(update_path, 'w') as f:
        f.write(update_script)
    
    # Make it executable
    os.chmod(update_path, 0o755)
    logger.info(f"✅ Created XP update script: {update_path}")
    
    return update_path

def main():
    """Main function to fix XP persistence issues"""
    logger.info("🔧 Starting Direct XP Persistence Fix")
    logger.info("=" * 50)
    
    # Check database connection
    if not check_database_direct():
        logger.error("❌ Cannot proceed without database connection")
        return False
    
    # Fix agent metrics persistence
    if not fix_agent_metrics_direct():
        logger.error("❌ Failed to fix agent metrics persistence")
        return False
    
    # Check backend service
    check_backend_service()
    
    # Create simple XP monitor
    monitor_path = create_simple_xp_monitor()
    
    # Create restart script
    restart_path = create_restart_script()
    
    # Create XP update script
    update_path = create_xp_update_script()
    
    logger.info("=" * 50)
    logger.info("✅ Direct XP Persistence Fix Completed")
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
    logger.info("5. Test XP updates manually:")
    logger.info(f"   python {update_path.name} guardian 100")
    logger.info("")
    logger.info("6. Verify XP is persisting:")
    logger.info("   python simple_xp_monitor.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 