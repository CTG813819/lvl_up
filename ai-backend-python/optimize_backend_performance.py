#!/usr/bin/env python3
"""
Optimize Backend Performance - Reduce AI agent load and improve responsiveness
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
        logging.FileHandler('backend_optimization.log')
    ]
)
logger = logging.getLogger(__name__)

class BackendPerformanceOptimizer:
    """Optimize backend performance by reducing AI agent load"""
    
    def __init__(self):
        # Reduced frequencies to improve performance
        self.optimized_config = {
            "imperium": {
                "testing_threshold": 0.92,
                "test_interval": 180,  # 3 hours instead of 45 minutes
                "comprehensive_test_interval": 360  # 6 hours
            },
            "sandbox": {
                "experimentation_interval": 240,  # 4 hours instead of 45 minutes
                "quality_threshold": 0.85,
                "new_code_only": True
            },
            "custodes": {
                "test_interval": 180,  # 3 hours instead of 45 minutes
                "comprehensive_test_interval": 360,  # 6 hours
                "ai_sources_learning": True
            },
            "guardian": {
                "self_heal_interval": 480,  # 8 hours instead of 60 minutes
                "sudo_required": True,
                "frontend_backend_healing": True
            }
        }
        
    async def create_optimized_router(self):
        """Create optimized AI agents router with reduced load"""
        logger.info("🔧 Creating Optimized AI Agents Router...")
        
        optimized_router = '''from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
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

# Optimized background task manager for AI agents
class OptimizedAIAgentsManager:
    def __init__(self):
        self.imperium_task = None
        self.sandbox_task = None
        self.custodes_task = None
        self.guardian_task = None
        self.is_running = False
        self.last_imperium_run = 0
        self.last_sandbox_run = 0
        self.last_custodes_run = 0
        self.last_guardian_run = 0
        
        # Resource monitoring
        self.max_cpu_percent = 80
        self.max_memory_percent = 85
        
    def check_system_resources(self):
        """Check if system has enough resources for AI tasks"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > self.max_cpu_percent:
            print(f"⚠️ High CPU usage: {cpu_percent}% - skipping AI tasks")
            return False
            
        if memory_percent > self.max_memory_percent:
            print(f"⚠️ High memory usage: {memory_percent}% - skipping AI tasks")
            return False
            
        return True
        
    async def start_imperium_cycle(self):
        """Imperium AI testing cycle - optimized"""
        while self.is_running:
            try:
                current_time = time.time()
                # Only run if enough time has passed and system resources are available
                if (current_time - self.last_imperium_run >= 10800 and  # 3 hours
                    self.check_system_resources()):
                    
                    print("🔧 Running Imperium AI testing...")
                    service = AIAgentService()
                    await service.run_imperium_testing(threshold=0.92)
                    self.last_imperium_run = current_time
                    print("✅ Imperium testing completed")
                
                await asyncio.sleep(3600)  # Check every hour instead of running continuously
            except Exception as e:
                print(f"Imperium error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_sandbox_cycle(self):
        """Sandbox AI experimentation cycle - optimized"""
        while self.is_running:
            try:
                current_time = time.time()
                # Only run if enough time has passed and system resources are available
                if (current_time - self.last_sandbox_run >= 14400 and  # 4 hours
                    self.check_system_resources()):
                    
                    print("🧪 Running Sandbox experimentation...")
                    service = AIAgentService()
                    await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
                    self.last_sandbox_run = current_time
                    print("✅ Sandbox experimentation completed")
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Sandbox error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_custodes_cycle(self):
        """Custodes AI testing cycle - optimized"""
        counter = 0
        while self.is_running:
            try:
                current_time = time.time()
                # Only run if enough time has passed and system resources are available
                if (current_time - self.last_custodes_run >= 10800 and  # 3 hours
                    self.check_system_resources()):
                    
                    service = AIAgentService()
                    if counter % 2 == 0:
                        print("🛡️ Running comprehensive Custodes testing...")
                        await service.run_comprehensive_custodes_testing()
                    else:
                        print("🛡️ Running regular Custodes testing...")
                        await service.run_custodes_testing()
                    
                    counter += 1
                    self.last_custodes_run = current_time
                    print("✅ Custodes testing completed")
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Custodes error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def start_guardian_cycle(self):
        """Guardian AI health monitoring cycle - optimized"""
        while self.is_running:
            try:
                current_time = time.time()
                # Only run if enough time has passed and system resources are available
                if (current_time - self.last_guardian_run >= 28800 and  # 8 hours
                    self.check_system_resources()):
                    
                    print("🛡️ Running Guardian health check...")
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
                        
                        print(f"📋 Guardian created healing proposal #{proposal.id}")
                    else:
                        print("✅ Guardian health check passed - no issues detected")
                    
                    self.last_guardian_run = current_time
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Guardian error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

# Global optimized AI agents manager
optimized_ai_agents_manager = OptimizedAIAgentsManager()

@router.post("/start")
async def start_ai_agents():
    """Start all AI agents with optimized scheduling"""
    if optimized_ai_agents_manager.is_running:
        raise HTTPException(status_code=400, detail="AI agents already running")
    
    optimized_ai_agents_manager.is_running = True
    
    # Start all AI agent cycles
    optimized_ai_agents_manager.imperium_task = asyncio.create_task(optimized_ai_agents_manager.start_imperium_cycle())
    optimized_ai_agents_manager.sandbox_task = asyncio.create_task(optimized_ai_agents_manager.start_sandbox_cycle())
    optimized_ai_agents_manager.custodes_task = asyncio.create_task(optimized_ai_agents_manager.start_custodes_cycle())
    optimized_ai_agents_manager.guardian_task = asyncio.create_task(optimized_ai_agents_manager.start_guardian_cycle())
    
    return {
        "message": "AI agents started successfully with optimized scheduling",
        "status": "running",
        "optimizations": {
            "imperium_interval_hours": 3,
            "sandbox_interval_hours": 4,
            "custodes_interval_hours": 3,
            "guardian_interval_hours": 8,
            "resource_monitoring": True
        }
    }

@router.post("/stop")
async def stop_ai_agents():
    """Stop all AI agents"""
    if not optimized_ai_agents_manager.is_running:
        raise HTTPException(status_code=400, detail="AI agents not running")
    
    optimized_ai_agents_manager.is_running = False
    
    # Cancel all tasks
    if optimized_ai_agents_manager.imperium_task:
        optimized_ai_agents_manager.imperium_task.cancel()
    if optimized_ai_agents_manager.sandbox_task:
        optimized_ai_agents_manager.sandbox_task.cancel()
    if optimized_ai_agents_manager.custodes_task:
        optimized_ai_agents_manager.custodes_task.cancel()
    if optimized_ai_agents_manager.guardian_task:
        optimized_ai_agents_manager.guardian_task.cancel()
    
    return {"message": "AI agents stopped successfully", "status": "stopped"}

@router.get("/status")
async def get_ai_agents_status():
    """Get AI agents status with performance metrics"""
    # Get system resource usage
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    
    return {
        "is_running": optimized_ai_agents_manager.is_running,
        "system_resources": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "resource_ok": optimized_ai_agents_manager.check_system_resources()
        },
        "agents": {
            "imperium": {
                "status": "running" if optimized_ai_agents_manager.imperium_task and not optimized_ai_agents_manager.imperium_task.done() else "stopped",
                "last_run": datetime.fromtimestamp(optimized_ai_agents_manager.last_imperium_run).isoformat() if optimized_ai_agents_manager.last_imperium_run > 0 else "never",
                "next_run_hours": 3,
                "config": {
                    "testing_threshold": 0.92,
                    "interval_hours": 3
                }
            },
            "sandbox": {
                "status": "running" if optimized_ai_agents_manager.sandbox_task and not optimized_ai_agents_manager.sandbox_task.done() else "stopped",
                "last_run": datetime.fromtimestamp(optimized_ai_agents_manager.last_sandbox_run).isoformat() if optimized_ai_agents_manager.last_sandbox_run > 0 else "never",
                "next_run_hours": 4,
                "config": {
                    "quality_threshold": 0.85,
                    "interval_hours": 4
                }
            },
            "custodes": {
                "status": "running" if optimized_ai_agents_manager.custodes_task and not optimized_ai_agents_manager.custodes_task.done() else "stopped",
                "last_run": datetime.fromtimestamp(optimized_ai_agents_manager.last_custodes_run).isoformat() if optimized_ai_agents_manager.last_custodes_run > 0 else "never",
                "next_run_hours": 3,
                "config": {
                    "regular_interval_hours": 3,
                    "comprehensive_interval_hours": 6
                }
            },
            "guardian": {
                "status": "running" if optimized_ai_agents_manager.guardian_task and not optimized_ai_agents_manager.guardian_task.done() else "stopped",
                "last_run": datetime.fromtimestamp(optimized_ai_agents_manager.last_guardian_run).isoformat() if optimized_ai_agents_manager.last_guardian_run > 0 else "never",
                "next_run_hours": 8,
                "config": {
                    "health_check_interval_hours": 8,
                    "sudo_required": True
                }
            }
        }
    }

