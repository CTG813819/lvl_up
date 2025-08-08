"""
Collaborative AI Router - API endpoints for Collaborative AI service
Provides endpoints for team coordination and knowledge sharing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.services.collaborative_ai_service import collaborative_ai_service, CollaborationType

logger = structlog.get_logger()
router = APIRouter(prefix="/api/collaborative-ai", tags=["Collaborative AI"])

# Pydantic models
class TeamCreationRequest(BaseModel):
    team_name: str
    ai_participants: List[str]
    collaboration_type: str

class SessionRequest(BaseModel):
    team_id: str
    session_topic: str
    session_duration: int = 3600

@router.post("/teams/create")
async def create_collaboration_team(request: TeamCreationRequest):
    """Create a new collaboration team"""
    try:
        logger.info("🤝 Creating collaboration team", team_name=request.team_name, type=request.collaboration_type)
        
        # Convert string to CollaborationType enum
        try:
            collaboration_type = CollaborationType(request.collaboration_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid collaboration type. Must be one of: {[c.value for c in CollaborationType]}")
        
        result = await collaborative_ai_service.create_collaboration_team(
            request.team_name, 
            request.ai_participants, 
            collaboration_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Collaboration team created successfully", team_id=result["team_id"])
        
        return {
            "status": "success",
            "message": "Collaboration team created successfully",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error creating collaboration team", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/start")
async def start_collaboration_session(request: SessionRequest):
    """Start a collaboration session for a team"""
    try:
        logger.info("🚀 Starting collaboration session", team_id=request.team_id, topic=request.session_topic)
        
        result = await collaborative_ai_service.start_collaboration_session(
            request.team_id, 
            request.session_topic, 
            request.session_duration
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Collaboration session completed", session_id=result["session_id"])
        
        return {
            "status": "success",
            "message": "Collaboration session completed",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error starting collaboration session", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams")
async def get_collaboration_teams():
    """Get all collaboration teams"""
    try:
        logger.info("🤝 Getting collaboration teams")
        
        result = await collaborative_ai_service.get_collaboration_teams()
        
        return {
            "status": "success",
            "message": "Collaboration teams retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting collaboration teams", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}/performance")
async def get_team_performance(team_id: str):
    """Get performance metrics for a specific team"""
    try:
        logger.info("📊 Getting team performance", team_id=team_id)
        
        result = await collaborative_ai_service.get_team_performance(team_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "status": "success",
            "message": "Team performance retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error getting team performance", error=str(e), team_id=team_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_collaboration_statistics():
    """Get comprehensive collaboration statistics"""
    try:
        logger.info("📊 Getting collaboration statistics")
        
        result = await collaborative_ai_service.get_collaboration_statistics()
        
        return {
            "status": "success",
            "message": "Collaboration statistics retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting collaboration statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration-types")
async def get_available_collaboration_types():
    """Get available collaboration types"""
    try:
        logger.info("🎯 Getting available collaboration types")
        
        result = await collaborative_ai_service.get_available_collaboration_types()
        
        return {
            "status": "success",
            "message": "Available collaboration types retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting available collaboration types", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_collaborative_ai_status():
    """Get Collaborative AI system status"""
    try:
        logger.info("📊 Getting Collaborative AI status")
        
        teams = await collaborative_ai_service.get_collaboration_teams()
        statistics = await collaborative_ai_service.get_collaboration_statistics()
        
        status = {
            "service": "Collaborative AI",
            "status": "operational",
            "total_teams": teams["total_teams"],
            "active_teams": teams["active_teams"],
            "total_sessions": teams["total_sessions"],
            "total_knowledge_shared": teams["total_knowledge_shared"],
            "learning_progress": statistics["learning_progress"],
            "collaboration_complexity": statistics["collaboration_complexity"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Collaborative AI status retrieved",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Collaborative AI status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 