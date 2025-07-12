"""
AI Growth Router - Endpoints for AI self-improvement and growth
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import structlog

from app.services.ai_growth_service import AIGrowthService

logger = structlog.get_logger()
router = APIRouter()

growth_service = AIGrowthService()


@router.get("/analysis/{ai_type}")
async def analyze_growth_potential(ai_type: str):
    """Analyze growth potential for a specific AI type"""
    try:
        logger.info(f"🔍 Analyzing growth potential for {ai_type}")
        result = await growth_service.analyze_growth_potential(ai_type)
        return result
    except Exception as e:
        logger.error(f"Error analyzing growth potential for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis")
async def analyze_all_growth_potential():
    """Analyze growth potential for all AI types"""
    try:
        logger.info("🔍 Analyzing growth potential for all AI types")
        ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
        results = {}
        
        for ai_type in ai_types:
            result = await growth_service.analyze_growth_potential(ai_type)
            results[ai_type] = result
        
        return {
            "ai_growth_analysis": results,
            "timestamp": "2025-07-05T16:00:00Z"
        }
    except Exception as e:
        logger.error("Error analyzing all growth potential", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/implement/{ai_type}")
async def implement_growth_recommendation(ai_type: str, recommendation: Dict[str, Any]):
    """Implement a growth recommendation for an AI type"""
    try:
        logger.info(f"🚀 Implementing growth recommendation for {ai_type}")
        result = await growth_service.implement_growth_recommendation(ai_type, recommendation)
        return result
    except Exception as e:
        logger.error(f"Error implementing growth recommendation for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train-models")
async def train_growth_models():
    """Train the AI growth prediction models"""
    try:
        logger.info("🔄 Training AI growth models")
        await growth_service.train_growth_models()
        return {
            "status": "success",
            "message": "Growth models trained successfully",
            "timestamp": "2025-07-05T16:00:00Z"
        }
    except Exception as e:
        logger.error("Error training growth models", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_growth_insights():
    """Get comprehensive growth insights"""
    try:
        logger.info("📊 Getting AI growth insights")
        insights = await growth_service.get_growth_insights()
        return insights
    except Exception as e:
        logger.error("Error getting growth insights", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_growth_status():
    """Get overall AI growth status"""
    try:
        # Get growth insights
        insights = await growth_service.get_growth_insights()
        
        # Calculate growth metrics
        overall_growth = insights.get('overall_growth', {})
        
        return {
            "growth_status": {
                "system_maturity": overall_growth.get('system_maturity', 'unknown'),
                "average_growth_score": overall_growth.get('average_growth_score', 0.0),
                "total_learning_entries": overall_growth.get('total_learning_entries', 0),
                "expansion_opportunities": overall_growth.get('total_expansion_opportunities', 0)
            },
            "ai_types_status": {
                ai_type: {
                    "growth_stage": insight.get('growth_potential', {}).get('growth_stage', 'unknown'),
                    "growth_score": insight.get('growth_potential', {}).get('growth_score', 0.0),
                    "opportunities_count": len(insight.get('expansion_opportunities', []))
                }
                for ai_type, insight in insights.get('ai_growth_insights', {}).items()
            },
            "timestamp": "2025-07-05T16:00:00Z"
        }
    except Exception as e:
        logger.error("Error getting growth status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-improve")
async def trigger_auto_improvement():
    """Trigger automatic AI improvement cycle"""
    try:
        logger.info("🤖 Triggering automatic AI improvement cycle")
        
        # Get growth insights
        insights = await growth_service.get_growth_insights()
        ai_growth_insights = insights.get('ai_growth_insights', {})
        
        improvements_made = []
        
        # Automatically implement top recommendations for each AI type
        for ai_type, insight in ai_growth_insights.items():
            recommendations = insight.get('growth_recommendations', [])
            
            if recommendations:
                # Get the highest priority recommendation
                top_recommendation = max(recommendations, key=lambda x: x.get('priority', 'low'))
                
                if top_recommendation.get('priority') in ['high', 'medium']:
                    logger.info(f"Auto-implementing {top_recommendation.get('title')} for {ai_type}")
                    
                    result = await growth_service.implement_growth_recommendation(ai_type, top_recommendation)
                    improvements_made.append({
                        'ai_type': ai_type,
                        'recommendation': top_recommendation.get('title'),
                        'result': result.get('result', {}).get('status', 'unknown')
                    })
        
        return {
            "status": "success",
            "improvements_made": improvements_made,
            "total_improvements": len(improvements_made),
            "timestamp": "2025-07-05T16:00:00Z"
        }
    except Exception as e:
        logger.error("Error triggering auto-improvement", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 