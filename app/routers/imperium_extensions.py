"""
Imperium Extensions Router
API endpoints for Imperium AI extension creation and management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import structlog

from ..services.imperium_extension_service import ImperiumExtensionService, ExtensionType, ExtensionTarget

logger = structlog.get_logger()
router = APIRouter(prefix="/imperium/extensions", tags=["Imperium Extensions"])


class ExtensionCreateRequest(BaseModel):
    target_ai: str
    extension_type: str
    description: str
    requirements: Dict[str, Any]


class ExtensionTestRequest(BaseModel):
    extension_id: str


class ExtensionDeployRequest(BaseModel):
    extension_id: str


class ExtensionListRequest(BaseModel):
    target_ai: Optional[str] = None
    status: Optional[str] = None


@router.post("/create")
async def create_extension_proposal(request: ExtensionCreateRequest):
    """Create a new extension proposal"""
    try:
        service = ImperiumExtensionService()
        
        # Convert string to enum
        try:
            ext_type = ExtensionType(request.extension_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid extension type: {request.extension_type}")
        
        result = await service.create_extension_proposal(
            target_ai=request.target_ai,
            extension_type=ext_type,
            description=request.description,
            requirements=request.requirements
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating extension proposal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_extension_in_sandbox(request: ExtensionTestRequest):
    """Test extension in sandbox environment"""
    try:
        service = ImperiumExtensionService()
        
        result = await service.test_extension_in_sandbox(request.extension_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing extension: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy")
async def deploy_extension(request: ExtensionDeployRequest):
    """Deploy extension after successful testing"""
    try:
        service = ImperiumExtensionService()
        
        result = await service.deploy_extension(request.extension_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error deploying extension: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_extension_analytics():
    """Get extension creation analytics"""
    try:
        service = ImperiumExtensionService()
        
        analytics = await service.get_extension_analytics()
        
        if "error" in analytics:
            raise HTTPException(status_code=500, detail=analytics["error"])
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting extension analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_extensions(target_ai: Optional[str] = None, status: Optional[str] = None):
    """List extensions with optional filtering"""
    try:
        service = ImperiumExtensionService()
        
        result = await service.list_extensions(target_ai=target_ai, status=status)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing extensions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{extension_id}")
async def get_extension_details(extension_id: str):
    """Get detailed information about an extension"""
    try:
        service = ImperiumExtensionService()
        
        result = await service.get_extension_details(extension_id)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting extension details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_extension_types():
    """Get available extension types"""
    try:
        return {
            "extension_types": [e.value for e in ExtensionType],
            "target_ais": [t.value for t in ExtensionTarget]
        }
        
    except Exception as e:
        logger.error(f"Error getting extension types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-test")
async def batch_test_extensions(background_tasks: BackgroundTasks):
    """Test all pending extensions in background"""
    try:
        service = ImperiumExtensionService()
        
        # Get all pending extensions
        pending_extensions = await service.list_extensions(status="proposed")
        
        if pending_extensions.get("status") == "error":
            raise HTTPException(status_code=400, detail=pending_extensions["message"])
        
        # Add background task to test all pending extensions
        background_tasks.add_task(_batch_test_extensions, pending_extensions["extensions"])
        
        return {
            "status": "success",
            "message": f"Started batch testing of {len(pending_extensions['extensions'])} extensions",
            "extensions_count": len(pending_extensions["extensions"])
        }
        
    except Exception as e:
        logger.error(f"Error starting batch test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _batch_test_extensions(extensions: List[Dict[str, Any]]):
    """Background task to test multiple extensions"""
    try:
        service = ImperiumExtensionService()
        
        for extension in extensions:
            try:
                await service.test_extension_in_sandbox(extension["id"])
                logger.info(f"Batch tested extension: {extension['id']}")
            except Exception as e:
                logger.error(f"Error batch testing extension {extension['id']}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in batch testing: {str(e)}")


@router.post("/auto-deploy")
async def auto_deploy_tested_extensions(background_tasks: BackgroundTasks):
    """Automatically deploy all tested extensions"""
    try:
        service = ImperiumExtensionService()
        
        # Get all tested extensions
        tested_extensions = await service.list_extensions(status="tested")
        
        if tested_extensions.get("status") == "error":
            raise HTTPException(status_code=400, detail=tested_extensions["message"])
        
        # Add background task to deploy all tested extensions
        background_tasks.add_task(_auto_deploy_extensions, tested_extensions["extensions"])
        
        return {
            "status": "success",
            "message": f"Started auto-deployment of {len(tested_extensions['extensions'])} extensions",
            "extensions_count": len(tested_extensions["extensions"])
        }
        
    except Exception as e:
        logger.error(f"Error starting auto-deploy: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def _auto_deploy_extensions(extensions: List[Dict[str, Any]]):
    """Background task to deploy multiple extensions"""
    try:
        service = ImperiumExtensionService()
        
        for extension in extensions:
            try:
                await service.deploy_extension(extension["id"])
                logger.info(f"Auto-deployed extension: {extension['id']}")
            except Exception as e:
                logger.error(f"Error auto-deploying extension {extension['id']}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in auto-deployment: {str(e)}") 