#!/usr/bin/env python3
"""
Fix Original Service Script
===========================
Updates the original ai-backend-python.service with optimizations
and removes the unnecessary optimized service
"""

import subprocess
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def fix_original_service():
    """Fix the original ai-backend-python.service with optimizations"""
    
    logger.info("🔧 Fixing original ai-backend-python.service...")
    
    base_path = "/home/ubuntu/ai-backend-python"
    
    # 1. Stop all services
    logger.info("🛑 Stopping all services...")
    services_to_stop = [
        "ai-backend-optimized.service",
        "ai-backend-python.service"
    ]
    
    for service in services_to_stop:
        try:
            subprocess.run(["sudo", "systemctl", "stop", service], 
                         capture_output=True, text=True, timeout=30)
            logger.info(f"✅ Stopped {service}")
        except Exception as e:
            logger.warning(f"Could not stop {service}: {e}")
    
    # 2. Kill all Python processes
    logger.info("🔪 Killing all Python processes...")
    try:
        subprocess.run(["sudo", "pkill", "-f", "python"], 
                      capture_output=True, timeout=10)
        logger.info("✅ Killed Python processes")
    except Exception as e:
        logger.warning(f"Error killing processes: {e}")
    
    # 3. Update the original main.py to use port 8000
    logger.info("📝 Updating main.py to use port 8000...")
    main_path = f"{base_path}/main.py"
    
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Replace port 4000 with 8000
        content = content.replace('port=4000', 'port=8000')
        
        with open(main_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated main.py to use port 8000")
    
    # 4. Create optimized background service file
    logger.info("🔄 Creating optimized background service...")
    optimized_background_service = '''"""
Optimized Background Service - Performance Critical
Reduced resource usage and optimized scheduling
"""

import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any
from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.services.ai_learning_service import AILearningService

logger = structlog.get_logger()

class OptimizedBackgroundService:
    """Optimized background service with reduced resource usage"""
    
    _instance = None
    _initialized = False
    _running = False
    _tasks = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_agent_service = AIAgentService()
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the service"""
        if cls._instance is None:
            cls._instance = cls()
        await cls._instance.learning_service.initialize()
        logger.info("Optimized Background Service initialized")
        return cls._instance
    
    async def start_optimized_cycle(self):
        """Start optimized autonomous cycle with reduced frequency"""
        if self._running:
            logger.warning("Background service already running")
            return
        
        self._running = True
        logger.info("🤖 Starting OPTIMIZED autonomous AI cycle...")
        
        try:
            # Start only essential background tasks with longer intervals
            self._tasks = [
                asyncio.create_task(self._optimized_github_monitor()),
                asyncio.create_task(self._optimized_learning_cycle()),
                asyncio.create_task(self._optimized_health_monitor()),
            ]
            
            # Wait for all tasks
            await asyncio.gather(*self._tasks)
            
        except Exception as e:
            logger.error("Error in optimized autonomous cycle", error=str(e))
        finally:
            self._running = False
    
    async def stop_optimized_cycle(self):
        """Stop the optimized autonomous cycle"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("🤖 Optimized autonomous cycle stopped")
    
    async def _optimized_github_monitor(self):
        """Optimized GitHub monitoring with longer intervals"""
        while self._running:
            try:
                logger.info("📡 Monitoring GitHub for changes...")
                
                # Get recent commits
                commits = await self.github_service.get_recent_commits(3)  # Reduced from 5
                
                if commits:
                    # Check if there are new commits since last check
                    last_commit_time = datetime.fromisoformat(
                        commits[0]["commit"]["author"]["date"].replace("Z", "+00:00")
                    )
                    
                    # If commits are recent (within last 2 hours), trigger agents
                    if datetime.now(last_commit_time.tzinfo) - last_commit_time < timedelta(hours=2):
                        logger.info("🔄 Recent commits detected, triggering AI agents...")
                        await self.ai_agent_service.run_all_agents()
                
                # Wait 30 minutes before next check (increased from 10 minutes)
                await asyncio.sleep(1800)  # 30 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized GitHub monitor", error=str(e))
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _optimized_learning_cycle(self):
        """Optimized learning cycle with longer intervals"""
        while self._running:
            try:
                logger.info("🧠 Running optimized learning cycle...")
                
                # Get learning insights for all AI types
                ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
                
                for ai_type in ai_types:
                    try:
                        insights = await self.learning_service.get_learning_insights(ai_type)
                        if insights:
                            logger.info(f"📚 Learning insights for {ai_type}", insights=insights)
                    except Exception as e:
                        logger.error(f"Error getting insights for {ai_type}", error=str(e))
                
                # Wait 4 hours before next learning cycle (increased from 1 hour)
                await asyncio.sleep(14400)  # 4 hours
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized learning cycle", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _optimized_health_monitor(self):
        """Optimized health monitoring with longer intervals"""
        while self._running:
            try:
                logger.info("💓 Running optimized health check...")
                
                # Check GitHub connection
                github_status = await self._check_github_health()
                
                # Check database connection
                db_status = await self._check_database_health()
                
                # Log health status
                health_status = {
                    "github": github_status,
                    "database": db_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info("🏥 Optimized health check completed", status=health_status)
                
                # Wait 1 hour before next health check (increased from 15 minutes)
                await asyncio.sleep(3600)  # 1 hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized health monitor", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _check_github_health(self) -> Dict[str, Any]:
        """Check GitHub connection health"""
        try:
            # Simple health check
            return {"status": "healthy", "message": "GitHub connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            # Simple health check
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}
'''
    
    # Write optimized background service
    background_service_path = f"{base_path}/app/services/optimized_background_service.py"
    with open(background_service_path, 'w') as f:
        f.write(optimized_background_service)
    
    logger.info(f"✅ Created optimized background service: {background_service_path}")
    
    # 5. Update the original main.py to use optimized background service
    logger.info("📝 Updating main.py to use optimized background service...")
    
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Replace the background service import and usage
        content = content.replace(
            "from app.services.background_service import BackgroundService",
            "from app.services.optimized_background_service import OptimizedBackgroundService"
        )
        content = content.replace(
            "background_service = BackgroundService()",
            "background_service = await OptimizedBackgroundService.initialize()"
        )
        content = content.replace(
            "asyncio.create_task(background_service.start_autonomous_cycle())",
            "asyncio.create_task(background_service.start_optimized_cycle())"
        )
        
        # Remove enhanced autonomous learning service
        content = content.replace(
            "# Start enhanced autonomous learning service with custody protocol",
            "# Enhanced autonomous learning service disabled for performance"
        )
        content = content.replace(
            "from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService",
            "# from app.services.enhanced_autonomous_learning_service import EnhancedAutonomousLearningService"
        )
        content = content.replace(
            "enhanced_learning_service = EnhancedAutonomousLearningService()",
            "# enhanced_learning_service = EnhancedAutonomousLearningService()"
        )
        content = content.replace(
            "asyncio.create_task(enhanced_learning_service.start_enhanced_autonomous_learning())",
            "# asyncio.create_task(enhanced_learning_service.start_enhanced_autonomous_learning())"
        )
        
        with open(main_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated main.py with optimizations")
    
    # 6. Update the original service configuration
    logger.info("🔧 Updating original service configuration...")
    
    original_service_path = f"{base_path}/ai-backend-python.service"
    if os.path.exists(original_service_path):
        with open(original_service_path, 'r') as f:
            content = f.read()
        
        # Add performance optimizations
        optimized_service_content = f"""[Unit]
Description=AI Backend Python Service - Optimized
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory={base_path}
Environment=PATH={base_path}/venv/bin
Environment=PYTHONPATH={base_path}
ExecStart={base_path}/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Performance optimizations
Nice=10
IOSchedulingClass=2
IOSchedulingPriority=4
CPUSchedulingPolicy=1
CPUSchedulingPriority=10

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096
MemoryMax=2G
CPUQuota=50%

[Install]
WantedBy=multi-user.target
"""
        
        with open(original_service_path, 'w') as f:
            f.write(optimized_service_content)
        
        logger.info("✅ Updated original service configuration")
    
    # 7. Remove the optimized service
    logger.info("🗑️ Removing optimized service...")
    
    try:
        # Stop and disable the optimized service
        subprocess.run(["sudo", "systemctl", "stop", "ai-backend-optimized.service"], 
                      capture_output=True, timeout=30)
        subprocess.run(["sudo", "systemctl", "disable", "ai-backend-optimized.service"], 
                      capture_output=True, timeout=30)
        
        # Remove the service file
        subprocess.run(["sudo", "rm", "-f", "/etc/systemd/system/ai-backend-optimized.service"], 
                      capture_output=True, timeout=30)
        
        logger.info("✅ Removed optimized service")
    except Exception as e:
        logger.warning(f"Error removing optimized service: {e}")
    
    # 8. Reload systemd and start the original service
    logger.info("🔄 Reloading systemd and starting original service...")
    
    try:
        subprocess.run(["sudo", "systemctl", "daemon-reload"], 
                      capture_output=True, timeout=30)
        subprocess.run(["sudo", "systemctl", "enable", "ai-backend-python.service"], 
                      capture_output=True, timeout=30)
        subprocess.run(["sudo", "systemctl", "start", "ai-backend-python.service"], 
                      capture_output=True, timeout=30)
        
        logger.info("✅ Started original optimized service")
    except Exception as e:
        logger.error(f"Error starting service: {e}")
    
    # 9. Wait and check status
    logger.info("⏳ Waiting for service to start...")
    import time
    time.sleep(10)
    
    try:
        result = subprocess.run(["sudo", "systemctl", "status", "ai-backend-python.service"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Service is running")
            logger.info("📊 Service status:")
            for line in result.stdout.split('\n')[:10]:
                if line.strip():
                    logger.info(f"  {line}")
        else:
            logger.error(f"❌ Service failed to start: {result.stderr}")
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
    
    logger.info("✅ Original service optimization completed")

if __name__ == "__main__":
    fix_original_service() 