@router.post("/guardian/execute-healing/{proposal_id}")
async def execute_guardian_healing(proposal_id: int, db: AsyncSession = Depends(get_db)):
    """Execute Guardian healing proposal after user approval"""
    proposal = await db.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.status != "approved":
        raise HTTPException(status_code=400, detail="Proposal must be approved to execute")
    
    if proposal.ai_type != "guardian":
        raise HTTPException(status_code=400, detail="Only Guardian proposals can be executed here")
    
    try:
        service = AIAgentService()
        content = json.loads(proposal.content)
        actions = content.get("proposed_actions", [])
        
        # Execute healing actions
        healing_result = await service.execute_guardian_healing(
            actions=actions,
            sudo_required=True
        )
        
        # Update proposal with results
        proposal.status = "completed"
        proposal.content = json.dumps({
            **content,
            "execution_results": healing_result,
            "completed_at": datetime.now().isoformat()
        })
        await db.commit()
        
        return {
            "message": "Guardian healing executed successfully",
            "proposal_id": proposal_id,
            "results": healing_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Healing execution failed: {str(e)}")

@router.get("/config")
async def get_ai_agents_config():
    """Get optimized AI agents configuration"""
    return {
        "imperium": {
            "testing_threshold": 0.92,
            "test_interval_hours": 3,
            "comprehensive_test_interval_hours": 6
        },
        "sandbox": {
            "experimentation_interval_hours": 4,
            "quality_threshold": 0.85,
            "new_code_only": True
        },
        "custodes": {
            "test_interval_hours": 3,
            "comprehensive_test_interval_hours": 6,
            "ai_sources_learning": True
        },
        "guardian": {
            "self_heal_interval_hours": 8,
            "sudo_required": True,
            "frontend_backend_healing": True
        },
        "performance_optimizations": {
            "resource_monitoring": True,
            "max_cpu_percent": 80,
            "max_memory_percent": 85,
            "check_interval_minutes": 60
        }
    }

@router.post("/manual-run/{agent_type}")
async def manual_run_agent(agent_type: str):
    """Manually trigger an AI agent run"""
    if not optimized_ai_agents_manager.is_running:
        raise HTTPException(status_code=400, detail="AI agents not running")
    
    if not optimized_ai_agents_manager.check_system_resources():
        raise HTTPException(status_code=503, detail="System resources too high for AI tasks")
    
    try:
        service = AIAgentService()
        
        if agent_type == "imperium":
            await service.run_imperium_testing(threshold=0.92)
            optimized_ai_agents_manager.last_imperium_run = time.time()
        elif agent_type == "sandbox":
            await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
            optimized_ai_agents_manager.last_sandbox_run = time.time()
        elif agent_type == "custodes":
            await service.run_custodes_testing()
            optimized_ai_agents_manager.last_custodes_run = time.time()
        elif agent_type == "guardian":
            health_status = await service.monitor_system_health()
            optimized_ai_agents_manager.last_guardian_run = time.time()
            return {"message": f"Guardian health check completed", "health_status": health_status}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        return {"message": f"{agent_type} manual run completed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual run failed: {str(e)}")
'''
        
        # Create the optimized router file
        router_path = Path("app/routers/ai_agents_optimized.py")
        router_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(router_path, 'w') as f:
            f.write(optimized_router)
        
        logger.info("✅ Created optimized AI agents router")
        
    async def update_main_app(self):
        """Update main FastAPI app to use optimized router"""
        logger.info("🔧 Updating Main FastAPI App...")
        
        # Read existing main.py
        main_path = Path("app/main.py")
        if main_path.exists():
            with open(main_path, 'r') as f:
                main_content = f.read()
            
            # Replace old AI agents router with optimized one
            lines = main_content.split('\n')
            updated_lines = []
            
            for line in lines:
                if "ai_agents_integrated" in line:
                    # Replace with optimized import
                    updated_lines.append("from app.routers.ai_agents_optimized import router as ai_agents_router")
                else:
                    updated_lines.append(line)
            
            # Write updated main.py
            with open(main_path, 'w') as f:
                f.write('\n'.join(updated_lines))
            
            logger.info("✅ Updated main.py with optimized AI agents router")
        else:
            logger.warning("⚠️ main.py not found - you'll need to manually add the optimized AI agents router")
        
    async def create_optimized_startup_script(self):
        """Create optimized startup script"""
        logger.info("🔧 Creating Optimized Startup Script...")
        
        startup_script = '''#!/bin/bash
# Start Optimized AI Backend
echo "🚀 Starting Optimized AI Backend..."

cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI backend with optimized AI agents
echo "📡 Starting FastAPI backend on port 8000..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait a moment for backend to start
sleep 5

# Start optimized AI agents through the API
echo "🤖 Starting optimized AI agents..."
curl -X POST http://localhost:8000/ai-agents/start

echo "✅ Optimized AI Backend started!"
echo "📊 Check status: curl http://localhost:8000/ai-agents/status"
echo "🛑 Stop agents: curl -X POST http://localhost:8000/ai-agents/stop"
echo "🔧 Manual run: curl -X POST http://localhost:8000/ai-agents/manual-run/{agent_type}"
'''
        
        with open("start_optimized_backend.sh", 'w') as f:
            f.write(startup_script)
        
        os.chmod("start_optimized_backend.sh", 0o755)
        
        logger.info("✅ Created optimized startup script")
        
    async def create_optimized_systemd_service(self):
        """Create optimized systemd service"""
        logger.info("🔧 Creating Optimized Systemd Service...")
        
        service_content = '''[Unit]
Description=Optimized AI Backend with Reduced Load
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/start_optimized_backend.sh
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
'''
        
        with open("ai-backend-optimized.service", 'w') as f:
            f.write(service_content)
        
        logger.info("✅ Created optimized systemd service")
        
    async def create_optimization_deployment_script(self):
        """Create deployment script for optimized backend"""
        logger.info("🔧 Creating Optimization Deployment Script...")
        
        deployment_script = '''#!/bin/bash
# Deploy Optimized AI Backend
echo "🚀 Deploying Optimized AI Backend..."

# Stop old services
echo "🛑 Stopping old services..."
sudo systemctl stop ai-backend-integrated.service 2>/dev/null || true
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable old services
sudo systemctl disable ai-backend-integrated.service 2>/dev/null || true
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
sudo rm -f /etc/systemd/system/ai-backend-integrated.service
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Install optimized backend service
echo "📋 Installing optimized backend service..."
sudo cp ai-backend-optimized.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start optimized service
echo "✅ Starting optimized backend..."
sudo systemctl enable ai-backend-optimized.service
sudo systemctl start ai-backend-optimized.service

# Check status
echo "📊 Service Status:"
sudo systemctl status ai-backend-optimized.service --no-pager -l

echo "✅ Optimized AI Backend deployed successfully!"
echo ""
echo "📋 Performance Optimizations Applied:"
echo "• Imperium: Every 3 hours (was 45 minutes)"
echo "• Sandbox: Every 4 hours (was 45 minutes)"
echo "• Custodes: Every 3 hours (was 45 minutes)"
echo "• Guardian: Every 8 hours (was 60 minutes)"
echo "• Resource monitoring: CPU/Memory limits"
echo "• Manual trigger: Available for immediate runs"
echo ""
echo "🔍 API Endpoints:"
echo "• GET  /ai-agents/status - Check status with resource metrics"
echo "• POST /ai-agents/start - Start optimized agents"
echo "• POST /ai-agents/stop - Stop agents"
echo "• POST /ai-agents/manual-run/{agent} - Manual trigger"
echo ""
echo "📊 Monitor with:"
echo "sudo journalctl -u ai-backend-optimized.service -f"
'''
        
        with open("deploy_optimized_backend.sh", 'w') as f:
            f.write(deployment_script)
        
        os.chmod("deploy_optimized_backend.sh", 0o755)
        
        logger.info("✅ Created optimization deployment script")
        
    async def run_optimization(self):
        """Run the complete optimization"""
        logger.info("🚀 Starting Backend Performance Optimization...")
        
        try:
            # Create all optimization components
            await self.create_optimized_router()
            await self.update_main_app()
            await self.create_optimized_startup_script()
            await self.create_optimized_systemd_service()
            await self.create_optimization_deployment_script()
            
            logger.info("✅ Backend Performance Optimization completed!")
            
            # Print summary
            print("\n" + "="*60)
            print("🎯 Backend Performance Optimization Complete")
            print("="*60)
            print("📋 Performance Improvements:")
            print("• Imperium: 3 hours (was 45 minutes) - 75% reduction")
            print("• Sandbox: 4 hours (was 45 minutes) - 82% reduction")
            print("• Custodes: 3 hours (was 45 minutes) - 75% reduction")
            print("• Guardian: 8 hours (was 60 minutes) - 87% reduction")
            print("• Resource monitoring prevents overload")
            print("• Manual triggers available for immediate needs")
            print("\n📁 Files Created:")
            print("• app/routers/ai_agents_optimized.py")
            print("• start_optimized_backend.sh")
            print("• ai-backend-optimized.service")
            print("• deploy_optimized_backend.sh")
            print("\n🚀 Next Steps:")
            print("1. Run: chmod +x deploy_optimized_backend.sh")
            print("2. Run: ./deploy_optimized_backend.sh")
            print("3. Backend will be much faster and more responsive")
            print("4. Monitor performance: curl http://localhost:8000/ai-agents/status")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Error during optimization: {e}")
            raise

async def main():
    """Main function"""
    optimizer = BackendPerformanceOptimizer()
    await optimizer.run_optimization()

if __name__ == "__main__":
    asyncio.run(main()) 