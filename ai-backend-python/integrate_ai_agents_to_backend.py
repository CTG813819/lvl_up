#!/usr/bin/env python3
"""
Integrate AI Agents to Main Backend - All agents work through port 8000
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
        logging.FileHandler('ai_agents_integration.log')
    ]
)
logger = logging.getLogger(__name__)

class AIAgentsBackendIntegration:
    """Integrate AI agents to work through main FastAPI backend"""
    
    def __init__(self):
        self.config = {
            "imperium": {
                "testing_threshold": 0.92,
                "test_interval": 45,  # minutes
                "comprehensive_test_interval": 90
            },
            "sandbox": {
                "experimentation_interval": 45,
                "quality_threshold": 0.85,
                "new_code_only": True
            },
            "custodes": {
                "test_interval": 45,
                "comprehensive_test_interval": 90,
                "ai_sources_learning": True
            },
            "guardian": {
                "self_heal_interval": 60,
                "sudo_required": True,
                "frontend_backend_healing": True
            }
        }
        
    async def create_backend_integration_routes(self):
        """Create FastAPI routes for AI agent integration"""
        logger.info("🔧 Creating Backend Integration Routes...")
        
        # Create AI agents router
        ai_agents_router = '''from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional
import asyncio
import json
from datetime import datetime

from app.core.database import get_db
from app.models.sql_models import Proposal, Learning
from app.services.ai_agent_service import AIAgentService

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

# Background task manager for AI agents
class AIAgentsManager:
    def __init__(self):
        self.imperium_task = None
        self.sandbox_task = None
        self.custodes_task = None
        self.guardian_task = None
        self.is_running = False
        
    async def start_imperium_cycle(self):
        """Imperium AI testing cycle"""
        while self.is_running:
            try:
                service = AIAgentService()
                await service.run_imperium_testing(threshold=0.92)
                await asyncio.sleep(2700)  # 45 minutes
            except Exception as e:
                print(f"Imperium error: {e}")
                await asyncio.sleep(60)
    
    async def start_sandbox_cycle(self):
        """Sandbox AI experimentation cycle"""
        while self.is_running:
            try:
                service = AIAgentService()
                await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
                await asyncio.sleep(2700)  # 45 minutes
            except Exception as e:
                print(f"Sandbox error: {e}")
                await asyncio.sleep(60)
    
    async def start_custodes_cycle(self):
        """Custodes AI testing cycle"""
        counter = 0
        while self.is_running:
            try:
                service = AIAgentService()
                if counter % 2 == 0:
                    await service.run_comprehensive_custodes_testing()
                else:
                    await service.run_custodes_testing()
                counter += 1
                await asyncio.sleep(2700)  # 45 minutes
            except Exception as e:
                print(f"Custodes error: {e}")
                await asyncio.sleep(60)
    
    async def start_guardian_cycle(self):
        """Guardian AI health monitoring cycle"""
        while self.is_running:
            try:
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
                
                await asyncio.sleep(3600)  # 60 minutes
            except Exception as e:
                print(f"Guardian error: {e}")
                await asyncio.sleep(60)

# Global AI agents manager
ai_agents_manager = AIAgentsManager()

@router.post("/start")
async def start_ai_agents():
    """Start all AI agents"""
    if ai_agents_manager.is_running:
        raise HTTPException(status_code=400, detail="AI agents already running")
    
    ai_agents_manager.is_running = True
    
    # Start all AI agent cycles
    ai_agents_manager.imperium_task = asyncio.create_task(ai_agents_manager.start_imperium_cycle())
    ai_agents_manager.sandbox_task = asyncio.create_task(ai_agents_manager.start_sandbox_cycle())
    ai_agents_manager.custodes_task = asyncio.create_task(ai_agents_manager.start_custodes_cycle())
    ai_agents_manager.guardian_task = asyncio.create_task(ai_agents_manager.start_guardian_cycle())
    
    return {"message": "AI agents started successfully", "status": "running"}

@router.post("/stop")
async def stop_ai_agents():
    """Stop all AI agents"""
    if not ai_agents_manager.is_running:
        raise HTTPException(status_code=400, detail="AI agents not running")
    
    ai_agents_manager.is_running = False
    
    # Cancel all tasks
    if ai_agents_manager.imperium_task:
        ai_agents_manager.imperium_task.cancel()
    if ai_agents_manager.sandbox_task:
        ai_agents_manager.sandbox_task.cancel()
    if ai_agents_manager.custodes_task:
        ai_agents_manager.custodes_task.cancel()
    if ai_agents_manager.guardian_task:
        ai_agents_manager.guardian_task.cancel()
    
    return {"message": "AI agents stopped successfully", "status": "stopped"}

@router.get("/status")
async def get_ai_agents_status():
    """Get AI agents status"""
    return {
        "is_running": ai_agents_manager.is_running,
        "agents": {
            "imperium": {
                "status": "running" if ai_agents_manager.imperium_task and not ai_agents_manager.imperium_task.done() else "stopped",
                "config": {
                    "testing_threshold": 0.92,
                    "interval_minutes": 45
                }
            },
            "sandbox": {
                "status": "running" if ai_agents_manager.sandbox_task and not ai_agents_manager.sandbox_task.done() else "stopped",
                "config": {
                    "quality_threshold": 0.85,
                    "interval_minutes": 45
                }
            },
            "custodes": {
                "status": "running" if ai_agents_manager.custodes_task and not ai_agents_manager.custodes_task.done() else "stopped",
                "config": {
                    "regular_interval_minutes": 45,
                    "comprehensive_interval_minutes": 90
                }
            },
            "guardian": {
                "status": "running" if ai_agents_manager.guardian_task and not ai_agents_manager.guardian_task.done() else "stopped",
                "config": {
                    "health_check_interval_minutes": 60,
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
    """Get AI agents configuration"""
    return {
        "imperium": {
            "testing_threshold": 0.92,
            "test_interval_minutes": 45,
            "comprehensive_test_interval_minutes": 90
        },
        "sandbox": {
            "experimentation_interval_minutes": 45,
            "quality_threshold": 0.85,
            "new_code_only": True
        },
        "custodes": {
            "test_interval_minutes": 45,
            "comprehensive_test_interval_minutes": 90,
            "ai_sources_learning": True
        },
        "guardian": {
            "self_heal_interval_minutes": 60,
            "sudo_required": True,
            "frontend_backend_healing": True
        }
    }
'''
        
        # Create the router file
        router_path = Path("app/routers/ai_agents_integrated.py")
        router_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(router_path, 'w') as f:
            f.write(ai_agents_router)
        
        logger.info("✅ Created AI agents integration router")
        
    async def update_main_app(self):
        """Update main FastAPI app to include AI agents router"""
        logger.info("🔧 Updating Main FastAPI App...")
        
        # Read existing main.py
        main_path = Path("app/main.py")
        if main_path.exists():
            with open(main_path, 'r') as f:
                main_content = f.read()
            
            # Check if AI agents router is already included
            if "ai_agents_integrated" not in main_content:
                # Add import
                if "from app.routers" in main_content:
                    # Find the last router import and add after it
                    lines = main_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith("from app.routers") and i + 1 < len(lines):
                            if not lines[i + 1].startswith("from app.routers"):
                                lines.insert(i + 1, "from app.routers.ai_agents_integrated import router as ai_agents_router")
                                break
                else:
                    # Add import section
                    lines = main_content.split('\n')
                    for i, line in enumerate(lines):
                        if "from fastapi import" in line:
                            lines.insert(i + 1, "from app.routers.ai_agents_integrated import router as ai_agents_router")
                            break
                
                # Add router to app
                for i, line in enumerate(lines):
                    if "app.include_router" in line and i + 1 < len(lines):
                        if not lines[i + 1].strip().startswith("app.include_router"):
                            lines.insert(i + 1, "app.include_router(ai_agents_router)")
                            break
                
                # Write updated main.py
                with open(main_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                logger.info("✅ Updated main.py with AI agents router")
            else:
                logger.info("✅ AI agents router already included in main.py")
        else:
            logger.warning("⚠️ main.py not found - you'll need to manually add the AI agents router")
        
    async def create_startup_script(self):
        """Create script to start AI agents with backend"""
        logger.info("🔧 Creating Startup Script...")
        
        startup_script = '''#!/bin/bash
# Start AI Backend with Integrated AI Agents
echo "🚀 Starting AI Backend with Integrated AI Agents..."

cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Start the FastAPI backend (this will include AI agents)
echo "📡 Starting FastAPI backend on port 8000..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait a moment for backend to start
sleep 5

# Start AI agents through the API
echo "🤖 Starting AI agents through backend API..."
curl -X POST http://localhost:8000/ai-agents/start

echo "✅ AI Backend with Integrated AI Agents started!"
echo "📊 Check status: curl http://localhost:8000/ai-agents/status"
echo "🛑 Stop agents: curl -X POST http://localhost:8000/ai-agents/stop"
'''
        
        with open("start_ai_backend_integrated.sh", 'w') as f:
            f.write(startup_script)
        
        os.chmod("start_ai_backend_integrated.sh", 0o755)
        
        logger.info("✅ Created startup script")
        
    async def create_systemd_service(self):
        """Create systemd service for integrated backend"""
        logger.info("🔧 Creating Integrated Backend Systemd Service...")
        
        service_content = '''[Unit]
Description=AI Backend with Integrated AI Agents
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/start_ai_backend_integrated.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
        
        with open("ai-backend-integrated.service", 'w') as f:
            f.write(service_content)
        
        logger.info("✅ Created integrated backend systemd service")
        
    async def create_deployment_script(self):
        """Create deployment script for integrated backend"""
        logger.info("🔧 Creating Deployment Script...")
        
        deployment_script = '''#!/bin/bash
# Deploy Integrated AI Backend
echo "🚀 Deploying Integrated AI Backend..."

# Stop old services
echo "🛑 Stopping old services..."
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable old services
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Install integrated backend service
echo "📋 Installing integrated backend service..."
sudo cp ai-backend-integrated.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start integrated service
echo "✅ Starting integrated backend..."
sudo systemctl enable ai-backend-integrated.service
sudo systemctl start ai-backend-integrated.service

# Check status
echo "📊 Service Status:"
sudo systemctl status ai-backend-integrated.service --no-pager -l

echo "✅ Integrated AI Backend deployed successfully!"
echo ""
echo "📋 All AI agents now run through port 8000:"
echo "• Imperium: 92% testing threshold, every 45 minutes"
echo "• Sandbox: 85% quality threshold, new code only, every 45 minutes"
echo "• Custodes: Comprehensive testing every 90 minutes, regular every 45 minutes"
echo "• Guardian: Self-healing every 60 minutes with sudo approval"
echo ""
echo "🔍 API Endpoints:"
echo "• GET  /ai-agents/status - Check agent status"
echo "• POST /ai-agents/start - Start all agents"
echo "• POST /ai-agents/stop - Stop all agents"
echo "• GET  /ai-agents/config - Get configuration"
echo "• POST /ai-agents/guardian/execute-healing/{id} - Execute Guardian healing"
echo ""
echo "📊 Monitor with:"
echo "sudo journalctl -u ai-backend-integrated.service -f"
'''
        
        with open("deploy_integrated_backend.sh", 'w') as f:
            f.write(deployment_script)
        
        os.chmod("deploy_integrated_backend.sh", 0o755)
        
        logger.info("✅ Created deployment script")
        
    async def run_integration(self):
        """Run the complete integration"""
        logger.info("🚀 Starting AI Agents Backend Integration...")
        
        try:
            # Create all integration components
            await self.create_backend_integration_routes()
            await self.update_main_app()
            await self.create_startup_script()
            await self.create_systemd_service()
            await self.create_deployment_script()
            
            logger.info("✅ AI Agents Backend Integration completed!")
            
            # Print summary
            print("\n" + "="*60)
            print("🎯 AI Agents Backend Integration Complete")
            print("="*60)
            print("📋 Integration Summary:")
            print("• All AI agents now run through FastAPI backend on port 8000")
            print("• No more separate systemd services")
            print("• Unified API endpoints for all AI agent operations")
            print("• Background tasks managed by FastAPI")
            print("\n📁 Files Created:")
            print("• app/routers/ai_agents_integrated.py")
            print("• start_ai_backend_integrated.sh")
            print("• ai-backend-integrated.service")
            print("• deploy_integrated_backend.sh")
            print("\n🚀 Next Steps:")
            print("1. Run: chmod +x deploy_integrated_backend.sh")
            print("2. Run: ./deploy_integrated_backend.sh")
            print("3. All AI agents will run through port 8000")
            print("4. Monitor with: sudo journalctl -u ai-backend-integrated.service -f")
            print("="*60)
            
        except Exception as e:
            logger.error(f"❌ Error during integration: {e}")
            raise

async def main():
    """Main function"""
    integration = AIAgentsBackendIntegration()
    await integration.run_integration()

if __name__ == "__main__":
    asyncio.run(main()) 