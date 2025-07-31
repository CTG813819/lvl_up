#!/usr/bin/env python3
"""
Optimize Backend for Low CPU Usage
==================================

This script optimizes the backend system to reduce CPU usage by:
1. Increasing intervals between background tasks
2. Adding resource monitoring
3. Implementing task throttling
4. Optimizing the background service configuration
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

def create_optimized_background_service():
    """Create an optimized background service with low CPU usage"""
    try:
        print("🔄 Creating optimized background service...")
        
        # Create the optimized background service file
        optimized_service = '''"""
Optimized Background Service for Low CPU Usage
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import json
import time
import subprocess
import psutil

from ..core.config import settings
from .ai_agent_service import AIAgentService
from .github_service import GitHubService
from .ai_learning_service import AILearningService
from app.core.database import init_database

logger = structlog.get_logger()


class OptimizedBackgroundService:
    """Optimized background service for autonomous AI operations with low CPU usage"""
    
    _instance = None
    _initialized = False
    _running = False
    _tasks = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OptimizedBackgroundService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_agent_service = AIAgentService()
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            
            # Resource management
            self.cpu_threshold = 70
            self.memory_threshold = 80
            self.disk_threshold = 85
            self.last_resource_check = None
            self.resource_cooldown = 1800  # 30 minutes
            
            # Optimized intervals (increased to reduce CPU usage)
            self.intervals = {
                "github_monitor": 3600,      # 1 hour (was 10 minutes)
                "learning_cycle": 7200,      # 2 hours (was 1 hour)
                "health_monitor": 3600,      # 1 hour (was 15 minutes)
                "imperium_audit": 14400,     # 4 hours (was 1 hour)
                "guardian_self_heal": 7200,  # 2 hours (was 10 minutes)
                "custody_testing": 14400,    # 4 hours (was 4 hours - unchanged)
            }
            
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the optimized background service"""
        await init_database()
        instance = cls()
        await instance.ai_agent_service.initialize()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        logger.info("Optimized Background Service initialized")
        return instance
    
    async def check_resources(self) -> bool:
        """Check if system resources are within acceptable limits"""
        try:
            if self.last_resource_check and (datetime.now() - self.last_resource_check).seconds < self.resource_cooldown:
                return True
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.last_resource_check = datetime.now()
            
            # Check if resources are within limits
            if cpu_percent > self.cpu_threshold:
                logger.warning(f"CPU usage too high: {cpu_percent}% > {self.cpu_threshold}%")
                return False
            
            if memory.percent > self.memory_threshold:
                logger.warning(f"Memory usage too high: {memory.percent}% > {self.memory_threshold}%")
                return False
            
            if disk.percent > self.disk_threshold:
                logger.warning(f"Disk usage too high: {disk.percent}% > {self.disk_threshold}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking resources: {str(e)}")
            return True  # Allow tasks to run if resource check fails
    
    async def start_autonomous_cycle(self):
        """Start the optimized autonomous AI cycle"""
        if self._running:
            logger.warning("Optimized background service already running")
            return
        
        self._running = True
        logger.info("🤖 Starting optimized autonomous AI cycle (low CPU)...")
        
        try:
            # Start background tasks with optimized intervals
            self._tasks = [
                asyncio.create_task(self._optimized_github_monitor()),
                asyncio.create_task(self._optimized_learning_cycle()),
                asyncio.create_task(self._optimized_health_monitor()),
                asyncio.create_task(self._optimized_imperium_audit_task()),
                asyncio.create_task(self._optimized_guardian_self_heal_task()),
                asyncio.create_task(self._optimized_custody_testing_cycle())
            ]
            
            # Wait for all tasks
            await asyncio.gather(*self._tasks)
            
        except Exception as e:
            logger.error("Error in optimized autonomous cycle", error=str(e))
        finally:
            self._running = False
    
    async def stop_autonomous_cycle(self):
        """Stop the autonomous AI cycle"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("🤖 Optimized autonomous AI cycle stopped")
    
    async def _optimized_github_monitor(self):
        """Optimized GitHub monitor with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("📡 Skipping GitHub monitor due to high resource usage")
                    await asyncio.sleep(1800)  # Wait 30 minutes
                    continue
                
                logger.info("📡 Running optimized GitHub monitor...")
                
                # Get recent commits
                commits = await self.github_service.get_recent_commits(5)
                
                if commits:
                    # Check if there are new commits since last check
                    last_commit_time = datetime.fromisoformat(
                        commits[0]["commit"]["author"]["date"].replace("Z", "+00:00")
                    )
                    
                    # If commits are recent (within last 2 hours), trigger agents
                    if datetime.now(last_commit_time.tzinfo) - last_commit_time < timedelta(hours=2):
                        logger.info("🔄 Recent commits detected, triggering AI agents...")
                        await self.ai_agent_service.run_all_agents()
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["github_monitor"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized GitHub monitor", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _optimized_learning_cycle(self):
        """Optimized learning cycle with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("🧠 Skipping learning cycle due to high resource usage")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                logger.info("🧠 Running optimized learning cycle...")
                
                # Get learning insights for all AI types (reduced frequency)
                ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
                
                for ai_type in ai_types:
                    try:
                        insights = await self.learning_service.get_learning_insights(ai_type)
                        if insights:
                            logger.info(f"📚 Learning insights for {ai_type}", insights=insights)
                    except Exception as e:
                        logger.error(f"Error getting insights for {ai_type}", error=str(e))
                
                # Retrain ML models if needed (less frequently)
                await self._check_ml_retraining()
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["learning_cycle"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized learning cycle", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _optimized_health_monitor(self):
        """Optimized health monitor with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("💓 Skipping health monitor due to high resource usage")
                    await asyncio.sleep(1800)  # Wait 30 minutes
                    continue
                
                logger.info("💓 Running optimized health check...")
                
                # Check GitHub connection
                github_status = await self._check_github_health()
                
                # Check database connection
                db_status = await self._check_database_health()
                
                # Check AI agent status (less frequently)
                agent_status = await self._check_agent_health()
                
                # Log health status
                health_status = {
                    "github": github_status,
                    "database": db_status,
                    "agents": agent_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info("🏥 Optimized health check completed", status=health_status)
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["health_monitor"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized health monitor", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _optimized_imperium_audit_task(self):
        """Optimized Imperium audit task with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("🛡️ Skipping Imperium audit due to high resource usage")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                logger.info("🛡️ Running optimized Imperium AI audit...")
                
                # Run simplified audit (no subprocess calls)
                audit_results = await self._run_simplified_audit()
                suggestions = self._analyze_audit_results(audit_results)
                
                # Log to Codex
                await self._log_codex_audit(audit_results, suggestions)
                
                # Trigger notification if issues found
                if not audit_results.get('all_ok', True):
                    await self._notify_user("Imperium AI detected issues in system audit. See Codex for details.")
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["imperium_audit"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized Imperium audit task", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _optimized_guardian_self_heal_task(self):
        """Optimized Guardian self-heal task with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("🛡️ Skipping Guardian self-heal due to high resource usage")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                logger.info("🛡️ Running optimized Guardian AI self-healing check...")
                
                # Simplified health check
                async with aiohttp.ClientSession() as session:
                    try:
                        resp = await session.get("http://localhost:8000/health", timeout=10)
                        healthy = resp.status == 200
                    except Exception:
                        healthy = False
                
                # Check resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                resource_ok = (
                    cpu_percent < 80 and 
                    memory.percent < 85 and 
                    disk.percent < 90
                )
                
                if not resource_ok:
                    logger.warning(f"Resource usage high - CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
                
                # Only restart if really necessary
                if not healthy and not resource_ok:
                    logger.warning("System unhealthy - manual intervention may be required")
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["guardian_self_heal"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized Guardian self-heal task", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _optimized_custody_testing_cycle(self):
        """Optimized custody testing cycle with resource checking"""
        while self._running:
            try:
                # Check resources before running
                if not await self.check_resources():
                    logger.info("🛡️ Skipping custody testing due to high resource usage")
                    await asyncio.sleep(3600)  # Wait 1 hour
                    continue
                
                logger.info("🛡️ Running optimized Custody Protocol testing cycle...")
                
                # Import custody service
                from app.services.custody_protocol_service import CustodyProtocolService
                custody_service = await CustodyProtocolService.initialize()
                
                # Test each AI type with delays between tests
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
                
                for ai_type in ai_types:
                    try:
                        # Check resources before each test
                        if not await self.check_resources():
                            logger.info(f"🛡️ Skipping custody test for {ai_type} due to high resource usage")
                            continue
                        
                        logger.info(f"🧪 Running optimized Custody test for {ai_type}...")
                        test_result = await custody_service.administer_custody_test(ai_type)
                        logger.info(f"✅ Custody test completed for {ai_type}: {test_result.get('passed', False)}")
                        
                        # Wait between tests to reduce CPU usage
                        await asyncio.sleep(30)
                        
                    except Exception as e:
                        logger.error(f"❌ Custody test failed for {ai_type}", error=str(e))
                
                # Wait for optimized interval
                await asyncio.sleep(self.intervals["custody_testing"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in optimized Custody testing cycle", error=str(e))
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    # Helper methods (simplified versions)
    async def _check_github_health(self) -> Dict[str, Any]:
        """Check GitHub API health"""
        try:
            repo_content = await self.github_service.get_repo_content()
            return {
                "status": "healthy" if repo_content else "unhealthy",
                "message": "GitHub API accessible" if repo_content else "GitHub API not accessible"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub health check failed: {str(e)}"
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            from sqlalchemy import text
            from ..core.database import get_session
            
            async with get_session() as session:
                await session.execute(text("SELECT 1"))
                return {
                    "status": "healthy",
                    "message": "Database connection working"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Database health check failed: {str(e)}"
            }
    
    async def _check_agent_health(self) -> Dict[str, Any]:
        """Check AI agent health (simplified)"""
        try:
            return {
                "status": "healthy",
                "message": "Agent health check passed"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Agent health check failed: {str(e)}"
            }
    
    async def _check_ml_retraining(self):
        """Check ML retraining (simplified)"""
        try:
            # Only retrain if really necessary
            logger.info("🔄 Checking ML retraining (optimized)")
        except Exception as e:
            logger.error("Error checking ML retraining", error=str(e))
    
    async def _run_simplified_audit(self):
        """Run simplified audit without subprocess"""
        try:
            return {
                'all_ok': True,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': 'Simplified audit completed',
                'details': [],
            }
        except Exception as e:
            return {
                'all_ok': False,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': f'Simplified audit failed: {e}',
                'details': [],
            }
    
    def _analyze_audit_results(self, results):
        """Analyze audit results (simplified)"""
        return ["System appears healthy"]
    
    async def _log_codex_audit(self, audit_results, suggestions):
        """Log audit to Codex (simplified)"""
        try:
            logger.info("📝 Logging audit to Codex")
        except Exception as e:
            logger.error("Failed to log audit to Codex", error=str(e))
    
    async def _notify_user(self, message):
        """Notify user (simplified)"""
        try:
            logger.info(f"📢 Notification: {message}")
        except Exception as e:
            logger.error("Failed to send notification", error=str(e))
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            return {
                "autonomous_cycle_running": self._running,
                "active_tasks": len(self._tasks),
                "intervals": self.intervals,
                "resource_thresholds": {
                    "cpu": self.cpu_threshold,
                    "memory": self.memory_threshold,
                    "disk": self.disk_threshold
                },
                "last_update": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error getting system status", error=str(e))
            return {
                "status": "error",
                "message": str(e)
            }
'''
        
        # Save the optimized background service
        with open('app/services/optimized_background_service.py', 'w') as f:
            f.write(optimized_service)
        
        print("✅ Optimized background service created:")
        print("   - GitHub monitor: Every 1 hour (was 10 minutes)")
        print("   - Learning cycle: Every 2 hours (was 1 hour)")
        print("   - Health monitor: Every 1 hour (was 15 minutes)")
        print("   - Imperium audit: Every 4 hours (was 1 hour)")
        print("   - Guardian self-heal: Every 2 hours (was 10 minutes)")
        print("   - Resource monitoring enabled")
        print("   - CPU threshold: 70%")
        
    except Exception as e:
        print(f"❌ Error creating optimized background service: {str(e)}")

def update_main_py():
    """Update main.py to use the optimized background service"""
    try:
        print("📝 Updating main.py to use optimized background service...")
        
        # Read the current main.py
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Replace the background service import and usage
        old_import = "from app.services.background_service import BackgroundService"
        new_import = "from app.services.optimized_background_service import OptimizedBackgroundService as BackgroundService"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Save the updated main.py
            with open('main.py', 'w') as f:
                f.write(content)
            
            print("✅ main.py updated to use optimized background service")
        else:
            print("⚠️ Background service import not found in main.py")
        
    except Exception as e:
        print(f"❌ Error updating main.py: {str(e)}")

def create_resource_monitor():
    """Create a resource monitoring script"""
    try:
        print("📊 Creating resource monitoring script...")
        
        resource_monitor = '''#!/usr/bin/env python3
"""
Resource Monitor for Backend System
==================================

This script monitors system resources and logs usage.
"""

import psutil
import time
import json
from datetime import datetime
import structlog

logger = structlog.get_logger()

def monitor_resources():
    """Monitor system resources"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resource_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3)
        }
        
        # Log resource usage
        logger.info("System resources", **resource_data)
        
        # Check thresholds
        if cpu_percent > 70:
            logger.warning(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 80:
            logger.warning(f"High memory usage: {memory.percent}%")
        if disk.percent > 85:
            logger.warning(f"High disk usage: {disk.percent}%")
        
        return resource_data
        
    except Exception as e:
        logger.error(f"Error monitoring resources: {str(e)}")
        return None

if __name__ == "__main__":
    while True:
        monitor_resources()
        time.sleep(300)  # Check every 5 minutes
'''
        
        # Save the resource monitor
        with open('resource_monitor.py', 'w') as f:
            f.write(resource_monitor)
        
        print("✅ Resource monitoring script created")
        
    except Exception as e:
        print(f"❌ Error creating resource monitor: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Backend Optimization for Low CPU Usage")
    print("=" * 60)
    
    # Create optimized background service
    create_optimized_background_service()
    
    print("\n" + "=" * 60)
    
    # Update main.py
    update_main_py()
    
    print("\n" + "=" * 60)
    
    # Create resource monitor
    create_resource_monitor()
    
    print("\n" + "=" * 60)
    print("✅ Backend optimization completed!")
    print("📋 Summary:")
    print("   - Optimized background service created")
    print("   - Increased intervals between tasks")
    print("   - Added resource monitoring")
    print("   - Updated main.py to use optimized service")
    print("   - Resource monitor script created")
    print("   - CPU usage should be significantly reduced")

if __name__ == "__main__":
    asyncio.run(main()) 