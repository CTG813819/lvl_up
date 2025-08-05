from fastapi import APIRouter, HTTPException
from app.services.conquest_ai_service import ConquestAIService
from app.core.logging import logger

router = APIRouter(prefix="/conquest-ai", tags=["Conquest AI"])

@router.get("/statistics")
async def get_conquest_statistics():
    """Get Conquest AI statistics"""
    try:
        service = ConquestAIService()
        result = await service.get_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting Conquest AI statistics: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/enhanced-statistics")
async def get_enhanced_statistics():
    """Get enhanced Conquest AI statistics including learning data and validation progress"""
    try:
        service = ConquestAIService()
        result = await service.get_enhanced_statistics()
        return result
    except Exception as e:
        logger.error(f"Error getting enhanced Conquest AI statistics: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/deployments")
async def list_deployments():
    """List all Conquest AI deployments"""
    try:
        service = ConquestAIService()
        result = await service.list_deployments()
        return result
    except Exception as e:
        logger.error(f"Error listing Conquest AI deployments: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/create-app")
async def create_app(app_name: str, description: str):
    """Create a new Conquest AI app"""
    try:
        service = ConquestAIService()
        result = await service.create_app(app_name, description)
        return result
    except Exception as e:
        logger.error(f"Error creating Conquest AI app: {str(e)}")
        return {"status": "error", "message": str(e)} 