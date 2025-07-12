"""
AI Agents Router - Endpoints for autonomous AI agents
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import structlog

from app.services.ai_agent_service import AIAgentService
from app.services.background_service import BackgroundService
from app.services.ai_learning_service import AILearningService
from app.services.ai_growth_service import AIGrowthService
from app.services.github_service import GitHubService
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()
router = APIRouter()

ai_agent_service = AIAgentService()
background_service = BackgroundService()
ai_learning_service = AILearningService()
ai_growth_service = AIGrowthService()
github_service = GitHubService()


@router.post("/run-all")
async def run_all_agents():
    """Run all AI agents manually"""
    try:
        logger.info("🚀 Manual trigger: Running all AI agents")
        result = await ai_agent_service.run_all_agents()
        return result
    except Exception as e:
        logger.error("Error running all agents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/{agent_type}")
async def run_specific_agent(agent_type: str):
    """Run a specific AI agent"""
    try:
        agent_type = agent_type.lower()
        
        if agent_type == "imperium":
            result = await ai_agent_service.run_imperium_agent()
        elif agent_type == "guardian":
            result = await ai_agent_service.run_guardian_agent()
        elif agent_type == "sandbox":
            result = await ai_agent_service.run_sandbox_agent()
        elif agent_type == "conquest":
            result = await ai_agent_service.run_conquest_agent()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        logger.info(f"🚀 Manual trigger: Running {agent_type} agent")
        return result
    except Exception as e:
        logger.error(f"Error running {agent_type} agent", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/start")
async def start_autonomous_cycle():
    """Start the autonomous AI cycle"""
    try:
        logger.info("🤖 Starting autonomous AI cycle")
        await background_service.start_autonomous_cycle()
        return {"status": "success", "message": "Autonomous cycle started"}
    except Exception as e:
        logger.error("Error starting autonomous cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autonomous/stop")
async def stop_autonomous_cycle():
    """Stop the autonomous AI cycle"""
    try:
        logger.info("🛑 Stopping autonomous AI cycle")
        await background_service.stop_autonomous_cycle()
        return {"status": "success", "message": "Autonomous cycle stopped"}
    except Exception as e:
        logger.error("Error stopping autonomous cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autonomous/status")
async def get_autonomous_status():
    """Get autonomous cycle status"""
    try:
        status = await background_service.get_system_status()
        return status
    except Exception as e:
        logger.error("Error getting autonomous status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual-cycle")
async def run_manual_cycle():
    """Run a manual AI agent cycle"""
    try:
        logger.info("🔄 Running manual AI agent cycle")
        result = await background_service.run_manual_cycle()
        return result
    except Exception as e:
        logger.error("Error running manual cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agents_status():
    """Get overall AI agents status"""
    try:
        # Test each agent
        agents_status = {}
        
        # Test Imperium
        try:
            imperium_result = await ai_agent_service.run_imperium_agent()
            agents_status["imperium"] = {
                "status": "healthy" if imperium_result["status"] == "success" else "warning",
                "last_run": imperium_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["imperium"] = {"status": "error", "error": str(e)}
        
        # Test Guardian
        try:
            guardian_result = await ai_agent_service.run_guardian_agent()
            agents_status["guardian"] = {
                "status": "healthy" if guardian_result["status"] == "success" else "warning",
                "last_run": guardian_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["guardian"] = {"status": "error", "error": str(e)}
        
        # Test Sandbox
        try:
            sandbox_result = await ai_agent_service.run_sandbox_agent()
            agents_status["sandbox"] = {
                "status": "healthy" if sandbox_result["status"] == "success" else "warning",
                "last_run": sandbox_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["sandbox"] = {"status": "error", "error": str(e)}
        
        # Test Conquest
        try:
            conquest_result = await ai_agent_service.run_conquest_agent()
            agents_status["conquest"] = {
                "status": "healthy" if conquest_result["status"] == "success" else "warning",
                "last_run": conquest_result.get("timestamp", "unknown")
            }
        except Exception as e:
            agents_status["conquest"] = {"status": "error", "error": str(e)}
        
        return {
            "agents": agents_status,
            "autonomous_cycle_running": background_service._running,
            "timestamp": "2025-07-05T16:00:00Z"
        }
    except Exception as e:
        logger.error("Error getting agents status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/cycle-status", summary="Get current AI cycle/status", tags=["Agents"])
async def get_ai_cycle_status():
    """
    Returns the current cycle/status for all AIs (e.g., idle, internet_searching, improving, etc.)
    """
    try:
        # Simulate or fetch real status from background service/learning service
        # For now, return a static example
        status = {
            "Imperium": {"status": "idle", "last_action": "audit", "timestamp": "2025-07-06T15:00:00Z"},
            "Guardian": {"status": "internet_searching", "last_action": "security_scan", "timestamp": "2025-07-06T14:55:00Z"},
            "Sandbox": {"status": "improving", "last_action": "test_run", "timestamp": "2025-07-06T14:50:00Z"},
            "Conquest": {"status": "idle", "last_action": "deployment_check", "timestamp": "2025-07-06T14:45:00Z"},
        }
        # TODO: Integrate with real background/learning service state
        return {"agents": status, "timestamp": "2025-07-06T15:00:00Z"}
    except Exception as e:
        logger.error("Error getting AI cycle status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get AI cycle status") 