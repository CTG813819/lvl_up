"""
Custodes AI Router - API endpoints for Custodes AI service
Provides endpoints for security testing and monitoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.services.custodes_ai_service import custodes_ai_service, CustodesTestType

logger = structlog.get_logger()
router = APIRouter(prefix="/api/custodes-ai", tags=["Custodes AI"])

# Pydantic models
class CustodesTestRequest(BaseModel):
    ai_type: str
    test_type: str
    severity_level: str = "medium"

@router.post("/tests/initiate")
async def initiate_custodes_test(request: CustodesTestRequest):
    """Initiate a Custodes test for an AI system"""
    try:
        logger.info("🛡️ Initiating Custodes test", ai_type=request.ai_type, test_type=request.test_type)
        
        # Convert string to CustodesTestType enum
        try:
            test_type = CustodesTestType(request.test_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid test type. Must be one of: {[t.value for t in CustodesTestType]}")
        
        result = await custodes_ai_service.initiate_custodes_test(request.ai_type, test_type, request.severity_level)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Custodes test completed", test_id=result["test_id"])
        
        return {
            "status": "success",
            "message": "Custodes test completed",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error initiating Custodes test", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tests/history")
async def get_custodes_test_history(ai_type: Optional[str] = None):
    """Get Custodes test history"""
    try:
        logger.info("📋 Getting Custodes test history", ai_type=ai_type)
        
        result = await custodes_ai_service.get_custodes_test_history(ai_type)
        
        return {
            "status": "success",
            "message": "Custodes test history retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Custodes test history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_custodes_statistics():
    """Get comprehensive Custodes statistics"""
    try:
        logger.info("📊 Getting Custodes statistics")
        
        result = await custodes_ai_service.get_custodes_statistics()
        
        return {
            "status": "success",
            "message": "Custodes statistics retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Custodes statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-types")
async def get_available_test_types():
    """Get available Custodes test types"""
    try:
        logger.info("🎯 Getting available Custodes test types")
        
        result = await custodes_ai_service.get_available_test_types()
        
        return {
            "status": "success",
            "message": "Available Custodes test types retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting available Custodes test types", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_custodes_ai_status():
    """Get Custodes AI system status"""
    try:
        logger.info("📊 Getting Custodes AI status")
        
        statistics = await custodes_ai_service.get_custodes_statistics()
        
        status = {
            "service": "Custodes AI",
            "status": "operational",
            "total_tests": statistics["total_tests"],
            "total_vulnerabilities": statistics["total_vulnerabilities"],
            "test_types": len(statistics["test_types"]),
            "learning_progress": statistics["learning_progress"],
            "custodes_complexity": statistics["custodes_complexity"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Custodes AI status retrieved",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Custodes AI status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 