#!/usr/bin/env python3
"""
Simple AI Coordination Scheduler
Manages all AI agents with timeout handling and ensures Custodes runs after each AI completion
"""

import asyncio
import json
import os
import sys
import time
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/ai_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleAICoordinationScheduler:
    """Simple AI coordination scheduler with timeout handling"""
    
    def __init__(self):
        self.schedule_config = self._load_schedule_config()
        self.ai_status = {
            "guardian": {"running": False, "last_run": None, "last_success": None},
            "imperium": {"running": False, "last_run": None, "last_success": None},
            "sandbox": {"running": False, "last_run": None, "last_success": None},
            "conquest": {"running": False, "last_run": None, "last_success": None},
            "custodes": {"running": False, "last_run": None, "last_success": None}
        }
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
                }
            }
    
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
            logger.info(f"🔧 Running {ai_type.capitalize()} tasks...")
            
            # Simulate AI-specific tasks
            if ai_type == "guardian":
                await self._run_guardian_tasks()
            elif ai_type == "imperium":
                await self._run_imperium_tasks()
            elif ai_type == "sandbox":
                await self._run_sandbox_tasks()
            elif ai_type == "conquest":
                await self._run_conquest_tasks()
            
            return {"status": "success", "ai_type": ai_type}
            
        except Exception as e:
            logger.error(f"Error executing {ai_type} tasks: {e}")
            raise
    
    async def _run_guardian_tasks(self):
        """Run Guardian-specific tasks"""
        try:
            logger.info("🛡️ Running Guardian health checks and optimizations...")
            
            # Health checks
            await asyncio.sleep(5)  # Simulate health checks
            
            # Performance optimization
            await asyncio.sleep(8)  # Simulate optimization
            
            # Proposal validation
            await asyncio.sleep(5)  # Simulate validation
            
            logger.info("✅ Guardian tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Guardian tasks failed: {e}")
    
    async def _run_imperium_tasks(self):
        """Run Imperium-specific tasks"""
        try:
            logger.info("👑 Running Imperium orchestration tasks...")
            
            # Master orchestration
            await asyncio.sleep(10)  # Simulate orchestration
            
            # Learning coordination
            await asyncio.sleep(8)  # Simulate coordination
            
            logger.info("✅ Imperium tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Imperium tasks failed: {e}")
    
    async def _run_sandbox_tasks(self):
        """Run Sandbox-specific tasks"""
        try:
            logger.info("🏖️ Running Sandbox experimentation tasks...")
            
            # Experiment management
            await asyncio.sleep(6)  # Simulate experiments
            
            # Repository analysis
            await asyncio.sleep(4)  # Simulate analysis
            
            logger.info("✅ Sandbox tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Sandbox tasks failed: {e}")
    
    async def _run_conquest_tasks(self):
        """Run Conquest-specific tasks"""
        try:
            logger.info("⚔️ Running Conquest deployment tasks...")
            
            # App deployment
            await asyncio.sleep(15)  # Simulate deployment
            
            # Build management
            await asyncio.sleep(8)  # Simulate builds
            
            logger.info("✅ Conquest tasks completed")
            
        except Exception as e:
            logger.error(f"❌ Conquest tasks failed: {e}")
    
    async def _schedule_custodes_test(self, ai_type: str, ai_result: dict):
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
    
    async def run_custodes_test(self, ai_type: str, ai_result: dict):
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
    
    async def _execute_custodes_test(self, ai_type: str, ai_result: dict):
        """Execute Custodes test for an AI"""
        try:
            logger.info(f"🧪 Testing {ai_type} results with Custodes...")
            
            # Test AI's learning outcomes
            await asyncio.sleep(3)  # Simulate testing
            
            # Test AI's performance metrics
            await asyncio.sleep(3)  # Simulate testing
            
            # Generate quality assessment
            await asyncio.sleep(2)  # Simulate assessment
            
            return {"status": "success", "ai_tested": ai_type, "tests_passed": True}
            
        except Exception as e:
            logger.error(f"Custodes test execution failed: {e}")
            raise
    
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
    
    async def save_status_to_file(self):
        """Save current status to file"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "ai_status": self.ai_status,
                "pending_tests": len(self.pending_custodes_tests),
                "scheduler_running": not self.shutdown_requested
            }
            
            status_file = Path(__file__).parent / "ai_scheduler_status.json"
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    async def run_scheduler_loop(self):
        """Main scheduler loop with robust error handling"""
        logger.info("🔄 Starting Simple AI Coordination scheduler loop...")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
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
                
                # Save status to file
                await self.save_status_to_file()
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        logger.info("🛑 Scheduler shutdown complete")

async def main():
    """Main function"""
    scheduler = SimpleAICoordinationScheduler()
    
    try:
        await scheduler.run_scheduler_loop()
    except Exception as e:
        logger.error(f"❌ Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 