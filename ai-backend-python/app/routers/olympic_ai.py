"""
Olympic AI Router - API endpoints for Olympic AI service
Provides endpoints for competitive AI events and competitions
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.services.olympic_ai_service import olympic_ai_service, OlympicEvent

logger = structlog.get_logger()
router = APIRouter(prefix="/api/olympic-ai", tags=["Olympic AI"])

# Pydantic models
class CompetitorRegistrationRequest(BaseModel):
    ai_type: str
    capabilities: Dict[str, Any]

class CompetitionRequest(BaseModel):
    event_type: str
    competitors: List[str]

@router.post("/competitors/register")
async def register_competitor(request: CompetitorRegistrationRequest):
    """Register an AI competitor for Olympic events"""
    try:
        logger.info("🏅 Registering AI competitor", ai_type=request.ai_type)
        
        result = await olympic_ai_service.register_ai_competitor(request.ai_type, request.capabilities)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ AI competitor registered successfully", competitor_id=result["competitor_id"])
        
        return {
            "status": "success",
            "message": "AI competitor registered successfully",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error registering AI competitor", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/competitions/start")
async def start_competition(request: CompetitionRequest):
    """Start an Olympic competition event"""
    try:
        logger.info("🏆 Starting Olympic competition", event_type=request.event_type, competitors=len(request.competitors))
        
        # Convert string to OlympicEvent enum
        try:
            event_type = OlympicEvent(request.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type. Must be one of: {[e.value for e in OlympicEvent]}")
        
        result = await olympic_ai_service.start_olympic_competition(event_type, request.competitors)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Olympic competition completed", competition_id=result["competition_id"])
        
        return {
            "status": "success",
            "message": "Olympic competition completed",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error starting Olympic competition", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_olympic_leaderboard():
    """Get Olympic leaderboard with current rankings"""
    try:
        logger.info("🏅 Getting Olympic leaderboard")
        
        result = await olympic_ai_service.get_olympic_leaderboard()
        
        return {
            "status": "success",
            "message": "Olympic leaderboard retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Olympic leaderboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_olympic_statistics():
    """Get comprehensive Olympic statistics"""
    try:
        logger.info("📊 Getting Olympic statistics")
        
        result = await olympic_ai_service.get_olympic_statistics()
        
        return {
            "status": "success",
            "message": "Olympic statistics retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Olympic statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_available_events():
    """Get available Olympic events"""
    try:
        logger.info("🎯 Getting available Olympic events")
        
        result = await olympic_ai_service.get_available_events()
        
        return {
            "status": "success",
            "message": "Available Olympic events retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting available Olympic events", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_olympic_ai_status():
    """Get Olympic AI system status"""
    try:
        logger.info("📊 Getting Olympic AI status")
        
        leaderboard = await olympic_ai_service.get_olympic_leaderboard()
        statistics = await olympic_ai_service.get_olympic_statistics()
        
        status = {
            "service": "Olympic AI",
            "status": "operational",
            "total_competitors": leaderboard["total_competitors"],
            "total_events": leaderboard["total_events"],
            "learning_progress": statistics["learning_progress"],
            "olympic_complexity": statistics["olympic_complexity"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Olympic AI status retrieved",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Olympic AI status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 