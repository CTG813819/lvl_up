"""
Learning router for AI learning endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
import structlog

from app.services.ml_service import MLService
ml_service = MLService()

from app.services.ai_learning_service import AILearningService
ai_learning_service = AILearningService()

from app.models.sql_models import AILearningHistory
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.database import get_session
from collections import defaultdict
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter()


@router.get("/stats/{ai_type}")
async def get_learning_stats(ai_type: str):
    """Get learning statistics for an AI type"""
    return {"message": f"Learning stats for {ai_type} - simplified test"}


@router.get("/insights/{ai_type}")
async def get_learning_insights(ai_type: str):
    """Get learning insights and recommendations"""
    try:
        insights = await ai_learning_service.get_learning_insights(ai_type)
        return insights
    except Exception as e:
        logger.error("Error getting learning insights", error=str(e), ai_type=ai_type)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_models():
    """Train ML models"""
    try:
        await ml_service.train_models()
        return {"message": "Models trained successfully"}
    except Exception as e:
        logger.error("Error training models", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ml-insights")
async def get_ml_insights():
    """Get ML insights"""
    try:
        insights = await ml_service.get_ml_insights()
        return insights
    except Exception as e:
        logger.error("Error getting ML insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data")
async def get_learning_data():
    """Get learning data for all AI types"""
    try:
        data = {
            "Imperium": {
                "experiments": [
                    {
                        "id": "exp-1",
                        "description": "Testing code optimization",
                        "timestamp": "2025-07-05T12:00:00Z",
                        "success": True,
                    },
                ],
                "insights": ["Code optimization improves performance"],
            },
            "Sandbox": {
                "experiments": [
                    {
                        "id": "exp-2",
                        "description": "Testing new features",
                        "timestamp": "2025-07-05T12:00:00Z",
                        "success": True,
                    },
                ],
                "insights": ["New features enhance user experience"],
            },
            "Guardian": {
                "experiments": [
                    {
                        "id": "exp-3",
                        "description": "Security testing",
                        "timestamp": "2025-07-05T12:00:00Z",
                        "success": True,
                    },
                ],
                "insights": ["Security measures are effective"],
            },
        }
        return data
    except Exception as e:
        logger.error("Error getting learning data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_learning_metrics():
    """Get learning metrics for all AI types"""
    try:
        metrics = {
            "Imperium": {
                "totalExperiments": 15,
                "successRate": 0.87,
                "lastExperiment": "2025-07-05T12:00:00Z",
                "learningProgress": 0.75,
            },
            "Sandbox": {
                "totalExperiments": 23,
                "successRate": 0.91,
                "lastExperiment": "2025-07-05T12:00:00Z",
                "learningProgress": 0.82,
            },
            "Guardian": {
                "totalExperiments": 8,
                "successRate": 0.94,
                "lastExperiment": "2025-07-05T12:00:00Z",
                "learningProgress": 0.68,
            },
        }
        return metrics
    except Exception as e:
        logger.error("Error getting learning metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_learning_status():
    """Get learning system status"""
    try:
        status = {
            "status": "active",
            "message": "AI Learning system is running",
            "timestamp": "2025-07-05T12:00:00Z",
            "ai_types": ["Imperium", "Guardian", "Sandbox", "Conquest"],
            "active_learning": True,
            "last_activity": "2025-07-05T12:00:00Z",
            "total_experiments": 46,
            "success_rate": 0.89
        }
        return status
    except Exception as e:
        logger.error("Error getting learning status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug-log")
async def get_debug_log():
    """Get debug log for learning system"""
    try:
        log_data = {
            "entries": [
                {
                    "timestamp": "2025-07-05T12:00:00Z",
                    "level": "INFO",
                    "message": "Learning system initialized",
                    "ai_type": "Imperium",
                },
                {
                    "timestamp": "2025-07-05T12:01:00Z",
                    "level": "INFO",
                    "message": "Proposal analyzed successfully",
                    "ai_type": "Imperium",
                },
            ],
            "total_entries": 2,
            "last_updated": "2025-07-05T12:01:00Z",
        }
        return log_data
    except Exception as e:
        logger.error("Error getting debug log", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/periodic-learning-status")
async def get_periodic_learning_status():
    """Get status of periodic internet learning for all AIs"""
    try:
        # Get periodic learning information from the service
        learning_info = ai_learning_service.get_last_periodic_learning_info()
        
        status = {
            "status": "active" if learning_info["is_periodic_learning_active"] else "inactive",
            "message": "Periodic internet learning system status",
            "timestamp": "2025-07-05T12:00:00Z",
            "periodic_learning": {
                "is_active": learning_info["is_periodic_learning_active"],
                "last_learning_time": learning_info["last_learning_time"],
                "next_learning_in_minutes": learning_info["next_learning_in_minutes"],
                "cycle_interval_minutes": 60,
                "ai_types": ["Imperium", "Guardian", "Sandbox", "Conquest"],
                "features": [
                    "Automatic internet search every 60 minutes",
                    "Topic-specific learning for each AI",
                    "Real-time learning value tracking",
                    "Search results integration",
                    "Learning notifications"
                ]
            },
            "internet_learning_enabled": True,
            "learning_topics": {
                "Imperium": [
                    "system architecture patterns",
                    "strategic planning methodologies",
                    "complex problem solving techniques"
                ],
                "Guardian": [
                    "security best practices",
                    "code quality standards",
                    "testing methodologies"
                ],
                "Sandbox": [
                    "experimental programming",
                    "rapid prototyping",
                    "creative problem solving"
                ],
                "Conquest": [
                    "app development frameworks",
                    "mobile app design patterns",
                    "user experience design"
                ]
            }
        }
        return status
    except Exception as e:
        logger.error("Error getting periodic learning status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-periodic-learning")
async def trigger_periodic_learning():
    """Manually trigger a periodic learning cycle"""
    try:
        # Trigger the periodic learning manually
        learning_results = await ai_learning_service._perform_periodic_internet_learning()
        
        return {
            "message": "Periodic learning cycle triggered successfully",
            "results": learning_results,
            "timestamp": "2025-07-05T12:00:00Z"
        }
    except Exception as e:
        logger.error("Error triggering periodic learning", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/codex/chapters")
async def get_codex_chapters(db: AsyncSession = Depends(get_session)):
    """Get Codex chapters: each day is a chapter, entries are what AIs learned/discussed with timestamps."""
    # Fetch all learning history, order by created_at
    result = await db.execute(
        AILearningHistory.__table__.select().order_by(AILearningHistory.created_at.asc())
    )
    rows = result.fetchall()
    # Group by day (YYYY-MM-DD)
    chapters = defaultdict(list)
    for row in rows:
        created_at = row.created_at
        day_str = created_at.strftime('%Y-%m-%d')
        chapters[day_str].append({
            "ai_type": row.ai_type,
            "content": row.learning_event if not row.details else f"{row.learning_event}: {row.details}",
            "timestamp": created_at.strftime('%H:%M:%S'),
        })
    # Format for frontend: list of {day, entries}
    chapter_list = [
        {"day": day, "entries": entries}
        for day, entries in sorted(chapters.items())
    ]
    return {"chapters": chapter_list} 