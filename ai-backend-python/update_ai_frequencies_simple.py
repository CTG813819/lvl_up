#!/usr/bin/env python3
"""
Update AI Agent Frequencies - Optimized Timing with Staggered Execution
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_frequency_update.log')
    ]
)
logger = logging.getLogger(__name__)

class AIFrequencyUpdater:
    """Update AI agent frequencies with optimized staggered timing"""
    
    def __init__(self):
        # New optimized frequencies with staggered execution
        self.updated_config = {
            "imperium": {
                "testing_threshold": 0.92,
                "test_interval": 90,  # 1.5 hours (90 minutes)
                "comprehensive_test_interval": 180,  # 3 hours
                "start_delay": 0  # Start immediately
            },
            "sandbox": {
                "experimentation_interval": 120,  # 2 hours (120 minutes)
                "quality_threshold": 0.85,
                "new_code_only": True,
                "start_delay": 30  # Start 30 minutes after Imperium
            },
            "guardian": {
                "self_heal_interval": 300,  # 5 hours (300 minutes)
                "sudo_required": True,
                "frontend_backend_healing": True,
                "start_delay": 60  # Start 1 hour after Imperium
            },
            "custodes": {
                "test_interval": 90,  # 1.5 hours (90 minutes)
                "comprehensive_test_interval": 180,  # 3 hours
                "ai_sources_learning": True,
                "start_delay": 90  # Start 1.5 hours after Imperium
            }
        }
        
    async def create_updated_router(self):
        """Create updated AI agents router with new frequencies"""
        logger.info("Creating Updated AI Agents Router with New Frequencies...")
        
        updated_router = '''from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
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
'''
        
        # Write the updated router
        router_path = Path("app/routers/ai_agents_updated.py")
        router_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(router_path, 'w') as f:
            f.write(updated_router)
        
        logger.info(f"Created updated AI agents router: {router_path}")
        return router_path
    
    async def update_main_app(self):
        """Update main app to use the new AI agents router"""
        logger.info("Updating main app to use new AI agents router...")
        
        main_app_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.core.database import engine
from app.models.sql_models import Base
from app.routers.ai_agents_updated import router as ai_agents_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LVL UP AI Backend - Updated Frequencies",
    description="AI Backend with optimized agent frequencies and staggered execution",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_agents_router)

@app.get("/")
async def root():
    return {
        "message": "LVL UP AI Backend - Updated Frequencies",
        "version": "2.0.0",
        "status": "running",
        "ai_agents": {
            "imperium": "Every 1.5 hours",
            "sandbox": "Every 2 hours (starts 30min after Imperium)",
            "guardian": "Every 5 hours (starts 1hr after Imperium)",
            "custodes": "Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-15T12:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
        
        # Write the updated main app
        main_path = Path("main_updated.py")
        with open(main_path, 'w') as f:
            f.write(main_app_content)
        
        logger.info(f"Created updated main app: {main_path}")
        return main_path
    
    async def create_updated_startup_script(self):
        """Create updated startup script"""
        logger.info("Creating updated startup script...")
        
        startup_script = '''#!/bin/bash
# Updated AI Backend Startup Script - New Frequencies
echo "Starting LVL UP AI Backend with Updated Frequencies..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"
export AI_BACKEND_ENV="production"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start the updated backend
echo "Starting updated AI backend..."
python main_updated.py

echo "Updated AI backend started successfully!"
echo "New Schedule:"
echo "  * Imperium: Every 1.5 hours (starts immediately)"
echo "  * Sandbox: Every 2 hours (starts 30min after Imperium)"
echo "  * Guardian: Every 5 hours (starts 1hr after Imperium)"
echo "  * Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
'''
        
        # Write the startup script
        startup_path = Path("start_updated_backend.sh")
        with open(startup_path, 'w') as f:
            f.write(startup_script)
        
        # Make executable
        os.chmod(startup_path, 0o755)
        
        logger.info(f"Created updated startup script: {startup_path}")
        return startup_path
    
    async def create_deployment_script(self):
        """Create deployment script for the updated frequencies"""
        logger.info("Creating deployment script...")
        
        deployment_script = '''#!/bin/bash
# Deploy Updated AI Backend with New Frequencies
echo "Deploying Updated AI Backend with New Frequencies..."

# Stop existing services
echo "Stopping existing services..."
sudo systemctl stop ai-backend.service 2>/dev/null || true
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Wait for services to stop
sleep 5

# Kill any remaining processes
echo "Cleaning up processes..."
pkill -f "main.py" 2>/dev/null || true
pkill -f "main_updated.py" 2>/dev/null || true
pkill -f "imperium_runner.py" 2>/dev/null || true
pkill -f "sandbox_runner.py" 2>/dev/null || true
pkill -f "custodes_runner.py" 2>/dev/null || true
pkill -f "guardian_runner.py" 2>/dev/null || true

# Wait for cleanup
sleep 3

# Make startup script executable
chmod +x start_updated_backend.sh

# Start the updated backend
echo "Starting updated backend..."
nohup ./start_updated_backend.sh > backend_updated.log 2>&1 &

# Wait for startup
sleep 10

# Check if backend is running
if pgrep -f "main_updated.py" > /dev/null; then
    echo "Updated backend started successfully!"
    echo "Backend process: $(pgrep -f 'main_updated.py')"
    echo "New AI Agent Schedule:"
    echo "  * Imperium: Every 1.5 hours (starts immediately)"
    echo "  * Sandbox: Every 2 hours (starts 30min after Imperium)"
    echo "  * Guardian: Every 5 hours (starts 1hr after Imperium)"
    echo "  * Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
    echo ""
    echo "Check status: curl http://localhost:8000/ai-agents/status"
    echo "Check health: curl http://localhost:8000/health"
else
    echo "Failed to start updated backend"
    echo "Check logs: tail -f backend_updated.log"
fi
'''
        
        # Write the deployment script
        deployment_path = Path("deploy_updated_frequencies.sh")
        with open(deployment_path, 'w') as f:
            f.write(deployment_script)
        
        # Make executable
        os.chmod(deployment_path, 0o755)
        
        logger.info(f"Created deployment script: {deployment_path}")
        return deployment_path
    
    async def run_update(self):
        """Run the complete frequency update"""
        logger.info("Starting AI Agent Frequency Update...")
        
        try:
            # Create updated router
            await self.create_updated_router()
            
            # Update main app
            await self.update_main_app()
            
            # Create startup script
            await self.create_updated_startup_script()
            
            # Create deployment script
            await self.create_deployment_script()
            
            logger.info("AI Agent Frequency Update completed successfully!")
            logger.info("Created files:")
            logger.info("* app/routers/ai_agents_updated.py")
            logger.info("* main_updated.py")
            logger.info("* start_updated_backend.sh")
            logger.info("* deploy_updated_frequencies.sh")
            logger.info("")
            logger.info("To deploy:")
            logger.info("1. Run: chmod +x deploy_updated_frequencies.sh")
            logger.info("2. Run: ./deploy_updated_frequencies.sh")
            logger.info("")
            logger.info("New Schedule:")
            logger.info("* Imperium: Every 1.5 hours (starts immediately)")
            logger.info("* Sandbox: Every 2 hours (starts 30min after Imperium)")
            logger.info("* Guardian: Every 5 hours (starts 1hr after Imperium)")
            logger.info("* Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)")
            
        except Exception as e:
            logger.error(f"Error during frequency update: {e}")
            raise

async def main():
    """Main function"""
    updater = AIFrequencyUpdater()
    await updater.run_update()

if __name__ == "__main__":
    asyncio.run(main()) 