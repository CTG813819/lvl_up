"""
Chaos Toolkit Router
- Exposes endpoints to register chaos-language tool constructs
- Lists constructs and research catalog
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import structlog

from ..services.chaos_toolkit_service import chaos_toolkit_service
from ..services.chaos_execution_service import chaos_execution_service
from ..services.chaos_language_service import chaos_language_service

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


@router.post("/sys/run")
async def sys_run(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single chaos-language system run (safely)."""
    try:
        return await chaos_execution_service.sys_run(
            payload.get("target_system"),
            payload.get("command") or payload.get("argv"),
            cwd=payload.get("cwd"),
            timeout=payload.get("timeout"),
        )
    except Exception as e:
        logger.error(f"sys.run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sys/pipeline")
async def sys_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a chaos-language pipeline across steps (safely)."""
    try:
        steps = payload.get("steps") or []
        return await chaos_execution_service.sys_pipeline(steps)
    except Exception as e:
        logger.error(f"sys.pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest-constructs")
async def latest_constructs(limit: int = 50) -> Dict[str, Any]:
    """Return latest chaos-language constructs with origin and timestamps for dashboard display."""
    try:
        doc = await chaos_language_service.get_complete_chaos_language_documentation()
        core = doc.get("language_core", {})
        derived = core.get("ai_derived_constructs", {})
        weapons = core.get("weapon_specific_constructs", {})
        all_items = []
        for name, data in {**derived, **weapons}.items():
            created = data.get("created") or data.get("timestamp") or ""
            origin = data.get("origin", "unknown")
            domain = data.get("domain") or data.get("weapon_category") or "general"
            all_items.append({
                "name": name,
                "origin": origin,
                "domain": domain,
                "syntax": data.get("syntax", ""),
                "created": created,
            })
        # Sort descending by created (fallback name)
        def _key(item):
            return item.get("created") or ""
        all_items.sort(key=_key, reverse=True)
        return {"items": all_items[: max(1, min(500, int(limit)))], "total": len(all_items)}
    except Exception as e:
        logger.error(f"latest_constructs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))



