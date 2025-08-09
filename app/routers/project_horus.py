"""
Project Horus Router - API endpoints for Project Horus service
Provides endpoints for Chaos code generation and assimilation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.services.project_horus_service import project_horus_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/project-horus", tags=["Project Horus"])

# Pydantic models
class ChaosCodeRequest(BaseModel):
    target_context: Optional[str] = None

class AssimilationRequest(BaseModel):
    target_codebase: str

class DeployChaosRequest(BaseModel):
    chaos_id: str
    target_system: str

@router.post("/chaos/generate")
async def generate_chaos_code(request: ChaosCodeRequest):
    """Generate brand new Chaos code for assimilation and attack"""
    try:
        logger.info("🌀 Generating Chaos code", context=request.target_context)
        
        result = await project_horus_service.generate_chaos_code(request.target_context)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Chaos code generated successfully", chaos_id=result["chaos_id"])
        
        return {
            "status": "success",
            "message": "Chaos code generated successfully",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error generating Chaos code", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assimilate")
async def assimilate_existing_code(request: AssimilationRequest):
    """Assimilate knowledge from existing codebase"""
    try:
        logger.info("🔄 Assimilating existing codebase", target=request.target_codebase)
        
        result = await project_horus_service.assimilate_existing_code(request.target_codebase)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Codebase assimilation completed", target=request.target_codebase)
        
        return {
            "status": "success",
            "message": "Codebase assimilation completed",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error assimilating codebase", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chaos/deploy")
async def deploy_chaos_code(request: DeployChaosRequest):
    """Deploy Chaos code to target system"""
    try:
        logger.info("🚀 Deploying Chaos code", chaos_id=request.chaos_id, target=request.target_system)
        
        result = await project_horus_service.deploy_chaos_code(request.chaos_id, request.target_system)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("✅ Chaos code deployed successfully", chaos_id=request.chaos_id)
        
        return {
            "status": "success",
            "message": "Chaos code deployed successfully",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error deploying Chaos code", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chaos/repository")
async def get_chaos_code_repository():
    """Get all generated Chaos code"""
    try:
        logger.info("📚 Getting Chaos code repository")
        
        result = await project_horus_service.get_chaos_code_repository()
        
        return {
            "status": "success",
            "message": "Chaos code repository retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Chaos code repository", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chaos/{chaos_id}")
async def get_chaos_code_by_id(chaos_id: str):
    """Get specific Chaos code by ID"""
    try:
        logger.info("🔍 Getting Chaos code by ID", chaos_id=chaos_id)
        
        result = await project_horus_service.get_chaos_code_by_id(chaos_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Chaos code not found")
        
        return {
            "status": "success",
            "message": "Chaos code retrieved",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("❌ Error getting Chaos code by ID", error=str(e), chaos_id=chaos_id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_project_horus_status():
    """Get Project Horus system status"""
    try:
        logger.info("📊 Getting Project Horus status")
        
        # Prefer comprehensive live status if available
        live_status = await project_horus_service.get_project_horus_status()
        if "error" not in live_status:
            return {
                "status": "success",
                "message": "Project Horus status retrieved",
                "data": live_status,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Fallback: repository-based basic status
        repository = await project_horus_service.get_chaos_code_repository()
        status = {
            "service": "Project Horus",
            "status": "operational",
            "chaos_codes_generated": repository.get("total_codes", 0),
            "learning_progress": repository.get("learning_progress", 0.0),
            "chaos_complexity": repository.get("chaos_complexity", 0.0),
            "knowledge_base_size": repository.get("knowledge_base_size", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Project Horus status retrieved",
            "data": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("❌ Error getting Project Horus status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 