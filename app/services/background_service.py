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
from ..core.railway_utils import should_skip_external_requests
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
    _test_lock = None  # Lock to prevent overlapping test executions
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackgroundService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_agent_service = AIAgentService()
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            self._test_lock = asyncio.Lock()  # Initialize test lock
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the background service"""
        await init_database()
        instance = cls()
        await instance.ai_agent_service.initialize()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        
        # Initialize enhanced test generator
        try:
            from app.services.enhanced_test_generator import EnhancedTestGenerator
            instance.enhanced_test_generator = await EnhancedTestGenerator.initialize()
            logger.info("✅ Enhanced Test Generator initialized in background service")
        except Exception as e:
            logger.warning(f"Failed to initialize Enhanced Test Generator: {e}")
            instance.enhanced_test_generator = None
        
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
            # Start background tasks without waiting for them to complete
            self._tasks = [
                # asyncio.create_task(self._agent_scheduler()),  # DISABLED: Only proposals.py should generate proposals
                asyncio.create_task(self._learning_cycle()),
                asyncio.create_task(self._custody_testing_cycle()),  # Custody testing every 20 minutes
                asyncio.create_task(self._olympic_events_cycle()),   # Olympic events every 45 minutes
                asyncio.create_task(self._collaborative_tests_cycle())  # Collaborative tests every 90 minutes
            ]
            # Removed: _imperium_audit_task
            
            # Don't wait for tasks to complete - they are infinite loops
            logger.info("✅ Background tasks started successfully")
            
        except Exception as e:
            logger.error(f"Error in autonomous cycle: {str(e)}")
            self._running = False
    
    async def stop_autonomous_cycle(self):
        """Stop the autonomous AI cycle"""
        self._running = False
        for task in self._tasks:
            task.cancel()
        logger.info("🤖 Autonomous AI cycle stopped")
    
    async def _learning_cycle(self):
        """Learning cycle that runs every 30 minutes"""
        while self._running:
            try:
                logger.info("🧠 Starting learning cycle...")
                await self.learning_service.learn_from_internet()
                logger.info("✅ Learning cycle completed")
            except Exception as e:
                logger.error(f"Error in learning cycle: {str(e)}")
            
            await asyncio.sleep(1800)  # 30 minutes
    
    async def _custody_testing_cycle(self):
        """Custody testing cycle that runs every 20 minutes"""
        while self._running:
            try:
                logger.info("🔒 Starting custody testing cycle...")
                await self._administer_custody_tests()
                logger.info("✅ Custody testing cycle completed")
            except Exception as e:
                logger.error(f"Error in custody testing cycle: {str(e)}")
            
            await asyncio.sleep(1200)  # 20 minutes
    
    async def _olympic_events_cycle(self):
        """Olympic events cycle that runs every 45 minutes"""
        while self._running:
            try:
                logger.info("🏆 Starting Olympic events cycle...")
                await self._trigger_olympic_events()
                logger.info("✅ Olympic events cycle completed")
            except Exception as e:
                logger.error(f"Error in Olympic events cycle: {str(e)}")
            
            await asyncio.sleep(2700)  # 45 minutes
    
    async def _collaborative_tests_cycle(self):
        """Collaborative tests cycle that runs every 90 minutes"""
        while self._running:
            try:
                logger.info("🤝 Starting collaborative tests cycle...")
                await self._run_collaborative_tests()
                logger.info("✅ Collaborative tests cycle completed")
            except Exception as e:
                logger.error(f"Error in collaborative tests cycle: {str(e)}")
            
            await asyncio.sleep(5400)  # 90 minutes
    
    async def _administer_custody_tests(self):
        """Administer custody tests for all AI types"""
        try:
            from .custody_service import CustodyService
            custody_service = CustodyService()
            
            # Test Horus AI
            await self._administer_test_with_fallback(custody_service, "horus")
            
            # Test Berserk AI
            await self._administer_test_with_fallback(custody_service, "berserk")
            
        except Exception as e:
            logger.error(f"Error administering custody tests: {str(e)}")
    
    async def _trigger_olympic_events(self):
        """Trigger Olympic AI events"""
        try:
            from .olympic_ai_service import OlympicAIService
            olympic_service = OlympicAIService()
            await olympic_service.trigger_olympic_event()
        except Exception as e:
            logger.error(f"Error triggering Olympic events: {str(e)}")
    
    async def _run_collaborative_tests(self):
        """Run collaborative AI tests"""
        try:
            from .collaborative_ai_service import CollaborativeAIService
            collaborative_service = CollaborativeAIService()
            await collaborative_service.run_collaborative_test()
        except Exception as e:
            logger.error(f"Error running collaborative tests: {str(e)}")
    
    async def _administer_test_with_fallback(self, custody_service, ai_type: str) -> Dict[str, Any]:
        """Administer test with fallback handling"""
        try:
            async with self._test_lock:
                result = await custody_service.administer_test(ai_type)
                logger.info(f"✅ {ai_type.capitalize()} custody test completed: {result.get('status', 'unknown')}")
                return result
        except Exception as e:
            logger.error(f"Error administering {ai_type} test: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def trigger_learning_cycle(self):
        """Trigger an immediate learning cycle"""
        try:
            logger.info("🧠 Triggering immediate learning cycle...")
            await self.learning_service.learn_from_internet()
            logger.info("✅ Immediate learning cycle completed")
            return {"status": "success", "message": "Learning cycle triggered successfully"}
        except Exception as e:
            logger.error(f"Error triggering learning cycle: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # Scheduler interval properties
    @property
    def agent_scheduler_interval(self):
        return 30  # minutes
    
    @property
    def github_monitor_interval(self):
        return 15  # minutes
    
    @property
    def learning_cycle_interval(self):
        return 30  # minutes
    
    @property
    def custody_testing_interval(self):
        return 20  # minutes
    
    async def reschedule_all(self):
        """Reschedule all background tasks"""
        logger.info("🔄 Rescheduling all background tasks...")
        await self.stop_autonomous_cycle()
        await asyncio.sleep(1)
        await self.start_autonomous_cycle()

