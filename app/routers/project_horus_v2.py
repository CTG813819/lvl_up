from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import structlog

from app.services.project_horus_service import project_horus_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/project-horus-v2", tags=["Project Horus V2"])


@router.get("/status")
async def get_project_horus_status_v2() -> Dict[str, Any]:
    """Alias for Project Horus status expected by the frontend (v2 path)."""
    try:
        status = await project_horus_service.get_project_horus_status()
        if "error" in status:
            raise HTTPException(status_code=500, detail=status["error"])
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project Horus V2 status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-test/results")
async def get_system_test_results_v2() -> Dict[str, Any]:
    """Alias for system test results expected by the frontend (v2 path)."""
    try:
        results = await project_horus_service.get_system_test_results()
        return results
    except Exception as e:
        logger.error(f"Project Horus V2 system-test results failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
