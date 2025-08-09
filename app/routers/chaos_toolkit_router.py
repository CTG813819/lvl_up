"""
Chaos Toolkit Router
- Exposes endpoints to register chaos-language tool constructs
- Lists constructs and research catalog
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import structlog

from ..services.chaos_toolkit_service import chaos_toolkit_service

logger = structlog.get_logger()

router = APIRouter(prefix="/api/chaos-toolkit", tags=["Chaos Toolkit"])


@router.post("/register-base-tools")
async def register_base_tools() -> Dict[str, Any]:
    try:
        result = await chaos_toolkit_service.register_base_tools()
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("message", "failed"))
        return result
    except Exception as e:
        logger.error(f"Failed to register base tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/constructs")
async def get_constructs() -> Dict[str, Any]:
    try:
        return {"status": "ok", "constructs": chaos_toolkit_service.get_constructs()}
    except Exception as e:
        logger.error(f"Failed to list constructs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/research-catalog")
async def research_catalog() -> Dict[str, Any]:
    try:
        return chaos_toolkit_service.research_tools_catalog()
    except Exception as e:
        logger.error(f"Failed to get research catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))



