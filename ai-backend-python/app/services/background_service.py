"""
Background Service for Autonomous AI Operations
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import json
import time
import subprocess

from ..core.config import settings
from .ai_agent_service import AIAgentService
from .github_service import GitHubService
from .ai_learning_service import AILearningService
from app.core.database import init_database

logger = structlog.get_logger()


class BackgroundService:
    """Background service for autonomous AI operations"""
    
    _instance = None
    _initialized = False
    _running = False
    _tasks = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackgroundService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_agent_service = AIAgentService()
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the background service"""
        await init_database()
        instance = cls()
        await instance.ai_agent_service.initialize()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        logger.info("Background Service initialized")
        return instance
    
    async def start_autonomous_cycle(self):
        """Start the autonomous AI cycle"""
        if self._running:
            logger.warning("Background service already running")
            return
        
        self._running = True
        logger.info("🤖 Starting autonomous AI cycle...")
        
        try:
            # Start background tasks (disable _agent_scheduler to avoid duplicate proposal generation)
            self._tasks = [
                # asyncio.create_task(self._agent_scheduler()),  # DISABLED: Only proposals.py should generate proposals
                asyncio.create_task(self._github_monitor()),
                asyncio.create_task(self._learning_cycle()),
                asyncio.create_task(self._health_monitor()),
                asyncio.create_task(self._imperium_audit_task()),  # NEW: Imperium audit every 2 hours
                asyncio.create_task(self._guardian_self_heal_task())  # NEW: Guardian self-healing
            ]
            
            # Wait for all tasks
            await asyncio.gather(*self._tasks)
            
        except Exception as e:
            logger.error("Error in autonomous cycle", error=str(e))
        finally:
            self._running = False
    
    async def stop_autonomous_cycle(self):
        """Stop the autonomous AI cycle"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("🤖 Autonomous AI cycle stopped")
    
    async def _agent_scheduler(self):
        """Schedule and run AI agents"""
        while self._running:
            try:
                logger.info("🕐 Running scheduled AI agent cycle...")
                
                # Run all AI agents
                result = await self.ai_agent_service.run_all_agents()
                
                if result["status"] == "success":
                    logger.info("✅ AI agent cycle completed", 
                               agents_run=result["agents_run"],
                               proposals_created=result["total_proposals_created"])
                else:
                    logger.error("❌ AI agent cycle failed", error=result.get("message"))
                
                # Wait 30 minutes before next cycle
                await asyncio.sleep(1800)  # 30 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in agent scheduler", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _github_monitor(self):
        """Monitor GitHub for changes and trigger agents"""
        while self._running:
            try:
                logger.info("📡 Monitoring GitHub for changes...")
                
                # Get recent commits
                commits = await self.github_service.get_recent_commits(5)
                
                if commits:
                    # Check if there are new commits since last check
                    last_commit_time = datetime.fromisoformat(
                        commits[0]["commit"]["author"]["date"].replace("Z", "+00:00")
                    )
                    
                    # If commits are recent (within last hour), trigger agents
                    if datetime.now(last_commit_time.tzinfo) - last_commit_time < timedelta(hours=1):
                        logger.info("🔄 Recent commits detected, triggering AI agents...")
                        await self.ai_agent_service.run_all_agents()
                
                # Wait 10 minutes before next check
                await asyncio.sleep(600)  # 10 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in GitHub monitor", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _learning_cycle(self):
        """Continuous learning cycle"""
        while self._running:
            try:
                logger.info("🧠 Running learning cycle...")
                
                # Get learning insights for all AI types
                ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
                
                for ai_type in ai_types:
                    try:
                        insights = await self.learning_service.get_learning_insights(ai_type)
                        if insights:
                            logger.info(f"📚 Learning insights for {ai_type}", insights=insights)
                    except Exception as e:
                        logger.error(f"Error getting insights for {ai_type}", error=str(e))
                
                # Retrain ML models if needed
                await self._check_ml_retraining()
                
                # Wait 1 hour before next learning cycle
                await asyncio.sleep(3600)  # 1 hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in learning cycle", error=str(e))
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _health_monitor(self):
        """Monitor system health and performance"""
        while self._running:
            try:
                logger.info("💓 Running health check...")
                
                # Check GitHub connection
                github_status = await self._check_github_health()
                
                # Check database connection
                db_status = await self._check_database_health()
                
                # Check AI agent status
                agent_status = await self._check_agent_health()
                
                # Log health status
                health_status = {
                    "github": github_status,
                    "database": db_status,
                    "agents": agent_status,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info("🏥 Health check completed", status=health_status)
                
                # Wait 15 minutes before next health check
                await asyncio.sleep(900)  # 15 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health monitor", error=str(e))
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def _imperium_audit_task(self):
        """Run a full backend (and optionally frontend) check every 1 hour, log to Codex, trigger notifications."""
        while self._running:
            try:
                logger.info("🛡️ Imperium AI running full system audit...")
                # Run real backend audit script
                audit_results = await self._run_backend_audit()
                # Analyze and suggest improvements
                suggestions = self._analyze_audit_results(audit_results)
                # Log to Codex (as a new event/chapter)
                await self._log_codex_audit(audit_results, suggestions)
                # Trigger notification if issues found
                if not audit_results.get('all_ok', True):
                    await self._notify_user("Imperium AI detected issues in system audit. See Codex for details.")
                # Wait 1 hour before next audit
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in Imperium audit task", error=str(e))
                await asyncio.sleep(600)  # Wait 10 minutes on error

    async def _run_backend_audit(self):
        """Run backend check and return results by calling the real script."""
        import json
        try:
            result = subprocess.run([
                'python3', 'test_backend_comprehensive_check.py'
            ], capture_output=True, text=True, cwd='/home/ubuntu/ai-backend-python'),
            output = result[0].stdout
            # Try to parse output as JSON
            audit_data = json.loads(output)
            audit_data['all_ok'] = audit_data.get('status', 'success') == 'success'
            audit_data['timestamp'] = datetime.utcnow().isoformat()
            return audit_data
        except Exception as e:
            logger.error(f"Failed to run backend audit script: {e}")
            return {
                'all_ok': False,
                'timestamp': datetime.utcnow().isoformat(),
                'summary': f'Backend audit script failed: {e}',
                'details': [],
            }

    def _analyze_audit_results(self, results):
        """Imperium analyzes audit results and suggests improvements."""
        # Real analysis based on audit results
        suggestions = []
        if results.get('all_ok', True):
            suggestions.append('No issues found. System is healthy.')
        else:
            suggestions.append('Review failed endpoints and logs.')
            
        # Add specific suggestions based on audit details
        details = results.get('details', [])
        for detail in details:
            if 'error' in detail.lower():
                suggestions.append(f'Fix error in {detail}')
            elif 'timeout' in detail.lower():
                suggestions.append('Optimize response times')
            elif 'memory' in detail.lower():
                suggestions.append('Monitor memory usage')
                
        return suggestions

    async def _log_codex_audit(self, audit_results, suggestions):
        """Log audit results and suggestions to the Codex (as a new event/chapter)."""
        logger.info("[Codex] Imperium AI Audit Log", audit=audit_results, suggestions=suggestions)
        # Actually log to Codex via API
        import aiohttp
        codex_event = {
            "type": "imperium_audit",
            "summary": audit_results.get('summary', ''),
            "details": audit_results.get('details', []),
            "suggestions": suggestions,
            "all_ok": audit_results.get('all_ok', True),
        }
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "http://localhost:8000/api/codex/log",
                    json=codex_event,
                    timeout=10
                )
        except Exception as e:
            logger.error("Failed to log Codex audit event via API", error=str(e))

    async def _notify_user(self, message):
        """Trigger a notification to the user (extend as needed)."""
        logger.info("[Notification]", message=message)
        # TODO: Implement actual notification logic (WebSocket, push, etc.)
    
    async def _check_ml_retraining(self):
        """Check if ML models need retraining"""
        try:
            # Get recent learning data
            from sqlalchemy import select, func
            from ..models.sql_models import Learning
            from ..core.database import get_session
            
            async with get_session() as session:
                # Count recent learning entries
                stmt = select(func.count(Learning.id)).where(
                    Learning.created_at >= datetime.utcnow() - timedelta(days=7)
                )
                result = await session.execute(stmt)
                recent_entries = result.scalar()
                
                # If we have enough new data, retrain models
                if recent_entries > 50:
                    logger.info("🔄 Retraining ML models due to new learning data")
                    await self.ai_agent_service.ml_service.train_models()
                
        except Exception as e:
            logger.error("Error checking ML retraining", error=str(e))
    
    async def _check_github_health(self) -> Dict[str, Any]:
        """Check GitHub API health"""
        try:
            # Test GitHub API connection
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
                # Test database connection
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
        """Check AI agent health"""
        try:
            # Test agent functionality
            result = await self.ai_agent_service.run_imperium_agent()
            return {
                "status": "healthy" if result["status"] == "success" else "warning",
                "message": f"Agent test: {result.get('message', 'Unknown')}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Agent health check failed: {str(e)}"
            }
    
    async def run_manual_cycle(self) -> Dict[str, Any]:
        """Run a manual AI agent cycle"""
        try:
            logger.info("🔄 Running manual AI agent cycle...")
            
            result = await self.ai_agent_service.run_all_agents()
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error in manual cycle", error=str(e))
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            return {
                "autonomous_cycle_running": self._running,
                "active_tasks": len(self._tasks),
                "github_health": await self._check_github_health(),
                "database_health": await self._check_database_health(),
                "agent_health": await self._check_agent_health(),
                "last_update": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error getting system status", error=str(e))
            return {
                "status": "error",
                "message": str(e)
            } 

    async def _guardian_self_heal_task(self):
        """Guardian AI: Monitor and self-heal backend every 10 minutes."""
        import aiohttp
        import subprocess
        while self._running:
            try:
                logger.info("🛡️ Guardian AI running self-healing check...")
                # 1. Check backend health endpoint
                async with aiohttp.ClientSession() as session:
                    try:
                        resp = await session.get("http://localhost:8000/health", timeout=10)
                        healthy = resp.status == 200
                    except Exception:
                        healthy = False
                # 2. Check resource usage (real monitoring)
                try:
                    import psutil
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
                        
                except ImportError:
                    logger.warning("psutil not available, using fallback resource check")
                    resource_ok = True
                # 3. If unhealthy, attempt automated fix
                healing_action = None
                healing_success = None
                if not healthy or not resource_ok:
                    healing_action = "restart_service"
                    try:
                        subprocess.run(["sudo", "systemctl", "restart", "ai-backend-python"], check=True)
                        healing_success = True
                    except Exception as e:
                        healing_success = False
                        logger.error("Guardian failed to restart backend", error=str(e))
                # 4. Log healing action to Codex
                codex_event = {
                    "type": "guardian_self_heal",
                    "summary": f"Guardian AI ran self-healing. Healthy: {healthy}, Resource OK: {resource_ok}",
                    "details": {
                        "healing_action": healing_action,
                        "healing_success": healing_success
                    },
                    "all_ok": healthy and resource_ok,
                }
                try:
                    async with aiohttp.ClientSession() as session:
                        await session.post(
                            "http://localhost:8000/api/codex/log",
                            json=codex_event,
                            timeout=10
                        )
                except Exception as e:
                    logger.error("Failed to log Guardian Codex event via API", error=str(e))
                # 5. Notify user if manual intervention needed
                if not healthy or not resource_ok:
                    await self._notify_user("Guardian AI attempted self-healing. Manual intervention may be required.")
                # Wait 10 minutes before next check
                await asyncio.sleep(600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in Guardian self-heal task", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error 