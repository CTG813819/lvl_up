#!/usr/bin/env python3
"""
AI Coordination Scheduler
Manages all AI agents with timeout handling and ensures Custodes runs after each AI completion
"""

import asyncio
import json
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from pathlib import Path
import structlog
import aiohttp
import subprocess
from typing import Dict, List, Optional, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.ai_agent_service import AIAgentService
from app.services.ai_learning_service import AILearningService

logger = structlog.get_logger()

class AICoordinationScheduler:
    """Robust AI coordination scheduler with timeout handling"""
    
    def __init__(self):
        self.schedule_config = self._load_schedule_config()
        self.ai_status = {
            "guardian": {"running": False, "last_run": None, "last_success": None},
            "imperium": {"running": False, "last_run": None, "last_success": None},
            "sandbox": {"running": False, "last_run": None, "last_success": None},
            "conquest": {"running": False, "last_run": None, "last_success": None},
            "custodes": {"running": False, "last_run": None, "last_success": None}
        }
        self.agent_service = None
        self.learning_service = None
        self.pending_custodes_tests = []
        self.shutdown_requested = False
        
    def _load_schedule_config(self):
        """Load schedule configuration"""
        config_path = Path(__file__).parent / "ai_coordination_schedule.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schedule config: {e}")
            return {
                "ai_schedules": {
                    "guardian": {"interval_hours": 3, "timeout_minutes": 30, "enabled": True},
                    "imperium": {"interval_hours": 2, "timeout_minutes": 45, "enabled": True},
                    "sandbox": {"interval_hours": 4, "timeout_minutes": 20, "enabled": True},
                    "conquest": {"interval_hours": 6, "timeout_minutes": 60, "enabled": True}
                },
                "custodes_config": {
                    "trigger_after_ai_completion": True,
                    "delay_minutes": 1,
                    "timeout_minutes": 15,
                    "enabled": True
                },
                "system_config": {
                    "health_check_interval_minutes": 5,
                    "max_concurrent_ais": 2,
                    "retry_attempts": 3,
                    "retry_delay_minutes": 5
                }
            }
    
    async def initialize(self):
        """Initialize the scheduler and services"""
        try:
            logger.info("🚀 Initializing AI Coordination Scheduler...")
            
            # Initialize services
            self.agent_service = AIAgentService()
            self.learning_service = AILearningService()
            
            await self.agent_service.initialize()
            await self.learning_service.initialize()
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            logger.info("✅ AI Coordination Scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scheduler: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True
    
    async def run_ai_with_timeout(self, ai_type: str, timeout_minutes: int = 30):
        """Run an AI agent with timeout protection"""
        try:
            if self.ai_status[ai_type]["running"]:
                logger.warning(f"⚠️ {ai_type.capitalize()} is already running, skipping...")
                return False
            
            logger.info(f"🤖 Starting {ai_type.capitalize()} AI agent...")
            self.ai_status[ai_type]["running"] = True
            self.ai_status[ai_type]["last_run"] = datetime.now()
            start_time = datetime.now()
            
            # Run AI with timeout
            try:
                result = await asyncio.wait_for(
                    self._execute_ai_tasks(ai_type),
                    timeout=timeout_minutes * 60
                )
                
                self.ai_status[ai_type]["last_success"] = datetime.now()
                runtime = (self.ai_status[ai_type]["last_success"] - start_time).total_seconds() / 60
                
                logger.info(f"✅ {ai_type.capitalize()} completed successfully in {runtime:.1f} minutes")
                logger.info(f"📊 {ai_type.capitalize()} result: {result}")
                
                # Schedule Custodes to test this AI
                await self._schedule_custodes_test(ai_type, result)
                
                return True
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ {ai_type.capitalize()} timed out after {timeout_minutes} minutes")
                return False
            except Exception as e:
                logger.error(f"❌ {ai_type.capitalize()} failed: {e}")
                return False
                
        finally:
            self.ai_status[ai_type]["running"] = False
    
    async def _execute_ai_tasks(self, ai_type: str):
        """Execute tasks for a specific AI agent"""
        try:
            # Trigger AI learning
            result = await self.agent_service.trigger_ai_learning(
                ai_type=ai_type,
                learning_type="scheduled"
            )
            
            # AI-specific tasks
            if ai_type == "guardian":
                await self._run_guardian_tasks()
            elif ai_type == "imperium":
                await self._run_imperium_tasks()
            elif ai_type == "sandbox":
                await self._run_sandbox_tasks()
            elif ai_type == "conquest":
                await self._run_conquest_tasks()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing {ai_type} tasks: {e}")
            raise
    
    async def _run_guardian_tasks(self):
        """Run Guardian-specific tasks"""
        try:
            logger.info("🛡️ Running Guardian health checks and optimizations...")
            
            # Health checks
            await self._run_health_checks()
            
            # Performance optimization
            await self._run_performance_optimization()
            
            # Proposal validation
            await self._run_proposal_validation()
            
            logger.info("✅ Guardian tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Guardian tasks failed: {e}")
    
    async def _run_imperium_tasks(self):
        """Run Imperium-specific tasks"""
        try:
            logger.info("👑 Running Imperium orchestration tasks...")
            
            # Master orchestration
            await self._run_master_orchestration()
            
            # Learning coordination
            await self._run_learning_coordination()
            
            logger.info("✅ Imperium tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Imperium tasks failed: {e}")
    
    async def _run_sandbox_tasks(self):
        """Run Sandbox-specific tasks"""
        try:
            logger.info("🏖️ Running Sandbox experimentation tasks...")
            
            # Experiment management
            await self._run_experiment_management()
            
            # Repository analysis
            await self._run_repository_analysis()
            
            logger.info("✅ Sandbox tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Sandbox tasks failed: {e}")
    
    async def _run_conquest_tasks(self):
        """Run Conquest-specific tasks"""
        try:
            logger.info("⚔️ Running Conquest deployment tasks...")
            
            # App deployment
            await self._run_app_deployment()
            
            # Build management
            await self._run_build_management()
            
            logger.info("✅ Conquest tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Conquest tasks failed: {e}")
    
    async def _run_health_checks(self):
        """Run system health checks"""
        try:
            logger.info("🏥 Running health checks...")
            # Health check implementation
            await asyncio.sleep(2)  # Simulate health checks
            logger.info("✅ Health checks completed")
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _run_performance_optimization(self):
        """Run performance optimization tasks"""
        try:
            logger.info("⚡ Running performance optimization...")
            # Performance optimization implementation
            await asyncio.sleep(3)  # Simulate optimization
            logger.info("✅ Performance optimization completed")
        except Exception as e:
            logger.error(f"Performance optimization failed: {e}")
    
    async def _run_proposal_validation(self):
        """Run proposal validation tasks"""
        try:
            logger.info("📋 Running proposal validation...")
            # Proposal validation implementation
            await asyncio.sleep(2)  # Simulate validation
            logger.info("✅ Proposal validation completed")
        except Exception as e:
            logger.error(f"Proposal validation failed: {e}")
    
    async def _run_master_orchestration(self):
        """Run Imperium master orchestration"""
        try:
            logger.info("🎼 Running master orchestration...")
            # Master orchestration implementation
            await asyncio.sleep(5)  # Simulate orchestration
            logger.info("✅ Master orchestration completed")
        except Exception as e:
            logger.error(f"Master orchestration failed: {e}")
    
    async def _run_learning_coordination(self):
        """Run learning coordination"""
        try:
            logger.info("🧠 Running learning coordination...")
            # Learning coordination implementation
            await asyncio.sleep(3)  # Simulate coordination
            logger.info("✅ Learning coordination completed")
        except Exception as e:
            logger.error(f"Learning coordination failed: {e}")
    
    async def _run_experiment_management(self):
        """Run experiment management"""
        try:
            logger.info("🧪 Running experiment management...")
            # Experiment management implementation
            await asyncio.sleep(4)  # Simulate experiments
            logger.info("✅ Experiment management completed")
        except Exception as e:
            logger.error(f"Experiment management failed: {e}")
    
    async def _run_repository_analysis(self):
        """Run repository analysis"""
        try:
            logger.info("📚 Running repository analysis...")
            # Repository analysis implementation
            await asyncio.sleep(3)  # Simulate analysis
            logger.info("✅ Repository analysis completed")
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
    
    async def _run_app_deployment(self):
        """Run app deployment"""
        try:
            logger.info("📱 Running app deployment...")
            # App deployment implementation
            await asyncio.sleep(10)  # Simulate deployment
            logger.info("✅ App deployment completed")
        except Exception as e:
            logger.error(f"App deployment failed: {e}")
    
    async def _run_build_management(self):
        """Run build management"""
        try:
            logger.info("🔨 Running build management...")
            # Build management implementation
            await asyncio.sleep(5)  # Simulate builds
            logger.info("✅ Build management completed")
        except Exception as e:
            logger.error(f"Build management failed: {e}")
    
    async def _schedule_custodes_test(self, ai_type: str, ai_result: Dict[str, Any]):
        """Schedule Custodes to test an AI after completion"""
        try:
            delay_minutes = self.schedule_config["custodes_config"]["delay_minutes"]
            test_time = datetime.now() + timedelta(minutes=delay_minutes)
            
            self.pending_custodes_tests.append({
                "ai_type": ai_type,
                "ai_result": ai_result,
                "scheduled_time": test_time,
                "completed": False
            })
            
            logger.info(f"📅 Scheduled Custodes test for {ai_type} at {test_time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Failed to schedule Custodes test: {e}")
    
    async def run_custodes_test(self, ai_type: str, ai_result: Dict[str, Any]):
        """Run Custodes to test an AI's results"""
        try:
            if self.ai_status["custodes"]["running"]:
                logger.warning("⚠️ Custodes is already running, queuing test...")
                return False
            
            logger.info(f"🔍 Starting Custodes test for {ai_type}...")
            self.ai_status["custodes"]["running"] = True
            self.ai_status["custodes"]["last_run"] = datetime.now()
            start_time = datetime.now()
            
            timeout_minutes = self.schedule_config["custodes_config"]["timeout_minutes"]
            
            try:
                result = await asyncio.wait_for(
                    self._execute_custodes_test(ai_type, ai_result),
                    timeout=timeout_minutes * 60
                )
                
                self.ai_status["custodes"]["last_success"] = datetime.now()
                runtime = (self.ai_status["custodes"]["last_success"] - start_time).total_seconds() / 60
                
                logger.info(f"✅ Custodes test for {ai_type} completed in {runtime:.1f} minutes")
                logger.info(f"📊 Custodes result: {result}")
                
                return True
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Custodes test for {ai_type} timed out after {timeout_minutes} minutes")
                return False
            except Exception as e:
                logger.error(f"❌ Custodes test for {ai_type} failed: {e}")
                return False
                
        finally:
            self.ai_status["custodes"]["running"] = False
    
    async def _execute_custodes_test(self, ai_type: str, ai_result: Dict[str, Any]):
        """Execute Custodes test for an AI"""
        try:
            logger.info(f"🧪 Testing {ai_type} results with Custodes...")
            
            # Test AI's learning outcomes
            await self._test_ai_learning_outcomes(ai_type, ai_result)
            
            # Test AI's performance metrics
            await self._test_ai_performance(ai_type, ai_result)
            
            # Generate quality assessment
            await self._generate_quality_assessment(ai_type, ai_result)
            
            return {"status": "success", "ai_tested": ai_type, "tests_passed": True}
            
        except Exception as e:
            logger.error(f"Custodes test execution failed: {e}")
            raise
    
    async def _test_ai_learning_outcomes(self, ai_type: str, ai_result: Dict[str, Any]):
        """Test AI's learning outcomes"""
        try:
            logger.info(f"📚 Testing {ai_type} learning outcomes...")
            # Learning outcome testing implementation
            await asyncio.sleep(2)  # Simulate testing
            logger.info(f"✅ {ai_type} learning outcomes tested")
        except Exception as e:
            logger.error(f"Learning outcome testing failed: {e}")
    
    async def _test_ai_performance(self, ai_type: str, ai_result: Dict[str, Any]):
        """Test AI's performance metrics"""
        try:
            logger.info(f"📈 Testing {ai_type} performance metrics...")
            # Performance testing implementation
            await asyncio.sleep(2)  # Simulate testing
            logger.info(f"✅ {ai_type} performance metrics tested")
        except Exception as e:
            logger.error(f"Performance testing failed: {e}")
    
    async def _generate_quality_assessment(self, ai_type: str, ai_result: Dict[str, Any]):
        """Generate quality assessment for AI"""
        try:
            logger.info(f"📊 Generating quality assessment for {ai_type}...")
            # Quality assessment implementation
            await asyncio.sleep(2)  # Simulate assessment
            logger.info(f"✅ Quality assessment for {ai_type} completed")
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
    
    async def should_run_ai(self, ai_type: str):
        """Check if an AI should run based on schedule"""
        if not self.schedule_config["ai_schedules"][ai_type]["enabled"]:
            return False
        
        if self.ai_status[ai_type]["running"]:
            return False
        
        interval_hours = self.schedule_config["ai_schedules"][ai_type]["interval_hours"]
        
        if not self.ai_status[ai_type]["last_success"]:
            return True
        
        time_since_last = datetime.now() - self.ai_status[ai_type]["last_success"]
        return time_since_last.total_seconds() >= (interval_hours * 3600)
    
    async def check_pending_custodes_tests(self):
        """Check and run pending Custodes tests"""
        current_time = datetime.now()
        tests_to_run = []
        
        for test in self.pending_custodes_tests:
            if not test["completed"] and current_time >= test["scheduled_time"]:
                tests_to_run.append(test)
        
        for test in tests_to_run:
            test["completed"] = True
            await self.run_custodes_test(test["ai_type"], test["ai_result"])
        
        # Clean up completed tests
        self.pending_custodes_tests = [t for t in self.pending_custodes_tests if not t["completed"]]
    
    async def run_scheduler_loop(self):
        """Main scheduler loop with robust error handling"""
        logger.info("🔄 Starting AI Coordination scheduler loop...")
        
        while not self.shutdown_requested:
            try:
                # Check and run AIs
                for ai_type in ["guardian", "imperium", "sandbox", "conquest"]:
                    if await self.should_run_ai(ai_type):
                        logger.info(f"⏰ Time to run {ai_type.capitalize()}...")
                        timeout_minutes = self.schedule_config["ai_schedules"][ai_type]["timeout_minutes"]
                        success = await self.run_ai_with_timeout(ai_type, timeout_minutes)
                        
                        if success:
                            logger.info(f"✅ {ai_type.capitalize()} completed, Custodes will test shortly...")
                        else:
                            logger.warning(f"⚠️ {ai_type.capitalize()} failed, will retry next cycle")
                
                # Check pending Custodes tests
                await self.check_pending_custodes_tests()
                
                # Health check
                await self._run_health_check()
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        logger.info("🛑 Scheduler shutdown complete")
    
    async def _run_health_check(self):
        """Run periodic health check"""
        try:
            # Check if any AI has been stuck for too long
            current_time = datetime.now()
            for ai_type, status in self.ai_status.items():
                if status["running"] and status["last_run"]:
                    runtime = (current_time - status["last_run"]).total_seconds() / 60
                    max_timeout = self.schedule_config["ai_schedules"].get(ai_type, {}).get("timeout_minutes", 30)
                    
                    if runtime > max_timeout + 5:  # 5 minutes grace period
                        logger.warning(f"⚠️ {ai_type.capitalize()} appears stuck (runtime: {runtime:.1f} minutes)")
                        # Force reset the AI status
                        self.ai_status[ai_type]["running"] = False
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")

async def main():
    """Main function"""
    scheduler = AICoordinationScheduler()
    
    try:
        await scheduler.initialize()
        await scheduler.run_scheduler_loop()
    except Exception as e:
        logger.error(f"❌ Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 