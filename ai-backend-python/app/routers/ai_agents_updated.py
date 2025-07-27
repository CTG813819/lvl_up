from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional
import asyncio
import json
import time
from datetime import datetime
import psutil

from app.core.database import get_db
from app.models.sql_models import Proposal, Learning
from app.services.ai_agent_service import AIAgentService

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

# Updated background task manager with new frequencies
class UpdatedAIAgentsManager:
    def __init__(self):
        self.imperium_task = None
        self.sandbox_task = None
        self.custodes_task = None
        self.guardian_task = None
        self.is_running = False
        self.start_time = time.time()
        
        # Initialize last run times with staggered delays
        self.last_imperium_run = 0
        self.last_sandbox_run = 0
        self.last_custodes_run = 0
        self.last_guardian_run = 0
        
        # Resource monitoring
        self.max_cpu_percent = 80
        self.max_memory_percent = 85
        
        # Performance tracking
        self.agent_stats = {
            "imperium": {"runs": 0, "last_duration": 0, "errors": 0},
            "sandbox": {"runs": 0, "last_duration": 0, "errors": 0},
            "custodes": {"runs": 0, "last_duration": 0, "errors": 0},
            "guardian": {"runs": 0, "last_duration": 0, "errors": 0}
        }
        
    def check_system_resources(self):
        """Check if system has enough resources for AI tasks"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.max_cpu_percent:
            print(f"High CPU usage: {cpu_percent}% - skipping AI tasks")
            return False
            
        if memory_percent > self.max_memory_percent:
            print(f"High memory usage: {memory_percent}% - skipping AI tasks")
            return False
            
        return True
        
    def should_run_agent(self, agent_name: str, interval_seconds: int, start_delay: int = 0):
        """Check if agent should run based on timing and system resources"""
        current_time = time.time()
        last_run = getattr(self, f"last_{agent_name}_run", 0)
        
        # Check if enough time has passed since last run
        time_since_last = current_time - last_run
        
        # Check if initial delay has passed
        time_since_start = current_time - self.start_time
        if time_since_start < start_delay:
            return False
            
        # Check if interval has passed
        if time_since_last < interval_seconds:
            return False
            
        # Check system resources
        return self.check_system_resources()
        
    async def start_imperium_cycle(self):
        """Imperium AI testing cycle - every 1.5 hours"""
        print("Starting Imperium cycle (every 1.5 hours)")
        while self.is_running:
            try:
                if self.should_run_agent("imperium", 5400, 0):  # 90 minutes = 5400 seconds
                    start_time = time.time()
                    print("Running Imperium AI testing...")
                    
                    service = AIAgentService()
                    await service.run_imperium_testing(threshold=0.92)
                    
                    duration = time.time() - start_time
                    self.last_imperium_run = time.time()
                    self.agent_stats["imperium"]["runs"] += 1
                    self.agent_stats["imperium"]["last_duration"] = duration
                    
                    print(f"Imperium testing completed in {duration:.2f}s")
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Imperium error: {e}")
                self.agent_stats["imperium"]["errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_sandbox_cycle(self):
        """Sandbox AI experimentation cycle - every 2 hours"""
        print("Starting Sandbox cycle (every 2 hours, starts 30min after Imperium)")
        while self.is_running:
            try:
                if self.should_run_agent("sandbox", 7200, 1800):  # 2 hours = 7200 seconds, 30min delay
                    start_time = time.time()
                    print("Running Sandbox experimentation...")
                    
                    service = AIAgentService()
                    await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
                    
                    duration = time.time() - start_time
                    self.last_sandbox_run = time.time()
                    self.agent_stats["sandbox"]["runs"] += 1
                    self.agent_stats["sandbox"]["last_duration"] = duration
                    
                    print(f"Sandbox experimentation completed in {duration:.2f}s")
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Sandbox error: {e}")
                self.agent_stats["sandbox"]["errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_guardian_cycle(self):
        """Guardian AI health monitoring cycle - every 5 hours"""
        print("Starting Guardian cycle (every 5 hours, starts 1hr after Imperium)")
        while self.is_running:
            try:
                if self.should_run_agent("guardian", 18000, 3600):  # 5 hours = 18000 seconds, 1hr delay
                    start_time = time.time()
                    print("Running Guardian health check...")
                    
                    service = AIAgentService()
                    health_status = await service.monitor_system_health()
                    
                    if health_status.get('issues_detected', False):
                        # Create healing proposal for user approval
                        issues = health_status.get('issues', [])
                        proposed_actions = health_status.get('proposed_actions', [])
                        
                        proposal_data = {
                            "title": f"Guardian Self-Healing Proposal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            "description": "Guardian AI has detected system issues requiring sudo privileges for resolution",
                            "ai_type": "guardian",
                            "proposal_type": "system_healing",
                            "content": {
                                "issues_detected": issues,
                                "proposed_actions": proposed_actions,
                                "sudo_required": True,
                                "risk_assessment": health_status.get('risk_assessment', 'Low'),
                                "estimated_downtime": health_status.get('estimated_downtime', 'None'),
                                "backup_plan": health_status.get('backup_plan', 'System state will be preserved')
                            },
                            "status": "pending_user_approval",
                            "priority": "high" if health_status.get('risk_assessment') == 'High' else "medium"
                        }
                        
                        # Save proposal to database
                        async with get_db() as db:
                            proposal = Proposal(
                                title=proposal_data["title"],
                                description=proposal_data["description"],
                                ai_type=proposal_data["ai_type"],
                                proposal_type=proposal_data["proposal_type"],
                                content=json.dumps(proposal_data["content"]),
                                status=proposal_data["status"],
                                priority=proposal_data["priority"]
                            )
                            db.add(proposal)
                            await db.commit()
                            await db.refresh(proposal)
                        
                        print(f"Guardian created healing proposal #{proposal.id}")
                    else:
                        print("Guardian health check passed - no issues detected")
                    
                    duration = time.time() - start_time
                    self.last_guardian_run = time.time()
                    self.agent_stats["guardian"]["runs"] += 1
                    self.agent_stats["guardian"]["last_duration"] = duration
                    
                    print(f"Guardian health check completed in {duration:.2f}s")
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Guardian error: {e}")
                self.agent_stats["guardian"]["errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_custodes_cycle(self):
        """Custodes AI testing cycle - every 1.5 hours, tests other agents"""
        print("Starting Custodes cycle (every 1.5 hours, starts 1.5hr after Imperium)")
        counter = 0
        while self.is_running:
            try:
                if self.should_run_agent("custodes", 5400, 5400):  # 1.5 hours = 5400 seconds, 1.5hr delay
                    start_time = time.time()
                    service = AIAgentService()
                    
                    if counter % 2 == 0:
                        print("Running comprehensive Custodes testing...")
                        await service.run_comprehensive_custodes_testing()
                    else:
                        print("Running regular Custodes testing...")
                        await service.run_custodes_testing()
                    
                    # Test other agents after Custodes runs
                    print("Custodes testing other agents...")
                    await self.test_other_agents()
                    
                    duration = time.time() - start_time
                    self.last_custodes_run = time.time()
                    self.agent_stats["custodes"]["runs"] += 1
                    self.agent_stats["custodes"]["last_duration"] = duration
                    
                    counter += 1
                    print(f"Custodes testing completed in {duration:.2f}s")
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Custodes error: {e}")
                self.agent_stats["custodes"]["errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def test_other_agents(self):
        """Custodes tests other agents after its own testing"""
        try:
            service = AIAgentService()
            
            # Test Imperium
            print("Custodes testing Imperium...")
            await service.run_imperium_testing(threshold=0.92)
            
            # Test Sandbox
            print("Custodes testing Sandbox...")
            await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
            
            # Test Guardian
            print("Custodes testing Guardian...")
            await service.monitor_system_health()
            
            print("Custodes completed testing all other agents")
        except Exception as e:
            print(f"Custodes agent testing error: {e}")
    
    async def start_all_cycles(self):
        """Start all AI agent cycles"""
        self.is_running = True
        print("Starting all AI agent cycles with updated frequencies...")
        print("Schedule:")
        print("  * Imperium: Every 1.5 hours (starts immediately)")
        print("  * Sandbox: Every 2 hours (starts 30min after Imperium)")
        print("  * Guardian: Every 5 hours (starts 1hr after Imperium)")
        print("  * Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)")
        
        self.imperium_task = asyncio.create_task(self.start_imperium_cycle())
        self.sandbox_task = asyncio.create_task(self.start_sandbox_cycle())
        self.custodes_task = asyncio.create_task(self.start_custodes_cycle())
        self.guardian_task = asyncio.create_task(self.start_guardian_cycle())
        
        print("All AI agent cycles started successfully")
    
    async def stop_all_cycles(self):
        """Stop all AI agent cycles"""
        self.is_running = False
        print("Stopping all AI agent cycles...")
        
        if self.imperium_task:
            self.imperium_task.cancel()
        if self.sandbox_task:
            self.sandbox_task.cancel()
        if self.custodes_task:
            self.custodes_task.cancel()
        if self.guardian_task:
            self.guardian_task.cancel()
        
        print("All AI agent cycles stopped")
    
    def get_agent_stats(self):
        """Get current agent statistics"""
        return self.agent_stats

# Global manager instance
ai_agents_manager = UpdatedAIAgentsManager()

@router.on_event("startup")
async def startup_event():
    """Start AI agents on startup"""
    await ai_agents_manager.start_all_cycles()

@router.on_event("shutdown")
async def shutdown_event():
    """Stop AI agents on shutdown"""
    await ai_agents_manager.stop_all_cycles()

@router.get("/status")
async def get_ai_agents_status():
    """Get AI agents status and statistics"""
    return {
        "status": "running" if ai_agents_manager.is_running else "stopped",
        "start_time": datetime.fromtimestamp(ai_agents_manager.start_time).isoformat(),
        "agent_stats": ai_agents_manager.get_agent_stats(),
        "last_runs": {
            "imperium": datetime.fromtimestamp(ai_agents_manager.last_imperium_run).isoformat() if ai_agents_manager.last_imperium_run > 0 else "Never",
            "sandbox": datetime.fromtimestamp(ai_agents_manager.last_sandbox_run).isoformat() if ai_agents_manager.last_sandbox_run > 0 else "Never",
            "custodes": datetime.fromtimestamp(ai_agents_manager.last_custodes_run).isoformat() if ai_agents_manager.last_custodes_run > 0 else "Never",
            "guardian": datetime.fromtimestamp(ai_agents_manager.last_guardian_run).isoformat() if ai_agents_manager.last_guardian_run > 0 else "Never"
        },
        "schedule": {
            "imperium": "Every 1.5 hours",
            "sandbox": "Every 2 hours (starts 30min after Imperium)",
            "guardian": "Every 5 hours (starts 1hr after Imperium)",
            "custodes": "Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
        }
    }

@router.post("/manual-trigger/{agent_name}")
async def manual_trigger_agent(agent_name: str):
    """Manually trigger an AI agent"""
    if agent_name not in ["imperium", "sandbox", "custodes", "guardian"]:
        raise HTTPException(status_code=400, detail="Invalid agent name")
    
    print(f"Manually triggering {agent_name}...")
    service = AIAgentService()
    
    try:
        if agent_name == "imperium":
            await service.run_imperium_testing(threshold=0.92)
        elif agent_name == "sandbox":
            await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
        elif agent_name == "custodes":
            await service.run_custodes_testing()
        elif agent_name == "guardian":
            await service.monitor_system_health()
        
        return {"message": f"{agent_name} triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering {agent_name}: {str(e)}")

@router.post("/restart")
async def restart_ai_agents():
    """Restart all AI agents"""
    await ai_agents_manager.stop_all_cycles()
    await asyncio.sleep(2)
    await ai_agents_manager.start_all_cycles()
    return {"message": "AI agents restarted successfully"}

@router.get("/health")
async def ai_agents_health():
    """Get AI agents health status"""
    return {
        "status": "healthy" if ai_agents_manager.is_running else "unhealthy",
        "agents_running": ai_agents_manager.is_running,
        "system_resources": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent
        }
    }
